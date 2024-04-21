import time
import uos
import machine
import ubinascii
from umqtt.simple import MQTTClient

from config import settings
from utils.utils import get_unit_uuid, get_unit_topics, get_unit_state

def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()
    
def sub_cb(topic, msg):
    print((topic, msg))

def main():

    unit_uuid = get_unit_uuid(settings.PEPEUNIT_TOKEN)

    mqttClient = MQTTClient(
        unit_uuid,
        settings.PEPEUNIT_URL,
        user=settings.PEPEUNIT_TOKEN.encode(),
        password=" ".encode(),
        keepalive=60
    )
    mqttClient.set_callback(sub_cb)
    mqttClient.connect()

    unit_topics = get_unit_topics()

    for input_topic in unit_topics['input_topic']:
        mqttClient.subscribe(f'input/{unit_uuid}/{input_topic}')
    
    for input_topic in unit_topics['input_base_topic']:
        mqttClient.subscribe(f'input_base/{unit_uuid}/{input_topic}')

    print(f"Connected to MQTT  Broker :: {settings.PEPEUNIT_URL}")
    
    last_state_pub = time.time()
    last_ping = time.time()
    while True:
        # time_true_pulse_us = machine.time_pulse_us(machine.Pin(15, machine.Pin.IN), 1000000)
        # ppm = 2000 * (time_true_pulse_us/1000000)
        # print(time_true_pulse_us)

        ppm = 3228
        random_temp = f'{time.ticks_ms()//10000} - ppm - {str(ppm)}'
        print(f"millis - {time.ticks_ms()//10000} - ppm - {str(ppm)}")
        
        for item in range(0, 1):
            mqttClient.publish(f'output/{unit_uuid}/{unit_topics['output_topic'][0]}'.encode(), str(random_temp).encode())
        
        mqttClient.check_msg()

        if (time.time() - last_state_pub) >= settings.STATE_SEND_INTERVAL:
            mqttClient.publish(
                f'output_base/{unit_uuid}/{unit_topics['output_base_topic'][0]}'.encode(),
                get_unit_state(sta_if.ifconfig()).encode()
            )
            last_state_pub = time.time()

        if (time.time() - last_ping) >= settings.PING_INTERVAL:
            mqttClient.ping()
            last_ping = time.time()

        time.sleep(1)

    mqttClient.disconnect()
    
    
if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("Error: " + str(e))
        reset()