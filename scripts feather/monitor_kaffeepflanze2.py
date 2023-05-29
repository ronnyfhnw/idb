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
WIFI_SSID = "5G"
WIFI_PASSWORD = "QyWxEcRvTb1928!"

# variables
tmp_values = []
wifi_connection = False
last_timestamp = time.monotonic()
time.sleep(3)
print(last_timestamp - time.monotonic())

# http client
adafruit_requests.set_socket(adafruit_esp32spi_socket, esp)

while esp.is_connected == False:
    print("\nConnecting to Wi-Fi...")
    try:
        esp.connect_AP(WIFI_SSID, WIFI_PASSWORD)
        print("connected to wifi")

    except ConnectionError as e:
        print("Cannot connect to Wi-Fi", e)

while True:
    if last_timestamp - time.monotonic() > 30:
        if esp.is_connected:
            temperature = int(round(dht.temperature))
            humidity = int(round(dht.humidity))
            light_value = light_sensor.value
            bulk_update = {
                        "t": temperature,
                        "h": humidity,
                        "l": light_value
                    }
            response = adafruit_requests.post("http://raspberry.local:5500/coffeeplant", json=bulk_update).json()
            print(response)

