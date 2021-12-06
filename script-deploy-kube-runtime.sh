#!/bin/bash

printf "checking if first script is done\n" | tee -a /home/ubuntu/log.txt
while true
do
    #check if first script is done
    FILE=/home/ubuntu/done.txt
    if [[ -f "$FILE" ]]; then
        break
    fi
    sleep 2
done
printf "deploying again\n" | tee -a /home/ubuntu/log.txt
#deploy function
(sudo kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo) | sudo faas-cli login -s
cd /etc/Openfaas-Performance-Testing-as-a-Service/
sudo faas-cli deploy -f ptas.yml
#finished
printf "finish second deployment\n" | tee -a /home/ubuntu/log.txt
