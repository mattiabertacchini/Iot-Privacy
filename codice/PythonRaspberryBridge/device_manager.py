import json, cv2, urllib.request, threading, time, requests, atexit
import paho.mqtt.client as mqtt_client
import platform
if platform.system() != "Darwin": from pyzbar import pyzbar
from esp_camera_manager import *
from datetime import datetime, timedelta
from getmac import get_mac_address as gma

json_db_path = "devices.json"
DEBUG = True

def add_device(ip_string, type, id):
    """
    Register a new dev inside Json DB
    :param ip_string: ip dot-decimal format
    :param type: device type
    :param id: device unique identifier
    """
    URL = f"https://paoloristori.eu.pythonanywhere.com/shelf/{id}/{type}"
    f = open(json_db_path, "r")
    devices_json = json.load(f)
    f.close()

    # Publish to cloud connected device infos in order to keep updated the DT status
    web_data = {}
    prefix = "camera_" if type == "camera" else "rfid_"
    web_data[prefix+"ip"] = ip_string
    web_data[prefix+"status"] = 1
    r = requests.post(URL, data=web_data)

    # Create dev if not existing
    cur_dev_list = devices_json.get("current_available", [])
    if id not in [diz["shelf_id"] for diz in cur_dev_list]:

        rfid_ip = "" if type == "camera" else ip_string
        camera_ip = "" if type == "rfid" else ip_string

        devices_json["current_available"].append({"shelf_id": id, "camera_ip": camera_ip, "rfid_ip": rfid_ip})
        f = open(json_db_path, "w")
        json.dump(devices_json, f, indent=4)
        f.close()

    # Update dev if id already exists
    else:
        for dev_dict in cur_dev_list:
            if dev_dict["shelf_id"] == id:

                if type == "camera":
                    dev_dict["camera_ip"] = ip_string

                if type == "rfid":
                    dev_dict["rfid_ip"] = ip_string

        updated_json = {"current_available": cur_dev_list}
        f = open(json_db_path, "w")
        json.dump(updated_json, f, indent=4)
        f.close()

def add_last_rfid(ip_string, type, id, rfid):
    """
    Register a new dev inside Json DB
    :param ip_string: ip dot-decimal format
    :param type: device type
    :param id: device unique identifier
    :param rfid: rfid last tag value
    """
    URL = f"https://paoloristori.eu.pythonanywhere.com/shelf/{id}/{type}"
    f = open(json_db_path, "r")
    devices_json = json.load(f)
    f.close()

    # Publish to cloud connected device infos in order to keep updated the DT status
    web_data = {}
    prefix = "camera_" if type == "camera" else "rfid_"
    web_data[prefix+"ip"] = ip_string
    web_data[prefix+"status"] = 1
    web_data[prefix+"last_tag"] = rfid
    r = requests.post(URL, data=web_data)

    # Create dev if not existing
    cur_dev_list = devices_json.get("current_available", [])
    if id not in [diz["shelf_id"] for diz in cur_dev_list]:

        rfid_ip = "" if type == "camera" else ip_string
        camera_ip = "" if type == "rfid" else ip_string

        devices_json["current_available"].append({"shelf_id": id, "camera_ip": camera_ip, "rfid_ip": rfid_ip})
        f = open(json_db_path, "w")
        json.dump(devices_json, f, indent=4)
        f.close()

    # Update dev if id already exists
    else:
        for dev_dict in cur_dev_list:
            if dev_dict["shelf_id"] == id:

                if type == "camera":
                    dev_dict["camera_ip"] = ip_string

                if type == "rfid":
                    dev_dict["rfid_ip"] = ip_string

        updated_json = {"current_available": cur_dev_list}
        f = open(json_db_path, "w")
        json.dump(updated_json, f, indent=4)
        f.close()

