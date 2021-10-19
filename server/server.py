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
from urllib.parse import urljoin, unquote

PROXYOPENFAASULR = None
PROXYFUNCTION = None
PROXYFUNCTIONURL = None
PROXYASYNCFUNCTIONURL = None

OPENFAASULR = None
FUNCTION = None
FUNCTIONURL = None
ASYNCFUNCTIONURL = None
DIRECT = None

app = Flask(__name__)

def get_theme():
    theme = request.cookies.get('theme')
    if theme is None:
        theme = 'light'
    return theme

@app.route('/')
def index():
    theme = get_theme()
    return render_template('index.html', openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=theme)

@app.route('/explore')
def explore():
    theme = get_theme()
    return render_template('explore.html', openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=theme)

@app.route('/license')
def license():
    theme = get_theme()
    return render_template('license.html', openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=theme)

@app.route('/test/<id>')
def test(id):
    theme = get_theme()
    return render_template('test.html', id=id, openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=theme)

@app.route('/stream/<id>')
def stream(id):
    data = {'command':4,'id': id}
    url = request.cookies.get('openfaasurl')
    if url is not None:
        url = unquote(url)
        url = urljoin(url, 'function/')
        url = urljoin(url, FUNCTION)
        if url == FUNCTIONURL:
            url = PROXYFUNCTIONURL
    else:
        url = PROXYFUNCTIONURL
    def stats_stream():
        while True:
            response = requests.post(url, data=json.dumps(data))
            yield f'data: {response.text}\n\n'
            gevent.sleep(1)
    return Response(stats_stream(), mimetype="text/event-stream")

@app.route('/proxy', methods=['POST'])
def proxy():
    url = request.cookies.get('openfaasurl')
    if url is not None:
        url = unquote(url)
        url = urljoin(url, 'function/')
        url = urljoin(url, FUNCTION)
        if url == FUNCTIONURL:
            url = PROXYFUNCTIONURL
    else:
        url = PROXYFUNCTIONURL
    res = requests.post(url, data=request.data.decode("utf-8"))
    return Response(
        response=res.content,
        status=res.status_code,
        headers=dict(res.headers)
    )

if __name__ == '__main__':
    extern = False
    if not len(sys.argv) > 1:
        host = '0.0.0.0'
        port = 80
        url = 'http://127.0.0.1:8080/'
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
        requiredNamed.add_argument('-e', '--extern', action='store_true', help='use if openfass is running on the external ip address of your machine')
        requiredNamed.add_argument('-f','--function', help='function name',metavar='',required=True)
        requiredNamed.add_argument('-d','--direct', help='can the browser connect to openfaas directly? <true || false>',metavar='',required=True)

        args = parser.parse_args()

        host = args.host
        port = args.port
        url = args.url
        extern = args.extern
        function = args.function
        direct = args.direct

        if direct != 'true' and direct != 'false':
            print('-d , --direct can only be true or false')
            exit()

        if url is None and extern == False:
            print('please provide an openfaasurl using -u or -e')
            exit()
        
    OPENFAASULR = url
    PROXYOPENFAASULR = url
    DIRECT = direct

    if extern == True:
        if platform.system() == 'Linux':
            host = subprocess.Popen("echo $(/sbin/ip -o -4 addr list  | awk '{print $4}' | cut -d/ -f1)", shell=True, stdout=subprocess.PIPE).stdout.read().decode('UTF-8').split(' ')[1]
            OPENFAASULR = ('http://'+host+':8080/')
        else:
            if url is None:
                print('if you are not using Linux please provide your external ip address manually')
                exit()
        if DIRECT == 'false':
            PROXYOPENFAASULR = "http://127.0.0.1:8080/"
        else:
            PROXYOPENFAASULR = OPENFAASULR



    FUNCTION = function
    SYNC = urljoin(OPENFAASULR, 'function/')
    ASYNC = urljoin(OPENFAASULR, 'async-function/')
    FUNCTIONURL = urljoin(SYNC, FUNCTION)
    ASYNCFUNCTIONURL = urljoin(ASYNC, FUNCTION)

    PROXYSYNC = urljoin(PROXYOPENFAASULR, 'function/')
    PROXYASYNC = urljoin(PROXYOPENFAASULR, 'async-function/')
    PROXYFUNCTIONURL = urljoin(PROXYSYNC, FUNCTION)
    PROXYASYNCFUNCTIONURL = urljoin(PROXYASYNC, FUNCTION)
    
    print(f'\nopenfaas url: {OPENFAASULR}')
    print(f'sync function call: {FUNCTIONURL}')
    print(f'async function call: {ASYNCFUNCTIONURL}')
    if direct == 'false':
        print(f'\nproxy openfaas url: {PROXYOPENFAASULR}')
        print(f'proxy sync function call: {PROXYFUNCTIONURL}')
        print(f'proxy async function call: {PROXYASYNCFUNCTIONURL}')
    print(f'\ndirect: {direct}')
    print(f'server running on {host}:{port}')
    serve(app, host=host, port=port,threads=8)