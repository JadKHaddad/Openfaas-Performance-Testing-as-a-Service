FROM openfaas/of-watchdog:0.7.7 as watchdog
FROM python:3.7-slim-buster

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

ARG ADDITIONAL_PACKAGE
# Alternatively use ADD https:// (which will not be cached by Docker builder)

RUN apt-get -qy update && apt-get -qy install gcc make ${ADDITIONAL_PACKAGE}

WORKDIR /home/

COPY index.py           .
COPY requirements.txt   .
COPY limits.conf        .

USER root
RUN cp limits.conf /etc/security/limits.conf
RUN pip install -r requirements.txt

# Build the function directory and install any user-specified components
RUN mkdir -p function
RUN touch ./function/__init__.py
WORKDIR /home/function/
COPY function/requirements.txt	.
RUN pip install --user -r requirements.txt

#install function code
USER root

COPY function/   .
ARG TEST_COMMAND=tox
ARG TEST_ENABLED=true
RUN if [ "$TEST_ENABLED" == "false" ]; then \
    echo "skipping tests";\
    else \
    eval "$TEST_COMMAND"; \
    fi

WORKDIR /home/

#configure WSGI server and healthcheck
USER root

ENV fprocess="python index.py"

ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5000"

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
