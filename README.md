# Performance Testing


## Installation

Install Mulltipass from https://multipass.run/<br />
Download **cloud-config.txt** file to your environment<br />
Replace the public key in **cloud-config.txt** with your own public key<br /><br />
Boot the VM:
```sh
multipass launch --cloud-init cloud-config.txt --name performance --cpus 6 --mem 6G --disk 20G
```
Get the VM's IP and connect with **ssh**:
```sh
 multipass info performance
```
```sh
Name:           performance
State:          Running
IPv4:           172.17.136.33
                172.18.0.1
                10.62.0.1
Release:        Ubuntu 20.04.3 LTS
Image hash:     db49f99b5162 (Ubuntu 20.04 LTS)
Load:           0.28 0.12 0.04
Disk usage:     7.8G out of 19.2G
Memory usage:   1.2G out of 6.0G
Mounts:         --
```
Set the variable **IP**:
```sh
export IP="172.17.136.33"
```
Connect to the VM listed via **ssh**:
```sh
ssh ubuntu@$IP
```
Once you are logged in, deploy the **OpenFaaS** function:
```sh
sudo faas-cli up -f /etc/Openfaas-Performance-Testing-as-a-Service/ptas.yml
```
## Usage

Paste the VM's **IP** in your browser<br /><br />

## OpenFaaS REST API

Use port 8080 for the **OpenFaaS REST API**<br />
```sh
username: admin
password: ie9ZhJhq5aqoYXb6uPrKF4DbvIoonfwuxpmu2JnicmDMMJO8tOsnc9jOG730DuW
```
Get your password:
```sh
ssh ubuntu@$IP "sudo cat /var/lib/faasd/secrets/basic-auth-password"
```
or directly in the VM:
```sh
sudo cat /var/lib/faasd/secrets/basic-auth-password
```



