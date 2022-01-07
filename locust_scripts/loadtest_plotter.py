import csv
import glob
import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import readline

from common.Common import readResponseTimesFromLogFile

num_clients = []
avg_time_allowed = []
max_time_allowed = []
average_response_time = []
min_response_time = []
max_response_time = []


def readMeasurementsFromCsvAndAppendToList(path):
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        print(row['Average response time'], row['Min response time'], row['Max response time'])
        average_response_time.append(float(row['Average response time']) / 1000)
        min_response_time.append(float(row['Min response time']) / 1000)
        max_response_time.append(float(row['Max response time']) / 1000)


def readMeasurementsFromLogFileAndAppendToList(path):
    with open(path) as logfile:
        for line in logfile:
            if 'Clients' not in line:
                continue

            lineAfterClients = line.split('Clients')[1]

            cleanedLine = lineAfterClients.replace('s', '')
            cleanedLine = cleanedLine.replace(',', '')
            cleanedLine = cleanedLine.replace('avg', '')
            cleanedLine = cleanedLine.replace('max', '')

            splittedLine = cleanedLine.split(':')

            clients = float(splittedLine[1])
            avg = float(splittedLine[3])
            max = float(splittedLine[4])

            num_clients.append(clients)
            average_response_time.append(avg)
            max_response_time.append(max)

            avg_time_allowed.append(10)
            max_time_allowed.append(30)

            print(clients, avg, max)


def plot_response_times(response_times, logfile):
    dates = list(response_times.keys())
    times = list(response_times.values())

    plt.plot(dates, times, 'o', color='black', label='Response time')

    stops1 = [
        datetime(2020, 5, 5, 9, 25, 26),
        datetime(2020, 5, 5, 9, 26, 26),
        datetime(2020, 5, 5, 9, 27, 37)
    ]

    starts1 = [
        datetime(2020, 5, 5, 9, 25, 59),
        datetime(2020, 5, 5, 9, 27, 1),
        datetime(2020, 5, 5, 9, 28, 16)
    ]

    stops2 = [
        datetime(2020, 5, 5, 11, 26, 28),
        datetime(2020, 5, 5, 11, 28, 2)
    ]

    starts2 = [
        datetime(2020, 5, 5, 11, 27, 6),
        datetime(2020, 5, 5, 11, 28, 36)
    ]

    stops3 = [
        datetime(2020, 5, 5, 12, 20, 23),
        datetime(2020, 5, 5, 12, 21, 36),
        datetime(2020, 5, 5, 12, 22, 42)
    ]

    starts3 = [
        datetime(2020, 5, 5, 12, 21, 3),
        datetime(2020, 5, 5, 12, 22, 9),
        datetime(2020, 5, 5, 12, 23, 14)
    ]

    allStops = stops1 + stops2 + stops3
    allStarts = starts1 + starts2 + starts3

    print("-- Stop-Start --")
    for i in range(len(allStops)):
        diff = abs(allStops[i] - allStarts[i])
        print("{} - {} = {}".format(allStops[i].time(), allStarts[i].time(), diff.total_seconds()))
    print("--")

    # if '_1' in logfile:
    #     for d in stops1:
    #         plt.axvline(d, color='orange')
    #     for d in starts1:
    #         plt.axvline(d, color='green')
    # elif '_2' in logfile:
    #     for d in stops2:
    #         plt.axvline(d, color='orange')
    #     for d in starts2:
    #         plt.axvline(d, color='green')
    # elif '_3' in logfile:
    #     for d in stops3:
    #         plt.axvline(d, color='orange')
    #     for d in starts3:
    #         plt.axvline(d, color='green')
    # else:
    #     for d in allStops:
    #         plt.axvline(d, color='orange')
    #     for d in allStarts:
    #         plt.axvline(d, color='green')

    print("-- Response times as measured by Locust sorted by value and then time --")
    max_response_times = sorted(response_times, key=response_times.get, reverse=True)[:8]
    for i in sorted(max_response_times):
        print("{} {}".format(i.strftime("%H:%M:%S"), response_times[i]))
    print("--")

    en50136_max_response_time = 30

    print("-- Response times statistics --")
    print("Number of responses: {}".format(len(times)))
    times_above_ten_seconds = list(filter(lambda t: t > 10, times))
    print("Number of faults: {}".format(len(times_above_ten_seconds)))
    times_above_max_response_time = list(filter(lambda t: t > en50136_max_response_time, times))
    print("Response times above requirements: {}".format(len(times_above_max_response_time)))

    print("Min response time: {}".format(min(times)))
    print("---")

    min_times = min(times)

    corrected_times = [t - min_times for t in times]
    plt.plot(dates, corrected_times, 'x', color='gray', label='Response time - Minimum response time')

    plt.axhline(min_times, color='blue', label='Minimum response time measured')
    #plt.axhline(max(times), color='r', label='Maximum response time measured')

    plt.axhline(en50136_max_response_time, color='r', label='Maximum response time allowed')

    # plt.axhline(28, color='orange', label='Expected min fault time')
    # plt.axhline(36, color='orange', label='Expected max fault time')

    # beautify the x-labels
    myFmt = mdates.DateFormatter('%H:%M:%S')
    plt.gca().xaxis.set_major_formatter(myFmt)
    #plt.gca().xaxis.set_major_locator(mdates.SecondLocator(interval=30))
    #plt.gca().xaxis.set_minor_locator(mdates.SecondLocator(interval=10))
    #plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%Ss'))
    plt.gcf().autofmt_xdate()

    plt.xlabel('Time')
    plt.ylabel('Response time in s')
    plt.legend(loc='lower right')


def complete(text, state):
    # replace ~ with the user's home dir. See https://docs.python.org/2/library/os.path.html
    if '~' in text:
        text = os.path.expanduser('~')

    # autocomplete directories with having a trailing slash
    if os.path.isdir(text):
        text += '/'

    return [x for x in glob.glob(text + '*.log')][state]


readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)
logfile = input('Path to the logfile: ')

response_times = readResponseTimesFromLogFile(logfile)
if len(response_times) > 0:
    plot_response_times(response_times, logfile)
else:
    readMeasurementsFromLogFileAndAppendToList(logfile)

    plt.plot(num_clients, avg_time_allowed, 'y--', label='Average time allowed')
    plt.plot(num_clients, max_time_allowed, 'r--', label='Maximum time allowed')
    # plt.plot(num_clients, min_response_time, label='min')
    plt.plot(num_clients, average_response_time, label='avg')
    plt.plot(num_clients, max_response_time, label='max')

    plt.xlabel('Number of alarm devices')
    plt.ylabel('Response time in s')
    plt.legend(loc='upper left')
    # plt.grid()

plt.show()
