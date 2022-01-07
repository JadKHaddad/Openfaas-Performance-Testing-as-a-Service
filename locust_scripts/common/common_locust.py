import logging
from abc import ABC, abstractmethod

import requests
from locust import events

from stopwatch import Stopwatch


class RepeatingClient(ABC):
    """
    Base class that implements the repetition, but not the actual data transfer.
    This way, we can create a client for different protocols, e.g., RepeatingHttpClient, RepeatingTCPClient, ...
    """
    def __init__(self, base_url):
        self.base_url = base_url

    @abstractmethod
    def send_impl(self, endpoint, data=None) -> (object, bool):
        pass

    def send(self, endpoint, data=None):
        logger = logging.getLogger('RepeatingClient')

        url = self.base_url + endpoint

        logger.info("Sending to %s", url)

        stopwatch = Stopwatch()

        response = None
        successfully_sent = False
        while not successfully_sent:
            # noinspection PyBroadException
            try:
                response, successfully_sent = self.send_impl(url, data)
                logger.info("{} {}".format(response, successfully_sent))
            except Exception:
                pass

        stopwatch.stop()
        total_time_ms = int(stopwatch.duration * 1000)
        events.request_success.fire(request_type="POST", name=endpoint, response_time=total_time_ms, response_length=0)

        logger.info("Response time %s ms", total_time_ms)

        return response


class RepeatingHttpClient(RepeatingClient):
    def send_impl(self, url, data=None) -> (object, bool):
        logger = logging.getLogger('RepeatingHttpClient')

        logger.info("POST")
        if data is not None:
            response = requests.post(url, json=data)
        else:
            response = requests.post(url)
        logger.info("Response: %s", response.status_code)

        successfully_sent = 200 <= response.status_code < 300

        return response, successfully_sent
