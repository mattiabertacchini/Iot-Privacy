import pandas as pd
import json
import matplotlib.pyplot as plt
from prophet import Prophet
from prophet.serialize import model_to_json
from datetime import datetime

# https://facebook.github.io/prophet/docs/quick_start.html
MOV_DB_PATH = "CloudApplication/static/local_db/mov_qty_new.json"
SHELF_DB_PATH = "CloudApplication/static/local_db/shelf_new.json"
mov_json = None
shelf_json = None
with open(MOV_DB_PATH) as f:
    mov_json = json.load(f)
with open(SHELF_DB_PATH) as f:
    shelf_json = json.load(f)
# define a model for each shelf_id
models = {}
mov_shelf = {}
initial_qty = {}
print("Initializing data structure...")
for shelf in shelf_json.get("shelves", []):
    mov_shelf[shelf.get("id")] = []
    initial_qty[shelf.get("id")] = 10000 #shelf.get("qty")

# add for each move all related movements
movements_sorted = sorted(mov_json.get("movements", []),
    key=lambda k: datetime.strptime(k['datetime'], '%d/%m/%Y %H:%M:%S'),
    reverse=False
)
print("Adding sorted movements to each shelf...")
for index, mov in enumerate(movements_sorted):
    mov_with_balance = mov
    mov_with_balance["balance"] = initial_qty[mov.get("shelf_id")]+mov.get("qty") if len(mov_shelf[mov.get("shelf_id")]) == 0 \
        else mov_shelf[mov.get("shelf_id")][len(mov_shelf[mov.get("shelf_id")])-1]["balance"]+mov.get("qty")
    mov_shelf[mov.get("shelf_id")].append(mov_with_balance)


# reconstruct balance at each time before and after qty variation
# Load the data
df = {}
for key in mov_shelf:
    df[key] = pd.DataFrame(mov_shelf[key])
    df[key] = df[key][['datetime', 'balance']]
    df[key]['datetime'] = pd.to_datetime(df[key]['datetime'], format="%d/%m/%Y %H:%M:%S").dt.strftime('%Y-%m-%d %H:%M:%S')
# debug dataframe and check required cols
# datetime format:
# YYYY-MM-DD HH:MM:SS
# load data from json file and convert datetime cols format
for key in df:
    print(f"Training shelf '{key}' models...")
    m = Prophet()
    df[key] = df[key].rename(columns={"datetime": "ds", "balance": "y"})
    m.fit(df[key])
    models[key] = m
    # serialize model to output
    with open(f'CloudApplication/static/model/serialized_model_{key}.json', 'w') as fout:
        fout.write(model_to_json(m))  # Save model
exit(1)