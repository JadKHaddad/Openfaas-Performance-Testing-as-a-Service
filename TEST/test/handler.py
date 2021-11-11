import subprocess

def handle(req):
	p = subprocess.Popen(req,shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	out, err = p.communicate()
	return "out: " + str(out) + " | err: " + str(err)