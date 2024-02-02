import sys
import traceback
import git
import json
import pandas as pd
from datetime import datetime
from flask import Flask, request, render_template
from OOP.FrameProcessing import FrameProcessing
from OOP.ShelfManager import get_shelf, update_rfid_tag, update_camera_status, update_camera_ip, update_rfid_ip, \
    update_local_db, read_local_db, get_location, get_products, get_locations
from OOP.UserRfidManager import get_user
from OOP.MovQtyManager import add_movement, read_local_db as read_mov_qty
from prophet.serialize import model_from_json

app = Flask(__name__)


@app.route('/', methods=["GET"])
def hello_world():
    return render_template('homepage.html', name="Home Page")


@app.route('/shelves', methods=["GET"])
def shelves():
    return render_template('shelves.html', name="Shelves")


@app.route('/history', methods=["GET"])
def history():
    return render_template('history.html', name="History")


@app.route('/homepage', methods=["GET"])
def homepage():
    return render_template('homepage.html', name="Homepage")


@app.route("/clone_repo", methods=["POST"])
def clone_repo():
    """Il metodo crea un endpoint da fornire a git hub affinchè possa gestire in
    autonomia le pull in arrivo sul branch di nostro interesse.
    I dati di configurazione sono gestiti all'interno del file Config/Git/PAT.json"""
    try:
        # salvo il nome delle variabili che servono per scaricare gli aggiornamenti
        branch_name, repo_name = "main", "BPR_IoT_Project"
        repo = git.Repo(f"../../")
        origin = repo.remotes.origin
        repo.create_head(f'{branch_name}',
                         origin.refs.main).set_tracking_branch(origin.refs.main).checkout()
        origin.pull()
        # conclusa la sincronizzazione con git hub ritorno un success
        return f"Sincronizzazione conclusa con successo", 200
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return f"Errore in fase di sincronizzazione con Git: {e}", 404


@app.route('/frame_processing', methods=["POST"])
def frame_processing():
    try:
        # read headers information
        camera_ip = request.headers.get("X-Camera-IP")
        rfid_ip = request.headers.get("X-Rfid-IP")
        shelf_id = request.headers.get("X-Shelf-ID")
        arcodart = request.headers.get("X-Item-ID")
        ardesart = request.headers.get("X-Item-Description")
        camera_ip = request.headers.get("X-Camera-IP")
        rfid_tag_value = request.headers.get("X-RFID-Tag")
        # define files structure
        files_dict_unstructured = dict(request.files.lists()) if request.files is not None and len(
            request.files) > 0 else []
        files_dict_structured = {}
        for file_dict in files_dict_unstructured:
            files_dict_structured[file_dict] = files_dict_unstructured[file_dict][0]
        fp = FrameProcessing(files_dict_structured, camera_ip=camera_ip)
        # detect content direction
        check, direction_msg = fp.detect_direction()
        if not check: raise Exception(direction_msg)
        update_local_db(shelf_id, direction_msg.get("qty", 0))
        user_dict = get_user(rfid_tag_value)
        mov = {
            "user_id": rfid_tag_value,
            "user_description": user_dict["description"],
            "shelf_id": shelf_id,
            "arcodart": arcodart,
            "ardesart": ardesart,
            "qty": direction_msg.get("qty", 0),
            "datetime": datetime.today().strftime('%d/%m/%Y %H:%M:%S')
        }
        add_movement(mov)
        return json.dumps({"direction": direction_msg, "user": user_dict}), 200
    except Exception as e:
        return json.dumps({"error": str(traceback.format_exc())}), 200


@app.route('/shelf_ref/<id>', methods=["GET"])
def shelf_ref(id):
    try:
        return json.dumps(get_shelf(id)), 200
    except Exception as e:
        return json.dumps({"error": str(e)}), 404


@app.route('/shelf/<id>/<dev_type>', methods=["POST"])
def shelf(id, dev_type):
    try:
        camera_ip = request.form.get("camera_ip", "0.0.0.0")
        camera_status = request.form.get("camera_status", 0)
        rfid_ip = request.form.get("rfid_ip", "0.0.0.0")
        rfid_status = request.form.get("rfid_status", 0)
        rfid_last_tag = request.form.get("rfid_last_tag", "")
        print(request.form, file=sys.stderr)
        if dev_type == "rfid":
            update_rfid_ip(id, rfid_ip)
            update_rfid_tag(id, rfid_status, rfid_last_tag)

        elif dev_type == "camera":
            update_camera_ip(id, camera_ip)
            update_camera_status(id, camera_status)

        return json.dumps(get_shelf(id)), 200
    except Exception as e:
        return json.dumps({"error": str(e)}), 404


@app.route('/shelves_dt', methods=["GET"])
def shelves_dt():
    json_raw = read_local_db()
    dt_cols = [
        {'data': 'product_id'},
        {'data': 'product_description'},
        {'data': 'qty'},
        {'data': 'location'}
    ]
    json_raw['cols'] = dt_cols
    return json_raw


@app.route('/history_dt', methods=["GET"])
def history_dt():
    json_raw = read_mov_qty()
    for el in json_raw.get("movements"):
        shelf_id = el.get("shelf_id")
        el['location'] = get_location(shelf_id)
    dt_cols = [
        {'data': 'datetime'},
        {'data': 'user_description'},
        {'data': 'shelf_id'},
        {'data': 'location'},
        {'data': 'arcodart'},
        {'data': 'ardesart'},
        {'data': 'qty'}
    ]
    json_raw['cols'] = dt_cols
    return json_raw


@app.route('/predict_shelf', methods=["POST"])
def predict_shelf():
    """
    shelf_id: id of the shelf to consider for the prediction
    datetime_str: datetime to predict for (%Y-%m-%d %H:%M:%S format)
    """
    m = None
    shelf_id, datetime_str = request.form.get("shelf_id"), request.form.get("datetime_str")
    with open(f'static/model/serialized_model_{shelf_id}.json', 'r') as fin:
        m = model_from_json(fin.read())
    future = pd.DataFrame([[datetime_str]], columns=['ds'])
    forecast = m.predict(future)
    output_ds = {"ds": forecast['ds'].iloc[0].strftime("%d/%m/%Y %H:%M:%S"),
                 "yhat": forecast['yhat'].iloc[0],
                 "yhat_lower": forecast['yhat_lower'].iloc[0],
                 "yhat_upper": forecast['yhat_upper'].iloc[0]
                 }
    return json.dumps(output_ds), 200


@app.route('/get_all_products', methods=["GET"])
def get_all_products():
    return json.dumps(get_products())


@app.route('/get_all_locations', methods=["POST"])
def get_all_locations():
    data = request.form.get("product_id")
    locations = get_locations(data)
    return json.dumps(locations)
