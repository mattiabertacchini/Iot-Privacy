import requests


URL = f"https://paoloristori.eu.pythonanywhere.com/shelf/A0001/camera"

# Publish to cloud connected device infos in order to keep updated the DT status
web_data = {}
prefix = "camera_"
web_data[prefix+"ip"] = "192.168.68.113"
web_data[prefix+"status"] = 1
r = requests.post(URL, data=web_data)
print(r.status_code, r.content.decode())