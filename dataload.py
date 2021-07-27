#!/usr/bin/env python

import sys, getopt, time, socket, os

# Wavefront re-time metrics data utility
# --------------------------------------
# author: Howard Yoo
# created: May 11, 2019
# 
# read a file (txt), and
# get the third token which is timestamp (delimited by white space)
# get start and end time by accessing first and last row of the file
# scan through the file, and calculate the time.
# the assumptions:
# 1. all the timestamps in the file are sorted in ASC order
# 2. data is in Wavefront format
#
# the script will get the mid point time of the data, via start and end time, and align this mid point
# with whatever current time it is running, back-filling the first half, and then filling the lattter half in
# per second intervals.
# 
# The script may not handle a VERY large file, as it is going to buffer the latter half into memory, all at once

# global variables
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 2878
# when enabled, prints output to stdout, rather than to the socket
# when disabled, it will send the data to proxy host and port in socket communication
DEBUG = False

# extracts timestamp value from the wf data line
def getTimestamp(line):
  tokens = line.split(" ", 4)
  return long(tokens[2])

# updates the timestamp value from the wf data line
def updateTimestamp(line, newtime):
  tokens = line.split(" ")
  s = tokens[0] + " " + tokens[1] + " " + str(newtime)
  for t in tokens[3:]:
    s += " " + t
  return s

# reads lines of file from backward
def readlines_reverse(filename):
  with open(filename) as qfile:
    qfile.seek(0, os.SEEK_END)
    position = qfile.tell()
    line = ''
    while position >= 0:
      qfile.seek(position)
      next_char = qfile.read(1)
      if next_char == "\n":
        yield line[::-1]
        line = ''
      else:
        line += next_char
      position -= 1
    yield line[::-1]

# print out help
def print_help():
  print 'dataload.py -i <inputfile> [-d] [-t <proxy_host>] [-p <proxy_port>]'

# the main function
def main(argv):
  DEBUG = False
  inputfile = ''
  try:
    opts, args = getopt.getopt(argv, "h:i:d:t:p:", ["help","input","debug","target","port"])
  except getopt.GetOptError:
    print_help()
    sys.exit(2)
  for opt, arg in opts:
    if opt in ("-h", "--help"):
      print_help()
      sys.exit()
    elif opt in ("-i", "--input"):
      inputfile = arg
    elif opt in ("-d", "--debug"):
      DEBUG = True
    elif opt in ("-t", "--target"):
      PROXY_HOST = arg
    elif opt in ("-p", "--port"):
      PROXY_PORT = int(arg)

  if inputfile == '':
    print_help()
    sys.exit(2)

  # time measurement
  start = 0
  end = 0
  mid = 0

  # first, read line from the start and get the starting timestamp,
  # assuming all the timestamps are properly sorted in ASC order in
  # the file. This will break if timestamps are NOT sorted.
  with open(inputfile) as fp:
    line = fp.readline()
    cnt = 1
    while line:
      if len(line.strip()) > 0:
        timestamp = getTimestamp(line)
        if cnt == 1:
          start = timestamp
          break
        end = timestamp
        cnt += 1
      line = fp.readline()

  # then, read line in reverse order and get the last timestamp of the
  # file.
  for rline in readlines_reverse(inputfile):
    if len(rline.strip()) > 0:
      timestamp = getTimestamp(rline)
      end = timestamp
      break; 

  # get current time
  epoch_time = int(time.time())
  # calcualte mid time
  mid = ((end - start) / 2) + start

  # retime start epoch sec
  r_start = epoch_time - mid

  print "> Running re-time utility..."
  if DEBUG is True:
    print "> DEBUG mode is true (output to be printed into stdout)."
  print "> ------------ Timestamp Range Found in {:s} ------------".format(inputfile)
  print "> start:",start,"midpoint:",mid,"end:",end,"(unit: epoch sec)"

  # futures metrics data which need to be buffered
  future = []

  s = ''
  if DEBUG is False:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((PROXY_HOST, PROXY_PORT))
  # second loop to produce updates
  with open(inputfile) as fp:
    line = fp.readline()
    cnt = 1
    while line:
      if len(line.strip()) > 0:
        timestamp = getTimestamp(line)
        diff = mid - timestamp
        newtime = epoch_time - diff
        ns = updateTimestamp(line.strip(), newtime)
        if newtime <= epoch_time:
          # >>>>>>>>>>>>>> SEND IT TO WAVEFRONT (BACKFILL)
          if DEBUG is False:
            print("sending to to: " + ns)
            s.send(ns + "\n")
          else:
            print ns
        else:
          # print "buffering:",ns
          future.append(ns)
      line = fp.readline()

  if DEBUG is False:
    s.close()
  print "> Half point data backfilled until current time: {:d}".format(epoch_time)

  # now, for a given interval, iterating over the future buffer,
  # until all the data in the buffer are depleted.
  future_size = len(future)
  print "> Future buffer size is {:d}".format(future_size)
  print "> Filling up the data using future data..."
  now = 0
  while future_size > now:
    curr_time = int(time.time())
    line = future[now]
    ft = getTimestamp(line)
    s = ''
    if DEBUG is False:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((PROXY_HOST, PROXY_PORT))
    while ft <= curr_time and future_size > now:
      # >>>>>>>>>>>>> SEND IT TO WAVEFRONT
      if DEBUG is False: 
        s.send(line + "\n")
      else:
        print line
      now += 1
      if future_size > now:
        line = future[now]
        ft = getTimestamp(line)
    if DEBUG is False:
      s.close()
    time.sleep(1)

  # after everything is done, end the loading
  print "> End of data reached, exiting..."

if __name__ == "__main__":
  main(sys.argv[1:])

