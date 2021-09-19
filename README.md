Edit ptas.yml; set your gateway, set your docker prefix.
Deploy openfaas function; faas-cli up -f ptas.yml.

Install requirements; pip install -r requirements.txt
Run server; python server.py --host <host> --port <port> --url <openfaas url> --function <funcion name>

TODO:

Openfaas function:
    handle None values
    handle wrong test parameters,
    zip files,
    create plots,
    enable download,

server:
    front:
        whats wrong with the buttons?,
        handle elapsed
    back:
        fix waitress.queue

![alt text](https://github.com/JadKHaddad/Openfaas-Performance-Testing-as-a-Service/blob/main/assets/img.jpg?raw=true)
    
![alt text](https://github.com/JadKHaddad/Openfaas-Performance-Testing-as-a-Service/blob/main/assets/seq.jpg?raw=true)
    
synchronous taskts like stop, delete and download work like deploy

