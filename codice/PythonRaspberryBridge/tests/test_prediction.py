import requests

shelf_id = "B0001"
datetime_str = "2024-01-01 12:00:00"
url = "https://paoloristori.eu.pythonanywhere.com/predict_shelf"

r = requests.post(url, data={"shelf_id": shelf_id, "datetime_str": datetime_str})
print(r.status_code)
print(r.content.decode())
exit(1)