#!/bin/bash

gunicorn --bind 127.0.0.1:8050 --worker-class eventlet -w 1 graph:server --log-level DEBUG --reload # --log-file /tmp/app.log
