#!/bin/bash

# TODO
# - install SDK ? or ./Redist enough ? => TerraBee 80x60

BASEPATH="$(dirname "$(readlink -f "$0")")"
cd "$BASEPATH"

# Dependencies
sudo apt-get install python3-opencv python3-numpy python3-protobuf python3-venv 

# Venv
# python3 -m venv --system-site-packages venv
# source venv/bin/activate
# pip install setuptools
# pip install -r requirements.txt

# Poetry
poetry install


ln -sf "$BASEPATH/3dcam" /usr/local/bin/
ln -sf "$BASEPATH/3dcam.service" /etc/systemd/system/
systemctl daemon-reload

echo "3dcam INSTALLED"
echo
