#!/bin/bash

check_env() {
  yafp_venv=${VIRTUAL_ENV##*/} || yafp_venv=""
  if [ -z "$yafp_venv" ]; then
    source bin/activate 
  fi
  yafp_venv=${VIRTUAL_ENV##*/} || yafp_venv=""
  if [ -z "$yafp_venv" ]; then
     echo "Can't set env!"
     exit 1
  fi
}

check_env
pip3 install -r requirements.txt
