#!/usr/bin/env python3

import os
import time
import board
import adafruit_dht
import paho.mqtt.client as mqtt
from tinydb import TinyDB
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
    db.insert({
        u'datetime': now.strftime(u'%Y-%m-%d %H:%M:%S%z'),
        u'temp': temp,
        u'humidity': humidity,
        u'status': status
    })

def getTempConf():
    global tempConf
    t = int(open("config/temp.conf", "r").read())
    print(u'temp set at {}'.format(t))
    return t

db = TinyDB(datetime.now().strftime(u'temps-%Y-%m-%d.json'))

last5Temps = []

dhtDevice = adafruit_dht.DHT22(board.D4)

while True:
    try:
        maxTemp = getTempConf()
        minTemp = maxTemp - 2
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
