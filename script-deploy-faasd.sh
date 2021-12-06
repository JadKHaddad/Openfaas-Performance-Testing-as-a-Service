#!/bin/bash

#deploy function
sudo cat /var/lib/faasd/secrets/basic-auth-password | faas-cli login -s
cd /etc/Openfaas-Performance-Testing-as-a-Service/
sudo faas-cli up -f ptas.yml