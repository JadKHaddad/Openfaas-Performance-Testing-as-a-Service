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
import traceback

headers = {'Access-Control-Allow-Origin': '*','Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type'}
tests = {}

tests_dir = join(dirname(realpath(__file__)), 'tests')
if not Path(tests_dir).exists():
    os.mkdir(tests_dir)

class Test():
    def __init__(self, id:str, users:int, spawn_rate:int, host:str, time:int, req:bool):
        time_command = f'-t {str(time)}s' if time is not None else ''
        host_command = f'--host {host}' if host is not None else ''
        test_dir = join(tests_dir, id)
        file_path = join(test_dir, f'{id}.py')
        results_name = join(test_dir, id)
        requirements_path = join(test_dir, f'requirements.txt')
        requirements_command = f'pip install -r {requirements_path} &&' if req else ''
        command = f'{requirements_command} locust -f {file_path} {host_command} --users {users} --spawn-rate {spawn_rate} --headless {time_command} --csv {results_name} --html {results_name}.html'
        self.started_at = t.time()
        self.process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, preexec_fn=os.setsid)

    def stop(self):
        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            
# static functions
def get_test_info(id):
    test_dir = join(tests_dir, id)
    csv_file_path = join(test_dir, f'{id}_stats.csv')
    info_file_path = join(test_dir, f'{id}_info.txt')
    code_file_path = join(test_dir, f'{id}.py')
    valid = True

    if Path(csv_file_path).exists():
        pd_data = pd.read_csv(csv_file_path) 
        j = pd_data.to_json(orient='records')
    else:
        j = None
    if Path(info_file_path).exists():
        with open(info_file_path, 'r') as file:
            info = file.read()
    else:
        info = None
    if Path(code_file_path).exists():
        with open(code_file_path, 'r') as file:
            code = file.read()
    else:
        code = None
    if not Path(csv_file_path).exists(): # test is not valid
        valid = False
    if id in tests:
        data = {"id":id, "status":1, "started_at": tests[id].started_at, "data":j, "info":info, "code":code, "valid":valid} # status 1 -> test is running 
    else:
        data = {"id":id, "status":0, "data":j, "info":info, "code":code, "valid":valid} # status 0 -> test is not running
    return data 

def clean_up_cache(id):
    test_dir = join(tests_dir, id)
    cache = join(test_dir, f'__pycache__')
    if Path(cache).exists():
        shutil.rmtree(cache)

def zip_files(id): # creates zip file if zip file does not exist, returns True if zip file is created or is already there
    clean_up_cache(id)
    test_dir = join(tests_dir, id)
    if not Path(test_dir).exists():
        return False
    if not Path(join(tests_dir, f'{id}.zip')).exists(): # creates zip file if it does not exist
        shutil.make_archive(test_dir, 'zip', test_dir)
    return True

def delete_zip_file(id):
    zip_file = join(tests_dir, f'{id}.zip')
    if Path(zip_file).exists():
        os.remove(zip_file)

