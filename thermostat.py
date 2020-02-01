#!/usr/bin/env python3

import time
import board
import adafruit_dht
import sys
import paho.mqtt.client as mqtt
 
prevOn = None

def offon(on):
    global prevOn
    if prevOn is None or prevOn != on:
        client = mqtt.Client()
        client.connect("localhost",1883,60)
        print("sending %d via MQTT" % (on))
        client.publish("test/message/cmnd/heater/power", on );
        client.disconnect()
        prevOn = on
 
dhtDevice = adafruit_dht.DHT22(board.D4)
last5Temps = []
minTemp = int(sys.argv[1])
maxTemp = int(sys.argv[2])

while True:
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
              .format(temperature_f, temperature_c, humidity))
        last5Temps = last5Temps[-4:] + [temperature_f]
        avgOfLast5 = sum(last5Temps) / len(last5Temps)
        print(avgOfLast5, last5Temps)
        if avgOfLast5 < minTemp:
            offon(1)
        elif avgOfLast5 > maxTemp:
            offon(0)
            
 
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
 
    time.sleep(2.0)
