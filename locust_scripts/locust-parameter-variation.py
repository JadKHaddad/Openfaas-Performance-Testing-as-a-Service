#!/usr/bin/env python
import argparse
import csv
import glob

import platform
import os
import logging
import time

from common.Common import call_locust_with, call_locust_and_distribute_work

input_args = argparse.Namespace()

plt = platform.system()

if plt != "Windows":
    import readline


def complete_python(text, state):
    # replace ~ with the user's home dir. See https://docs.python.org/2/library/os.path.html
    if '~' in text:
        text = os.path.expanduser('~')

    # autocomplete directories with having a trailing slash
    if os.path.isdir(text):
        text += '/'

    return [x for x in glob.glob(text + '*.py')][state]


if plt != "Windows":
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete_python)

locust_script = input('Path to the Locust script: ')

if plt != "Windows":
    readline.set_completer(None)

# url = input('URL of the software to test: ')

url = "http://localhost:1337"

fh = logging.FileHandler('locust-parameter-variation.log')
fh.setLevel(logging.DEBUG)

logging.basicConfig(format="%(asctime)s %(message)s",
                    level=os.environ.get("LOGLEVEL", "INFO"),
                    handlers=[fh])

avg_time_allowed_in_s = 10
max_time_allowed_in_s = 30
average_response_time = {}
min_response_time = {}
max_response_time = {}


def read_measurements_from_locust_csv_and_append_to_dictonaries(path, num_clients):
    logger = logging.getLogger('readMeasurementsFromCsvAndAppendToDictonaries')

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        avg = 0
        min = 0
        max = 0
        for row in reader:
            v = float(row['Average Response Time'])
            avg = v if avg < v else avg

            v = float(row['Min Response Time'])
            min = v if min < v else min

            v = float(row['Max Response Time'])
            max = v if max < v else max

        logger.info("Avg: {}, Min: {}, Max: {}".format(avg, min, max))
        average_response_time[num_clients] = float(avg)
        min_response_time[num_clients] = float(min)
        max_response_time[num_clients] = float(max)


def config_complies_with_real_time_requirements(num_clients):
    logger = logging.getLogger('config_complies_with_real_time_requirements')

    # return True, because we have no measurements yet
    if len(average_response_time) == 0 or len(max_response_time) == 0:
        return True

    if average_response_time[num_clients] == 0 or max_response_time[num_clients] == 0:
        logger.error("Something went wrong: average or max response time was 0")
        return False

    average_response_time_s = average_response_time[num_clients] / 1000
    max_response_time_s = max_response_time[num_clients] / 1000

    logger.info(f"Clients: {num_clients}: avg: {average_response_time_s}s, max: {max_response_time_s}s")

    exceeds_average_response_time = average_response_time_s > avg_time_allowed_in_s
    exceeds_max_response_time = max_response_time_s > max_time_allowed_in_s

    is_compliant = not (exceeds_average_response_time or exceeds_max_response_time)

    logger.info(f"--> {is_compliant}")

    return is_compliant


def parameter_variation_loop():
    logger = logging.getLogger('parameter_variation_loop')

    num_clients = 1
    multiplier = 5000
    x = 1

    logger.info(f"Starting performance test.")

    is_first_run = True
    while config_complies_with_real_time_requirements(num_clients):
        if not is_first_run:
            logger.info("Sleeping for 1 min ...")
            time.sleep(60)
        is_first_run = False

        # start with one client, then increase linearly (multiplier, 2*multiplier, ... x*multiplier)
        num_clients = max(x * multiplier, 1)
        x += 1

        call_locust_and_distribute_work(locust_script, url, num_clients, runtime_in_min=10)
        # call_locust_with(locust_script, url, num_clients, runtime_in_min=10, omit_csv_files=True)

        read_measurements_from_locust_csv_and_append_to_dictonaries(f"loadtest_{num_clients}_clients_stats.csv", num_clients)

    logger.info(f"Finished performance test. System failed at {num_clients}")


def read_cli_args():
    parser = argparse.ArgumentParser(description='Locust Wrapper.')
    parser.add_argument('-p', '--parametervariation', action='store_true', help='run the test and variate parameters.')

    global input_args

    input_args = parser.parse_args()
    print("Args: " + str(input_args))


if __name__ == "__main__":
    read_cli_args()

    if input_args.parametervariation:
        parameter_variation_loop()
    else:
        call_locust_with(locust_script, url, clients=1)

        read_measurements_from_locust_csv_and_append_to_dictonaries("loadtest_1_clients_stats.csv", 1)
