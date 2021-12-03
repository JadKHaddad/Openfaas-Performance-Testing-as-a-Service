#!/bin/bash

while true
do
    if [ $(systemctl is-active performance-testing.service) = "active" ]; then
    echo "Active. leaving."
#deploy function
    touch done.txt
    break
    fi
    sleep 2
done