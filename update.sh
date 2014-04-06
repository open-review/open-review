#!/bin/bash
set -e

git pull
git submodule init
git submodule update

cd static/
bower install
cd ..

python3 manage.py syncdb
python3 manage.py migrate

