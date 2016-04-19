#! /bin/bash
test=`ping -q -c 1 -t2 $1 > /dev/null`

if [ $? -eq 0 ]; then
	
	echo 0
else
	echo 1
fi
