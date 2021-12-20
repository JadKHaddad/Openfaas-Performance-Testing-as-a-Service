import json, os, shutil, subprocess, signal, platform, traceback, pathlib, socket, atexit
from flask import jsonify, send_from_directory, request
from os.path import join
import time as t
from pathlib import Path
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from threading import Thread, Lock
from time import sleep


headers = {'Access-Control-Allow-Origin': '*','Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type'}
tasks = {}
installation_tasks = {}
LOCK = Lock() # for installation
LOCK2 = Lock() # for tests

# create projects dir
projects_dir = 'projects'
if not Path(projects_dir).exists():
    os.mkdir(projects_dir)

# create errors dir
errors_dir = 'errors'
if not Path(errors_dir).exists():
    os.mkdir(errors_dir)
            
# static functions
def is_port_in_use(port): # checks if a port is in use. used to distribute work
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_script_dir(project_name, script_name):
    return f'{projects_dir}/{project_name}/locust/{script_name}'

def get_test_dir(project_name, script_name, id):
    return f'{projects_dir}/{project_name}/locust/{script_name}/{id}'

def create_task_id(project_name, script_name, id):
    return f'TASK${project_name}${script_name}${id}' 

def kill_running_tasks():
    print("killing all tasks")
    if platform.system() == 'Windows': # windows
        for task_id in tasks:
            tasks[task_id].send_signal(signal.CTRL_BREAK_EVENT)
            tasks[task_id].kill()
        tasks.clear()
        for task_id in installation_tasks:
            installation_tasks[task_id].send_signal(signal.CTRL_BREAK_EVENT)
            installation_tasks[task_id].kill()
        # thread will clear the installation tasks
    else:
        for task_id in tasks:
            os.killpg(os.getpgid(tasks[task_id].pid), signal.SIGTERM)
        tasks.clear()
        for task_id in installation_tasks:
            os.killpg(os.getpgid(installation_tasks[task_id].pid), signal.SIGTERM)
        # thread will clear the installation tasks

def clean_up(): # deletes everything
    kill_running_tasks()
    if platform.system() == 'Windows': # windows
        sleep(2)
    if Path(projects_dir).exists():
        for f in os.scandir(projects_dir):
            if f.is_dir():
                shutil.rmtree(f.path)
            if f.is_file():
                os.remove(f.path)
    if Path('env/').exists():
        shutil.rmtree('env/')

def get_test_info(project_name, script_name, id):
    test_dir = get_test_dir(project_name, script_name, id)
    csv_file_path = f'{test_dir}/results_stats.csv'
    info_file_path = f'{test_dir}/info.txt'
    task_id = create_task_id(project_name, script_name, id)
    valid = True
    j = None
    if Path(csv_file_path).exists():
        if not os.stat(csv_file_path).st_size == 0:
            pd_data = pd.read_csv(csv_file_path) 
            j = pd_data.to_json(orient='records')

    if Path(info_file_path).exists():
        with open(info_file_path, 'r') as file:
            info = file.read()
    else:
        info = None

    if not Path(csv_file_path).exists(): # test is not valid
        valid = False
        if tasks[task_id].poll() == None:
            valid = True
        
    if task_id in tasks:
        data = {"id":id, "status":1, "data":j, "info":info,  "valid":valid, "project_name":project_name, "script_name":script_name} # status 1 -> test is running 
    else:
        data = {"id":id, "status":0, "data":j, "info":info, "valid":valid, "project_name":project_name, "script_name":script_name} # status 0 -> test is not running
    return data 

def clean_up_cache(project_name, script_name, id): # cleans up cache of a locust test before download
    test_dir = get_test_dir(project_name, script_name, id)
    cache = f'{test_dir}/__pycache__'
    if Path(cache).exists():
        shutil.rmtree(cache)

def zip_files(project_name, script_name, id): # creates zip file if zip file does not exist, returns True if zip file is created or is already there
    clean_up_cache(project_name, script_name, id)
    test_dir = get_test_dir(project_name, script_name, id)
    if not Path(test_dir).exists():
        return False
    script_dir = get_script_dir(project_name,script_name)
    if not Path(f'{script_dir}/{id}.zip').exists(): # creates zip file if it does not exist
        shutil.make_archive(test_dir, 'zip', test_dir)
    return True

