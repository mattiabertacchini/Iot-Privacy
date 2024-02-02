#!python3
import paho.mqtt.client as mqtt_client  # import the client1
import time, atexit
from getmac import get_mac_address as gma
from device_manager import add_device

Connected = False

broker_address = "broker.hivemq.com"
port = 1883
client_id = f"PythonRef_reader_{gma()}"
topic = "BertacchiniPanseraRistori/ip_refs/#"


# client.username_pw_set(user, password=password)    #set username and password

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            pass
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker_address, port)
    return client


def subscribe(client):
    def on_subscribe(msq, obj, mid, granted_qos):
        print("=> Subscribed to topic: " + topic)
        print("Granted QOS: " + str(granted_qos))

    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        ip_address = msg.payload.decode()
        device_type = msg.topic.split("/")[-2]
        device_id = msg.topic.split("/")[-1]
        add_device(ip_address, device_type, device_id)

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


if __name__ == '__main__':
    run()
