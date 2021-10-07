# Performance Testing


## Installation

Install Mulltipass from https://multipass.run/<br />
Download **cloud.config** file to your environment<br />
Replace the public key in **cloud.config** with your own public key<br /><br />
Boot the VM:
```sh
multipass launch --cloud-init cloud-config.txt  --name performance --cpus 4 --mem 4G --disk 20G
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
Once you are logged in, deploy the Openfaas function:
```sh
sudo faas-cli up -f /etc/Openfaas-Performance-Testing-as-a-Service/ptas.yml
```
Paste the VM's IP in your browser

