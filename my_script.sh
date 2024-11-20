#!/bin/bash
URL=<Rest API Endpoint>
while true; do
	echo "$(date +%F_%H%M%S) - $(curl -s $URL)"
	sleep 5
done
