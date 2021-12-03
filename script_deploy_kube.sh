#!/bin/bash

while true
do
    if [ $(systemctl is-active port-forward.service) = "active" ]; then
    touch /home/ubuntu/port_forward_running.txt
#deploy function

    (sudo kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo) | sudo faas-cli login -s
    cd /etc/Openfaas-Performance-Testing-as-a-Service/
    sudo faas-cli up -f ptas.yml

    touch /home/ubuntu/deployed.txt
    break
    fi
    sleep 2
done