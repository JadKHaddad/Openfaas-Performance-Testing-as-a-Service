FROM python:3.7-slim-buster

WORKDIR /home/

COPY server/server.py ./server/server.py
ADD server/dist ./server/dist/
COPY requirements.txt .
ADD ptas   ./ptas

USER root
RUN pip install -r ./requirements.txt
RUN pip install -r ./ptas/requirements.txt

WORKDIR /home/server

CMD ["python", "/home/server/server.py", "-l", "-p", "8080"]