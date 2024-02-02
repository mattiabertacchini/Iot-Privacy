import json
from datetime import datetime

json_db_path = "static/local_db/shelf_new.json"


def read_local_db():
    with open(json_db_path, "r") as f:
        shelf_json = json.load(f)
    f.close()
    return shelf_json


def write_local_db(shelf_json):
    with open(json_db_path, "w") as f:
        json.dump(shelf_json, f, indent=4)
    f.close()


def get_shelf(id_shelf):
    shelf_json = read_local_db()
    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_location(id_shelf):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["location"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_latitude(id_shelf):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["latitude"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_longitude(id_shelf):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["longitude"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_product_id(id_shelf):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["product_id"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_product_description(id_shelf):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["product_description"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_qty(id_shelf):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["qty"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def increment_qty(id_shelf):
    """
    Increment quantity of an item of 1 unit
    """
    qty = get_qty(id_shelf)

    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            shelf["qty"] = int(qty) + 1
            break

    write_local_db(shelf_json)


def decrement_qty(id_shelf):
    """
    Decrement quantity of an item of 1 unit
    """
    qty = get_qty(id_shelf)

    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            shelf["qty"] = int(qty) - 1
            break

    write_local_db(shelf_json)


def distance(id_shelf1, id_shelf2):
    """
    Get distance between 2 shelf
    :param id_shelf1: id of the first shelf to compare
    :param id_shelf2: id of the second shelf to compare
    :return: lat/long based distance between 2 shelf
    """
    latitude = abs(float(get_latitude(id_shelf1)) - float(get_latitude(id_shelf2)))
    longitude = abs(float(get_longitude(id_shelf1)) - float(get_longitude(id_shelf2)))
    return latitude + longitude


def get_camera_ip(id_shelf):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["camera_ip"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_shelf_from_ip(camera_ip):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["camera_ip"] == camera_ip:
            return shelf["id"]
    raise Exception(f"Camera ip '{camera_ip}' not found")


def get_camera_status(id_shelf):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["camera_status"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_rfid_ip(id_shelf):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["rfid_ip"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_rfid_status(id_shelf):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["rfid_status"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_rfid_last_time_read(id_shelf):
    """
    Returns %d/%m/%Y %H:%M:%S
    """
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["rfid_last_time_read"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_rfid_last_tag(id_shelf):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            return shelf["rfid_last_tag"]
    raise Exception(f"Shelf id '{id_shelf}' not found")


def get_locations(product_id):
    shelf_json = read_local_db()
    locations = []

    for shelf in shelf_json.get("shelves", []):
        if shelf['product_id'] == product_id:
            element = {
                'shelf_id': shelf['id'],
                'location': shelf['location'],
                'latitude': shelf['latitude'],
                'longitude': shelf['longitude'],
            }
            if element not in locations:
                locations.append(element)

    return locations


def get_products():
    shelf_json = read_local_db()
    products = []

    for shelf in shelf_json.get("shelves", []):
        element = {
            'product_id': shelf['product_id'],
            'product_description': shelf['product_description'],
        }
        if element not in products:
            products.append(element)

    return products


def update_camera_status(id_shelf, status):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            shelf["camera_status"] = status
            break

    write_local_db(shelf_json)


def update_camera_ip(id_shelf, ip_address):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            shelf["camera_ip"] = ip_address
            break

    write_local_db(shelf_json)


def update_rfid_ip(id_shelf, ip_address):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            shelf["rfid_ip"] = ip_address
            break

    write_local_db(shelf_json)


def update_rfid_tag(id_shelf, status, tag):
    shelf_json = read_local_db()

    for shelf in shelf_json.get("shelves", []):
        if shelf["id"] == id_shelf:
            shelf["rfid_status"] = status
            shelf["rfid_last_tag"] = tag
            shelf["rfid_last_time_read"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            break

    write_local_db(shelf_json)


def update_local_db(id_shelf, qty):
    if qty == 1:
        increment_qty(id_shelf)
    elif qty == -1:
        decrement_qty(id_shelf)
    elif qty == 0:
        pass
    else:
        raise Exception("qty. other than +1 and -1")
