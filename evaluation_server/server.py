#!/usr/bin/env python3

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, render_template, request, Response, jsonify
from flask_socketio import SocketIO, emit
from threading import Lock
import json, os
from pathlib import Path
import subprocess
from random import randrange

if not Path('results').exists():
    os.mkdir('results')

if not Path('results/first_questions').exists():
    os.mkdir('results/first_questions')

if not Path('results/last_questions').exists():
    os.mkdir('results/last_questions')

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

    # get j_data
    j_data = json.loads(request.data)

    # save json_data
    with open(f'results/first_questions/{id}_json.txt','w',encoding='utf-8') as file:
        file.write(json.dumps(j_data))
    
    #save as text
    with open(f'results/first_questions/{id}_text.txt','w',encoding='utf-8') as file:
        for item in j_data:
            q = item.get('q')
            a = item.get('a')
            file.write(f'{q}:{a}\n')

    # create user and copy the projects to his dir
    username = 'user_' + str(randrange(10000))
    password = '123456'
    cmd = f'sudo useradd -p $(openssl passwd -1 {password}) -m {username}  && sudo cp -a ../modified_server/. /home/{username}/modified_server/'
    subprocess.Popen(cmd, shell=True).wait()

    # run the service
    cmd = f'cd /home/{username}/modified_server/server/ && sudo python3 ./server.py -l -s 0.0.0.0 -p 5001'
    subprocess.Popen(cmd, shell=True)

    return jsonify(success=True, username=username, password=password, port="8909")

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
    if id in CLIENTS:
        with L:
            del CLIENTS[id]
    print('Client disconnected', id)

if __name__ == '__main__':
    server = pywsgi.WSGIServer(("0.0.0.0", 80), app, handler_class=WebSocketHandler)
    server.serve_forever()
