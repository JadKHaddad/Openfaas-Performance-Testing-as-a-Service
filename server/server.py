from flask import Flask, render_template, request, Response
from waitress import serve
import requests
import json
import gevent

OPENFAASURL = "http://172.17.123.151:8080/"
FUNCTIONURL = OPENFAASURL + "function/ptas"
ASYNCFUNCTIONURL = OPENFAASURL + "async-function/ptas"

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/explore')
def explore():
    return render_template('explore.html')

@app.route('/tests')
def tests():
    data = {'command':6}
    response = requests.post(FUNCTIONURL, data=json.dumps(data))
    return response.text

@app.route('/deploy', methods=['POST'])
def deploy():
    users = request.form.get('users') or None
    spawn_rate = request.form.get('spawn_rate') or None
    host = request.form.get('host') or None
    time = int(request.form.get('time')) or None
    code = request.form.get('code') or None
    data = {'command':1,'users': int(users), 'spawn_rate': int(spawn_rate), 'host': host, 'time':time, 'code':code}
    response = requests.post(FUNCTIONURL, data=json.dumps(data))
    return response.text

@app.route('/start/<id>', methods=['POST'])
def start(id):
    data = {'command':2,'id': id}
    requests.post(ASYNCFUNCTIONURL, data=json.dumps(data))
    return json.dumps({"status": "sent"})

@app.route('/stop/<id>', methods=['POST'])
def stop(id):
    data = {'command':3,'id': id}
    response = requests.post(FUNCTIONURL, data=json.dumps(data))
    return response.text

@app.route('/stream/<id>')
def stream(id):
    data = {'command':4,'id': id}
    def stats_stream():
        while True:
            response = requests.post(FUNCTIONURL, data=json.dumps(data))
            yield f'data: {response.text}\n\n'
            gevent.sleep(1)
    return Response(stats_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    print ("localhost:8070")
    serve(app, host="0.0.0.0", port=8070)