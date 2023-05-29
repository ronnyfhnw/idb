from datetime import datetime
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger
import time
import json
import requests

sonar = GroveUltrasonicRanger(5) # pin12, slot D12
print(sonar.get_distance())

with open("/home/rsb/idb/raspberry/secrets.env", "r") as f:
    secrets = json.load(f)

url_ts_bulk = "https://api.thingspeak.com/channels/" + str(secrets['TS_DESK_ID']) + "/bulk_update.json"
last_request = datetime.now()

while True:
    try:
        if (datetime.now() - last_request).total_seconds() > 5 * 60:
            bulk_update = {
                    "write_api_key": secrets['TS_DESK_KEY'],
                    "updates": [{
                            "created_at": datetime.now().isoformat(),
                            "field1": sonar.get_distance()
                        }
                    ]
                }

            response = requests.post(url_ts_bulk, json=bulk_update)
            last_request = datetime.now()
            print(response)
    except RuntimeError as error:
           print(error)
