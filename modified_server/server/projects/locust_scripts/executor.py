#!/usr/bin/env python
import csv
import logging
import os

import typer

from common.Common import call_locust_with

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


def main(
        locust_script: str = typer.Argument(
            ...,
            help="Path to the locust script to execute"
        ),
        url: str = typer.Option(
            "http://localhost:1337",
            "--url", "-u",
            help="URL of the System under Test"
        ),
        num_clients: int = typer.Option(
            1,
            "--num_clients", "-n",
            help="How many users should be simulated"
        ),
        runtime: int = typer.Option(
            -1,
            "--runtime", "-t",
            help="How many minutes the test should run."
        ),
        silent: bool = typer.Option(
            False,
            "--silent", "-s",
            help="Omit .csv and log files"
        )
):
    if silent is False:
        fh = logging.FileHandler('executor.log')
        fh.setLevel(logging.DEBUG)

        logging.basicConfig(format="%(asctime)s %(message)s",
                            level=os.environ.get("LOGLEVEL", "INFO"),
                            handlers=[fh])

    call_locust_with(locust_script, url, num_clients, runtime, silent)

    if silent is False:
        read_measurements_from_locust_csv_and_append_to_dictonaries(f"loadtest_{num_clients}_clients_stats.csv", 1)


if __name__ == "__main__":
    typer.run(main)
