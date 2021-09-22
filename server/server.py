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
    return render_template('index.html', function_call=FUNCTIONURL, direct=DIRECT)

@app.route('/explore')
def explore():
    return render_template('explore.html', function_call=FUNCTIONURL, direct=DIRECT)

@app.route('/test/<id>')
def test(id):
    return render_template('test.html', id=id, function_call=FUNCTIONURL, direct=DIRECT)

@app.route('/stream/<id>')
def stream(id):
    data = {'command':4,'id': id}
    def stats_stream():
        while True:
            response = requests.post(FUNCTIONURL, data=json.dumps(data))
            yield f'data: {response.text}\n\n'
            gevent.sleep(1)
    return Response(stats_stream(), mimetype="text/event-stream")

@app.route('/tests')
def tests():
    data = {'command':6}
    response = requests.post(FUNCTIONURL, data=json.dumps(data))
    return response.text

@app.route('/test-info/<id>', methods=['POST'])
def test_info(id):
    data = {'command':8,'id': id}
    response = requests.post(FUNCTIONURL, data=json.dumps(data))
    return response.text

@app.route('/deploy', methods=['POST'])
def deploy():
    users = request.form.get('users') or None
    spawn_rate = request.form.get('spawn_rate') or None
    host = request.form.get('host') or None
    time = request.form.get('time') or None
    code = request.form.get('code') or None
    requirements = request.form.get('requirements') or None
    if time is not None:
        time = int(time)
    if users is not None:
        users = int(users)
    if spawn_rate is not None:
        spawn_rate = int(spawn_rate)
    data = {'command':1,'users': users, 'spawn_rate': spawn_rate, 'host': host, 'time':time, 'code':code, 'requirements':requirements}
    response = requests.post(FUNCTIONURL, data=json.dumps(data))
    return response.text

@app.route('/start/<id>', methods=['POST'])
def start(id):
    data = {'command':2,'id': id}
    response = requests.post(FUNCTIONURL, data=json.dumps(data))#, timeout=0.0000000001)
    return response.text

@app.route('/stop/<id>', methods=['POST'])
def stop(id):
    data = {'command':3,'id': id}
    response = requests.post(FUNCTIONURL, data=json.dumps(data))
    return response.text

@app.route('/delete', methods=['POST'])
def delete():
    ids = request.form.get('ids')
    data = '{"command":7,"ids":'+ids+'}'
    response = requests.post(FUNCTIONURL, data)
    return response.text

@app.route('/download/<id>', methods=['POST'])
def download(id):
    data = {'command':5,'id': id}
    res = requests.post(FUNCTIONURL, data=json.dumps(data))
    return Response(
        response=res.content,
        status=res.status_code,
        headers=dict(res.headers)
    )
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,help='help')
    parser.add_argument('-v', '--version', action='version',version='%(prog)s 1.0', help='version')
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-s', '--host', help='server host',metavar='',required=True)
    requiredNamed.add_argument('-p', '--port', help='server port',metavar='',required=True)
    requiredNamed.add_argument('-u', '--url', help='openfaas url',metavar='',required=True)
    requiredNamed.add_argument('-f','--function', help='function name',metavar='',required=True)
    requiredNamed.add_argument('-d','--direct', help='can the browser connect to openfaas directly? <true || false>',metavar='',required=True)

    args = parser.parse_args()

    host = args.host
    port = args.port
    url = args.url
    function = args.function
    direct = args.direct

    OPENFAASULR = url
    FUNCTION = function
    SYNC = urljoin(OPENFAASULR, 'function/')
    ASYNC = urljoin(OPENFAASULR, 'async-function/')
    FUNCTIONURL = urljoin(SYNC, FUNCTION)
    ASYNCFUNCTIONURL = urljoin(ASYNC, FUNCTION)
    DIRECT = direct

    print(f'openfaas url: {OPENFAASULR}')
    print(f'sync function call: {FUNCTIONURL}')
    print(f'async function call: {ASYNCFUNCTIONURL}')
    print(f'direct: {direct}')
    print(f'server running on {host}:{port}')
    serve(app, host=host, port=port,threads=8)
