# Why use OpenFaaS if we can sail with docker!

<br >

Let's build the function image:
```sh
docker build -t ptas:1.0 -f ptas.Dockerfile .
```
Run it:
```sh
docker-compose -f ptas.docker-compose.yml up
```
Try it:
```sh
curl 'http://localhost:8081/function/ptas' --data-raw '{"command":914}'
```
```sh
{"success":true}
```
Async:
```sh
curl 'http://localhost:8081/async-function/ptas' --data-raw '{"command":914}'
```
```sh
{"task_id":"17b4e3c03a65430792f9387c5debecec"}
```
Run with callback:
```sh
curl 'http://localhost:8081/async-function/ptas' --data-raw '{"command":914}' -H "X-Callback-Url: http://192.168.178.72:8888"
```
```sh
{"task_id":"17b4e3c03a65430792f9387c5debecec"}
```
While listening on port 8888 with netcat: 
```sh
sudo nc -l 8888
```
You will recieve a response after the async function is finished:
```sh
POST / HTTP/1.1
Host: 192.168.178.72:8888
User-Agent: python-requests/2.27.1
Accept-Encoding: gzip, deflate
Accept: */*
Connection: keep-alive
Content-Length: 17

{"success":true}
```
Use your own IP address instead of **192.168.178.72**<br><br>
Use **localhost:8081** as your OpenFaaS url and you are good to go!

## Note
This approach does **NOT** replace OpenFaaS by any means, it just simulates hanivg a serverless function called **ptas** that runs on an OpenFaaS server on host **localhost:8081**. Do **NOT** use it as an OpenFaaS function. As a serveless function? **No**, this approach is just **SIMULATION**
