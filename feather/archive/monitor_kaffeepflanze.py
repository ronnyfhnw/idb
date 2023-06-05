import analogio
import digitalio
import busio
import board
import time
from adafruit_datetime import datetime, timedelta
import adafruit_dht
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_socket
import adafruit_requests

# setup pins and wifi
light_sensor = analogio.AnalogIn(board.A2)
dht = adafruit_dht.DHT11(board.D9)
cs = digitalio.DigitalInOut(board.D13)
rdy = digitalio.DigitalInOut(board.D11)
rst = digitalio.DigitalInOut(board.D12)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, cs, rdy, rst)

# wifi connection
WIFI_SSID = ""
WIFI_PASSWORD = ""

# thingspeak
thingspeak_key = "I1ZMQYLB4J7K5F9J"
channel_id = 2153671
thingspeak_bulkupdate = "https://api.thingspeak.com/channels/" + str(channel_id) + "/bulk_update.json"

# variables
tmp_values = []
wifi_connection = False
last_timestamp = None


day_mapping = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
}

# http client
adafruit_requests.set_socket(adafruit_esp32spi_socket, esp)

print("\nConnecting to Wi-Fi...")
try:
    esp.connect_AP(WIFI_SSID, WIFI_PASSWORD)
    wifi_connection = True
    print("connected to wifi")

except ConnectionError as e:
    print("Cannot connect to Wi-Fi", e)

while True:
    if datetime.now().minute % 29 == 0 and datetime.now().minute != 0:
        if esp.is_connected:
            response = adafruit_requests.get("https://timeapi.io/api/Time/current/zone?timeZone=Europe/Zurich").json()
            last_timestamp = time.struct_time([int(response['year']), int(response['month']), int(response['day']), int(response['hour']), int(response['minute']), int(response['seconds']), day_mapping[response['dayOfWeek']], -1, -1])
            last_timestamp = time.mktime(last_timestamp)
            temperature = int(round(dht.temperature))
            humidity = int(round(dht.humidity))
            light_value = light_sensor.value
            print("sending request")
            bulk_update = {
                "write_api_key": thingspeak_key,
                "updates": [{
                        "created_at": datetime.fromtimestamp(last_timestamp).isoformat(),
                        "field1": temperature,
                        "field2": humidity,
                        "field3": light_value
                    }
                ]
            }

            try:
                response = adafruit_requests.post(thingspeak_bulkupdate, json=bulk_update)
                print(response.status_code)

            except RuntimeError as error:
                print(error)
        else:
            try:
                esp.connect_AP(WIFI_SSID, WIFI_PASSWORD)
                wifi_connection = True
                print("connected to wifi")


                # write tmp values to thingspeak
                for i, value in enumerate(tmp_values):
                    # append new value in case uploading takes longer
                    if datetime.now().minute % 29 == 0 and datetime.now().minute != 0:
                        response = adafruit_requests.get("https://timeapi.io/api/Time/current/zone?timeZone=Europe/Zurich").json()
                        last_timestamp = time.struct_time([int(response['year']), int(response['month']), int(response['day']), int(response['hour']), int(response['minute']), int(response['seconds']), day_mapping[response['dayOfWeek']], -1, -1])
                        last_timestamp = time.mktime(last_timestamp)
                        temperature = int(round(dht.temperature))
                        humidity = int(round(dht.humidity))
                        light_value = light_sensor.value

                        tmp_values.append({
                            "write_api_key": thingspeak_key,
                            "updates": [{
                                    "created_at": datetime.fromtimestamp(last_timestamp).isoformat(),
                                    "field1": temperature,
                                    "field2": humidity,
                                    "field3": light_value
                                }
                            ]
                        })
                        print("appended value to array")

                    response = adafruit_requests.post(thingspeak_bulkupdate, json=value)
                    print(response.status_code)
                    print("sent request, sleeping for 15s to stay within api limitations...")
                    time.sleep(15)

                tmp_values = []

            except ConnectionError as e:
                print("Cannot connect to Wi-Fi", e)

                # append to tmp
                temperature = int(round(dht.temperature))
                humidity = int(round(dht.humidity))
                light_value = light_sensor.value

                last_timestamp = last_timestamp + 30 * 60

                tmp_values.append({
                    "write_api_key": thingspeak_key,
                    "updates": [{
                            "created_at": datetime.fromtimestamp(last_timestamp).isoformat(),
                            "field1": temperature,
                            "field2": humidity,
                            "field3": light_value
                        }
                    ]
                })
                print("appended values")
