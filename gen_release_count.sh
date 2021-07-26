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
	METRIC=cs.releases
else 
	VALUE=$1
fi

if [ -z "$2" ]
then 
	VALUE=$((1 + $RANDOM % 10))
else 
	VALUE=$2
fi
METRIC=cs.releases
TOKEN=<API KEY HERE>
URL=https://longboard.wavefront.com/report
TYPES=("Bug Fix" "New Feature")
selectedType=${TYPES[$RANDOM % 2]}
date
echo "Sending $METRIC $VALUE $selectedType" 
curl -H "Authorization: Bearer $TOKEN" --data "$METRIC $VALUE source=$SOURCE type=\"$selectedType\" " $URL



