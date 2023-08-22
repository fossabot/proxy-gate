#!/bin/bash -eux

set -o allexport 
source ./default.env
set +o allexport


python3 bootup.py

gunicorn --config $PROXY_GATE_CONFIG_DIR/gunicorn.conf.py wsgi:app
