
from getmac import get_mac_address as gma


topic = "BertacchiniPanseraRistori/data/rfid/A0001"
payload = "351952216"
hostname = "broker.hivemq.com"

import paho.mqtt.client as paho

def on_publish(client,userdata,result):
    print("data published \n")
    pass

client1= paho.Client(f"{gma()}")
client1.on_publish = on_publish
client1.connect(hostname, 1883)
ret= client1.publish(topic, payload)
