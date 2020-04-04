# Installation

1. raspi-config
  * set up wifi
  * set up US locale - I chose utf-8 and iso-859something-15 + another one that was on the same line
  * 
2. pip3
  * apt install python3-pip
  * cat requirements.txt | xargs pip3 install

sudo apt-get install libgpiod2 mosquitto

try to follow guidance here, then reboot: https://www.raspberrypi.org/documentation/configuration/uart.md


