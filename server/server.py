#!/usr/bin/env python3

import platform
import subprocess
import datetime
from flask import Flask, render_template, request, Response, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from waitress import serve
import requests
import json
import argparse
from urllib.parse import urljoin, unquote
import os, sys
import random
import string
import pathlib
import shutil
from threading import Thread, Lock

# handler is needed if openfaas is not being used
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from ptas import handler

LOCAL = False
WEBSOCKET = None

PROXYOPENFAASULR = None
PROXYFUNCTION = None
PROXYFUNCTIONURL = None
PROXYASYNCFUNCTIONURL = None

ALLOWPROXY = None
OPENFAASULR = None
FUNCTION = None
FUNCTIONURL = None
ASYNCFUNCTIONURL = None
DIRECT = None

thread = None

dist_dir = os.path.abspath('./dist/')

app = Flask(__name__, template_folder=dist_dir, static_url_path='')
socketio = SocketIO(app, cors_allowed_origins='*')

# static functions
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

def extract_url(url):
    if url is not None:
        if url != 'None':
            url = unquote(url)
            url = urljoin(url, 'function/')
            url = urljoin(url, FUNCTION)
            if url == FUNCTIONURL:
                url = PROXYFUNCTIONURL
    else:
        url = PROXYFUNCTIONURL
    return url

