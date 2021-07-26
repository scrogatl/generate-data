#!/bin/bash


#### Functions ###
display_usage() { 
	echo -e "Usage: ./gen_metric.sh [metric.name] [metric value]"
} 

# Check params
#if [  $# -lt 1 ] 
#then 
#	display_usage
#	exit 1
#fi 

if [ -z "$1" ]
then 
	METRIC=cs.tickets
else 
	VALUE=$1
fi


if [ -z "$2" ]
then 
	VALUE=$((213 + $RANDOM % 425))
else 
	VALUE=$2
fi
TOKEN=<API KEY HERE>
URL=https://longboard.wavefront.com/report

date
echo "Sending $METRIC $VALUE" 
curl -H "Authorization: Bearer $TOKEN" --data "$METRIC $VALUE source=deb-docker-host" $URL



