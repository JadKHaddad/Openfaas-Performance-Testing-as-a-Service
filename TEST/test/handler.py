import subprocess


def handle(req):
	p = subprocess.Popen('ulimit -n 64000; ulimit -n',shell=True, stdout=subprocess.PIPE)
	out, err = p.communicate()
	return out
	

