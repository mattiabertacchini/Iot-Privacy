import json
from datetime import datetime

json_db_path = "static/local_db/users.json"


def read_local_db():
    with open(json_db_path, "r") as f:
        shelf_json = json.load(f)
    f.close()
    return shelf_json


def write_local_db(user_json):
    with open(json_db_path, "w") as f:
        json.dump(user_json, f, indent=4)
    f.close()


def get_user(rfid_id):
    users_json = read_local_db()
    for user in users_json.get("users", []):
        if user["rfid_id"] == rfid_id:
            return user
    raise Exception(f"Rfid id '{rfid_id}' not found")
