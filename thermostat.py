#!/usr/bin/env python3

import time
import board
import adafruit_dht
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
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
    doc_ref = db.collection(u'readings').document(now)
    doc_ref.set({
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

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': 'heater-267000',
})
db = firestore.client()
doc_ref = db.collection(u'config').document(u'maxTemp')
doc_ref.on_snapshot(onConfigChange)

dhtDevice = adafruit_dht.DHT22(board.D4)
last5Temps = []
maxTemp = doc_ref.get().get('temp')
print(u'initial temp {}'.format(maxTemp))
minTemp = maxTemp - 2

while True:
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        log(temperature_f, humidity)
        last5Temps = last5Temps[-4:] + [temperature_f]
        avgOfLast5 = sum(last5Temps) / len(last5Temps)
        if avgOfLast5 < minTemp:
            offon(1)
        elif avgOfLast5 > maxTemp:
            offon(0)
            
 
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
 
    time.sleep(2.0)
