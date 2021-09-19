from flask import Flask, render_template, request, Response
from waitress import serve
import requests
import json
import gevent
import argparse
from urllib.parse import urljoin

OPENFASSULR = None
FUNCTION = None
FUNCTIONURL = None
ASYNCFUNCTIONURL = None

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
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,help='help')
    parser.add_argument('-v', '--version', action='version',version='%(prog)s 1.0', help='version')
    parser.add_argument('-s', '--host', help='server host',metavar='')
    parser.add_argument('-p', '--port', help='server port',metavar='')
    parser.add_argument('-u', '--url', help='openfaas url',metavar='')
    parser.add_argument('-f','--function', help='function name',metavar='')

    args = parser.parse_args()

    host = args.host
    port = args.port
    url = args.url
    function = args.function
    if not host or not port or not url or not function:
        print('all arguments are required --host <host> --port <port> --url <openfaas url> --function <funcion name>')
        exit()

    OPENFASSULR = url
    FUNCTION = function
    SYNC = urljoin(OPENFASSULR, 'function/')
    ASYNC = urljoin(OPENFASSULR, 'async-function/')
    FUNCTIONURL = urljoin(SYNC, FUNCTION)
    ASYNCFUNCTIONURL = urljoin(ASYNC, FUNCTION)

    print(f'openfaas url {OPENFASSULR}')
    print(f'sync function call {FUNCTIONURL}')
    print(f'async function call {ASYNCFUNCTIONURL}')
    print(f'server running on {host}:{port}')
    serve(app, host=host, port=port)
