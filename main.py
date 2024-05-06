import io
import time
import os
import machine
import mrequests
import shutil

from lib.mqtt.simple import MQTTClient

from utils.utils import *
from utils.update import *
from config import settings

def reset():
    print("I'll be back")
    time.sleep(5)
    machine.reset()
    
def sub_callback(topic, state):

    backend_domain, destination, unit_uuid, topic_name = get_topic_split(topic.decode())

    print(state)

    if destination == 'input_base' and topic_name == 'update':

        new_version = json.loads(state.decode())['NEW_COMMIT_VERSION']
        if settings.COMMIT_VERSION != new_version:
            mqttClient.disconnect()
            gc.collect()

            headers = {
                'accept': 'application/json',
                'x-auth-token': settings.PEPEUNIT_TOKEN.encode()
            }

            url = f'http://{settings.PEPEUNIT_URL}/pepeunit/api/v1/units/firmware/tgz/{get_unit_uuid(settings.PEPEUNIT_TOKEN)}?wbits=9&level=9'
            
            r = mrequests.get(url=url, headers=headers)

            filepath = f'/tmp/update.tgz'
            if r.status_code == 200:
                r.save(filepath, buf=bytearray(256))

            r.close()
            
            tmp_update_path = '/update'
            unpack_tgz(filepath, tmp_update_path)
            os.remove(filepath)
            
            copy_directory(tmp_update_path, '')
            shutil.rmtree(tmp_update_path)

            reset()

def main():

    unit_uuid = get_unit_uuid(settings.PEPEUNIT_TOKEN)

    global mqttClient

    gc.collect()

    mqttClient = MQTTClient(
        unit_uuid,
        settings.MQTT_URL,
        user=settings.PEPEUNIT_TOKEN.encode(),
        password=" ".encode(),
        keepalive=60,
        ssl=True
    )

    mqttClient.set_callback(sub_callback)
    mqttClient.connect()

    unit_topics = get_unit_topics()

    for input_topic in unit_topics['input_topic']:
        mqttClient.subscribe(f'{settings.PEPEUNIT_URL}/input/{unit_uuid}/{input_topic}')
    
    for input_topic in unit_topics['input_base_topic']:
        mqttClient.subscribe(f'{settings.PEPEUNIT_URL}/input_base/{unit_uuid}/{input_topic}')

    print(f"Connected to MQTT  Broker :: {settings.MQTT_URL}")
    
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
            mqttClient.publish(f'{settings.PEPEUNIT_URL}/output/{unit_uuid}/{unit_topics['output_topic'][0]}'.encode(), str(random_temp).encode())
        
        mqttClient.check_msg()

        if (time.time() - last_state_pub) >= settings.STATE_SEND_INTERVAL:
            mqttClient.publish(
                f'{settings.PEPEUNIT_URL}/output_base/{unit_uuid}/{unit_topics['output_base_topic'][0]}'.encode(),
                get_unit_state(sta_if.ifconfig(), settings).encode()
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
