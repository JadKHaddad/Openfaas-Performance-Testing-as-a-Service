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
Test it:
```sh
curl 'http://localhost:8081/function/ptas' --data-raw '{"command":914}'
```
Use **localhost:8081** as your OpenFaaS url and you are good to go!

## Note
This approach does **NOT** replace OpenFaaS by any means, it just simulates hanivg a serverless function called **ptas** that runs on an OpenFaaS server on host **localhost:8081** and does **NOT** support callbacks or async calls.