def delete_zip_file(project_name, script_name, id):
    script_dir = get_script_dir(project_name,script_name)
    zip_file = f'{script_dir}/{id}.zip'
    if Path(zip_file).exists():
        os.remove(zip_file)

def create_plots(project_name, script_name, id): # creates plots if plots do no exist, returns True if plots are created or are already there
    test_dir = get_test_dir(project_name, script_name, id)
    stats_history_file = f'{test_dir}/results_stats_history.csv'
    if not Path(stats_history_file).exists():
        return 1 # test does not exist
    lin_path = join(test_dir, 'lin.png')
    reg_path = join(test_dir, 'reg.png')

    if not Path(lin_path).exists() or not Path(reg_path).exists():
        df = pd.read_csv(stats_history_file) 
        if len(df) > 4:
            if not Path(lin_path).exists():
                x = pd.to_datetime(df.iloc[:,0], unit='s').values
                plt.plot(x, df.iloc[:,19],color='b',label="Median Response Time") # med
                plt.plot(x, df.iloc[:,20],color='r',label="Average Response Time") # avg
                plt.plot(x, df.iloc[:,21],color='orange',label="Min Response Time") #min
                plt.plot(x, df.iloc[:,22],color='g',label="Max Response Time") #max
                plt.ylabel("Response Time (milliseconds)")
                plt.xlabel("Time")
                plt.xticks(rotation=45)
                plt.legend(loc="upper right")
                plt.savefig(lin_path,dpi=500,bbox_inches='tight')
                plt.close()
            if not Path(reg_path).exists():
                X = pd.to_datetime(df.iloc[:,0], unit='s').values
                X_plt = np.array(X).reshape((-1, 1))
                X_for_train = np.array(X.astype('float64')).reshape((-1, 1))
                Y = df.iloc[:,20].values.reshape(-1, 1)
                X_train, X_test, Y_train, Y_test = train_test_split(X_for_train, Y, test_size=0.2, random_state=0)
                linear_regressor = LinearRegression()  # create object for the class
                linear_regressor.fit(X_train, Y_train)  # perform linear regression
                Y_pred = linear_regressor.predict(X_for_train)  # make predictions
                plt.plot(X_plt, Y, label="Acutual average Response Time",)
                plt.plot(X_plt, Y_pred, color='red',label="Predicted average Response Time")
                plt.ylabel("Average response Time (milliseconds)")
                plt.xlabel("Time")
                plt.xticks(rotation=45)
                plt.legend(loc="upper right")
                plt.savefig(reg_path,dpi=500,bbox_inches='tight')
                plt.close()
        else:
            return 2 # not enough data
    return 0 # success

def clean_up_project_on_failed_installation(project_name): # runs in a thread!
    print(project_name +': clean up thread started')
    error_file = f'{errors_dir}/{project_name}.txt'
    while project_name in installation_tasks:
        print(project_name + ': sleeping')
        sleep(1)
        with LOCK:
            if installation_tasks[project_name].poll() is not None: # process finished
                print(project_name + ': task finished')
                if installation_tasks[project_name].returncode != 0:
                    if platform.system() != 'Windows':
                        out, err = installation_tasks[project_name].communicate()
                        print('Error caught in Thread: ' +  str(err))
                        # save installation error
                        with open(error_file, 'w', encoding='UTF-8') as file:
                            file.write(err.decode('UTF-8'))
                    print(project_name + ': cleaning up')
                    # delete project
                    project_path = f'{projects_dir}/{project_name}'
                    if Path(project_path).exists():
                        shutil.rmtree(project_path)
                    # delete project env
                    project_env_path = f'env/{project_name}'
                    if Path(project_env_path).exists():
                        shutil.rmtree(project_env_path)
                elif Path(error_file).exists():
                    # delete the file
                    os.remove(error_file)
                del installation_tasks[project_name]

    print(project_name +': terminating')