def check_openfaas():
    out, err = subprocess.Popen('faas-cli list', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    out = out.decode("utf-8")
    err = err.decode("utf-8")
    installed = False
    if err != "":
        check = "false"
        message = "OpenFaaS not installed"
        return installed, check, message   
    out = out.split('\n') 
    for line in out:
        if line.split('\t')[0].strip() == FUNCTION:
            installed = True
            break  
    if installed:
        message = "Function installed"
        check = "false"
    else:
        message = "Function not installed, or OpenFaaS not running yet"
        check = "true"
    return installed, check, message

def check_openfaas_thread():
    global thread
    while(True):
        installed, check, message = check_openfaas()
        socketio.emit('openfaas', {'data': installed})
        if installed:
            break
        socketio.sleep(3)
    thread = None

#definining all this junk because we want to build our frontend and use it out of the box. just build it and paste it in dist folder    
#for vue    
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(f'{dist_dir}/js', path)

#for vue
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(f'{dist_dir}/css', path)

#for errors
@app.route('/favicon.png')
def send_favs():
    return send_from_directory(f'{dist_dir}/fav', 'favicon.png')

#for vue
@app.route('/fav/<path:path>')
def send_fav(path):
    return send_from_directory(f'{dist_dir}/fav', path)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

# app routes    
@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/project/<name>')
def project(name):
    return render_template('index.html')
    
@app.route('/project/<project_name>/<script_name>')
def script(project_name, script_name):
    return render_template('index.html')
    
@app.route('/license')
def license():
    return render_template('index.html')
    
@app.route('/control')
def control():
    return render_template('index.html')
    
@app.route('/openfaas')
def openfaas_stats():
    return render_template('index.html')
    
@app.route('/egg')
def egg():
    return render_template('index.html')
    
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
        if not ALLOWPROXY:
            return jsonify(success=False)
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

@app.route('/check_connection', methods=['POST'])
def check_connection():
    url = json.loads(request.data)['url']
    url = url[:-1] if url[-1] == '/' else url
    try:
        res = requests.post(f'{url}/function/{FUNCTION}' , data=json.dumps({'command': 914}).encode('UTF-8'), timeout=3)  
        response = Response(
            response=res.content,
            status=res.status_code,
            headers=dict(res.headers)
        )

        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(days=90)
        response.set_cookie('openfaasurl', url, expires=expire_date)
        return response 
    except:
        response = jsonify(success=False)
        return response

@app.route('/defaults', methods=['POST'])
def defaults():
    response = jsonify(openfaas_url=OPENFAASULR, direct=DIRECT)
    url = OPENFAASULR
    if url is None:
        url = 'None'

    expire_date = datetime.datetime.now()
    expire_date = expire_date + datetime.timedelta(days=90)
    response.set_cookie('openfaasurl', url, expires=expire_date)
    return response 

@app.route('/openfaas', methods=['POST'])
def openfaas_info():
    installed, check, message = check_openfaas()
    return jsonify(installed=installed, check=check, message=message)
    
# socket
@socketio.on('stats')
def stats(message):
    project_name = message.get('project_name')
    script_name = message.get('script_name')
    id = message.get('id')
    if project_name is None or script_name is None or id is None:
        emit(id, {'data': None}, broadcast=False)
        return 
    url = extract_url(message.get('openfaasurl'))
    if url == 'None':
        data = {'command':6,'project_name':project_name, 'script_name':script_name, 'id': id, 'local':True}
        response = handler.handle(json.dumps(data), True)
        emit(id, {'data': response}, broadcast=False)
        return
    else:
        data = {'command':6,'project_name':project_name, 'script_name':script_name, 'id': id}
        response = requests.post(url, data=json.dumps(data))
        emit(id, {'data': response.text}, broadcast=False)
        return
    
@socketio.on('task_stats')
def task_stats(message):
    project_name = message.get('project_name')
    if project_name is None:
        emit(project_name, {'data': None}, broadcast=False)
        return 
    url = extract_url(message.get('openfaasurl'))
    data = {'command':2,'task_id': project_name}
    if url == 'None':
        response = handler.handle(json.dumps(data), True)
        emit(project_name, {'data': response}, broadcast=False)
        return
    else:
        response = requests.post(url, data=json.dumps(data))
        emit(project_name, {'data': response.text}, broadcast=False)
        return
       
@socketio.on('connect')
def connect():
    session_id = request.sid
    print('Client connected', session_id)

@socketio.on('openfaas')
def openfass_socket():
    global thread
    installed, check, message = check_openfaas()
    socketio.emit('openfaas', {'data': installed}, broadcast=False)
    if thread is None:
        thread = Thread(target=check_openfaas_thread)
        thread.start()


CONNECTED_CLIENTS = {}
T = None
T_LOCK = Lock()

def T_TASK():
    global T
    while True:
        #copy
        with T_LOCK:
            current_connected_clients = CONNECTED_CLIENTS
        if(len(current_connected_clients) < 1): break

        print('T is running')
        sent = {}
        for key, client in current_connected_clients.items():
            url = client['url']
            events = client['events']
            for event in events:
                #control
                if event['name'] == 'control':
                    if url + '_control' not in sent:
                        if url == 'None':
                            data = {'command':13, 'local':True}
                            response = handler.handle(json.dumps(data), True)
                            socketio.emit(url + '_control', response)
                        else:
                            data = {'command':13}
                            post_url = unquote(url)
                            post_url = urljoin(post_url, 'function/')
                            post_url = urljoin(post_url, FUNCTION)
                            try:
                                response = requests.post(post_url, data=json.dumps(data), timeout=2)
                                socketio.emit(url + '_control', response.text)
                            except:
                                socketio.emit(url + '_control', {'success': False})
                        print('sent to: ', url + '_control')
                        sent[url + '_control'] = None
                #script
                if event['name'] == 'script':
                    project_name = event['params']['project_name']
                    script_name = event['params']['script_name']
                    if url + '_' + project_name + '_' + script_name not in sent:
                        if url == 'None':
                            #todo
                            data = {'command':13, 'local':True}
                            response = handler.handle(json.dumps(data), True)
                            socketio.emit(url + '_' + project_name + '_' + script_name, response)
                        else:
                            data = {'command':13}
                            post_url = unquote(url)
                            post_url = urljoin(post_url, 'function/')
                            post_url = urljoin(post_url, FUNCTION)
                            try:
                                #todo
                                response = requests.post(post_url, data=json.dumps(data), timeout=2)
                                socketio.emit(url + '_' + project_name + '_' + script_name, response.text)
                            except:
                                socketio.emit(url + '_' + project_name + '_' + script_name, {'success': False})
                        print('sent to: ', url + '_' + project_name + '_' + script_name)
                        sent[url + '_' + project_name + '_' + script_name] = None
                #openfaas
                if event['name'] == 'openfaas':
                    pass
            if url not in sent:
                if url == 'None':
                    data = {'command':14, 'local':True}
                    response = handler.handle(json.dumps(data), True)
                    socketio.emit(url, response)
                else:
                    data = {'command':14}
                    post_url = unquote(url)
                    post_url = urljoin(post_url, 'function/')
                    post_url = urljoin(post_url, FUNCTION)
                    try:
                        response = requests.post(post_url, data=json.dumps(data), timeout=2)
                        socketio.emit(url, response.text)
                    except:
                        socketio.emit(url, {'success': False})
                print('sent to: ', url)
                sent[url] = None
        socketio.sleep(2)
    print('T has stopped')
    T = None   

@socketio.on('register')
def register(message):
    client = request.sid
    url = message.get('openfaasurl')
    if url is None:
        url = 'None',
    with T_LOCK:
        if client in CONNECTED_CLIENTS:
            events = CONNECTED_CLIENTS[client]['events']
            CONNECTED_CLIENTS[client] = {'url':url, 'events':events}
        else:    
            CONNECTED_CLIENTS[client] = {'url':url, 'events':[]}
    print('\nT Client registered: ', client)
    print('T OpenFaas Url: ', url)
    print('T Current connected clients: ', CONNECTED_CLIENTS)
    global T
    if T is None:
        T = Thread(target=T_TASK)
        T.daemon = True
        T.start()

@socketio.on('register_control')
def register_control(message):
    client = request.sid
    url = message.get('openfaasurl')
    if url is None:
        url = 'None',
    with T_LOCK:
        CONNECTED_CLIENTS[client]['events'].append({'name':'control'})
    print('\nClient registered control: ', client)
    print('OpenFaas Url: ', url)
    print('Current connected clients: ', CONNECTED_CLIENTS)


@socketio.on('disconnect_control')
def disconnect_control():
    client = request.sid
    with T_LOCK:
        if client in CONNECTED_CLIENTS:
           CONNECTED_CLIENTS[client]['events'].remove({'name':'control'})
    print('\nClient unsunscribed control', client)
    print('Current connected clients: ', CONNECTED_CLIENTS)

@socketio.on('register_script')
def register_script(message):
    client = request.sid
    url = message.get('openfaasurl')
    project_name = message.get('project_name')
    script_name = message.get('script_name')
    if url is None:
        url = 'None',
    with T_LOCK:
        CONNECTED_CLIENTS[client]['events'].append({'name':'script','params':{'project_name':project_name, 'script_name':script_name}})
    print('\nClient registered script: ', client)
    print('OpenFaas Url: ', url)
    print('Current connected clients: ', CONNECTED_CLIENTS)

@socketio.on('disconnect_script')
def disconnect_script(message):
    client = request.sid
    project_name = message.get('project_name')
    script_name = message.get('script_name')
    with T_LOCK:
        if client in CONNECTED_CLIENTS:
           CONNECTED_CLIENTS[client]['events'].remove({'name':'script','params':{'project_name':project_name, 'script_name':script_name}})
    print('\nClient unsunscribed script', client)
    print('Current connected clients: ', CONNECTED_CLIENTS)

@socketio.on('disconnect')
def disconnect():
    client = request.sid
    with T_LOCK:
        if client in CONNECTED_CLIENTS:
            del CONNECTED_CLIENTS[client]
    print('\nClient disconnected', client)
    print('Current connected clients: ', CONNECTED_CLIENTS)


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
    requiredNamed.add_argument('-w', '--websocket', action='store_true', help='use websockets instead of server sent events. Warning: app will run with WSGIServer instead of waitress')
    requiredNamed.add_argument('-f','--function', help='function name',metavar='')
    requiredNamed.add_argument('-d','--direct', help='can the browser connect to openfaas directly? <true || false>',metavar='')
    requiredNamed.add_argument('-t','--threads', help='waitress threads default 24',metavar='')

    args = parser.parse_args()

    host = args.host or '0.0.0.0'
    port = args.port or '80'
    port = '80' if not port.isdigit() else port
    url = args.url
    extern = args.extern
    function = args.function or 'ptas'
    direct = args.direct or 'true'
    threads = args.threads or '24'
    threads = '24' if not threads.isdigit() else threads
    WEBSOCKET = 'true' if args.websocket == True else 'false'
    LOCAL = args.local

    if direct != 'true' and direct != 'false':
        print('-d , --direct can only be true or false')
        exit()

    if url is None:
        ALLOWPROXY = False
    else:
        ALLOWPROXY = True

    if url is None and extern == False and LOCAL == False:
        print('please provide an openfaasurl using -u or -e or use -l if you dont want to use an openfaas server')
        exit()
        
    OPENFAASULR = url
    PROXYOPENFAASULR = url
    DIRECT = direct

    if extern == True:
        if platform.system() == 'Linux':
            host = subprocess.Popen("echo $(/sbin/ip -o -4 addr list  | awk '{print $4}' | cut -d/ -f1)", shell=True, stdout=subprocess.PIPE).stdout.read().decode('UTF-8').split(' ')[1].replace('\n','')
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
    if WEBSOCKET == 'true':
        print(f'running with websockets')
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler
        server = pywsgi.WSGIServer((host, int(port)), app, handler_class=WebSocketHandler)
        server.serve_forever()
    else:
        print(f'waitress threads: {threads}')
        serve(app, host=host, port=int(port), threads=int(threads))
