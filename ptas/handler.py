import json
from flask import jsonify, send_from_directory
from os.path import join, dirname, realpath
import time as t
from pathlib import Path
import os
import shutil
import pandas as pd
import subprocess
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import signal
import platform
import traceback
import pathlib

headers = {'Access-Control-Allow-Origin': '*','Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type'}
tasks = {}

projects_dir = 'projects'
if not Path(projects_dir).exists():
    os.mkdir(projects_dir)
            
# static functions
def get_script_dir(project_name, script_name):
    return f'{projects_dir}/{project_name}/locust/{script_name}'

def get_test_dir(project_name, script_name, id):
    return f'{projects_dir}/{project_name}/locust/{script_name}/{id}'

def kill_running_tasks():
    if platform.system() == 'Windows': # windows
        for task_id in tasks:
            tasks[task_id].send_signal(signal.CTRL_BREAK_EVENT)
            tasks[task_id].kill()
        tasks.clear()
    else:
        for task_id in tasks:
            print(task_id)
            os.killpg(os.getpgid(tasks[task_id].pid), signal.SIGTERM)
        tasks.clear()

def clean_up():
    kill_running_tasks()
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
    task_id = f'{project_name}_{script_name}_{id}' 
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
    if task_id in tasks:
        data = {"id":id, "status":1, "data":j, "info":info,  "valid":valid} # status 1 -> test is running 
    else:
        data = {"id":id, "status":0, "data":j, "info":info, "valid":valid} # status 0 -> test is not running
    return data 

def clean_up_cache(project_name, script_name, id):
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
                plt.plot(df.iloc[:,17], df.iloc[:,19],color='b',label="Median Response Time") # med
                plt.plot(df.iloc[:,17], df.iloc[:,20],color='r',label="Average Response Time") # avg
                plt.plot(df.iloc[:,17], df.iloc[:,21],color='orange',label="Min Response Time") #min
                plt.plot(df.iloc[:,17], df.iloc[:,22],color='g',label="Max Response Time") #max
                plt.ylabel("Time (milliseconds)")
                plt.xlabel("Requests Count")
                plt.legend(loc="upper right")
                plt.savefig(lin_path,dpi=300)
                plt.close()
            if not Path(reg_path).exists():
                X = df.iloc[:,17].values.reshape(-1, 1)
                Y = df.iloc[:,20].values.reshape(-1, 1)
                X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
                linear_regressor = LinearRegression()  # create object for the class
                linear_regressor.fit(X_train, Y_train)  # perform linear regression
                Y_pred = linear_regressor.predict(X_test)  # make predictions
                plt.scatter(X, Y, label="Acutuall average Response Time")
                plt.plot(X_test, Y_pred, color='red',label="Predicted average Response Time")
                plt.ylabel("Time (milliseconds)")
                plt.xlabel("Requests Count")
                plt.legend(loc="upper right")
                plt.savefig(reg_path,dpi=300)
                plt.close()
        else:
            return 2 # not enough data
    return 0 # success

