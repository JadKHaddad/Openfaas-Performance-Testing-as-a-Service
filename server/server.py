#!/usr/bin/env python3

import platform
import subprocess
from flask import Flask, render_template, request, Response
from waitress import serve
import requests
import json
import gevent
import argparse
from urllib.parse import urljoin, unquote
import os, sys
import random
import string
import pathlib
import shutil

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from ptas import handler

LOCAL = False

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

def get_noredges():
    noredges = request.cookies.get('noredges')
    if noredges is None:
        noredges = 'false'
    return noredges

@app.route('/')
def index():
    return render_template('index.html', noredges=get_noredges(), openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme())

@app.route('/task/<task_id>')
def task(task_id):
    url = request.cookies.get('openfaasurl')
    if url is not None:
        if url == 'None':
            data = {'command':2,'task_id': task_id}
            def task_stream():
                while True:
                    response = handler.handle(json.dumps(data), True)
                    yield f'data: {response}\n\n'
                    gevent.sleep(1)
            return Response(task_stream(), mimetype="text/event-stream")
        else:    
            url = unquote(url)
            url = urljoin(url, 'function/')
            url = urljoin(url, FUNCTION)
            if url == FUNCTIONURL:
                url = PROXYFUNCTIONURL
    else:
        url = PROXYFUNCTIONURL
    data = {'command':2,'task_id': task_id}
    def task_stream():
        while True:
            response = requests.post(url, data=json.dumps(data))
            yield f'data: {response.text}\n\n'
            gevent.sleep(1)
    return Response(task_stream(), mimetype="text/event-stream")

@app.route('/project/<name>')
def project(name):
    return render_template('project.html', noredges=get_noredges(), openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme(), project_name=name)

@app.route('/project/<project_name>/<script_name>')
def script(project_name, script_name):
    return render_template('script.html', noredges=get_noredges(), openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme(), project_name=project_name, script_name=script_name)

@app.route('/stream/<project_name>/<script_name>/<id>')
def stream(project_name,script_name,id):
    url = request.cookies.get('openfaasurl')
    if url is not None:
        if url == 'None':
            data = {'command':6,'project_name':project_name, 'script_name':script_name, 'id': id, 'local':True}
            def stats_stream():
                while True:
                    response = handler.handle(json.dumps(data), True)
                    yield f'data: {response}\n\n'
                    gevent.sleep(1)
            return Response(stats_stream(), mimetype="text/event-stream")
        else:    
            url = unquote(url)
            url = urljoin(url, 'function/')
            url = urljoin(url, FUNCTION)
            if url == FUNCTIONURL:
                url = PROXYFUNCTIONURL
    else:
        url = PROXYFUNCTIONURL
    data = {'command':6,'project_name':project_name, 'script_name':script_name, 'id': id}
    def stats_stream():
        while True:
            response = requests.post(url, data=json.dumps(data))
            yield f'data: {response.text}\n\n'
            gevent.sleep(1)
    return Response(stats_stream(), mimetype="text/event-stream")

@app.route('/license')
def license():
    return render_template('license.html', noredges=get_noredges(),openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme())

@app.route('/control')
def control():
    return render_template('control.html', noredges=get_noredges(), openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme())

@app.route('/egg')
def egg():
    return render_template('egg.html', noredges=get_noredges(), openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme())

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
    if 'file0' in request.files:
        ran = str(''.join(random.choices(string.ascii_uppercase + string.digits, k = 10)))    
        path = f'temp/{ran}'
        files = {}
        openfiles = []
        # save project files 
        for key in request.files:
            f = request.files[key]
            uploaded_file_name = f.filename
            uploaded_file_content_type = f.content_type
            uploaded_file_dir = '/'.join(uploaded_file_name.split('/')[:-1])
            pathlib.Path(f'{path}/{uploaded_file_dir}').mkdir(parents=True, exist_ok=True) 
            f.save(f'{path}/{uploaded_file_name}')
            o = open(f'{path}/{uploaded_file_name}', "rb")
            openfiles.append(o)
            files[key] = (uploaded_file_name, o, uploaded_file_content_type)
        res = requests.post(url, data=request.data, files=files)
        # close the files
        for o in openfiles:
            o.close()
        # delete the files
        shutil.rmtree(path)
    else:
        res = requests.post(url, data=request.data)   

    return Response(
        response=res.content,
        status=res.status_code,
        headers=dict(res.headers)
    )

@app.route('/local', methods=['POST'])
def local():
    return handler.handle(request.data)

if __name__ == '__main__':
    extern = False
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,help='help')
    parser.add_argument('-v', '--version', action='version',version='%(prog)s 1.0', help='version')
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-s', '--host', help='server host',metavar='')
    requiredNamed.add_argument('-p', '--port', help='server port',metavar='')
    requiredNamed.add_argument('-u', '--url', help='openfaas url',metavar='')
    requiredNamed.add_argument('-e', '--extern', action='store_true', help='use if openfass is running on the external ip address of your machine')
    requiredNamed.add_argument('-l', '--local', action='store_true', help='use if you dont want to use an openfaas server')
    requiredNamed.add_argument('-f','--function', help='function name',metavar='')
    requiredNamed.add_argument('-d','--direct', help='can the browser connect to openfaas directly? <true || false>',metavar='')

    args = parser.parse_args()

    host = args.host or '0.0.0.0'
    port = args.port or 80
    url = args.url
    extern = args.extern
    function = args.function or 'ptas'
    direct = args.direct or 'true'
    LOCAL = args.local

    if direct != 'true' and direct != 'false':
        print('-d , --direct can only be true or false')
        exit()

    if url is None and extern == False and LOCAL == False:
        print('please provide an openfaasurl using -u or -e or use -l if you dont want to use an openfaas server')
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
    
    if LOCAL == False:
        print(f'\nopenfaas url: {OPENFAASULR}')
        print(f'sync function call: {FUNCTIONURL}')
        print(f'async function call: {ASYNCFUNCTIONURL}')
        if direct == 'false':
            print(f'\nproxy openfaas url: {PROXYOPENFAASULR}')
            print(f'proxy sync function call: {PROXYFUNCTIONURL}')
            print(f'proxy async function call: {PROXYASYNCFUNCTIONURL}')
        print(f'\ndirect: {direct}')
    print(f'server running on {host}:{port}')
    serve(app, host=host, port=port,threads=24)