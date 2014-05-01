#!/bin/bash
set -e

git pull
git submodule init
git submodule update

bower install

python3 manage.py syncdb
python3 manage.py migrate