def handle(req, no_request=False):
    # we try the code block here to catch the error and get it displayed with the answer otherwise we get "server error 500" with no information about the error, could be removed after debugging phase
    try:
        if not no_request and 'file0' in request.files: # upload a new project
            # create an id for the project
            project_name = request.files['file0'].filename.split('/')[:-1][0]
            project_path = f'{projects_dir}/{project_name}'
            # check if project folder exists
            with LOCK:
                if Path(project_path).exists():
                    return jsonify(success=False,exit_code=2,message="project exists"), headers

                # save project files 
                for f in request.files.values():
                    uploaded_file_name = f.filename
                    uploaded_file_dir = '/'.join(uploaded_file_name.split('/')[:-1])
                    pathlib.Path(f'{projects_dir}/{uploaded_file_dir}').mkdir(parents=True, exist_ok=True) 
                    f.save(f'{projects_dir}/{uploaded_file_name}')

                # check locust scripts in locust folder
                if not Path(f'{project_path}/locust').exists():
                    shutil.rmtree(project_path)
                    return jsonify(success=False,exit_code=3,message="no locust dir found"), headers

                # check if locust tests exist
                locust_tests_exist = False
                for file in os.listdir(f'{project_path}/locust'):
                    if file.endswith('.py'):
                        locust_tests_exist = True
                        break
                if not locust_tests_exist:
                    shutil.rmtree(project_path)
                    return jsonify(success=False,exit_code=4,message="no locust tests found"), headers

                if not Path(f'{project_path}/requirements.txt').exists():
                    shutil.rmtree(project_path)
                    return jsonify(success=False,exit_code=5,message="no requirements found"), headers
                # create a virtual env and install req
                # check if req exists
                if platform.system() == 'Windows': # windows
                    req_cmd = f'&& .\env\{project_name}\Scripts\pip.exe install -r .\projects\{project_name}/requirements.txt'
                    installation_tasks[project_name] = subprocess.Popen(f'virtualenv env\{project_name} {req_cmd}', shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP) # stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                else:   
                    req_cmd = f'&& env/{project_name}/bin/pip3 install -r projects/{project_name}/requirements.txt'
                    installation_tasks[project_name] = subprocess.Popen(f'virtualenv env/{project_name} {req_cmd}', shell=True, stderr=subprocess.PIPE, preexec_fn=os.setsid) #stdout=subprocess.DEVNULL ,     
                thread = Thread(target=clean_up_project_on_failed_installation, args = (project_name, ))
                thread.start()
                
                return jsonify(success=True,exit_code=0,task_id=project_name,message="project added"), headers

        data = json.loads(req)
        command = data.get("command") or None

        if command is None:
            return  jsonify(success=False,exit_code=1,message="bad request"), headers

        if command == 1: # get installing projects -> sync
            projects = []
            with LOCK:
                for project_name in installation_tasks:
                    projects.append(project_name)
                return jsonify(success=True,exit_code=0,projects=projects,message='installing projects'), headers

        if command == 2: # check task -> sync
            task_id = data.get('task_id') or None
            if task_id is None:
                return json.dumps({'success':False,'exit_code':1,'message':'bad request'})
            with LOCK:
                if task_id in installation_tasks: # task running, thread will delete it when finished
                    return json.dumps({'success':True,'exit_code':0,'status_code':2,'message':'task not finished'})
                if not Path(f'{projects_dir}/{task_id}').exists():
                    err = None
                    error_file = f'{errors_dir}/{task_id}.txt'
                    if Path(error_file).exists():
                        with open(error_file, 'r', encoding='UTF-8') as file:
                            err = file.read()
                        # delete the file
                        os.remove(error_file)
                    return json.dumps({'success':True,'exit_code':0,'status_code':1,'message':'installation failed','error': str(err)})
                return json.dumps({'success':True,'exit_code':0,'status_code':0,'message':'task is finished'})

        if command == 3: # get installed projects -> sync
            projects = []
            with LOCK:
                with LOCK2:
                    for f in os.scandir(projects_dir):
                        if f.is_dir():
                            project_name = os.path.basename(f.path)
                            if project_name in installation_tasks:
                                if installation_tasks[project_name].poll() is not None:
                                    del installation_tasks[project_name]
                                    projects.append(project_name)
                            else:
                                projects.append(project_name)
                    return jsonify(success=True,exit_code=0,projects=projects,message="projects"), headers
        
        if command == 4: # get locust scripts of a project -> sync
            project_name = data.get('project_name') or None
            if project_name is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers 
            project_path = f'{projects_dir}/{project_name}'
            locust_scripts = []
            # check if project exists
            with LOCK2:
                if Path(project_path).exists():
                    for file in os.listdir(f'{project_path}/locust'):
                        if file.endswith('.py'):
                            locust_scripts.append(file.split('.')[0])
                return jsonify(success=True,exit_code=0,locust_scripts=locust_scripts,message="locust_scripts"), headers

        if command == 5: # start a test -> sync
            project_name = data.get("project_name") or None
            script_name = data.get("script_name") or None
            users = data.get("users") or None
            spawn_rate = data.get("spawn_rate") or None
            workers = data.get("workers") or None
            host = data.get("host") or None
            time = data.get("time") or None

            if project_name is None or script_name is None or users is None or spawn_rate is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers 

            # check if script exists
            script_path = f'{projects_dir}/{project_name}/locust/{script_name}.py'
            if not Path(script_path).exists():
                return jsonify(success=False,exit_code=5,message="script does not exist"), headers 

            id = str(t.time()).replace('.', '_')
            # create a test folder
            test_dir = get_test_dir(project_name, script_name, id)
            pathlib.Path(test_dir).mkdir(parents=True, exist_ok=True) 
            
            results_path = f'locust/{script_name}/{id}/results'
            log_path = f'locust/{script_name}/{id}/log.log'
            time_command = f'-t {str(time)}s' if time is not None else ''
            host_command = f'--host {host}' if host is not None else ''
            workers_count = workers if workers is not None else 0

            task_id = create_task_id(project_name, script_name, id)
            with LOCK2:
                if platform.system() == 'Windows': # windows
                    if workers_count > 0:
                        port = 5000
                        while is_port_in_use(port):
                            port = port + 1
                        worker_command = ''
                        for i in range(0, int(workers_count)):
                            worker_log_path = f'locust/{script_name}/{id}/worker_{i+1}_log.log'
                            worker_command = worker_command + f'cd .\{projects_dir}\{project_name} && ..\..\env\{project_name}\Scripts\locust.exe -f locust/{script_name}.py --logfile {worker_log_path} --worker --master-port={port} & '
                        master_command = f'cd .\{projects_dir}\{project_name} && ..\..\env\{project_name}\Scripts\locust.exe -f locust/{script_name}.py  {host_command} --users {users} --spawn-rate {spawn_rate} --headless {time_command} --csv {results_path} --logfile {log_path} --master --master-bind-port={port} --expect-workers={workers_count}'    
                        command = worker_command + master_command
                    else:
                        command = f'cd .\{projects_dir}\{project_name} && ..\..\env\{project_name}\Scripts\locust.exe -f locust/{script_name}.py  {host_command} --users {users} --spawn-rate {spawn_rate} --headless {time_command} --csv {results_path} --logfile {log_path}'
                    tasks[task_id] = subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
    
                else: # linux
                    if workers_count > 0:
                        port = 5000
                        while is_port_in_use(port):
                            port = port + 1
                        worker_command = ''
                        for i in range(0, int(workers_count)):
                            worker_log_path = f'locust/{script_name}/{id}/worker_{i+1}_log.log'
                            worker_command = worker_command + f'cd projects/{project_name} && ../../env/{project_name}/bin/locust -f locust/{script_name}.py --logfile {worker_log_path} --worker --master-port={port} &'
                        master_command = f'cd {projects_dir}/{project_name} && ../../env/{project_name}/bin/locust -f locust/{script_name}.py  {host_command} --users {users} --spawn-rate {spawn_rate} --headless {time_command} --csv {results_path} --logfile {log_path} --master --master-bind-port={port} --expect-workers={workers_count}'    
                        command = worker_command + master_command
                    else:
                        command = f'cd {projects_dir}/{project_name} && ../../env/{project_name}/bin/locust -f locust/{script_name}.py  {host_command} --users {users} --spawn-rate {spawn_rate} --headless {time_command} --csv {results_path} --logfile {log_path}'

                    tasks[task_id] = subprocess.Popen(f'ulimit -n 64000; {command}', shell=True, preexec_fn=os.setsid)#stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
                
                started_at = t.time()
                # save test info
                info_file = f'{test_dir}/info.txt'
                with open(info_file, "w", encoding="UTF-8") as file:
                    file.write(json.dumps({"users": users, "spawn_rate": spawn_rate, "host": host,"workers":workers_count, "time": time, "started_at":started_at}))

                return jsonify(success=True,exit_code=0,id=id,started_at=started_at,message="test started"), headers

        if command == 6: # get test stats -> sync
            project_name = data.get("project_name") or None
            script_name = data.get("script_name") or None
            id = data.get("id") or None
            local = data.get('local') or None
            if project_name is None or script_name is None or id is None:
                if local is not None:
                    return json.dumps({'success':False,'exit_code':1,'message':'bad request'})
                return jsonify(success=False,exit_code=1,message="bad request"), headers

            # check if test is runnig
            task_id = create_task_id(project_name, script_name, id)
            with LOCK2:
                if task_id in tasks:
                    test_dir = get_test_dir(project_name, script_name, id)
                    csv_file_path = f'{test_dir}/results_stats.csv'
                    if tasks[task_id].poll() is not None: # process finished
                        if not Path(csv_file_path).exists(): # test is not valid
                            del tasks[task_id]
                            if local is not None:
                                return json.dumps({'success':False,'exit_code':4,'message':'test is not valid'})
                            return jsonify(success=False,exit_code=4,message="test is not valid"), headers 
                        del tasks[task_id]
                    if not Path(csv_file_path).exists():
                        if local is not None:
                            return json.dumps({'success':False,'exit_code':3,'message':'csv file does not exist'})
                        return jsonify(success=False,exit_code=3,message="csv file does not exist"), headers
                    j = None
                    if not os.stat(csv_file_path).st_size == 0:
                        pd_data = pd.read_csv(csv_file_path) 
                        j = pd_data.to_json(orient='records')
                    if local is not None:
                        return json.dumps({'success':True,'exit_code':0,'status':1,'data':j,'message':'test running'})
                    return jsonify(success=True,exit_code=0,status=1,data=j,message="test running"), headers # status 1 -> test is running
                if local is not None:
                    return json.dumps({'success':True,'exit_code':0,'status':0,'data':None,'message':'test is not runnig'})
                return jsonify(success=True,exit_code=0,status=0,data=None,message="test is not runnig"), headers # status 0 -> test not running

        if command == 7: # get all tests of a script-> sync
            project_name = data.get("project_name") or None
            script_name = data.get("script_name") or None
            if project_name is None or script_name is None :
                return jsonify(success=False,exit_code=1,message="bad request"), headers
            tests_folders = {}
            scrpit_folder_path = f'{projects_dir}/{project_name}/locust/{script_name}'

            with LOCK2:
                if Path(scrpit_folder_path).exists():
                    for f in os.scandir(scrpit_folder_path):
                        if f.is_dir():
                            id = os.path.basename(f.path)
                            tests_folders[id]= get_test_info(project_name, script_name, id)

                return jsonify(success=True,exit_code=0,tests=tests_folders,message="folders"), headers

        if command == 8: # stop test -> sync
            project_name = data.get("project_name") or None
            script_name = data.get("script_name") or None
            id = data.get("id") or None
            if project_name is None or script_name is None or id is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers
            task_id = create_task_id(project_name, script_name, id)
            #stop the task
            with LOCK2:
                if task_id not in tasks:
                    return jsonify(success=True,exit_code=0,message="test is stopped"), headers
                if platform.system() == 'Windows': # windows
                    tasks[task_id].send_signal(signal.CTRL_BREAK_EVENT)
                    tasks[task_id].kill()
                else:
                    os.killpg(os.getpgid(tasks[task_id].pid), signal.SIGTERM)
                del tasks[task_id]
                return jsonify(success=True,exit_code=0,message="test is stopped"), headers

        if command == 9: # delete test -> sync
            project_name = data.get("project_name") or None
            script_name = data.get("script_name") or None
            id = data.get("id") or None
            if project_name is None or script_name is None or id is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers
            task_id = create_task_id(project_name, script_name, id)
            # stop the task  
            with LOCK2:
                if task_id in tasks:
                    if platform.system() == 'Windows': # windows
                        tasks[task_id].send_signal(signal.CTRL_BREAK_EVENT)
                        tasks[task_id].kill()
                        sleep(1)
                    else:
                        os.killpg(os.getpgid(tasks[task_id].pid), signal.SIGTERM)
                    del tasks[task_id]

                test_dir = get_test_dir(project_name, script_name, id)
                if not Path(test_dir).exists():
                    return jsonify(success=False,exit_code=6,message="test does not exist"), headers
                shutil.rmtree(test_dir) # remove test_dir
                delete_zip_file(project_name, script_name,id)
                return jsonify(success=True,exit_code=0,message="deleted"), headers

        if command == 10: # delete projects -> sync
            names = data.get("names") or None
            if names is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers
            deleted = []
            with LOCK2:
                for name in names:
                    # stop running tests
                    deleted = []
                    for task_id in tasks:
                        if task_id.startswith(f'TASK${name}$'):
                            deleted.append(task_id)
                            if platform.system() == 'Windows': # windows
                                tasks[task_id].send_signal(signal.CTRL_BREAK_EVENT)
                                tasks[task_id].kill()
                            else: # Linux
                                os.killpg(os.getpgid(tasks[task_id].pid), signal.SIGTERM)
                    for deleted_task in deleted:
                        del tasks[deleted_task]
                    # delete project dir
                    project_path = f'{projects_dir}/{name}'
                    if Path(project_path).exists():
                        shutil.rmtree(project_path)
                    # delete project env
                    project_env_path = f'env/{name}'
                    if Path(project_env_path).exists():
                        shutil.rmtree(project_env_path)
                    deleted.append(name)
                return jsonify(success=True,exit_code=0,deleted=deleted), headers

        if command == 11: # download a test -> sync
            project_name = data.get("project_name") or None
            script_name = data.get("script_name") or None
            id = data.get("id") or None
            if project_name is None or script_name is None or id is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers

            with LOCK2:
                # create plots
                create_plots(project_name, script_name, id)
                # zip files
                if zip_files(project_name,script_name,id):
                    script_dir = get_script_dir(project_name,script_name)
                    return send_from_directory(script_dir, f'{id}.zip'), headers
                else:
                    return jsonify(success=False,exit_code=2,message="test does not exist"), headers 

        if command == 12: # get plots -> sync
            project_name = data.get("project_name") or None
            script_name = data.get("script_name") or None
            id = data.get("id") or None
            type = data.get("type") or None
            if project_name is None or script_name is None or id is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers
            test_dir = get_test_dir(project_name, script_name, id)

            with LOCK2:
                if type == 1: # create
                    status_code = create_plots(project_name, script_name, id) # 0: success, 1 test does not exist, 2 not enough data
                    return jsonify(success=True,exit_code=0,status_code=status_code), headers 
                if type == 2: # linear
                    return send_from_directory(test_dir, f'lin.png'), headers
                if type == 3: # regression 
                    return send_from_directory(test_dir, f'reg.png'), headers
                else:
                    return jsonify(success=False,exit_code=1,message="bad request"), headers 

        if command == 13: # get all running tests -> sync
            local = data.get('local') or None
            running_tests = {}
            with LOCK2:
                for task_id in tasks:
                    task_id_splitted = task_id.split('$')
                    project_name = task_id_splitted[1]
                    script_name = task_id_splitted[2]
                    id = task_id_splitted[3]
                    if tasks[task_id].poll() == None: # still running
                        running_tests[id] = get_test_info(project_name, script_name, id)
                if local is not None:
                    return json.dumps({'success':True,'exit_code':0,'tests':running_tests,'message':'running tests'})
                return jsonify(success=True,exit_code=0,tests=running_tests,message="running tests"), headers

        if command == 14: # get count of running tests
            local = data.get('local') or None
            with LOCK2:
                count = len(tasks)
            if local is not None:
                return json.dumps({'success':True,'exit_code':0,'count':count,'message':'count of running tests'})
            return jsonify(success=True,exit_code=0,count=count,message="count of running tests"), headers

        if command == 15: # stop installing task
            task_id = data.get("project_name") or None
            if task_id is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers
            with LOCK:
                if platform.system() == 'Windows': # windows
                    if task_id in installation_tasks:
                        installation_tasks[task_id].send_signal(signal.CTRL_BREAK_EVENT)
                        installation_tasks[task_id].kill()
                    # thread will clear the installation task
                else:
                    if task_id in installation_tasks:
                        os.killpg(os.getpgid(installation_tasks[task_id].pid), signal.SIGTERM)
                    # thread will clear the installation task
                return jsonify(success=True,exit_code=0,message="task killed"), headers
        
        if command == 16: # delete all tests of script
            project_name = data.get("project_name") or None
            script_name = data.get("script_name") or None
            if project_name is None or script_name is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers
            #stop all running tests for this script
            with LOCK2:
                # stop running tests
                stopped = []
                for task_id in tasks:
                    if task_id.startswith(f'TASK${project_name}${script_name}$'):
                        print(task_id)
                        stopped.append(task_id)
                        if platform.system() == 'Windows': # windows
                            tasks[task_id].send_signal(signal.CTRL_BREAK_EVENT)
                            tasks[task_id].kill()
                        else: # Linux
                            os.killpg(os.getpgid(tasks[task_id].pid), signal.SIGTERM)
                if platform.system() == 'Windows': # windows
                    sleep(2)
                # delete stoped tasks
                for stopped_task in stopped:
                    del tasks[stopped_task]
                # delete tes dir
                script_path = get_script_dir(project_name,script_name)
                print(script_path)
                if Path(script_path).exists():
                    shutil.rmtree(script_path)
                return jsonify(success=True,exit_code=0,message="deleted"), headers

        if command == 17: # get all running tests of a script
            project_name = data.get("project_name") or None
            script_name = data.get("script_name") or None
            ids = data.get("ids") or None
            
            local = data.get('local') or None
            if project_name is None or script_name is None:
                if local is not None:
                    return json.dumps({'success':False,'exit_code':1,'message':'bad request'})
                return jsonify(success=False,exit_code=1,message="bad request"), headers
            if ids is None:
                ids = []
            tests = []
            with LOCK2:
                for id in ids:    
                    task_id = create_task_id(project_name, script_name, id)
                    if task_id in tasks:
                        test_dir = get_test_dir(project_name, script_name, id)
                        csv_file_path = f'{test_dir}/results_stats.csv'
                        if tasks[task_id].poll() is not None: # process finished
                            if not Path(csv_file_path).exists(): # test is not valid
                                del tasks[task_id]
                                tests.append({'id':id, 'status':3, 'message':'test is not valid'})
                                continue
                            del tasks[task_id]
                        if not Path(csv_file_path).exists():
                            tests.append({'id':id, 'status':2, 'message':'csv file does not exist'})
                            continue
                        j = None
                        if not os.stat(csv_file_path).st_size == 0:
                            pd_data = pd.read_csv(csv_file_path) 
                            j = pd_data.to_json(orient='records')
                        tests.append({'id':id, 'status':1, 'data':j,'message':'test running'}) # status 1 -> test is running
                        continue
                    tests.append({'id':id, 'status':0, 'data':None,'message':'test is not runnig'}) # status 0 -> test not running

            if local is not None:
                return json.dumps({'success':True,'tests':tests})
            return jsonify(success=True,tests=tests), headers 

        if command == 911: # kill all running tasks -> sync
            with LOCK:
                with LOCK2:
                    kill_running_tasks()
                    return jsonify(success=True,exit_code=0,message="tasks killed"), headers

        if command == 912: # clean up -> sync
            with LOCK:
                with LOCK2:
                    clean_up()
                    return jsonify(success=True,exit_code=0,message="clean up"), headers

        if command == 913: # show saved tasks -> sync
            saved_tasks = []
            saved_installation_tasks = []
            with LOCK:
                with LOCK2:
                    for key in tasks.keys():
                        saved_tasks.append(key)
                    for key in installation_tasks.keys():
                        saved_installation_tasks.append(key)
                    return jsonify(success=True,exit_code=0,tasks=saved_tasks, installation_tasks=saved_installation_tasks,message="saved tasks"), headers

        if command == 914: # test connection -> sync
            return jsonify(success=True), headers

    except Exception as e:
        print(traceback.format_exc())
        return jsonify(success=False,exit_code=-1,message=str(e),trace_back=traceback.format_exc()), headers

atexit.register(kill_running_tasks)