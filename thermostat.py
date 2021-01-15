#!/usr/bin/env python3

import os
import time
import board
import adafruit_dht
import paho.mqtt.client as mqtt
from datetime import datetime

status = None
def offon(on):
    global status
    if status is None or status != on:
        client = mqtt.Client()
        client.connect("localhost",1883,60)
        print("sending %d via MQTT" % (on))
        client.publish("test/message/cmnd/heater/power", on );
        client.disconnect()
        status = on

def log(temp, humidity):
    global db, status
    print("Temp: {:.1f} F | Humidity: {}% ".format(temp, humidity))
    now = datetime.now()
    l = "\t".join((
        now.strftime(u'%Y-%m-%d %H:%M:%S%z'),
        "{:.1f}".format(temp),
        str(humidity),
        str(status)
    ))

    fo = open("log/log-" + now.strftime(u'%Y-%m-%d') + ".log", "a")
    fo.write(l + "\n")
    fo.close()

def getTempConf():
    global tempConf
    t = int(open("config/temp.conf", "r").read())
    print(u'temp set at {}'.format(t))
    return t

def getThresholdConf():
    global thresholdConf
    t = int(open("config/threshold.conf", "r").read())
    print(u'threshold set at {}'.format(t))
    return t

last5Temps = []
os.makedirs("log", exist_ok=True)
dhtDevice = adafruit_dht.DHT22(board.D4)

while True:
    try:
        maxTemp = getTempConf()
        threshold = getThresholdConf()
        minTemp = maxTemp - threshold
        maxTemp += threshold
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        log(temperature_f, humidity)
        last5Temps = last5Temps[-4:] + [temperature_f]
        maxOfLast5 = max(last5Temps)

        if maxOfLast5 < minTemp:
            offon(1)
        elif maxOfLast5 > maxTemp:
            offon(0)

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])

    time.sleep(2.0)
