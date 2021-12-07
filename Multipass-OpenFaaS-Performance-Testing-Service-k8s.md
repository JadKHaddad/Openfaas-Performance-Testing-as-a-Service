# Multipass + OpenFaaS + Performance Testing [Microk8s + Docker]

## Installation

Get [multipass.run](https://multipass.run)<br /><br />
Get **cloud-config-kubernetes.txt**<br />

```sh
curl -sSLO https://raw.githubusercontent.com/JadKHaddad/Openfaas-Performance-Testing-as-a-Service/main/cloud-config-microk8s.txt
```
Replace the public key in **cloud-config-microk8s.txt** with your own public key<br /><br />
Boot the VM:
```sh
multipass launch --cloud-init cloud-config-microk8s.txt --name performance --cpus 6 --mem 6G --disk 20G
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
or:
```sh
multipass shell performance
```
**OpenFaaS** function will be deployed in the background. Check the **OpenFaaS** function status in the **OpenFaaS** tab in your browser. If the function faild to deploy automatically, you can deploy it manually with:
```sh
sudo /etc/Openfaas-Performance-Testing-as-a-Service/script-deploy-k8s.sh 
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
PASSWORD=$(sudo kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo $PASSWORD
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