def remove_device(ip_string, type):
    """
    Remove dev from Json DB
    :param ip_string: ip dot-decimal format
    """

    with open(json_db_path, "r") as f:
        devices_json = json.load(f)

    # Get shelf id in order to update D.T. status
    shelf_id = None
    cur_dev_list = devices_json.get("current_available", [])
    for dev_dict in cur_dev_list:
        if dev_dict["camera_ip"] == ip_string or dev_dict["rfid_ip"] == ip_string:
            shelf_id = dev_dict["shelf_id"]
            # while retrieving shelf id update ip list
            if type == "camera": dev_dict["camera_ip"] = ""
            if type == "rfid": dev_dict["rfid_ip"] = ""

    # Publish to cloud connected device infos in order to keep updated the DT status
    URL = f"https://paoloristori.eu.pythonanywhere.com/shelf/{shelf_id}/{type}"
    web_data = {}
    prefix = "camera_" if type == "camera" else "rfid_"
    web_data[prefix + "ip"] = ip_string
    web_data[prefix + "status"] = 0
    requests.post(URL, data=web_data)

    # Update local device.json file
    updated_json = {"current_available": cur_dev_list}
    f = open(json_db_path, "w")
    json.dump(updated_json, f, indent=4)
    f.close()


def get_active_devices():
    """Returns all active devices"""
    with open(json_db_path, "r") as f:
        devices_json = json.load(f)

    cur_dev_list = []
    for dev_dict in devices_json.get("current_available", []):
        if dev_dict["camera_ip"] != "":
            # Currently not checking ESP32 RFID Reader status
            cur_dev_list.append(dev_dict)

    return cur_dev_list


def check_working():
    """
    Check if devices inside current_available are all working
    otherwise inactive ones those will be removed.
    """
    f = open(json_db_path, "r")
    devices_json = json.load(f)
    f.close()
    cur_dev_list = devices_json.get("current_available", [])
    active_dev = []
    for ip_to_check_dict in cur_dev_list:
        try:
            dict_updated = {"shelf_id": ip_to_check_dict["shelf_id"], "camera_ip": "", "rfid_ip": ""}
            # check if camera is working
            ip_working_status = check_service_status(ip_to_check_dict["camera_ip"])
            if ip_to_check_dict["camera_ip"] != "" and ip_working_status:
                dict_updated["camera_ip"] = ip_to_check_dict["camera_ip"]

            # check if rfid is working
            # if ip_to_check_dict["rfid_ip"] != "" and check_service_status(ip_to_check_dict["rfid_ip"]):
            # Currently not updating RFID Tag reader status
            dict_updated["rfid_ip"] = ip_to_check_dict["rfid_ip"]

            # append only if one dev is currently active
            if (len(dict_updated["rfid_ip"]) + len(dict_updated["camera_ip"])) > 0:
                active_dev.append(dict_updated)

        except Exception as e:
            print("Bug during working check: ", e)
            pass

    output = {}
    output["current_available"] = active_dev
    f = open(json_db_path, "w")
    json.dump(output, f, indent=4)
    f.close()


def check_working_loop():
    """
    Check if devices inside current_available are all working
    otherwise inactive ones those will be removed.
    """
    while True:
        check_working()


def __deprecated_streaming_capture(ip_address):
    """
    :param ip_address: ip to monitor in order to detect a stream
    """
    try:
        full_ip = f"http://{ip_address}"
        full_image_ip = f"http://{ip_address}/capture?"
        set_resolution(full_ip, index=9)
        buff_max_len = 10
        buff = []

        while True:
            print(f"{datetime.now().strftime('%H:%M:%S')} - Frame captures n.{len(buff)}...")
            resp = urllib.request.urlopen(full_image_ip)
            buff.append(resp)
            # cv2.imshow(f"Frame {len(buff)}", frame)
            # cv2.imwrite(f"frame_testing/{len(buff)}.png", frame)
            # print(f"Frame n. {len(buff)}")
            if len(buff) == buff_max_len:
                # threading.Thread(target=publish_frames_buff, args=(buff.copy(), ip_address)).start()
                publish_frames_buff(buff.copy(), ip_address)
                buff.clear()
                return
            # cv2.waitKey(10)


        cv2.destroyAllWindows()

    except Exception as e:
        # print(f"Error capturing video streaming: \n{e}")
        cv2.destroyAllWindows()


