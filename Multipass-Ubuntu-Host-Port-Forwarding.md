# Multipass Ubuntu-Host Port-Forwarding

Access multipass instance on port **8000** from **localhost:9000**:
```sh
sudo ssh -L 9000:localhost:8000 -i /var/snap/multipass/common/data/multipassd/ssh-keys/id_rsa ubuntu@<Multipass-Instance-IP>
```
Access **localhost:9000** from **public ip address on port 8090**:

* Install **nginx**
```sh
sudo apt install nginx
```
* modify **/etc/nginx/sites-available/default**
```sh
sudo nano /etc/nginx/sites-available/default
```
* **/etc/nginx/sites-available/default** should look like this:
```sh
server {

	listen 8090;
	server_name development;
	location / {

		proxy_pass http://localhost:9000;
		# allow switching protocols to use websockets
		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "Upgrade";
		proxy_set_header Host $host;

	}

}
```
* You don't want to use an ssh-tunneling? just edit **/etc/nginx/sites-available/default** to look like this:
```sh
server {

	listen 8090;
	server_name development;
	location / {

		proxy_pass http://<Multipass-Instance-IP>;
		# allow switching protocols to use websockets
		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "Upgrade";
		proxy_set_header Host $host;

	}

}
```
* Restart **nginx**
```sh
sudo systemctl restart nginx
```
or
```sh
sudo service nginx restart
```
Now you can access your multipass instance on port **8000** from your **host public ip address on port 8090** ( or from **localhost:9000** if you are using ssh-tunneling )
