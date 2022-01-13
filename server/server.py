#!/usr/bin/env python3

import platform, subprocess, datetime, requests, json, argparse, os, sys, random, string, pathlib, shutil, redis
from redis.exceptions import ConnectionError
from flask import Flask, render_template, request, Response, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from urllib.parse import urljoin, unquote
from threading import Lock
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

# handler is needed if openfaas is not being used
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from ptas import handler

LOCAL = False

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

dist_dir = os.path.abspath('./dist/')

app = Flask(__name__, template_folder=dist_dir, static_url_path='')
socketio = SocketIO(app, cors_allowed_origins='*')

# static functions
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

#defining all this junk because we want to build our frontend and use it out of the box. just build it and paste it in dist folder 
   
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
    error = False
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
        try:
            res = requests.post(url, data=request.data, files=files)
        except:
            error = True
        # close the files
        for o in openfiles:
            o.close()
        # delete the files
        shutil.rmtree(path)
    else:
        try:
            res = requests.post(url, data=request.data)   
        except:
            error = True
    if error:
        return Response(
        status=503
        )
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
        if(res.status_code >= 400 or res.status_code < 200):
            return jsonify(success=False)
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
        return jsonify(success=False)

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
    print(f'Client connected: {session_id}')

CONNECTED_CLIENTS = {}
T = None
T_LOCK = Lock()

def T_TASK():
    global T
    while True:
        #copy
        with T_LOCK:
            current_connected_clients = CONNECTED_CLIENTS.copy()
        if(len(current_connected_clients) < 1): break
        sent = {}
        for key, client in current_connected_clients.items():
            url = client['url']
            events = client['events']
            for event, params in events.items():
                #control
                if event == 'control':
                    if f'{url}_control' not in sent:
                        if url == 'None':
                            data = {'command':13, 'local':True}
                            response = handler.handle(json.dumps(data), True)
                            socketio.emit(f'{url}_control', response)
                        else:
                            data = {'command':13}
                            post_url = unquote(url)
                            post_url = urljoin(post_url, 'function/')
                            post_url = urljoin(post_url, FUNCTION)
                            try:
                                response = requests.post(post_url, data=json.dumps(data), timeout=2)
                                socketio.emit(f'{url}_control', response.text)
                            except:
                                socketio.emit(f'{url}_control', {'success': False})
                        #print('sent to: ', f'{url}_control')
                        sent[f'{url}_control'] = None
                    continue
                #script
                if event == 'script':
                    for key, value in params.items():
                        project_name = value['project_name']
                        script_name = value['script_name']
                        ids = value['test_ids']
                        if len(ids) > 0:
                            if f'{url}_{project_name}_{script_name}' not in sent:
                                if url == 'None':
                                    data = {'command':6, 'project_name':project_name, 'script_name':script_name, 'ids': ids,'local':True}
                                    response = handler.handle(json.dumps(data), True)
                                    socketio.emit(f'{url}_{project_name}_{script_name}', response)
                                else:
                                    data = {'command':6, 'project_name':project_name, 'script_name':script_name, 'ids': ids}
                                    post_url = unquote(url)
                                    post_url = urljoin(post_url, 'function/')
                                    post_url = urljoin(post_url, FUNCTION)
                                    try:
                                        response = requests.post(post_url, data=json.dumps(data), timeout=2)
                                        socketio.emit(f'{url}_{project_name}_{script_name}', response.text)
                                    except:
                                        socketio.emit(f'{url}_{project_name}_{script_name}', {'success': False})
                                #print('sent to: ', f'{url}_{project_name}_{script_name}')
                                sent[f'{url}_{project_name}_{script_name}'] = None
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
                #print('sent to: ', url)
                sent[url] = None
        socketio.sleep(2)
    print('Background thread has stopped')
    with T_LOCK: 
        T = None   

@socketio.on('register')
def register(message):
    client = request.sid
    url = message.get('openfaasurl')
    if url is None:
        url = 'None',
    with T_LOCK:
        if client in CONNECTED_CLIENTS: #just update the url bro! o_O
            CONNECTED_CLIENTS[client]['url'] = url
        else:    
            CONNECTED_CLIENTS[client] = {'url':url, 'events':{}}
    print(f'Registered clients: {len(CONNECTED_CLIENTS)}')
    #print('\nT Client registered: ', client)
    #print('T OpenFaas Url: ', url)
    #print('T Current connected clients: ', CONNECTED_CLIENTS)
    global T
    with T_LOCK: 
        if T is None:
            T = socketio.start_background_task(target=T_TASK)#Thread(target=T_TASK)
            T.daemon = True
            T.start()
            print('Background thread started')

@socketio.on('register_control')
def register_control(message):
    client = request.sid
    url = message.get('openfaasurl')
    if url is None:
        url = 'None',
    with T_LOCK:
        CONNECTED_CLIENTS[client]['events']['control'] = None
    #print('\nClient registered control: ', client)
    #print('OpenFaas Url: ', url)
    #print('Current connected clients: ', CONNECTED_CLIENTS)