def rfid_tag_reader(camera_ip, rfid_ip, shelf_id, verbose=False, max_sec_validity=20):
    """
    Father function of streaming fuction in order to read data only when rfid tag is read.

    :param shelf_id: the id which is linked to the shelf in order to read mqtt broker data
    :param camera_ip: ip address of the streaming camera
    :param rfid_ip: ip address of the rfid reader
    :param verbose: no expl. needed
    :param max_sec_validity: max. delta second in order to handle the end of the streaming capture
    """
    broker_address = "broker.hivemq.com"
    port = 1883
    client_id = f"PythonRef_reader_{gma()}"
    topic = f"BertacchiniPanseraRistori/data/rfid/{shelf_id}"

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
            if verbose: print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            rfid_tag = msg.payload.decode()
            print(f"Tag rcv: {rfid_tag}")
            add_last_rfid(rfid_ip, 'rfid', shelf_id, rfid_tag)
            t = threading.Thread(target=streaming_capture,
                             args=(camera_ip, rfid_ip, shelf_id,
                              datetime.now()+timedelta(0, max_sec_validity), rfid_tag)
                             )
            t.start()

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


def streaming_capture(camera_ip, rfid_ip, shelf_id, max_time_available=datetime.now()+timedelta(0, 5), rfid_tag=None):
    """
    Capture, until time is over, images from streaming camera to send online.

    :param camera_ip: ip address of the streaming camera
    :param rfid_ip: ip address of the rfid tag reader
    :param shelf_id: id of the shelf where devices are located
    :max_time_available: datetime instances until i cannot read no more frames from my camera
    :rfid_tag: tag rfid to send online
    """
    try:
        full_ip = f"http://{camera_ip}"
        full_stream_ip = f"http://{camera_ip}:81/stream"
        set_resolution(full_ip, index=9)
        cap = cv2.VideoCapture(full_stream_ip)
        print(cap)
        buff_max_len = 15
        buff = []
        print("Sono entrato")
        while datetime.now() <= max_time_available:
            while datetime.now() <= max_time_available:

                if cap.isOpened():
                    ret, frame = cap.read()

                    if ret:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        barcodes = pyzbar.decode(gray)
                        if len(buff) == buff_max_len:
                            # write text inside
                            text = "Data published"
                            if DEBUG: cv2.putText(frame, text, (0, 0), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 255), 2)
                            if DEBUG: cv2.imshow("frame", frame)
                            # create a thread that publish data
                            t = threading.Thread(target=publish_frames_buff, args=(buff.copy(), camera_ip, rfid_ip, shelf_id, rfid_tag))
                            # set thread execution as blocking
                            t.start()
                            t.join()
                            # after frame publishing close all windows and rel. cap
                            cv2.destroyAllWindows()
                            cap.release()
                            buff.clear()
                            return

                        for barcode in barcodes:
                            # extract the bounding box location of the barcode and draw the
                            # bounding box surrounding the barcode on the image
                            (x, y, w, h) = barcode.rect
                            cv2.rectangle(frame, (x, y), (x + int(w/2), y + int(h/2)), (0, 128, 0), -1)
                            # the barcode data is a bytes object so if we want to draw it on
                            # our output image we need to convert it to a string first
                            barcodeData = barcode.data.decode("utf-8")
                            # draw the barcode data and barcode type on the image
                            # text = "{} ({})".format(barcodeData, barcodeType)
                            # cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            #            0.5, (0, 0, 255), 2)
                            buff.append({"img": frame, "content": json.loads(barcodeData)})

                    if DEBUG: cv2.imshow("frame", frame)

                    key = cv2.waitKey(40)
                    if key == 27:
                        break


            cv2.destroyAllWindows()
            cap.release()

    except Exception as e:
        if DEBUG: print(e)
        cv2.destroyAllWindows()


