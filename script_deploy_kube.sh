#!/bin/bash

while true
do
    #check if openfaas is ready
    if [ $(systemctl is-active port-forward.service) = "active" ]; then
    #deploy function
    (sudo kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo) | sudo faas-cli login -s
    cd /etc/Openfaas-Performance-Testing-as-a-Service/
    sudo faas-cli up -f ptas.yml
    break
    fi
    sleep 2
done