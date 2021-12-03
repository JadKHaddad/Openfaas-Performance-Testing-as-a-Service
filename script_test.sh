#!/bin/bash

touch /home/ubuntu/test.txt
while true
do
    now=$(date +"%T")
    printf "$now"| tee -a /home/ubuntu/test.txt
    sleep 2
done