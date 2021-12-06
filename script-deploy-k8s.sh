#!/bin/bash

printf "checking\n" | tee -a /home/ubuntu/log.txt
while true
do
    #check if openfaas is ready
    if [ $(systemctl is-active port-forward-k8s.service) = "active" ]; then
    break
    fi
    sleep 2
done
printf "deploying\n" | tee -a /home/ubuntu/log.txt
#deploy function
(sudo kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo) | sudo faas-cli login -s
cd /etc/Openfaas-Performance-Testing-as-a-Service/
sudo faas-cli up -f ptas-k8s.yml
#finished
printf "finish deploying\n" | tee -a /home/ubuntu/log.txt
touch /home/ubuntu/done.txt