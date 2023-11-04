import time
import uos
import machine
import ubinascii
from umqtt.simple import MQTTClient

from config import settings

# Default MQTT MQTT_BROKER to connect to
SERVER = settings.PEPEUNIT_URL
CLIENT_ID = b'test'
print(CLIENT_ID)

TOPIC = b"co2"


def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()
    

def main():
    mqttClient = MQTTClient(CLIENT_ID, SERVER, user='1234124'.encode(), password='23423423'.encode(), keepalive=60)
    mqttClient.connect()
    print(f"Connected to MQTT  Broker :: {SERVER}")

    while True:
        time_true_pulse_us = machine.time_pulse_us(machine.Pin(15, machine.Pin.IN), 1000000)
        print(time_true_pulse_us)
        ppm = 2000 * (time_true_pulse_us/1000000)
        random_temp = f'{time.ticks_ms()} - ppm - {str(ppm)}'
        print(f"millis - {time.ticks_ms()} - ppm - {str(ppm)}")
        mqttClient.publish(TOPIC, str(random_temp).encode())
        time.sleep(5.123)
    mqttClient.disconnect()
    
    
if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("Error: " + str(e))
        reset()