@socketio.on('disconnect_control')
def disconnect_control():
    client = request.sid
    with T_LOCK:
        if client in CONNECTED_CLIENTS:
            if 'control' in CONNECTED_CLIENTS[client]['events']:
                del CONNECTED_CLIENTS[client]['events']['control']
    #print('\nClient unsunscribed control', client)
    #print('Current connected clients: ', CONNECTED_CLIENTS)

@socketio.on('register_script')
def register_script(message):
    client = request.sid
    url = message.get('openfaasurl')
    project_name = message.get('project_name')
    script_name = message.get('script_name')
    test_ids = message.get('test_ids')
    if test_ids is None:
        test_ids = []
    if url is None:
        url = 'None',
    with T_LOCK:
        CONNECTED_CLIENTS[client]['events']['script'] = {f'{project_name}_{script_name}': {'project_name':project_name, 'script_name':script_name,'test_ids':test_ids}}
    #print('\nClient registered script: ', client)
    #print('OpenFaas Url: ', url)
    #print('Current connected clients: ', CONNECTED_CLIENTS)

@socketio.on('disconnect_script')
def disconnect_script(message):
    client = request.sid
    with T_LOCK:
        if client in CONNECTED_CLIENTS:
            if 'script' in CONNECTED_CLIENTS[client]['events']:
                del CONNECTED_CLIENTS[client]['events']['script']
    #print('\nClient unsunscribed script', client)
    #print('Current connected clients: ', CONNECTED_CLIENTS)

@socketio.on('register_test')
def register_test(message):
    client = request.sid
    url = message.get('openfaasurl')
    project_name = message.get('project_name')
    script_name = message.get('script_name')
    test_id = message.get('test_id')
    if url is None:
        url = 'None',
    with T_LOCK:
        if 'script' in CONNECTED_CLIENTS[client]['events']:
            CONNECTED_CLIENTS[client]['events']['script'][f'{project_name}_{script_name}']['test_ids'].append(test_id)
        else:
            CONNECTED_CLIENTS[client]['events']['script'] = {f'{project_name}_{script_name}': {'project_name':project_name, 'script_name':script_name,'test_ids':[test_id]}}
    #print('\nClient registered test: ', client)
    #print('OpenFaas Url: ', url)
    #print('Current connected clients: ', CONNECTED_CLIENTS)

@socketio.on('disconnect_test')
def disconnect_test(message):
    client = request.sid
    project_name = message.get('project_name')
    script_name = message.get('script_name')
    test_id = message.get('test_id')
    with T_LOCK:
        if client in CONNECTED_CLIENTS:
            if 'script' in CONNECTED_CLIENTS[client]['events']:
                if test_id in CONNECTED_CLIENTS[client]['events']['script'][f'{project_name}_{script_name}']['test_ids']:
                    CONNECTED_CLIENTS[client]['events']['script'][f'{project_name}_{script_name}']['test_ids'].remove(test_id)
    #print('\nClient unsunscribed test', client)
    #print('Current connected clients: ', CONNECTED_CLIENTS)

@socketio.on('test_start')
def test_start(message):
    url = message.get('openfaasurl')
    project_name = message.get('project_name')
    script_name = message.get('script_name')
    test = message.get('test')
    socketio.emit(f'{url}_{project_name}_{script_name}_test_start', test)

@socketio.on('test_delete')
def test_delete(message):
    url = message.get('openfaasurl')
    project_name = message.get('project_name')
    script_name = message.get('script_name')
    ids = message.get('ids')
    socketio.emit(f'{url}_{project_name}_{script_name}_test_delete', ids)
    socketio.emit(f'{url}_control_test_delete', ids)

@socketio.on('test_stop')
def test_stop(message):
    url = message.get('openfaasurl')
    id = message.get('id')
    socketio.emit(f'{url}_control_test_stop', id)

@socketio.on('project_upload')
def peoject_upload(message):
    url = message.get('openfaasurl')
    project_name = message.get('project_name')
    socketio.emit(f'{url}_project_upload', project_name)

@socketio.on('project_delete')
def peoject_delete(message):
    url = message.get('openfaasurl')
    project_names = message.get('project_names')
    socketio.emit(f'{url}_project_delete', project_names)
    for project_name in project_names:
        socketio.emit(f'{url}_project_delete_{project_name}')

@socketio.on('clean_up')
def clean_up(message):
    url = message.get('openfaasurl')
    socketio.emit(f'{url}_clean_up')

OPENFAAS_T = None
OPENFAAS_T_LOCK = Lock()
def check_openfaas_thread():
    global OPENFAAS_T
    while(True):
        installed, check, message = check_openfaas()
        socketio.emit('openfaas', {'data': installed})
        #print("sent")
        if installed:
            break
        socketio.sleep(3)
    with OPENFAAS_T_LOCK: 
        OPENFAAS_T = None
    
