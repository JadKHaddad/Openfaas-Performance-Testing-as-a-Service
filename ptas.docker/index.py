# this is a modified version of the original index.py.
# Copyright (c) Alex Ellis 2017. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from flask import Flask, request, current_app, request, Response
from function import handler
from waitress import serve
import os, threading
import uuid
from functools import wraps
from werkzeug.exceptions import HTTPException, InternalServerError
import requests

app = Flask(__name__)
tasks = {}

def flask_async(f):
    """
    This decorator transforms a sync route to asynchronous by running it in a background thread.
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        def task(app, environ, callback_url):
            # Create a request context similar to that of the original request
            with app.request_context(environ):
                try:
                    # Run the route function and record the response
                    tasks[task_id]['result'] = f(*args, **kwargs)
                    if callback_url is not None:
                        requests.post(callback_url, data=tasks[task_id]['result'][0].get_data(as_text=True))
                except HTTPException as e:
                    tasks[task_id]['result'] = current_app.handle_http_exception(e)
                except Exception as e:
                    # The function raised an exception, so we set a 500 error
                    tasks[task_id]['result'] = InternalServerError()
                    if current_app.debug:
                        # We want to find out if something happened so reraise
                        raise

        # Assign an id to the asynchronous task
        task_id = uuid.uuid4().hex

        # Record the task, and then launch it
        tasks[task_id] = {'task': threading.Thread(
            target=task, args=(current_app._get_current_object(), request.environ, request.headers.get('X-Callback-Url')))}
        tasks[task_id]['task'].start()

        # Return a 202 response, with an id that the client can use to obtain task status
        return {'task_id': task_id}, 202

    return wrapped

# distutils.util.strtobool() can throw an exception
def is_true(val):
    return len(val) > 0 and val.lower() == "true" or val == "1"

@app.before_request
def fix_transfer_encoding():
    """
    Sets the "wsgi.input_terminated" environment flag, thus enabling
    Werkzeug to pass chunked requests as streams.  The gunicorn server
    should set this, but it's not yet been implemented.
    """

    transfer_encoding = request.headers.get("Transfer-Encoding", None)
    if transfer_encoding == u"chunked":
        request.environ["wsgi.input_terminated"] = True

@app.route("/function/ptas", defaults={"path": ""}, methods=["POST", "GET"])
def main_route(path):
    raw_body = os.getenv("RAW_BODY", "false")

    as_text = True

    if is_true(raw_body):
        as_text = False
    
    ret = handler.handle(request.get_data(as_text=as_text))

    return ret

@app.route("/async-function/ptas", defaults={"path": ""}, methods=["POST", "GET"])
@flask_async
def main_route_async(path):
    raw_body = os.getenv("RAW_BODY", "false")

    as_text = True

    if is_true(raw_body):
        as_text = False

    return handler.handle(request.get_data(as_text=as_text))

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
