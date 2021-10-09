# config.py Local configuration for mqtt_as demo programs.
from secrets import wifi_PSK, wifi_SSID

from mqtt_as import config

config["server"] = "voyage.lan"

# Not needed if you're only using ESP8266
config["ssid"] = wifi_SSID
config["wifi_pw"] = wifi_PSK
