import json
from flask import jsonify
from os.path import join, dirname, realpath
import time as t
from pathlib import Path
import os
import shutil
import pandas as pd
import subprocess

headers = {'Access-Control-Allow-Origin': '*','Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type'}
tests = {}

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

        time_command = ''
        if self.time:
            time_command = f'-t {str(self.time)}s'

        test_dir = join(tests_dir, self.id)
        file_path = join(test_dir, f'{self.id}.py')
        csv_name = join(test_dir, self.id)

        self.command = f'locust -f {file_path} --host {self.host} --users {self.users} --spawn-rate {self.spawn_rate} --headless {time_command} --csv {csv_name}'
       
    def start(self):
        self.process = subprocess.call(self.command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,shell=True)

    def stop(self):
        if self.process:
            self.process.terminate()

def handle(req):
    # we try the code block here to catch the error and get it displayed with the answer otherwise we get "server error 500" with no information about the error, could be removed after debugging phase
    try:
        data = json.loads(req)
        command = data.get("command") or None
        if not command:
            return  jsonify(success=False,exit_code=1,message="bad request"), headers
        
        # to be removed
        if command == 9: # test -> sync
            id = data.get('id') or None
            test_dir = join(tests_dir, id)
            file_path = join(test_dir, f'{id}.py')
            exists = Path(file_path).exists()
            return jsonify(exists=exists)

        if command == 1: # deploy -> sync
            users = data.get("users") or None
            spawn_rate = data.get("spawn_rate") or None
            host = data.get("host") or None
            time = data.get("time") or None
            code = data.get("code") or None

            # TODO
            # handle None values
            if not users or not spawn_rate or not code:
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
            # configure test
            test = Test(id=id, users=users, spawn_rate=spawn_rate, host=host, time=time)
            # save test in tests
            tests[id] = test 
            return jsonify(success=True,exit_code=0,id=id,message="test deployed"), headers

        if command == 2: # start -> async
            id = data.get("id") or None
            if not id:
               return jsonify(success=False,exit_code=1,message="bad request"), headers 
            if id not in tests:
                return jsonify(success=True,exit_code=2,message="test is not deployed"), headers
            tests[id].start()
            # remove the test from the tests if not stopped via request
            if id in tests:
                del tests[id]
            return jsonify(success=True,exit_code=0,message="test started and finished successfully"), headers

        if command == 3: # stop -> sync
            id = data.get("id") or None
            if not id:
               return jsonify(success=False,exit_code=1,message="bad request"), headers 
            if id not in tests:
                return jsonify(success=False,exit_code=2,message="test is not deployed"), headers
            tests[id].stop()
            del tests[id]
            return jsonify(success=True,exit_code=0,message="test is stopped"), headers

        if command == 4: # stats -> sync
            id = data.get("id") or None
            if not id:
               return jsonify(success=False,exit_code=1,message="bad request"), headers 
            test_dir = join(tests_dir, id)
            csv_file_path = join(test_dir, f'{id}_stats.csv')
            if not Path(csv_file_path).exists():
                return jsonify(success=False,exit_code=3,message="csv file does not exist",path=csv_file_path), headers
            pd_data = pd.read_csv(csv_file_path) 
            j = pd_data.to_json(orient='records')
            # check if test is runnig
            if id in tests:
                return jsonify(success=True,exit_code=0,status=1,data=j,message="test running"), headers # status 1 -> test is running
            return jsonify(success=True,exit_code=0,status=0,data=j,message="test is not running"), headers # status 0 -> test not running

        if command == 5: # download -> sync
            # TODO
            # create plots
            # zip files
            return jsonify(success=True,exit_code=0,message="download"), headers
        if command == 6: # get tests -> sync
            tests_folders = [ os.path.basename(f.path) for f in os.scandir(tests_dir) if f.is_dir() ]   
            return jsonify(success=True,exit_code=0,tests=tests_folders,message="folders")

        if command == 7: # delete a test folder -> sync
            ids = data.get("ids") or None
            if not ids:
               return jsonify(success=False,exit_code=1,message="bad request"), headers
            deleted = []
            for id in ids:
                test_dir = join(tests_dir, id)
                if Path(test_dir).exists():
                    shutil.rmtree(test_dir)
                    deleted.append(id)
            return jsonify(success=True,exit_code=0,deleted=deleted), headers

        else:
            return jsonify(success=False,exit_code=1,message="bad request"), headers
    except Exception as e:
        return jsonify(success=False,exit_code=1,message=str(e)), headers
