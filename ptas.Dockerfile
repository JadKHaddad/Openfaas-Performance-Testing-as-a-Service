FROM python:3.7-slim-buster

WORKDIR /home/

COPY ptas.docker/index.py           .

USER root
RUN pip install flask waitress requests

RUN mkdir -p /home/function

WORKDIR /home/function/
COPY ptas/requirements.txt	.

RUN pip install -r requirements.txt

COPY ptas/handler.py	    .

WORKDIR /home/

CMD ["python", "-u", "/home/index.py"]