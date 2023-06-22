#!/bin/bash
if [ -r bin/activate ]; then
  source bin/activate
fi
python3 preview.py $*
