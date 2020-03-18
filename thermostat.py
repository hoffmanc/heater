#!/usr/bin/env python3

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
    doc_ref.insert({
        u'datetime': now,
        u'temp': temp,
        u'humidity': humidity,
        u'status': status
    })

def onConfigChange(doclist, changes, read_time):
    global maxTemp
    global minTemp
    maxTemp = doclist[0].get('temp')
    print(u'temp set to {}'.format(maxTemp))
    minTemp = maxTemp - 2

db = TinyDB(datetime.now().strftime(u'temps-%Y-%m-%d.json'))

last5Temps = []
maxTemp = int(open("config/temp.conf", "r").read())
print(u'initial temp {}'.format(maxTemp))
minTemp = maxTemp - 2

dhtDevice = adafruit_dht.DHT22(board.D4)

while True:
    try:
        # Print the values to the serial port
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
