# Multipass Ubuntu-Host Port-Forwarding

Access multipass instance on port ```8000``` from ```localhost:9000```:
```sh
sudo ssh -L 9000:localhost:8000 -i /var/snap/multipass/common/data/multipassd/ssh-keys/id_rsa ubuntu@<multipass instance ip>
```
Access ```localhost:9000``` from ```public ip address on port 8090```:

* Install **nginx**
```sh
sudo apt install nginx
```
* modify ```/etc/nginx/sites-available/default```
```sh
sudo nano /etc/nginx/sites-available/default
```
* ```/etc/nginx/sites-available/default``` should look like this:
```sh
server {

	listen 8090;
	server_name development;
	location / {

		proxy_pass http://localhost:9000;

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
Now you can access your multipass instance on port ```8000``` from your ```host public ip address on port 8090``` or from ```localhost:9000```
