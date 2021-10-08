## Local Serverless Functions Deployment [Kubernetes + OpenFaas]
Please read the notes at the end of the article<br /><br />

* Get [docker](https://www.docker.com/)<br /><br />
Linux users:<br />
Create the docker group if it does not exist:
```sh
sudo groupadd docker
```
Add your user to the docker group:
```sh
sudo usermod -aG docker $USER
```
Run the following command or Logout and login again and run (that doesn't work you may need to reboot your machine first):
```sh
newgrp docker
```
Check if docker can be run without root:
```sh
docker run hello-world
```
Reboot if still got error:
```sh
reboot
```
* Get **arkade**:

```sh
# Note: you can also run without `sudo` and move the binary yourself
curl -sLS https://get.arkade.dev | sudo sh

arkade --help
ark --help  # a handy alias

# Windows users with Git Bash
curl -sLS https://get.arkade.dev | sh
```
Windows users: arkade requires bash to be available, therefore Windows users can [install Git bash](https://git-scm.com/downloads)

* Get **kind, kubectl and faas-cli**:
```sh
arkade get kind
arkade get kubectl
arkade get faas-cli
```
* Set up a local docker registry
```sh
curl -sSLO https://kind.sigs.k8s.io/examples/kind-with-registry.sh
```
Linux users: make **kind-with-registry** executable:
```sh
chmod -x kind-with-registry.sh
```
* Add **localhost:5000** to docker's insecure registries<br /><br />
Windows users:<br />
image<br /><br />
Linux users: create **/etc/docker/daemon.json** file:
```sh
sudo touch /etc/docker/daemon.json
```
Paste the following text into the file:
```sh
{
    "insecure-registries":["localhost:5000"]
}
```
Save the file and restart **docker**<br /><br />
* Create kind cluster:
```sh
./kind-with-registry.sh
```
This may take a few minutes<br /><br />
* Wait until the nodes are ready:
```sh
kubectl get nodes

NAME                 STATUS   ROLES                  AGE    VERSION
kind-control-plane   Ready    control-plane,master   4d3h   v1.21.1
```
* Wait until the services are running:
```sh
kubectl get pods -n kube-system

NAME                                         READY   STATUS    RESTARTS   AGE
coredns-558bd4d5db-cgwfr                     1/1     Running   9          4d3h
coredns-558bd4d5db-tpvxr                     1/1     Running   9          4d3h
etcd-kind-control-plane                      1/1     Running   9          4d3h
kindnet-mc826                                1/1     Running   9          4d3h
kube-apiserver-kind-control-plane            1/1     Running   9          4d3h
kube-controller-manager-kind-control-plane   1/1     Running   10         4d3h
kube-proxy-bfn9n                             1/1     Running   9          4d3h
kube-scheduler-kind-control-plane            1/1     Running   10         4d3h
```
* Check if the registry is working:
```sh
docker logs -f kind-registry
```
* Install **openfaas**:
```sh
arkade install openfaas
```
*  Wait until openfaas services are running:
```sh
kubectl get pods -n openfaas

NAME                                 READY   STATUS    RESTARTS   AGE
alertmanager-68b4dbc886-n5j85        1/1     Running   9          4d3h
basic-auth-plugin-86d54f7c5f-nlxdc   1/1     Running   9          4d3h
gateway-55b44cd855-n2mph             2/2     Running   28         4d3h
nats-76844df8b4-fm28b                1/1     Running   9          4d3h
prometheus-6595ccc46c-56ccz          1/1     Running   9          4d3h
queue-worker-85545c4bd8-fdfk8        1/1     Running   22         4d3h
```
* View templates:
```sh
faas-cli template store list
```
or visit [openfaas templates](https://github.com/openfaas/templates)
* Pull a template:
```sh
faas-cli template store pull <template-name>
```
* Create a new function:
```sh
faas-cli new <function-name> --lang <template-name>
```
* Edit your **yml** file:
```sh
version: 1.0
provider:
  name: openfaas
  gateway: http://127.0.0.1:8080
functions:
  <function-name>:
    lang: <template-name>
    handler: ./<function-name>
    image: localhost:5000/<function-name>:latest
```
* Enable port forwarding:
```sh
kubectl port-forward -n openfaas svc/gateway 8080:8080
```
* Get your **openfaas** password:
```sh
PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
```
* Authenticate **fass-cli**:
```sh
echo -n $PASSWORD | faas-cli login -s
```
* In your browser, navigate to 127.0.0.1:8080 for the **OpenFaaS REST API** and log in using:
```sh
username: admin
password: $PASSWORD
```
* **Build** your function:
```sh
faas-cli build -f <function-name>.yml
```
* **Push** your function to the **docker** registry:
```sh
faas-cli push -f <function-name>.yml
```
* **Deploy** your function:
```sh
faas-cli deploy -f <function-name>.yml
```
* You can **build, push and deploy** your function with one command:
```sh
faas-cli up -f <function-name>.yml
```
* **Invoke** your function:<br />
```sh
# sync:
curl -i -d "input" http://127.0.0.1/function/<function-name>

# async:
curl -i -d "input" http://127.0.0.1/async-function/<function-name>

# async with a callback:
curl -i -d "input" -H "X-Callback-Url: http://some-request-bin.com/path" http://127.0.0.1/async-function/<function-name>
```

## Notes
Increase the number of **cpus** if you are using a virtuall machine

