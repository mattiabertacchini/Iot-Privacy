"""
For each device (shelf) check the predictions for 12 and 24 hours
Threshold for availabilty = 10000
sleep time = 10 seconds
"""

import requests
import json
from datetime import datetime, timedelta
import time

import paho.mqtt.client as mqtt

json_db_path = "devices.json"
url = "https://paoloristori.eu.pythonanywhere.com/predict_shelf"
broker_address = "broker.hivemq.com"
port = 1883
sleep_time = 10

client = mqtt.Client()
client.connect(broker_address, port)

while True:

    with open(json_db_path, "r") as f:
        device_json = json.load(f)
    f.close()

    datetime_twelve_hours = datetime.now() + timedelta(hours=12)
    datetime_tomorrow = datetime.now() + timedelta(days=1)


    for device in device_json.get("current_available", []):

        shelf_id = device["shelf_id"]
        topic = "BertacchiniPanseraRistori/data/future/" + shelf_id

        r = requests.post(url, data={"shelf_id": shelf_id, "datetime_str": datetime_twelve_hours})
        content_twelve_hours = eval(r.content.decode())
        r = requests.post(url, data={"shelf_id": shelf_id, "datetime_str": datetime_tomorrow})
        content_tomorrow = eval(r.content.decode())
        print(content_twelve_hours["yhat"])
        print(content_tomorrow["yhat"])
        p = ""

        if content_twelve_hours["yhat"] >= 10000:
            p = "12h: disponibile\n"
        else:
            p = "12h: non disponibile\n"

        if content_tomorrow["yhat"] >= 10000:
            p = p + "24h: disponibile\n"
        else:
            p = p + "24h: non disponibile\n"

        print(p)

        client.publish(topic, p)

    time.sleep(sleep_time)
