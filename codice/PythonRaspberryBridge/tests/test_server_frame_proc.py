import requests, time, cv2

URL = "https://paoloristori.eu.pythonanywhere.com/frame_processing"
files = {}
files_metadata = {'camera_ip': '192.168.68.112', 'metadata': {'img_0.png': {'arcodart': '#LAT001', 'ardesart': 'Latte UHT Parmalat'}, 'img_1.png': {'arcodart': '#LAT001', 'ardesart': 'Latte UHT Parmalat'}, 'img_2.png': {'arcodart': '#LAT001', 'ardesart': 'Latte UHT Parmalat'}, 'img_3.png': {'arcodart': '#LAT001', 'ardesart': 'Latte UHT Parmalat'}, 'img_4.png': {'arcodart': '#LAT001', 'ardesart': 'Latte UHT Parmalat'}, 'img_5.png': {'arcodart': '#LAT001', 'ardesart': 'Latte UHT Parmalat'}, 'img_6.png': {'arcodart': '#LAT001', 'ardesart': 'Latte UHT Parmalat'}, 'img_7.png': {'arcodart': '#LAT001', 'ardesart': 'Latte UHT Parmalat'}, 'img_8.png': {'arcodart': '#LAT001', 'ardesart': 'Latte UHT Parmalat'}, 'img_9.png': {'arcodart': '#LAT001', 'ardesart': 'Latte UHT Parmalat'}}}
print(f"Executing frames upload...")
headers = {'Content-type': 'application/json'}
print(files_metadata)
r = requests.post(URL, files=files, json=files_metadata, headers=headers)
print(r.content.decode())
