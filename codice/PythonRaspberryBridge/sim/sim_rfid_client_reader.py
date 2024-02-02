import paho.mqtt.client as mqtt_client
from getmac import get_mac_address as gma
import atexit

broker_address = "broker.hivemq.com"
port = 1883
shelf_id = "A0001"
client_id = f"PythonRef_reader_{gma()}"
topic = f"BertacchiniPanseraRistori/data/rfid/{shelf_id}"
verbose = True

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            if verbose: print("Connected to MQTT Broker!")
        else:
            if verbose: print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker_address, port)
    return client

def subscribe(client):
    def on_subscribe(msq, obj, mid, granted_qos):
        if verbose: print("=> Subscribed to topic: " + topic)
        if verbose: print("Granted QOS: " + str(granted_qos))

    def on_message(client, userdata, msg):
        if verbose:  print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        rfid_tag = msg.payload.decode()



    client.subscribe(topic)
    client.on_message = on_message
    client.on_subscribe = on_subscribe

def unsubscribe(client):
    client.unsubscribe(topic)

def run():
    client = connect_mqtt()
    atexit.register(unsubscribe, client=client)
    subscribe(client)
    client.loop_forever()

run()