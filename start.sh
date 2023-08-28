#!/bin/bash -eux

set -o allexport 
source ./default.env
set +o allexport

echo "** Running bootup.py"
python3 bootup.py
echo "** Completed running bootup.py"

gunicorn --config $PROXY_GATE_CONFIG_DIR/gunicorn.conf.py wsgi:app
