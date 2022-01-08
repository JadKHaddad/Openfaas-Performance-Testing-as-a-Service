# Config - Not for you
Hosted by Digitalocean <br /><br />
Clone into root <br /><br />
Add services:
```sh
sudo cp /home/root/Openfaas-Performance-Testing-as-a-Service/evaluation.service /etc/systemd/system/evaluation.service

sudo cp /home/root/Openfaas-Performance-Testing-as-a-Service/simulation.service /etc/systemd/system/simulation.service

sudo systemctl daemon-reload

sudo systemctl enable evaluation.service
sudo systemctl start evaluation.service

sudo systemctl enable simulation.service
sudo systemctl start simulation.service
```