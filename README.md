# BPR_IoT_Project
IoT Project based on ESP32-WebCam and Raspberry bridge for image processing.
## Goals
Building a distributed IoT arch. the purpose of the project is to handle items quantity variation inside a Wearhouse.
Thanks to several image processing techniques is possible to detect if an item is picked-up or released and then we can try to detect the subject of the action using NFC sensor.
Detect item 'movement' allows us to register a quantity variation inside a WMS-like application in order to monitor each item availability from remote.
## Process
- frame_collector.py reads each connected device streamed frames. (Raspberry will host this script so it must be connected to the same LAN of the ESP32 CAM)
- mqtt_broker_reader.py receives each ESP32 Cam IP address after wi-fi connection
- test_serverless_func.py is under development....
- other py are used to store esp32 config functions 
## TODO
- Update communication schemas with protocol & devices

