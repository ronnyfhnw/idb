import json
import os
from flask import Flask
from flask import render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

with open("secrets.env", "r") as f:
    secrets = json.load(f)

url_ts_bulk = "https://api.thingspeak.com/channels/" + str(secrets['TS_ID']) + "/bulk_update.json"
global last_request_coffeeplant
last_request_coffeeplant  = datetime.now()
print(last_request_coffeeplant)

@app.route("/coffeeplant", methods=['POST'])
def coffeeplant():
    global last_request_coffeeplant
    data = request.get_json()

    assert 't' in data.keys()
    assert 'h' in data.keys()
    assert 'l' in data.keys()

    bulk_update = {
        "write_api_key": secrets['TS_KEY'],
        "updates": [{
                "created_at": datetime.now().isoformat(),
                "field1": data['t'],
                "field2": data['h'],
                "field3": data['l']
            }
        ]
    }

    if (datetime.now() - last_request_coffeeplant).total_seconds() > 60 * 5:
        try:
            response = requests.post(url_ts_bulk, json=bulk_update)
            print(response.status_code)
            resp = jsonify({'message': 'Data sent to Thingspeak'})
            resp.status_code = 200
            last_request_coffeeplant = datetime.now()
            return resp
            
        except RuntimeError as error:
            print(error)
    
    else:
        resp = jsonify({'message': 'Last request newer than 5 minutes ... '})
        resp.status_code = 401
        return resp



if __name__ == '__main__':
    app.run("0.0.0.0", port=5500, debug=True)