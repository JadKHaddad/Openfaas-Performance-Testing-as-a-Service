# Performance Testing
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenFaaS](https://img.shields.io/static/v1?label=OpenFaaS&message=Serverless&color=blue)](https://www.openfaas.com/)
[![Multipass](https://img.shields.io/static/v1?label=Multipass&message=VM&color=orange)](https://multipass.run/)
[![Locust](https://img.shields.io/static/v1?label=Locust&message=Load-Testing&color=green)](https://locust.io/)

## Installation

Get [multipass.run](https://multipass.run)<br /><br />
Get **cloud-config-local.txt**<br />

```sh
curl -sSLO https://raw.githubusercontent.com/JadKHaddad/Openfaas-Performance-Testing-as-a-Service/main/cloud-config-local.txt
```
Replace the public key in **cloud-config-local.txt** with your own public key<br /><br />
Boot the VM:
```sh
multipass launch --cloud-init cloud-config-local.txt --name performance --cpus 2 --mem 2G --disk 10G
```
Get the VM's IP:
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
```sh
IPv4:           172.17.136.33
```

## Usage
Paste the VM's **IP** in your browser<br /><br />

## Notes
The VM's **IP** may change with time. View the VM's **IP** if needed:
```sh
 multipass info performance
```

## Or use Docker instead
Build the image:
```sh
docker build -t  performance:1.0 .
```
Run the image in a container:
```sh
docker run -p 5000:8080 performance:1.0 -l -p 8080
```
Or run it in an **interactive** container:
```sh
docker run --rm -it -p 5000:8080  performance:1.0 -l -p 8080
```
Visit **localhost:5000**

## You can also use a Redis container
Pull the official Redis image:
```sh
docker pull redis
```
Create a new network:
```sh
docker network create network
```
Run Redis:
```sh
docker run --rm -it --network network --name redis redis:latest
```
Run Performance:
```sh
docker run --rm -it -p 5000:8080 --network network performance:1.0 -l -p 8080 -r -rh redis
```
Or use docker-compose after building the image, creating the network and pulling redis:
```sh
docker-compose up
```
Visit **localhost:5000**

## Or install locally
Install requirements:
```sh
pip3 install -r requirements.txt
pip3 install -r ptas/requirements.txt
```
Run: ```recommended:``` navigate to /server/ directory:
```sh
cd server/
```

```sh
python3 server.py -l -p 5000
```
Visit **localhost:5000** <br /> <br />
For more help use:
```sh
python3 server.py -h
```
```sh
usage: server.py [-h] [-v] [-e] [-l] [-r] [-rh] [-rp] [-re] [-s] [-p] [-u] [-f] [-d]

optional arguments:
  -h, --help            help
  -v, --version         version
  -e, --extern          use if OpenFaaS is running on the external ip address of your machine
  -l, --local           use if you dont want to use an OpenFaaS server. server will run on 0.0.0.0:80 with no OpenFaaS server
  -r, --redis           use redis (cache). recommended if you dont have SSD
  -rh, --redishost      redis host, default: localhost
  -rp, --redisport      redis port, default: 6379
  -re, --redisexpire    redis (cache) expiration timer, default: 600 seconds
  -rd, --redisdatabase  redis database: 0 - 15, default: 0

required arguments:
  -s, --host            server host, default: 0.0.0.0
  -p, --port            server port, default: 80
  -u, --url             OpenFaaS url
  -f, --function        function name
  -d, --direct          can the browser connect to OpenFaaS directly?
```

## TODO
* Windows comp.

## Contributors
* Jad K. Haddad <jadkhaddad@gmail.com>

## License & copyright
© 2021 Jad K. Haddad
Licensed under the [MIT License](LICENSE).

## You may also like
[Multipass + OpenFaaS + Performance Testing [Faasd + Containerd]](Multipass-OpenFaaS-Performance-Testing-Service.md)<br />
[Multipass + OpenFaaS + Performance Testing [Kubernetes + Docker]](Multipass-OpenFaaS-Performance-Testing-Service-kube.md)<br />
[Multipass + OpenFaaS + Performance Testing [Microk8s + Docker]](Multipass-OpenFaaS-Performance-Testing-Service-k8s.md)<br />
[Local Serverless Functions Deployment [Kubernetes + OpenFaaS]](Local-Serverless-Functions-Deployment-Kubernetes-and-OpenFaas.md)<br />
[Multipass Ubuntu-Host Port-Forwarding](Multipass-Ubuntu-Host-Port-Forwarding.md)<br />
[Raising the Maximum Number of File Descriptors (Open Files) on Ubuntu](Raising-the-Maximum-Number-of-File-Descriptors-(Open-Files)-on-Ubuntu.md)<br />
[Faasd with Multipass](https://github.com/openfaas/faasd/blob/master/docs/MULTIPASS.md)


