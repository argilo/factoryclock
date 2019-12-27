#!/bin/bash

set -e

sudo apt-get update
sudo apt-get install -y python3-rpi.gpio

sudo cp /home/pi/clock.service /etc/systemd/system/clock.service
sudo systemctl enable clock.service
