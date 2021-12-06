#!/bin/bash

printf "deploying\n" | tee -a /home/ubuntu/log.txt
#deploy function
(sudo kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo) | sudo faas-cli login -s
cd /etc/Openfaas-Performance-Testing-as-a-Service/
sudo faas-cli up -f ptas-k8s.yml
#finished
printf "finish deploying\n" | tee -a /home/ubuntu/log.txt
touch /home/ubuntu/done.txt