def handle(req):
    # we try the code block here to catch the error and get it displayed with the answer otherwise we get "server error 500" with no information about the error, could be removed after debugging phase
    try:
        data = json.loads(req)
        command = data.get("command") or None
        if command is None:
            return  jsonify(success=False,exit_code=1,message="bad request"), headers

        if command == 1: # add a new project
            files = data.get('files') or None
            if files is None :
                return jsonify(success=False,exit_code=1,message="bad request"), headers 
            # create an id for the project
            project_name = files[0]['name'].split('/')[:-1][0]
            project_path = f'{projects_dir}/{project_name}'
            # check if project folder exists
            if Path(project_path).exists():
                return jsonify(success=False,exit_code=2,message="project exists"), headers
            # save project files 
            for uploaded_file in files:
                uploaded_file_name = uploaded_file['name']
                uploaded_file_dir = '/'.join(uploaded_file_name.split('/')[:-1])
                pathlib.Path(f'{projects_dir}/{uploaded_file_dir}').mkdir(parents=True, exist_ok=True) 
                content = str(uploaded_file['content'])
                if uploaded_file_name.endswith('.py'):
                    content = '# automatically added lines to manage imports\nimport os, sys\ncurrentdir = os.path.dirname(os.path.realpath(__file__))\nparentdir = os.path.dirname(currentdir)\nsys.path.append(parentdir)\n# original content\n' + content
                with open(f'{projects_dir}/{uploaded_file_name}', 'w', encoding='UTF-8') as file:
                    file.write(content)
            # check locust scripts in locust folder
            if not Path(f'{project_path}/locust').exists():
                return jsonify(success=False,exit_code=3,message="no locust dir found"), headers

            # check if locust tests exist
            locust_tests_exist = False
            for file in os.listdir(f'{project_path}/locust'):
                if file.endswith('.py'):
                    locust_tests_exist = True
                    break
            if not locust_tests_exist:
                return jsonify(success=False,exit_code=4,message="no locust tests found"), headers

            # create a virtual env and install req
            # check if req exists
            if platform.system() == 'Windows': # windows
                #if Path(f'{project_path}/requirements.txt').exists():
                    #tasks[project_name] = subprocess.Popen(f'virtualenv {project_path}/env && .\projects\{project_name}\env\Scripts\pip.exe install -r .\projects\{project_name}\\requirements.txt', shell=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP) #stdout=subprocess.DEVNULL , 
                pass
                # cerate a venv
            else:
                req_cmd = '' 
                if Path(f'{project_path}/requirements.txt').exists():    
                    req_cmd = f'&& env/{project_name}/bin/pip3 install -r projects/{project_name}/requirements.txt'
                tasks[project_name] = subprocess.Popen(f'virtualenv env/{project_name} {req_cmd}', shell=True, stderr=subprocess.DEVNULL, preexec_fn=os.setsid) #stdout=subprocess.DEVNULL ,     

            return jsonify(success=True,exit_code=0,task_id=project_name,message="project added"), headers

        if command == 2: # check task -> sync
            task_id = data.get('task_id') or None
            if task_id is None:
                return json.dumps({'success':False,'exit_code':1,'message':'bad request'})
            if task_id in tasks:
                if tasks[task_id].poll() is not None: # process finished
                    if tasks[task_id].returncode != 0:
                        return json.dumps({'success':True,'exit_code':0,'status_code':1,'message':'installation failed'}) 
                    return json.dumps({'success':True,'exit_code':0,'status_code':0,'message':'task finished'})
                return json.dumps({'success':True,'exit_code':0,'status_code':2,'message':'task not finished'})
            return json.dumps({'success':True,'exit_code':0,'status_code':0,'message':'task not found'})

        if command == 3: # get installed projects -> sync
            projects = []
            for f in os.scandir(projects_dir):
                if f.is_dir():
                    project_name = os.path.basename(f.path)
                    if project_name in tasks:
                        if tasks[project_name].poll() is not None:
                            del tasks[project_name]
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
            if Path(project_path).exists():
                for file in os.listdir(f'{project_path}/locust'):
                    if file.endswith('.py'):
                        locust_scripts.append(file.split('.')[0])
            return jsonify(success=True,exit_code=0,locust_scripts=locust_scripts,message="locust_scripts"), headers

        if command == 5:  # start a test -> sync
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

            if workers_count > 0:
                worker_command = ''
                for i in range(0, int(workers_count)):
                    worker_log_path = f'locust/{script_name}/{id}/worker_{i+1}_log.log'
                    worker_command = worker_command + f'cd projects/{project_name} && ../../env/{project_name}/bin/locust -f locust/{script_name}.py --logfile {worker_log_path} --worker &'
                master_command = f'cd projects/{project_name} && ../../env/{project_name}/bin/locust -f locust/{script_name}.py  {host_command} --users {users} --spawn-rate {spawn_rate} --headless {time_command} --csv {results_path} --logfile {log_path} --master --expect-workers={workers_count}'    
                command = worker_command + master_command
            else:
                command = f'cd {projects_dir}/{project_name} && ../../env/{project_name}/bin/locust -f locust/{script_name}.py  {host_command} --users {users} --spawn-rate {spawn_rate} --headless {time_command} --csv {results_path} --logfile {log_path}'
            
            started_at = t.time()
            # save test info
            info_file = f'{test_dir}/info.txt'
            with open(info_file, "w", encoding="UTF-8") as file:
                file.write(json.dumps({"users": users, "spawn_rate": spawn_rate, "host": host,"workers":workers_count, "time": time, "started_at":started_at}))

            task_id = f'{project_name}_{script_name}_{id}'
            if platform.system() == 'Windows': # windows
                #self.process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                pass        
            else: # linux
                tasks[task_id] = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)#stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL

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
            task_id = f'{project_name}_{script_name}_{id}'
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

        if command == 7: # get tests -> sync
            project_name = data.get("project_name") or None
            script_name = data.get("script_name") or None
            if project_name is None or script_name is None :
                return jsonify(success=False,exit_code=1,message="bad request"), headers
            tests_folders = []
            scrpit_folder_path = f'{projects_dir}/{project_name}/locust/{script_name}'
            if Path(scrpit_folder_path).exists():
                for f in os.scandir(scrpit_folder_path):
                    if f.is_dir():
                        id = os.path.basename(f.path)
                        tests_folders.append(get_test_info(project_name, script_name, id))
            return jsonify(success=True,exit_code=0,tests=tests_folders,message="folders"), headers

        if command == 8: # stop test -> sync
            project_name = data.get("project_name") or None
            script_name = data.get("script_name") or None
            id = data.get("id") or None
            if project_name is None or script_name is None or id is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers
            task_id = f'{project_name}_{script_name}_{id}'
            #stop the task
            if task_id not in tasks:
                return jsonify(success=False,exit_code=2,message="test is not deployed"), headers
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
            task_id = f'{project_name}_{script_name}_{id}'
            #stop the task    
            if task_id in tasks:
                if platform.system() == 'Windows': # windows
                    tasks[task_id].send_signal(signal.CTRL_BREAK_EVENT)
                    tasks[task_id].kill()
                else:
                    os.killpg(os.getpgid(tasks[task_id].pid), signal.SIGTERM)
                del tasks[task_id]

            test_dir = get_test_dir(project_name, script_name, id)
            if not Path(test_dir).exists():
                return jsonify(success=False,exit_code=6,message="test does not exist"), headers
            shutil.rmtree(test_dir) # remove test_dir
            delete_zip_file(project_name, script_name,id )
            return jsonify(success=True,exit_code=0,message="deleted"), headers

        if command == 10: # delete projects -> sync
            names = data.get("names") or None
            if names is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers
            deleted = []
            for name in names:
                print(name)
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
            #create plots
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
            if type == 1: # create
                status_code = create_plots(project_name, script_name, id) # 0: success, 1 test does not exist, 2 not enough data
                return jsonify(success=True,exit_code=0,status_code=status_code), headers 
            if type == 2: # linear
                return send_from_directory(test_dir, f'lin.png'), headers
            if type == 3: # regression 
                return send_from_directory(test_dir, f'reg.png'), headers
            else:
                return jsonify(success=False,exit_code=1,message="bad request"), headers 

        if command == 911: # kill all running tasks -> sync
            kill_running_tasks()
            return jsonify(success=True,exit_code=0,message="tasks killed"), headers

        if command == 912: # clean up -> sync
            clean_up()
            return jsonify(success=True,exit_code=0,message="clean up"), headers

    except Exception as e:
        print(traceback.format_exc())
        return jsonify(success=False,exit_code=-1,message=str(e),trace_back=traceback.format_exc()), headers
