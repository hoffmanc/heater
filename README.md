# Installation of Heater App

1. raspi-config
  * set up wifi
  * set up US locale - I chose utf-8 and iso-859something-15 + another one that was on the same line
  * 
2. pip3
  * apt install python3-pip
  * cat requirements.txt | xargs pip3 install

sudo apt-get install libgpiod2 mosquitto

try to follow guidance here, then reboot: https://www.raspberrypi.org/documentation/configuration/uart.md


# Using Pi to flash Sonoff R2

## Preparing Pi

## Disable Linux serial console
https://www.raspberrypi.org/documentation/configuration/uart.md

By default, the primary UART is assigned to the Linux console. If you wish to use the primary UART for other purposes, you must reconfigure Raspberry Pi OS. This can be done by using raspi-config:

Start raspi-config: sudo raspi-config.
Select option 5 - interfacing options.
Select option P6 - serial.
At the prompt Would you like a login shell to be accessible over serial? answer 'No'
At the prompt Would you like the serial port hardware to be enabled? answer 'Yes'
Exit raspi-config and reboot the Pi for changes to take effect.

## UARTs and Device Tree
Various UART Device Tree overlay definitions can be found in the kernel GitHub tree. The two most useful overlays are disable-bt and miniuart-bt.

disable-bt disables the Bluetooth device and makes the first PL011 (UART0) the primary UART. You must also disable the system service that initialises the modem, so it does not connect to the UART, using sudo systemctl disable hciuart.

miniuart-bt switches the Bluetooth function to use the mini UART, and makes the first PL011 (UART0) the primary UART. Note that this may reduce the maximum usable baud rate (see mini UART limitations below). You must also set the VPU core clock to a fixed frequency using either force_turbo=1 or core_freq=250.

The overlays uart2, uart3, uart4, and uart5 are used to enable the four additional UARTs on the Pi 4. There are other UART-specific overlays in the folder. Refer to /boot/overlays/README for details on Device Tree overlays, or run dtoverlay -h overlay-name for descriptions and usage information.

For full instructions on how to use Device Tree overlays see this page. In brief, add a line to the config.txt file to apply a Device Tree overlay. Note that the -overlay.dts part of the filename is removed. For example:

dtoverlay=disable-bt