def publish_frames_buff(frame_buffer, camera_ip, rfid_ip, shelf_id, rfid_tag):
    """
    :param frame_buffer: list of browser web response
    :param camera_ip: ip address of ESP-32 camera
    :param rfid_ip: ip address of my rfid tag reader
    :param shelf_id: id of the shelf where devices are located
    :param rfid_tag: rfid tag value read

    """
    URL = "https://paoloristori.eu.pythonanywhere.com/frame_processing"
    files = {}
    headers = {
                #"Content-Type": "application/json",
                "X-Camera-IP": camera_ip,
                "X-RFID-IP": rfid_ip,
                "X-Shelf-ID": shelf_id,
                "X-Item-ID": frame_buffer[0]["content"]["arcodart"],
                "X-Item-Description": frame_buffer[0]["content"]["ardesart"],
                "X-RFID-Tag": rfid_tag
               }
    for cont, frame_dict in enumerate(frame_buffer):
        # image = np.asarray(bytearray(resp.read()), dtype="uint8")
        # frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
        _, imdata = cv2.imencode('.PNG', frame_dict["img"])
        # cv2.imwrite(f"frame_testing/{cont}.png", frame)
        # files_metadata[f"img_{cont}.png"] = frame_dict["content"]
        files[f"img_{cont}.png"] = imdata
        # files_metadata.append(frame_dict)


    if DEBUG: print(f"Executing frames upload...")
    r = requests.post(URL, files=files, headers=headers)
    if DEBUG: print(f"Camera IP: {camera_ip}\n{r.content.decode()}")
    time.sleep(2)

    # print("Executing frames direction analysis...")
    # from test_frame_direction import find_direction_from_frame
    # find_direction_from_frame([frame_dict["img"] for frame_dict in frame_buffer])
    # exit(1)


def streaming_capture_not_working(camera_ip, rfid_ip, shelf_id, max_time_available=datetime.now()+timedelta(0, 5), rfid_tag=None):
    """
    Capture, until time is over, images from streaming camera to send online.
    Sends 20 frames each time until 5 sec aren't over.

    :param camera_ip: ip address of the streaming camera
    :param rfid_ip: ip address of the rfid tag reader
    :param shelf_id: id of the shelf where devices are located
    :max_time_available: datetime instances until I cannot read no more frames from my camera
    :rfid_tag: tag rfid to send online
    """
    try:
        full_ip = f"http://{camera_ip}"
        full_stream_ip = f"http://{camera_ip}:81/stream"
        set_resolution(full_ip, index=9)
        cap = cv2.VideoCapture(full_stream_ip)
        buff = []

        # while datetime.now() <= max_time_available:
        while datetime.now() <= max_time_available:
            if cap.isOpened():
                ret, frame = cap.read()

                if ret:
                    buff.append({"img": frame})

                if DEBUG: cv2.imshow("frame", frame)

                key = cv2.waitKey(40)
                if key == 27:
                    break

        # after the reading window is over send all frame to cloud
        text = "Data published"
        if DEBUG: cv2.putText(frame, text, (0, 0), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        if DEBUG: cv2.imshow("frame", frame)
        # consider only 20 images to send
        buff = [frame for index, frame in enumerate(buff) if index % 5 == 0]
        # create a thread that publish data
        t = threading.Thread(target=publish_frames_buff, args=(buff.copy(), camera_ip, rfid_ip, shelf_id, rfid_tag))
        # set thread execution as blocking
        t.start()
        t.join()
        # after frame publishing close all windows and rel. cap
        cv2.destroyAllWindows()
        cap.release()
        buff.clear()



    except Exception as e:
        # print(f"Error capturing video streaming: \n{e}")
        if DEBUG: print(e)
        cv2.destroyAllWindows()


def publish_frames_buff_not_working(frame_buffer, camera_ip, rfid_ip, shelf_id, rfid_tag):
    """
    :param frame_buffer: list of browser web response
    :param camera_ip: ip address of ESP-32 camera
    :param rfid_ip: ip address of my rfid tag reader
    :param shelf_id: id of the shelf where devices are located
    :param rfid_tag: rfid tag value read

    """
    URL = "https://paoloristori.eu.pythonanywhere.com/frame_processing"
    files = {}
    headers = {
                #"Content-Type": "application/json",
                "X-Camera-IP": camera_ip,
                "X-RFID-IP": rfid_ip,
                "X-Shelf-ID": shelf_id,
                "X-Item-ID": "DEPRECATED",
                "X-Item-Description": "DEPRECATED",
                "X-RFID-Tag": rfid_tag
               }

    for cont, frame_dict in enumerate(frame_buffer):
        _, imdata = cv2.imencode('.PNG', frame_dict["img"])
        files[f"img_{cont}.png"] = imdata


    if DEBUG: print(f"Executing frames upload...")
    r = requests.post(URL, files=files, headers=headers)
    if DEBUG: print(f"Camera IP: {camera_ip}\n{r.content.decode()}")
    time.sleep(2)


