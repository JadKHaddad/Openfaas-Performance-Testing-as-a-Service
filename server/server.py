#!/usr/bin/env python3

from ptas import handler
import platform
import subprocess
import datetime
from flask import Flask, render_template, request, Response, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from waitress import serve
import requests
import json
import gevent
import argparse
from urllib.parse import urljoin, unquote
import os
import sys
import random
import string
import pathlib
import shutil
from threading import Thread

# handler is needed if openfaas is not being used
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

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
    out, err = subprocess.Popen('faas-cli list', shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
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

# definining all this junk because we want to build our frontend and use it out of the box. just build it and paste it in dist folder
# for vue


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(f'{dist_dir}/js', path)

# for vue


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(f'{dist_dir}/css', path)

# for errors


@app.route('/favicon.png')
def send_favs():
    return send_from_directory(f'{dist_dir}/fav', 'favicon.png')

# for vue


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
    # return render_template('index.html', noredges=get_noredges(), openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme(), websocket=WEBSOCKET)


@app.route('/project/<name>')
def project(name):
    return render_template('index.html')
    # return render_template('project.html', noredges=get_noredges(), openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme(), project_name=name, websocket=WEBSOCKET)


@app.route('/project/<project_name>/<script_name>')
def script(project_name, script_name):
    return render_template('index.html')
    # return render_template('script.html', noredges=get_noredges(), openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme(), project_name=project_name, script_name=script_name, websocket=WEBSOCKET)


@app.route('/license')
def license():
    return render_template('index.html')
    # return render_template('license.html', noredges=get_noredges(),openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme(), websocket=WEBSOCKET)


@app.route('/control')
def control():
    return render_template('index.html')
    # return render_template('control.html', noredges=get_noredges(), openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme(), websocket=WEBSOCKET)


@app.route('/openfaas')
def openfaas_stats():
    return render_template('index.html')
    #installed, check, message = check_openfaas()
    # return render_template('openfaas.html', noredges=get_noredges(), openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme(), websocket=WEBSOCKET,check=check, message=message)


@app.route('/egg')
def egg():
    return render_template('index.html')
    # return render_template('egg.html', noredges=get_noredges(), openfaas_url=OPENFAASULR, function_name=FUNCTION, direct=DIRECT, theme=get_theme(), websocket=WEBSOCKET)


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
        ran = str(''.join(random.choices(
            string.ascii_uppercase + string.digits, k=10)))
        path = f'temp/{ran}'
        files = {}
        openfiles = []
        # save project files
        for key in request.files:
            f = request.files[key]
            uploaded_file_name = f.filename
            uploaded_file_content_type = f.content_type
            uploaded_file_dir = '/'.join(uploaded_file_name.split('/')[:-1])
            pathlib.Path(
                f'{path}/{uploaded_file_dir}').mkdir(parents=True, exist_ok=True)
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
        res = requests.post(f'{url}/function/{FUNCTION}',
                            data=json.dumps({'command': 914}).encode('UTF-8'), timeout=3)
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
        data = {'command': 6, 'project_name': project_name,
                'script_name': script_name, 'id': id, 'local': True}
        response = handler.handle(json.dumps(data), True)
        emit(id, {'data': response}, broadcast=False)
        return
    else:
        data = {'command': 6, 'project_name': project_name,
                'script_name': script_name, 'id': id}
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
    data = {'command': 2, 'task_id': project_name}
    if url == 'None':
        response = handler.handle(json.dumps(data), True)
        emit(project_name, {'data': response}, broadcast=False)
        return
    else:
        response = requests.post(url, data=json.dumps(data))
        emit(project_name, {'data': response.text}, broadcast=False)
        return


@socketio.on('server_stats')
def server_stats(message):
    url = extract_url(message.get('openfaasurl'))
    #print("getting from: " + url)
    if url == 'None':
        data = {'command': 14, 'local': True}
        response = handler.handle(json.dumps(data), True)
        socketio.emit('server_stats', {'data': response}, broadcast=False)
        return
    else:
        data = {'command': 14}
        try:
            response = requests.post(url, data=json.dumps(data), timeout=2)
            socketio.emit('server_stats', {
                          'data': response.text}, broadcast=False)
        except:
            socketio.emit('server_stats', {
                          'data': {'stop': True}}, broadcast=False)
        finally:
            return


@socketio.on('connect')
def connect():
    session_id = request.sid
    print('Client connected', session_id)


@socketio.on('disconnect')
def disconnect():
    session_id = request.sid
    print('Client disconnected', session_id)


@socketio.on('openfaas')
def openfass_socket():
    global thread
    installed, check, message = check_openfaas()
    socketio.emit('openfaas', {'data': installed}, broadcast=False)
    if thread is None:
        thread = Thread(target=check_openfaas_thread)
        thread.start()


if __name__ == '__main__':
    extern = False
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='help',
                        default=argparse.SUPPRESS, help='help')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 1.0', help='version')
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-s', '--host', help='server host', metavar='')
    requiredNamed.add_argument('-p', '--port', help='server port', metavar='')
    requiredNamed.add_argument('-u', '--url', help='openfaas url', metavar='')
    requiredNamed.add_argument('-e', '--extern', action='store_true',
                               help='use if openfass is running on the external ip address of your machine')
    requiredNamed.add_argument('-l', '--local', action='store_true',
                               help='use if you dont want to use an openfaas server')
    requiredNamed.add_argument('-w', '--websocket', action='store_true',
                               help='use websockets instead of server sent events. Warning: app will run with WSGIServer instead of waitress')
    requiredNamed.add_argument(
        '-f', '--function', help='function name', metavar='')
    requiredNamed.add_argument(
        '-d', '--direct', help='can the browser connect to openfaas directly? <true || false>', metavar='')
    requiredNamed.add_argument(
        '-t', '--threads', help='waitress threads default 24', metavar='')

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
            host = subprocess.Popen("echo $(/sbin/ip -o -4 addr list  | awk '{print $4}' | cut -d/ -f1)",
                                    shell=True, stdout=subprocess.PIPE).stdout.read().decode('UTF-8').split(' ')[1].replace('\n', '')
            OPENFAASULR = ('http://'+host+':8080/')
        else:
            if url is None:
                print(
                    'if you are not using Linux please provide your external ip address manually')
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
        server = pywsgi.WSGIServer(
            (host, int(port)), app, handler_class=WebSocketHandler)
        server.serve_forever()
    else:
        print(f'waitress threads: {threads}')
        serve(app, host=host, port=int(port), threads=int(threads))
