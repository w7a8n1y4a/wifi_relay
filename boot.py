import network
from config import settings

sta_if = network.WLAN(network.STA_IF)

if not sta_if.isconnected():
    sta_if.active(True)
    sta_if.connect(settings.WIFI_SSID, settings.WIFI_PASS)
    print(settings.WIFI_SSID, settings.WIFI_PASS)
    while not sta_if.isconnected():
        pass

print('network config:', sta_if.ifconfig())