@socketio.on('openfaas')
def openfass_socket():
    global OPENFAAS_T
    installed, check, message = check_openfaas()
    socketio.emit('openfaas', {'data': installed}, broadcast=False)
    with OPENFAAS_T_LOCK: 
        if OPENFAAS_T is None:
            OPENFAAS_T = socketio.start_background_task(target=check_openfaas_thread)#Thread(target=check_openfaas_thread)
            OPENFAAS_T.daemon = True
            OPENFAAS_T.start()

@socketio.on('disconnect')
def disconnect():
    client = request.sid
    with T_LOCK:
        if client in CONNECTED_CLIENTS:
            del CONNECTED_CLIENTS[client]
    print(f'Client disconnected: {client}')
    print(f'Registered clients: {len(CONNECTED_CLIENTS)}')
    
if __name__ == '__main__':
    extern = False
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,help='help')
    parser.add_argument('-v', '--version', action='version',version='%(prog)s 1.0', help='version')
    parser.add_argument('-e', '--extern', action='store_true', help='use if OpenFaaS is running on the external ip address of your machine')
    parser.add_argument('-l', '--local', action='store_true', help='use if you dont want to use an OpenFaaS server. server will run on 0.0.0.0:80 with no OpenFaaS server')
    parser.add_argument('-r', '--redis', action='store_true', help='use redis (cache). recommended if you dont have SSD')
    parser.add_argument('-rh', '--redishost', help='redis host, default: localhost',metavar='')
    parser.add_argument('-rp', '--redisport', help='redis port, default: 6379',metavar='')
    parser.add_argument('-re', '--redisexpire', help='redis (cache) expiration timer, default: 600 seconds',metavar='')
    parser.add_argument('-rd', '--redisdatabase', help='redis database: 0 - 15, default: 0',metavar='')
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-s', '--host', help='server host, default: 0.0.0.0',metavar='')
    requiredNamed.add_argument('-p', '--port', help='server port, default: 80',metavar='')
    requiredNamed.add_argument('-u', '--url', help='OpenFaaS url',metavar='')
    requiredNamed.add_argument('-f','--function', help='function name',metavar='')
    requiredNamed.add_argument('-d','--direct', action='store_true', help='can the browser connect to OpenFaaS directly?')
    
    args = parser.parse_args()

    host = args.host or '0.0.0.0'
    port = args.port or '80'
    port = '80' if not port.isdigit() else port

    redis_host = args.redishost or 'localhost'
    redis_port = args.redisport or '6379'
    redis_port = '6379' if not redis_port.isdigit() else redis_port
    redis_expire = args.redisexpire or '600'
    redis_expire = 600 if not redis_expire.isdigit() else int(redis_expire)
    redis_database = args.redisdatabase or '0'
    redis_database = 0 if not redis_database.isdigit() else int(redis_database)
    if redis_database > 15 or redis_database < 0:
        redis_database = 0
    use_redis = args.redis

    url = args.url
    extern = args.extern
    function = args.function or 'ptas'
    DIRECT = args.direct
    LOCAL = args.local

    if url is None:
        ALLOWPROXY = False
    else:
        ALLOWPROXY = True

    if url is None and extern == False and LOCAL == False:
        print('please provide an openfaasurl using -u or -e or use -l if you dont want to use an openfaas server')
        exit()
        
    OPENFAASULR = url
    PROXYOPENFAASULR = url

    if extern == True:
        if platform.system() == 'Linux':
            host = subprocess.Popen("echo $(/sbin/ip -o -4 addr list  | awk '{print $4}' | cut -d/ -f1)", shell=True, stdout=subprocess.PIPE).stdout.read().decode('UTF-8').split(' ')[1].replace('\n','')
            OPENFAASULR = (f'http://{host}:8080/')
        else:
            if url is None:
                print('if you are not using Linux please provide your external ip address manually')
                exit()
        if not DIRECT:
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
        if not DIRECT:
            print(f'\nproxy openfaas url: {PROXYOPENFAASULR}')
            print(f'proxy sync function call: {PROXYFUNCTIONURL}')
            print(f'proxy async function call: {PROXYASYNCFUNCTIONURL}')
        print(f'\ndirect: {DIRECT}')
    print(f'server running on {host}:{port}')
    print(f'running with websockets')
    if use_redis is True:
        redis = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_database,
        charset="utf-8", 
        decode_responses=True)
        try:
            redis.ping()
        except ConnectionError:
            print("Could not connect to redis. Please check your redis server and try again")
            exit()
        handler.REDIS = redis
        handler.EXPIRE = redis_expire
        print(f'using redis on {redis_host}:{redis_port} | database: [{redis_database}] | cache lifetime: {redis_expire} seconds')
    server = pywsgi.WSGIServer((host, int(port)), app, handler_class=WebSocketHandler)
    server.serve_forever()