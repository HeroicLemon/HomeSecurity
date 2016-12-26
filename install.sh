#!/bin/bash
sudo rm -r /srv/app/HomeSecurity/*
sudo cp -r . /srv/app/HomeSecurity
python3 /srv/app/HomeSecurity/common.py
