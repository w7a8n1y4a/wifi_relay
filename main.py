import io
import time
import os
import machine
import mrequests
import shutil
import json

from lib.mqtt.simple import MQTTClient

from utils.utils import *
from utils.update import *
from config import settings

def reset():
    print("I'll be back")
    time.sleep(5)
    machine.reset()
    
def sub_callback(topic, state):
    
    struct_topic = get_topic_split(topic.decode())

    print(struct_topic)
    
    if len(struct_topic) == 5:
        backend_domain, destination, unit_uuid, topic_name, *_ = struct_topic
        
        if destination == 'input_base_topic' and topic_name == 'update':

            new_version = json.loads(state.decode())['NEW_COMMIT_VERSION']
            if settings.COMMIT_VERSION != new_version:
                mqttClient.disconnect()
                gc.collect()

                headers = {
                    'accept': 'application/json',
                    'x-auth-token': settings.PEPEUNIT_TOKEN
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
                
        if destination == 'input_base_topic' and topic_name == 'schema_update':

            headers = {
                'accept': 'application/json',
                'x-auth-token': settings.PEPEUNIT_TOKEN
            }

            url = f'http://{settings.PEPEUNIT_URL}/pepeunit/api/v1/units/get_current_schema/{get_unit_uuid(settings.PEPEUNIT_TOKEN)}'
            
            r = mrequests.get(url=url, headers=headers)

            filepath = f'/schema.json'
            if r.status_code == 200:
                r.save(filepath, buf=bytearray(256))
            r.close()
            
            with open(filepath, 'r') as f:
                schema_dict = json.loads(json.loads(f.read()))
            
            with open(filepath, 'w') as f:
                f.write(json.dumps(schema_dict))
            
            print('schema is updated')
            gc.collect()
            
            reset()
    
    elif len(struct_topic) == 3:
        schema_dict = get_unit_schema()
        topic_type, topic_name = search_topic_in_schema(schema_dict, struct_topic[1])
    
        if topic_type == 'input_topic' and topic_name == 'set_relay_state/pepeunit':
            
            print(state.decode())
            
            relay_pin = machine.Pin(5, machine.Pin.OUT)
            try:
                relay_state_value = int(state.decode())
            except:
                relay_state_value = 0
                
            relay_pin(relay_state_value)
                
            for output_topic in schema_dict['output_topic']['current_relay_state/pepeunit']:
                print('set_state', relay_state_value)
                mqttClient.publish(output_topic, str(relay_state_value))
                    
def main():

    unit_uuid = get_unit_uuid(settings.PEPEUNIT_TOKEN)

    global mqttClient

    gc.collect()

    print(settings.PEPEUNIT_TOKEN)
    
    mqttClient = MQTTClient(
        unit_uuid,
        settings.MQTT_URL,
        user=settings.PEPEUNIT_TOKEN,
        password="",
        keepalive=60,
    )

    mqttClient.set_callback(sub_callback)
    mqttClient.connect()

    schema_dict = get_unit_schema()
    
    print(schema_dict)

    for input_topic in schema_dict['input_topic']['set_relay_state/pepeunit']:
        print(input_topic)
        mqttClient.subscribe(input_topic)
    
    for input_topic in schema_dict['input_base_topic']['update/pepeunit']:
        print(input_topic)
        mqttClient.subscribe(input_topic)
        
    for input_topic in schema_dict['input_base_topic']['schema_update/pepeunit']:
        print(input_topic)
        mqttClient.subscribe(input_topic)

    print(f"Connected to MQTT  Broker :: {settings.MQTT_URL}")
    
    last_state_pub = time.time()
    last_ping = time.time()
    while True:
        mqttClient.check_msg()

        if (time.time() - last_state_pub) >= settings.STATE_SEND_INTERVAL:
            for output_topic in schema_dict['output_base_topic']['state/pepeunit']:
                mqttClient.publish(
                    output_topic,
                    get_unit_state(sta_if.ifconfig(), settings)
                )
            last_state_pub = time.time()

        if (time.time() - last_ping) >= settings.PING_INTERVAL:
            mqttClient.ping()
            last_ping = time.time()

    mqttClient.disconnect()
    
    
if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("Error: " + str(e))
        reset()
