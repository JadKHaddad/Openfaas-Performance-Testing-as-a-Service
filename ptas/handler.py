import json
from flask import jsonify, send_from_directory
from os.path import join, dirname, realpath
import time as t
from pathlib import Path
import os
import shutil
import pandas as pd
import subprocess

headers = {'Access-Control-Allow-Origin': '*','Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type'}
tests = {}
not_valid_tests = {}

tests_dir = join(dirname(realpath(__file__)), 'tests')
if not Path(tests_dir).exists():
    os.mkdir(tests_dir)

class Test():
    def __init__(self, id:str, users:int, spawn_rate:int, host:str, time:int):
        self.id = id
        self.users = users
        self.spawn_rate = spawn_rate
        self.host = host
        self.time = time
        self.process = None
        self.started_at = 0
        time_command = ''
        if self.time is not None:
            time_command = f'-t {str(self.time)}s'
        
        host_command = ''
        if self.host is not None:
            host_command = f'--host {self.host}'

        test_dir = join(tests_dir, self.id)
        file_path = join(test_dir, f'{self.id}.py')
        csv_name = join(test_dir, self.id)
        requirements_path = join(test_dir, f'requirements.txt')

        self.command = f'pip install -r {requirements_path} && locust -f {file_path} {host_command} --users {self.users} --spawn-rate {self.spawn_rate} --headless {time_command} --csv {csv_name}'
       
    def start(self):
        self.started_at = t.time()
        self.process = subprocess.Popen(self.command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,shell=True)

    def stop(self):
        if self.process is not None:
            self.process.terminate()

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

    if id in not_valid_tests:
        valid = False

    if id in tests:
        if tests[id].process is not None and tests[id].process.poll() is None: # process not finished
            data = {"id":id, "status":1, "started_at": tests[id].started_at, "data":j, "info":info, "code":code, "valid":valid} # status 1 -> test is running 
        else:
            data = {"id":id, "status":2, "data":j,"info":info, "code":code, "valid":valid}# status 2 -> test is deployed
    else:
        data = {"id":id, "status":0, "data":j, "info":info, "code":code, "valid":valid} # status 0 -> test is no longer deployed
    return data 

def clean_up_cache(id):
    test_dir = join(tests_dir, id)
    cache = join(test_dir, f'__pycache__')
    if Path(cache).exists():
        shutil.rmtree(cache)

def zip_files(id):
    clean_up_cache(id)
    test_dir = join(tests_dir, id)
    if not Path(test_dir).exists():
        return False
    if not Path(join(tests_dir, f'{id}.zip')).exists(): #create zip file if it does not exist
        shutil.make_archive(test_dir, 'zip', test_dir)
    return True

def delete_zip_file(id):
    zip_file = join(tests_dir, f'{id}.zip')
    if Path(zip_file).exists():
        os.remove(zip_file)

def handle(req):
    # we try the code block here to catch the error and get it displayed with the answer otherwise we get "server error 500" with no information about the error, could be removed after debugging phase
    try:
        # clean up
        for id in tests:
            if tests[id].process is not None:
                if tests[id].process.poll() is not None: # process finished
                    test_dir = join(tests_dir, id)
                    csv_file_path = join(test_dir, f'{id}_stats.csv')
                    if not Path(csv_file_path).exists(): # test is not valid
                        not_valid_tests[id] = None
                    del tests[id]

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
                os.mkdir(test_dir)
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
            test = Test(id=id, users=users, spawn_rate=spawn_rate, host=host, time=time)
            # save test in tests
            tests[id] = test 
            return jsonify(success=True,exit_code=0,id=id,message="test deployed"), headers

        if command == 2: # start -> async
            id = data.get("id") or None
            if id is None:
               return jsonify(success=False,exit_code=1,message="bad request"), headers
            running_tets = 0
            for id in tests:
                if tests[id].process is not None and tests[id].process.poll() is None: # process is running
                    running_tets = running_tets + 1
            if running_tets > 3: 
                return jsonify(success=False,exit_code=5,message="too many tests"), headers
            if id not in tests:
                return jsonify(success=False,exit_code=2,message="test is not deployed"), headers
            tests[id].start()
            #debugging
            poll = 'undefined'
            if tests[id].process is not None:
                poll = tests[id].process.poll()
            #end of debugging
            return jsonify(success=True,exit_code=0,message="test started successfully", poll=poll), headers

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
            if id in not_valid_tests:
                return jsonify(success=False,exit_code=4,message="test is not valid"), headers 
            test_dir = join(tests_dir, id)
            csv_file_path = join(test_dir, f'{id}_stats.csv')
            if not Path(csv_file_path).exists():
                return jsonify(success=False,exit_code=3,message="csv file does not exist"), headers
            pd_data = pd.read_csv(csv_file_path) 
            j = pd_data.to_json(orient='records')
            # check if test is runnig
            if id in tests:
                if tests[id].process is not None and tests[id].process.poll() is None: # process not finished
                    return jsonify(success=True,exit_code=0,status=1,data=j,message="test running"), headers # status 1 -> test is running
                else:
                    return jsonify(success=True,exit_code=0,status=2,data=j,message="test is deployed"), headers # status 1 -> test is deployed
            return jsonify(success=True,exit_code=0,status=0,data=j,message="test is no longer deployed"), headers # status 0 -> test not running
        if command == 5: # download -> sync
            id = data.get("id") or None
            if id is None:
               return jsonify(success=False,exit_code=1,message="bad request"), headers 
            # TODO
            # create plots

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
                    if id in not_valid_tests:
                        del not_valid_tests[id]
                    deleted.append(id)
            return jsonify(success=True,exit_code=0,deleted=deleted), headers

        if command == 8: # get test
            id = data.get("id") or None
            if id is None:
               return jsonify(success=False,exit_code=1,message="bad request"), headers 
            data = get_test_info(id)
            return jsonify(success=True,exit_code=0,data=data,message="test info"), headers
        
        else:
            return jsonify(success=False,exit_code=1,message="bad request"), headers

    except Exception as e:
        return jsonify(success=False,exit_code=-1,message=str(e)), headers
