import json
from datetime import datetime

json_db_path = "static/local_db/mov_qty_new.json"


def read_local_db() -> dict:
    with open(json_db_path, "r") as f:
        mov_qty_json = json.load(f)
    f.close()
    return mov_qty_json


def write_local_db(mov_qty_json):
    with open(json_db_path, "w") as f:
        json.dump(mov_qty_json, f, indent=4)
    f.close()


def add_movement(mov):
    """
    Method allows adding (appending data passed as parameter) a new movement to mov_qty.json.

    Parameters
    ----------
    mov
        Movements to add.
        Param structure should be the following:

        >>> {
        >>>     "user_id": "351952216",
        >>>     "user_description": "Paolo Ristori",
        >>>     "shelf_id": "A0001",
        >>>     "arcodart": "AA000AA",
        >>>     "ardesart": "latte intero",
        >>>     "qty": "1",
        >>>     "datetime": "dd/mm/YYYY H:M:S"
        >>> }
    """
    mov_qty_json: dict = read_local_db()
    mov_qty_json["movements"].append(mov)
    write_local_db(mov_qty_json)


def get_mov(user_id, arcodart, datetime):
    """
    Method finds and returns a specific movement.
    A movement is identified by tuple (user_id, arcodart, datetime).
    """
    if user_id is None or arcodart is None or datetime is None:
        raise Exception(f"ERROR: 3 parameters are expected and none of them should be None, given: {user_id, arcodart, datetime}")

    mov_qty_json = read_local_db()
    for mov in mov_qty_json.get("movements", []):
        if mov["rfid_id"] == user_id and mov["arcodart"] == arcodart and mov["datetime"] == datetime:
            return mov
    raise Exception(f"Movement by user {user_id} on {datetime} for product {arcodart} not found")


def get_mov_by_user_id(user_id):
    mov_qty_json = read_local_db()
    movs = []
    for mov in mov_qty_json:
        if mov["user_id"] == user_id:
            movs.append(mov)
    return movs
