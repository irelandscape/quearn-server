#!/bin/bash
virtualenv --python=python3 env
source env/bin/activate && pip install -r ./requirements.txt
