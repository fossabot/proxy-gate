#!/bin/bash -eux

set -o allexport 
source ./default.env
set +o allexport

mkdir -p $PROXY_GATE_DATA_DIR
mkdir -p $PROXY_GATE_CONFIG_DIR

for config_file in flask-config.yml proxy-gate-config.yml gunicorn.conf.py; do
    if [ ! -f $PROXY_GATE_CONFIG_DIR/$config_file ]; then
        echo "Copying default $config_file"
        cp examples/$config_file $PROXY_GATE_CONFIG_DIR/$config_file
    fi
done

python3 bootup.py

gunicorn --config $PROXY_GATE_CONFIG_DIR/gunicorn.conf.py wsgi:app
