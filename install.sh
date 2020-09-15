#!/bin/bash

set -e

sed -i "s/console=serial0,115200//" /boot/cmdline.txt
systemctl disable hciuart
echo 'dtoverlay=disable-bt' >> /boot/config.txt
apt-get install -y python3-pip mosquitto mosquitto-clients libgpiod2
systemctl enable mosquitto
pip3 install adafruit_dht paho-mqtt adafruit-circuitpython-dht esptool


echo 'you will need to reboot the machine for the changes to take effect'
