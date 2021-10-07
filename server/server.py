#!/usr/bin/env python3

import platform
import subprocess
import sys
from flask import Flask, render_template, request, Response
from waitress import serve
import requests
import json
import gevent
import argparse
from urllib.parse import urljoin

OPENFAASULR = None
FUNCTION = None
FUNCTIONURL = None
ASYNCFUNCTIONURL = None
DIRECT = None

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', async_function_call=ASYNCFUNCTIONURL, function_call=FUNCTIONURL, direct=DIRECT)

@app.route('/explore')
def explore():
    return render_template('explore.html', async_function_call=ASYNCFUNCTIONURL, function_call=FUNCTIONURL, direct=DIRECT)

@app.route('/test/<id>')
def test(id):
    return render_template('test.html', id=id, async_function_call=ASYNCFUNCTIONURL, function_call=FUNCTIONURL, direct=DIRECT)

@app.route('/stream/<id>')
def stream(id):
    data = {'command':4,'id': id}
    def stats_stream():
        while True:
            response = requests.post(FUNCTIONURL, data=json.dumps(data))
            yield f'data: {response.text}\n\n'
            gevent.sleep(1)
    return Response(stats_stream(), mimetype="text/event-stream")

@app.route('/proxy', methods=['POST'])
def proxy():
    res = requests.post(FUNCTIONURL, data=request.data.decode("utf-8"))
    return Response(
        response=res.content,
        status=res.status_code,
        headers=dict(res.headers)
    )

if __name__ == '__main__':
    if not len(sys.argv) > 1:
        host = '0.0.0.0'
        port = 80
        url = 'http://172.17.129.200:8080/'
        function = 'ptas'
        direct = 'true'
    else:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,help='help')
        parser.add_argument('-v', '--version', action='version',version='%(prog)s 1.0', help='version')
        requiredNamed = parser.add_argument_group('required arguments')
        requiredNamed.add_argument('-s', '--host', help='server host',metavar='',required=True)
        requiredNamed.add_argument('-p', '--port', help='server port',metavar='',required=True)
        requiredNamed.add_argument('-u', '--url', help='openfaas url',metavar='')
        requiredNamed.add_argument('-e', '--extern', action='store_true', help='use if openfass is running on the external ip address of your linux machine')
        requiredNamed.add_argument('-f','--function', help='function name',metavar='',required=True)
        requiredNamed.add_argument('-d','--direct', help='can the browser connect to openfaas directly? <true || false>',metavar='',required=True)

        args = parser.parse_args()

        host = args.host
        port = args.port
        url = args.url
        extern = args.extern
        function = args.function
        direct = args.direct

        if direct != 'true' != 'false':
            print('-d , --direct can only be true or false')
            exit()

        if url is None and extern == False:
            print('please provide an openfaasurl using -u or -e')
            exit()
        
    OPENFAASULR = url
    FUNCTION = function
    SYNC = urljoin(OPENFAASULR, 'function/')
    ASYNC = urljoin(OPENFAASULR, 'async-function/')
    FUNCTIONURL = urljoin(SYNC, FUNCTION)
    ASYNCFUNCTIONURL = urljoin(ASYNC, FUNCTION)
    DIRECT = direct

    if extern == True:
        if platform.system() == 'Linux':
            subprocess = subprocess.Popen("echo $(/sbin/ip -o -4 addr list eth0 | awk '{print $4}' | cut -d/ -f1)d", shell=True, stdout=subprocess.PIPE)
            subprocess_return = subprocess.stdout.read()
            OPENFAASULR = ('http://'+subprocess_return.decode('UTF-8')+':8080/').replace('d','').replace('\n','')
            if DIRECT == 'false':
                OPENFAASULR = "http://127.0.0.1:8080/"
        else:
            print('if you are not using Linux please provide your external ip address manually')
            exit()
    
    print(f'openfaas url: {OPENFAASULR}')
    print(f'sync function call: {FUNCTIONURL}')
    print(f'async function call: {ASYNCFUNCTIONURL}')
    print(f'direct: {direct}')
    print(f'server running on {host}:{port}')
    serve(app, host=host, port=port,threads=8)