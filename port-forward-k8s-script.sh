#!/bin/bash

fuser -n tcp -k 8080; /snap/bin/kubectl port-forward -n openfaas svc/gateway 8080:8080 --address='0.0.0.0'