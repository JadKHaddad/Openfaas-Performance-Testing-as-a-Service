#!/usr/bin/env python
# Simulates an ARS with workloads measured in a productive environment.
# Set the constant MASCOTS2020 to True, in order to produce similar results as in our paper.
# HTTPServer based on https://gist.github.com/huyng/814831 Written by Nathan Hamiel (2010)
import asyncio
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
from random import random, seed
from uuid import uuid1

import sys
import uvicorn
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime, timedelta

from joblib import load

from stopwatch import Stopwatch

from dataclasses import dataclass

import logging

MASCOTS2020 = False

fh = logging.FileHandler('ARS_simulation_{:%Y-%m-%d}.log'.format(datetime.now()))
fh.setLevel(logging.WARN)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.WARN)

logging.basicConfig(format="[%(thread)d] %(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
                    level=os.environ.get("LOGLEVEL", "DEBUG"),
                    handlers=[fh, sh],
                    datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger('Audit')

scheduler = BackgroundScheduler(misfire_grace_time=100)
time_of_last_fault = datetime.now()
time_of_recovery = datetime.now()
chosen_fault_time: float = 0
_is_faulted = False


def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


@dataclass
class PredictiveModel:
    operator_reaction_time_s: float
    ars_recovery_time_s: float
    fault_detection_time_range_s: tuple
    this_ARS_number_in_the_server_list: int

    min_processing_time_s: float
    max_processing_time_s: float


# -- Fault Management Model --
# (26, 34) are the minimum and maximum times,
# the fault detection mechanism needs to detect a fault,
# based on the real-world fault detection mechanism.
# For every ARS running in the system, we have additional 2 seconds,
# so we include the position of the ARS in the "check list", to account for that.
#
# In addition to that, we have operator time---the time an operator needs to begin his work---
# and recovery time---the time the recovery action requires, e.g., how much time it takes to restart the ARS.
# --


# 2 sec min time measured with Locust in the staging environment,
# 10 sec max time is just for demonstration purposes
model_staging = PredictiveModel(1, 0.5, (26, 34), 2, 2, 10)

# -- min and max processing times of production environment measured from 16561 requests --
# this very high time actually happens at night, when other processes,
# like the database backups database are executed.
model_production = PredictiveModel(1, 0.5, (26, 34), 2, 6, 2799)
current_model = model_staging


def between(min, max):
    return min + random() * (max - min)


def notify_operator():
    logger.debug("operator reaction time: %f", current_model.operator_reaction_time_s)

    # Simulate the time it takes until an operator reacts to the notification
    # we call this operator reaction time
    due_date = datetime.now() + timedelta(0, current_model.operator_reaction_time_s)
    scheduler.add_job(recover, 'date', run_date=due_date)


def recover():
    # Simulate the time an operator needs to perform a recovery action
    # we call this recovery action time
    sleep(current_model.ars_recovery_time_s)

    global _is_faulted
    _is_faulted = False

    global time_of_recovery
    time_of_recovery = datetime.now()

    logger.info("ARS recovered @%s", time_of_recovery)


def is_faulted():
    return _is_faulted


def inject_a_fault_every_s_seconds(s):
    scheduler.add_job(simulate_fault, 'interval', seconds=s)


def inject_three_faults_in_a_row():
    due_date1 = datetime.now() + timedelta(0, minutes=5)
    due_date2 = due_date1 + timedelta(0, 60)
    due_date3 = due_date2 + timedelta(0, 60)

    scheduler.add_job(simulate_fault, 'date', run_date=due_date1)
    scheduler.add_job(simulate_fault, 'date', run_date=due_date2)
    scheduler.add_job(simulate_fault, 'date', run_date=due_date3)
    scheduler.add_job(inject_three_faults_in_a_row, 'date', run_date=due_date3)


def simulate_fault():
    """
    simulate a fault:

    * this method causes the function `is_faulted` to return true for `chosen_fault_time` seconds.
    * `chosen_fault_time` is set using the fault_detection_time_range_s of the current_model.
    """

    if is_faulted():
        return

    global chosen_fault_time

    # fault detection time:
    # indicates how long the fault detection mechanism requires to detect a fault
    chosen_fault_time = between(current_model.fault_detection_time_range_s[0],
                                current_model.fault_detection_time_range_s[1])

    logger.debug("chosen_fault_time: %f", chosen_fault_time)

    # + delay until check
    # the fault detection mechanism needs more time depending on the
    # position of the ARS in the "checklist".
    chosen_fault_time += 2 * (current_model.this_ARS_number_in_the_server_list - 1)

    logger.debug("# + delay until check: %f", chosen_fault_time)

    global time_of_last_fault
    time_of_last_fault = datetime.now()

    logger.info("ARS faulted @%s; operator will be notified in %ss",
                time_of_last_fault,
                chosen_fault_time)

    global _is_faulted
    _is_faulted = True

    due_date = datetime.now() + timedelta(0, chosen_fault_time)
    scheduler.add_job(notify_operator, 'date', run_date=due_date)


@synchronized
def simulate_minimal_workload():
    """
    Using this function we simulate an M/M/1 queuing system
    because only one thread executes the function and the others
    wait in a queue implicitly implemented by the synchronized annotation.
    """
    wait_time = current_model.min_processing_time_s

    logger.debug("Waiting for {}".format(wait_time))

    sleep(wait_time)

    return True


functionsLocks = {}


def simulate_workload_random(function: str):
    """
    Simulate workload based on real processing times
    randomly distributed between min and max processing time.

    Using this we have an M/M/c queuing system where c is the number
    of different requests the ARS can execute.
    That means that the same requests cannot be executed in parallel
    but different requests are executed in parallel.
    """

    if function not in functionsLocks:
        functionsLocks[function] = threading.Lock()

    lock = functionsLocks[function]

    with lock:
        # min_processing_time = current_model.min_processing_time_s
        min_processing_time = 0.2  # for demonstration purposes

        # max_processing_time = current_model.max_processing_time_s
        max_processing_time = current_model.min_processing_time_s  # for demonstration purposes
        # --

        # for simplicity we just take a random distribution
        # that is not representative for the production system's behavior
        random_processing_time = between(min_processing_time, max_processing_time)

        logger.debug("Waiting for {}".format(random_processing_time))

        sleep(random_processing_time)

        return True


pr_lock = threading.Lock()
number_of_parallel_requests_pending = 0
startedCommands = {}

predictive_model = load("Models/gs_model_prod_workload.joblib")
known_request_types = load("Models/gs_requests_mapping_prod_workload.joblib")


async def simulate_workload_using_predictive_model(function: str, use_await=False):
    """
    This function sleeps for the amount of time predicted
    by a predictive model.
    """

    global number_of_parallel_requests_pending

    with pr_lock:
        number_of_parallel_requests_at_beginning = number_of_parallel_requests_pending
        number_of_parallel_requests_pending = number_of_parallel_requests_pending + 1

    if use_await:
        tid = uuid1().int
    else:
        tid = threading.get_ident()

    startedCommands[tid] = {
        "cmd": function,
        "parallelCommandsStart": number_of_parallel_requests_at_beginning,
        "parallelCommandsFinished": 0
    }

    logger.debug(startedCommands)

    sleep_time_to_use = predict_sleep_time(predictive_model, tid, function)
    logger.debug(f"{function}: Waiting for {sleep_time_to_use}")
    if use_await:
        await asyncio.sleep(sleep_time_to_use)
    else:
        sleep(sleep_time_to_use)

    sleep_time_last_time = sleep_time_to_use
    while True:
        sleep_time_test = predict_sleep_time(predictive_model, tid, function)
        if sleep_time_test <= sleep_time_last_time:
            break
        else:
            sleep_time_to_use = sleep_time_test - sleep_time_last_time

        sleep_time_last_time = sleep_time_test
        logger.debug(f"{function}: Waiting for {sleep_time_to_use}")
        if use_await:
            await asyncio.sleep(sleep_time_to_use)
        else:
            sleep(sleep_time_to_use)

    with pr_lock:
        number_of_parallel_requests_pending -= 1

    startedCommands.pop(tid)

    with pr_lock:
        for cmd in startedCommands.values():
            cmd["parallelCommandsFinished"] = cmd["parallelCommandsFinished"] + 1

    logger.debug(startedCommands)

    return True


def predict_sleep_time(model, tid, command):
    from numpy import array

    now = datetime.now()

    time = now.timetz()
    milliseconds = time.microsecond / 1000000
    time_of_day_in_seconds = milliseconds + time.second + time.minute * 60 + time.hour * 3600

    weekday = now.weekday()

    request_type_as_int = known_request_types[command]

    # X = array([time_of_day_in_seconds,
    #            weekday,
    #            startedCommands[tid]["parallelCommandsStart"],
    #            startedCommands[tid]["parallelCommandsFinished"],
    #            request_type_as_int,
    #            1]) \
    #     .reshape(1, -1)

    X = array([startedCommands[tid]["parallelCommandsStart"],
               startedCommands[tid]["parallelCommandsFinished"],
               request_type_as_int]) \
        .reshape(1, -1)

    # print(f"X: {X}")
    y = model.predict(X)
    # print(f"y: {y}")

    y_value = y[0]
    y_value = max(0, y_value)

    return y_value


class RequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def do_GET(self):

        request_path = self.path

        print("\n----- Request Start ----->\n")
        print("Request path:", request_path)
        print("Request headers:", self.headers)
        print("<----- Request End -----\n")

        self.send_response(200)
        self.send_header("Set-Cookie", "foo=bar")
        self.end_headers()

    def do_POST(self):

        request_path = self.path

        logger.info("----- Request Start ----->")

        cmd_name = request_path.replace("/", "")

        logger.info("CMD-START: %s", cmd_name)

        request_headers = self.headers
        content_length = request_headers.get('Content-Length')
        length = int(content_length) if content_length else 0

        logger.debug("Content Length: %s", length)
        # logger.debug("Request headers: %s", request_headers)
        # logger.debug("Request payload: %s", self.rfile.read(length))

        if is_faulted():
            # logger.warning("System faulted for {} s".format(chosen_fault_time))
            is_successful = False
        else:
            stopwatch = Stopwatch()

            if MASCOTS2020:
                is_successful = simulate_minimal_workload()
            else:
                # is_successful = simulate_workload_random(cmd_name)
                is_successful = simulate_workload_using_predictive_model(cmd_name)
            stopwatch.stop()
            logger.info("Request execution time: %s", stopwatch)

        logger.info("CMD-ENDE: %s", cmd_name)
        logger.info("<----- Request End -----")

        self.send_response(200 if is_successful else 500)
        self.end_headers()

    do_PUT = do_POST
    do_DELETE = do_GET


def main():
    scheduler.start()

    # inject_a_fault_every_s_seconds(60)
    if MASCOTS2020:
        inject_three_faults_in_a_row()

    port = 1337
    logger.info('Listening on localhost:%s' % port)
    # server = HTTPServer(('', port), RequestHandler)
    server = ThreadingHTTPServer(('', port), RequestHandler)
    server.serve_forever()


async def app(scope, receive, send):
    assert scope['type'] == 'http'

    request_path = scope['path']

    logger.info("----- Request Start ----->")

    cmd_name = request_path.replace("/", "")

    logger.info("CMD-START: %s", cmd_name)

    stopwatch = Stopwatch()

    is_successful = await simulate_workload_using_predictive_model(cmd_name, use_await=True)
    stopwatch.stop()
    logger.info("Request execution time: %s", stopwatch)

    logger.info("CMD-ENDE: %s", cmd_name)
    logger.info("<----- Request End -----")

    await send({
        'type': 'http.response.start',
        'status': 200 if is_successful else 500,
        'headers': [
            [b'content-type', b'text/plain'],
        ]
    })

    await send({
        'type': 'http.response.body'
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Simulate an Alarm Receiving Software (ARS) based on the behavior of a real-world ARS.'
    )
    parser.add_argument('--prod', dest='workload_model', action='store_const',
                        const="production", default="staging",
                        help='simulate production workload (default: simulate staging workload)')

    args = parser.parse_args()

    current_model = model_production if args.workload_model == "production" else model_staging

    logger.info("Workload to simulate: %s", args.workload_model)

    # initialize the random seed value to get reproducible random sequences
    seed(42)

    # use one worker for now, because the program is not using shared memory
    uvicorn.run("ARS_simulation:app", host="127.0.0.1", port=1337, log_level="warning", workers=1)

    # main()
