# Performance Testing
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

Get [multipass.run](https://multipass.run)<br /><br />
Get **cloud-config.txt**<br />

```sh
curl -sSLO https://raw.githubusercontent.com/JadKHaddad/Openfaas-Performance-Testing-as-a-Service/main/cloud-config.txt
```
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
Connect to the VM listed with **ssh**:
```sh
ssh ubuntu@$IP
```
Once you are logged in, deploy the **OpenFaaS** function:
```sh
cd /etc/Openfaas-Performance-Testing-as-a-Service/
sudo faas-cli up -f ptas.yml
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

## Notes
The VM's **IP** may change with time. View the VM's **IP** if needed:
```sh
 multipass info performance
```
Restart the VM to handle **IP** changes:
```sh
 multipass restart performance
```
or restart the service in the VM: ```recommended```
```sh
sudo systemctl restart performance-testing.service
```

## TODO
* check extension of locust file before upload.
* enable in browser locust code editing.
* enable tests redeployment after editing.
* enable (in browser) choosing different openfaas servers.  

## Contributors
* Jad K. Haddad <jadkhaddad@gmail.com>

## License & copyright

© 2021 Jad K. Haddad
Licensed under the [MIT License](LICENSE).


