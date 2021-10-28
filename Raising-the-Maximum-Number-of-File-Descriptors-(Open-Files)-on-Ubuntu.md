# Raising the Maximum Number of File Descriptors (Open Files) on Ubuntu

Check the limits for your current session:
```sh
ulimit -n
```
The actual way to raise your descriptors consists of editing three files:<br/>

* **/etc/security/limits.conf** needs to have these lines in it:
```sh
*    soft nofile 64000
*    hard nofile 64000
root soft nofile 64000
root hard nofile 64000
```

* **/etc/pam.d/common-session** needs to have this line in it:
```sh
session required pam_limits.so
```

* **/etc/pam.d/common-session-noninteractive** also needs to have this line in it:
```sh
session required pam_limits.so
```

Reboot
```sh
sudo reboot
```
Check the new limits for your current session:
```sh
ulimit -n
```

Still having problems? read the full [article](https://underyx.me/articles/raising-the-maximum-number-of-file-descriptors)


