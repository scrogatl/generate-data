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
	METRIC=cs.tickets.closetime
else 
	VALUE=$1
fi


if [ -z "$2" ]
then 
	VALUE=$((60000 + $RANDOM % 3600000))
else 
	VALUE=$2
fi
TOKEN=<API KEY HERE>
URL=https://longboard.wavefront.com/report
SOURCE=<SOURCE / HOST HERE>

date
echo "Sending $METRIC $VALUE" 
curl -H "Authorization: Bearer $TOKEN" --data "$METRIC $VALUE source=$SOURCE" $URL



