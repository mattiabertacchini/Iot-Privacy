import json
import random
import numpy as np
from datetime import datetime
from datetime import timedelta



MOV_DB_PATH = "CloudApplication/static/local_db/mov_qty_new.json"
SHELF_DB_PATH = "CloudApplication/static/local_db/shelf_new.json"
SHELVES_STRUCT = [
    {
        "description": "CONAD C.C. La Rotonda",
        "shelves": [
                {"id": "A0001", "product_id": "AA000AC", "product_description": "Mozzarelle"},
                {"id": "A0002", "product_id": "AA000AE", "product_description": "Gorgonzola"},
                {"id": "A0003", "product_id": "AA000CD", "product_description": "Passata di pomodoro"}
            ]
    },
    {
        "description": "CONAD CITY",
        "shelves": [
                {"id": "B0002", "product_id": "AA000AD", "product_description": "Stracchino"},
                {"id": "B0001", "product_id": "AA000AC", "product_description": "Mozzarelle"},
                {"id": "B0003", "product_id": "AA000CD", "product_description": "Passata di pomodoro"},
                {"id": "B0004", "product_id": "AA000AE", "product_description": "Gorgonzola"}
            ]
     },
    {
        "description": "CONAD CITY Aeronautica",
        "shelves": [
            {"id": "C0001", "product_id": "AA000CD", "product_description": "Passata di pomodoro"},
            {"id": "C0002", "product_id": "AA000AE", "product_description": "Gorgonzola"},
            {"id": "C0003", "product_id": "AA000AD", "product_description": "Stracchino"}
        ]
    },
    {
        "description": "CONAD CITY Le torri",
        "shelves": [
            {"id": "D0001", "product_id": "AA000AD", "product_description": "Stracchino"}
        ]
    },
    {
        "description": "CONAD CITY Polo Leonardo",
        "shelves": [
            {"id": "E0001", "product_id": "AA000CD", "product_description": "Passata di pomodoro"},
        ]
    }
]
USER_STRUCT = [
    {"id": "351952216", "description": "Paolo Ristori"},
    {"id": "351952217", "description": "Alessandro Pansera"},
    {"id": "351952218", "description": "Mattia Bertacchini"}
]


# creo 2 liste con 720 numeri random in maniera uniforme
#
# suddivido in range da 0-0.2/0.21-0.40/0.41-0.60/0.61-0.8/0.81-1 per selezionare il super-mercato
# suddivido in range da 0-0.33/0.34-0.66/0.67-1 per selezionare l'utente
# dinamicamente scelgo dei numeri casuali da 0 a len(shelves) per scegliere il prodotto d'interesse

# per fare una cosa fatta bene è necessario che si aggiornino correttamente i dati legati alle
# giacenze oltre che alle movimentazioni

shelves_list = np.random.uniform(0, 1, 720)
user_list = np.random.uniform(0, 1, 720)
shelves_list_integer = []
user_list_integer = []
product_list_integer = []

print("Generating shelves...")
for el in shelves_list:
    if 0 <= el < 0.20: shelves_list_integer.append(0)
    elif 0.20 <= el < 0.40: shelves_list_integer.append(1)
    elif 0.40 <= el < 0.60: shelves_list_integer.append(2)
    elif 0.60 <= el < 0.80: shelves_list_integer.append(3)
    else: shelves_list_integer.append(4)

print("Generating user for movements...")
for el in user_list:
    if 0 <= el < 0.33: user_list_integer.append(0)
    elif 0.33 <= el < 0.66: user_list_integer.append(1)
    else: user_list_integer.append(2)

print("Generating shelves item...")
for shelf_index in shelves_list_integer:
    n_child = len(SHELVES_STRUCT[shelf_index]["shelves"])
    random_child_index = random.randint(0, n_child-1)
    product_list_integer.append(random_child_index)

# creazione di 720 datetime, suddivisi in 12 mesi diversi
print("Building dates...")
datetime_list = []
for month_offset in range(0, 12):
    for i in range(0, 60):
        start_date = datetime.now() + timedelta(days=30*(month_offset))
        end_date = start_date + timedelta(days=30)
        random_date = start_date + (end_date - start_date) * random.random()
        random_date_string = random_date.strftime("%d/%m/%Y %H:%M:%S")
        datetime_list.append(random_date_string)

print("Building qty...")
qty_list = []
for i in range(0, 720):
    # -1 is more likely to realize than +1
    qty = int(np.random.choice([-1, 1], 1, p=[0.7, 0.3])[0])
    qty_list.append(qty)


print("Building dictionary to write...")
dict_list = []
for i in range(0, 720):
    mov_dict = {
        "user_id": USER_STRUCT[user_list_integer[i]]["id"],
        "user_description": USER_STRUCT[user_list_integer[i]]["description"],
        "shelf_id": SHELVES_STRUCT[shelves_list_integer[i]]["shelves"][product_list_integer[i]]["id"],
        "arcodart": SHELVES_STRUCT[shelves_list_integer[i]]["shelves"][product_list_integer[i]]["product_id"],
        "ardesart": SHELVES_STRUCT[shelves_list_integer[i]]["shelves"][product_list_integer[i]]["product_description"],
        "qty": qty_list[i],
        "datetime": datetime_list[i]
    }
    dict_list.append(mov_dict)

print("Reading existing movements...")
existing_mov = []
with open(MOV_DB_PATH, "r") as f:
    file_content = json.load(f)
    existing_mov = file_content.get("movements", [])


print("Adding new movements...")
existing_mov.extend(dict_list)
with open(MOV_DB_PATH, "w") as f:
    new_json = {"movements": existing_mov}
    json.dump(new_json, f, indent=4)


print("Reconstruction of qty considering new movements...")
for el in dict_list:
    shelf_id, qty = el["shelf_id"], el["qty"]
    shelves_old = []

    with open(SHELF_DB_PATH) as json_file:
        shelves_old = json.load(json_file).get("shelves", [])

    for el in shelves_old:
        if el.get("id")==shelf_id:
            el["qty"]+=qty

    with open(SHELF_DB_PATH, "w") as json_file:
        json.dump({"shelves": shelves_old}, json_file, indent=4)



exit(1)

