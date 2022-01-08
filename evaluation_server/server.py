#!/usr/bin/env python3

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, render_template, request, Response, jsonify
from flask_socketio import SocketIO, emit
from threading import Lock
import json, os, subprocess, signal, socket
from pathlib import Path
from random import randrange

if not Path('results').exists():
    os.mkdir('results')

def username_exists(username):
    out, err = subprocess.Popen(f'id -u {username}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if out != b'':
        return True
    return False

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def on_finish(id):
    username = "user"
    delete_username = False
    if id in CLIENTS:
        # delete user
        if 'username' in CLIENTS[id]:
            username = CLIENTS[id]['username']
            delete_username = True

        if 'process' in CLIENTS[id]:
            os.killpg(os.getpgid(CLIENTS[id]['process'].pid), signal.SIGTERM)
        with L:
            del CLIENTS[id]
    if delete_username:
        cmd = f'sudo userdel -f -r {username}'
        subprocess.Popen(cmd, shell=True)

IP = subprocess.Popen("echo $(/sbin/ip -o -4 addr list  | awk '{print $4}' | cut -d/ -f1)", shell=True, stdout=subprocess.PIPE).stdout.read().decode('UTF-8').split(' ')[1].replace('\n','')
CLIENTS = {}
L = Lock()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    # get user id 
    id = request.headers.get('id')
    if id is None or id not in CLIENTS:
        return jsonify(success=False)

    # create user and copy the projects to his dir and create port
    while True:
        username = 'user_' + str(randrange(10000))
        if not username_exists(username):
            break

    port = 5000
    while True:
        if not is_port_in_use(port):
            break
        port = port + 1
        
    password = '123456'
    cmd = f'sudo useradd -p $(openssl passwd -1 {password}) -m {username} && sudo cp -a ../modified_server/. /home/{username}/modified_server/ && sudo cp -a ../locust_scripts/. /home/{username}/locust_scripts/ && sudo chown -R {username}:{username} /home/{username}/locust_scripts && sudo chmod 0750 /home/{username}'
    subprocess.Popen(cmd, shell=True).wait()

    # run the service
    cmd = f'cd /home/{username}/modified_server/server/ && sudo python3 ./server.py -l -s 0.0.0.0 -p {port}'
    CLIENTS[id]['process'] = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
    CLIENTS[id]['username'] = username
    return jsonify(success=True, username=username, password=password, port=port, ip=IP)

@app.route('/finish', methods=['POST'])
def finish():
    # get user id 
    id = request.headers.get('id')
    if id is None or id not in CLIENTS:
        return jsonify(success=False)

    # get j_data
    j_data = json.loads(request.data)

    # save json_data
    with open(f'results/{id}_json.txt','w',encoding='utf-8') as file:
        file.write(json.dumps(j_data))
    
    first = j_data.get('f')
    last = j_data.get('l')

    #save as text
    with open(f'results/{id}_text.txt','w',encoding='utf-8') as file:
        for item in first:
            q = item.get('q')
            a = item.get('a')
            file.write(f'{q}:{a}\n')
        for item in last:
            q = item.get('q')
            a = item.get('a')
            file.write(f'{q}:{a}\n')

    on_finish(id)

    return jsonify(success=True)

@socketio.on('connect')
def connect():
    id = request.sid
    with L:
        CLIENTS[id] = {}
    print('Client connected', id)
    emit('id', {'id':id}, broadcast=False)

@socketio.on('disconnect')
def disconnect():
    id = request.sid
    on_finish(id)
    print('Client disconnected', id)

if __name__ == '__main__':
    server = pywsgi.WSGIServer(("0.0.0.0", 80), app, handler_class=WebSocketHandler)
    server.serve_forever()
