#!/bin/bash

until esptool.py --port /dev/ttyAMA0 erase_flash
do
  sleep 1
  echo retrying ERASE NOW
done

echo "reboot device to start write. Hit enter when done"
read asdf

until esptool.py --port /dev/ttyAMA0 write_flash -fm dout 0x0 tasmota.bin
do
  sleep 1
  echo retrying WRITE NOW
done
