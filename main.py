import time
import uos
import machine
import ubinascii
from umqtt.simple import MQTTClient

from config import settings
from utils.utils import get_unit_uuid

# Default MQTT MQTT_BROKER to connect to
TOPIC = b"test/co2"
TOPIC2 = b"test/bebra"


def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()
    

def main():
    mqttClient = MQTTClient(
        get_unit_uuid(settings.PEPEUNIT_TOKEN),
        settings.PEPEUNIT_URL,
        user=settings.PEPEUNIT_TOKEN.encode(),
        password=" ".encode(),
        keepalive=60
        )
    mqttClient.connect()
    print(f"Connected to MQTT  Broker :: {settings.PEPEUNIT_URL}")

    test = [
        'first',
        'two',
        'three',
        'four',
        'five',
        'six',
        'seven',
        'acht',
        'neun',
        'zein',
        'elf',
        'zwelf'
        'n_first',
        'n_two',
        'n_three',
        'n_four',
        'n_five',
        'n_six',
        'n_seven',
        'n_acht',
        'n_neun',
        'n_zein',
        'n_elf',
        'n_zwelf'
        ]

    while True:
        # time_true_pulse_us = machine.time_pulse_us(machine.Pin(15, machine.Pin.IN), 1000000)
        # print(time_true_pulse_us)
        # ppm = 2000 * (time_true_pulse_us/1000000)
        ppm = 3228
        random_temp = f'{time.ticks_ms()} - ppm - {str(ppm)}'
        print(f"millis - {time.ticks_ms()} - ppm - {str(ppm)}")

        for item in range(0, 1):
            mqttClient.publish(f'test/{test[item]}'.encode(), str(random_temp).encode())
        
    mqttClient.disconnect()
    
    
if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("Error: " + str(e))
        reset()