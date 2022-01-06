#!/usr/bin/env python3

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, render_template, request, Response, jsonify
from flask_socketio import SocketIO, emit
from threading import Lock
import json

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
    print(j_data)
    # save json_data
    with open(f'results/first_questions/{id}_json.txt','w',encoding='utf-8') as file:
        file.write(json.dumps(j_data))
    
    #save as text
    with open(f'results/first_questions/{id}_text.txt','w',encoding='utf-8') as file:
        for item in j_data:
            q = item.get('q')
            a = item.get('a')
            file.write(f'{q}:{a}\n')

    # create user..
    return jsonify(success=True, username="user1", password="password1", port="8909")

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