def create_plots(id): # creates plots if plots do no exist, returns True if plots are created or are already there
    test_dir = join(tests_dir, id)
    stats_history_file = join(test_dir, f'{id}_stats_history.csv')
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
        
        if command == 1: # deploy -> sync
            users = data.get("users") or None
            spawn_rate = data.get("spawn_rate") or None
            host = data.get("host") or None
            time = data.get("time") or None
            code = data.get("code") or None
            requirements = data.get("requirements") or None
            if users is None or spawn_rate is None or code is None:
                return jsonify(success=False,exit_code=1,message="bad request"), headers 
            # create test id
            id = str(t.time()).replace('.', '_')
            # save test in tests dir        
            test_dir = join(tests_dir, id)
            if not Path(test_dir).exists():
                os.makedirs(test_dir)
            file_path = join(test_dir, f'{id}.py')
            with open(file_path, "w", encoding="UTF-8") as file:
                file.write(code)
            # save requirements
            requirements_file_path = join(test_dir, f'requirements.txt')
            with open(requirements_file_path, "w", encoding="UTF-8") as file:
                if requirements is not None:
                    file.write(requirements)
            info_file_path = join(test_dir, f'{id}_info.txt')
            with open(info_file_path, "w", encoding="UTF-8") as file:
                file.write(json.dumps({"users": users, "spawn_rate": spawn_rate, "host": host, "time": time, "date":t.time()}))
            # configure test
            test = Test(id=id, users=users, spawn_rate=spawn_rate, host=host, time=time, req=(requirements is not None))
            # save test in tests
            tests[id] = test
            return jsonify(success=True,exit_code=0,id=id,started_at=test.started_at,message="test deployed and started"), headers

        if command == 2: # get plots -> sync
            id = data.get("id") or None
            type = data.get("type") or None
            if id is None:
               return jsonify(success=False,exit_code=1,message="bad request"), headers 
            test_dir = join(tests_dir, id)
            if type == 1: # create
                status_code = create_plots(id) # 0: success, 1 test does not exist, 2 not enough data
                return jsonify(success=True,exit_code=0,status_code=status_code), headers 
            if type == 2: # linear
                return send_from_directory(test_dir, f'lin.png'), headers
            if type == 3: # regression 
                return send_from_directory(test_dir, f'reg.png'), headers
            else:
                return jsonify(success=False,exit_code=1,message="bad request"), headers 

        if command == 3: # stop -> sync
            id = data.get("id") or None
            if id is None:
               return jsonify(success=False,exit_code=1,message="bad request"), headers 
            if id not in tests:
                return jsonify(success=False,exit_code=2,message="test is not deployed"), headers
            tests[id].stop()
            del tests[id]
            return jsonify(success=True,exit_code=0,message="test is stopped"), headers

        if command == 4: # stats -> sync
            id = data.get("id") or None
            if id is None:
               return jsonify(success=False,exit_code=1,message="bad request"), headers
            # check if test is runnig
            if id in tests:
                test_dir = join(tests_dir, id)
                csv_file_path = join(test_dir, f'{id}_stats.csv')
                if tests[id].process.poll() is not None: # process finished
                    if not Path(csv_file_path).exists(): # test is not valid
                        del tests[id]
                        return jsonify(success=False,exit_code=4,message="test is not valid"), headers 
                    del tests[id]
                if not Path(csv_file_path).exists():
                    return jsonify(success=False,exit_code=3,message="csv file does not exist"), headers
                pd_data = pd.read_csv(csv_file_path) 
                j = pd_data.to_json(orient='records') 
                return jsonify(success=True,exit_code=0,status=1,data=j,message="test running"), headers # status 1 -> test is running
            return jsonify(success=True,exit_code=0,status=0,data=None,message="test is not runnig"), headers # status 0 -> test not running
            
        if command == 5: # download -> sync
            id = data.get("id") or None
            if id is None:
               return jsonify(success=False,exit_code=1,message="bad request"), headers 
            #create plots
            create_plots(id)
            # zip files
            if zip_files(id):
                return send_from_directory(tests_dir, f'{id}.zip'), headers
            else:
                return jsonify(success=False,exit_code=6,message="test does not exist"), headers 

        if command == 6: # get tests -> sync
            tests_folders = []
            for f in os.scandir(tests_dir):
                if f.is_dir():
                    id = os.path.basename(f.path)
                    tests_folders.append(get_test_info(id))
            return jsonify(success=True,exit_code=0,tests=tests_folders,message="folders"), headers

        if command == 7: # delete tests folders -> sync
            ids = data.get("ids") or None
            if ids is None:
               return jsonify(success=False,exit_code=1,message="bad request"), headers
            deleted = []
            for id in ids:
                test_dir = join(tests_dir, id)
                if Path(test_dir).exists():
                    shutil.rmtree(test_dir) # remove test_dir
                    delete_zip_file(id) # delete zip file
                    if id in tests: # stop the test if running 
                        tests[id].stop()
                        del tests[id]
                    deleted.append(id)
            return jsonify(success=True,exit_code=0,deleted=deleted), headers

        if command == 8: # get test -> sync
            id = data.get("id") or None
            if id is None:
               return jsonify(success=False,exit_code=1,message="bad request"), headers 
            data = get_test_info(id)
            return jsonify(success=True,exit_code=0,data=data,message="test info"), headers

        if command == 10: # clean up -> sync
            for id in tests: # clear deployed tests
                tests[id].stop()
                del tests[id]
            list_dir = os.listdir(tests_dir) # clean up tests folder
            for filename in list_dir:
                file_path = os.path.join(tests_dir, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            return jsonify(success=True,exit_code=0,data=data,message="all clean"), headers
        else:
            return jsonify(success=False,exit_code=1,message="bad request"), headers

    except Exception as e:
        return jsonify(success=False,exit_code=-1,message=str(e),trace_back=traceback.format_exc()), headers