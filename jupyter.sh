#!/bin/bash
# utility: This program is used to install jupyter, please run this script with the port you want.
apt-get update
apt-get -y install python3
apt-get install python3-pip -y
pip3 install jupyter
jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root
