gunicorn --bind 127.0.0.1:8050 --worker-class eventlet -w 1 graph:server --reload --log-level info # --log-file /tmp/app.log
