import io
import time
import uos
import machine
import ubinascii
import mrequests
import tarfile
import deflate
import shutil

from lib.simple import MQTTClient

from utils.utils import *

from config import settings
from utils.utils import get_unit_uuid, get_unit_topics, get_unit_state, copy_directory, makedirs

def reset():
    print("I'll be back")
    time.sleep(5)
    machine.reset()
    
def sub_cb(topic, msg):

    print((topic, msg))

    mqttClient.disconnect()
    gc.collect()

    headers = {
        'accept': 'application/json',
        'token': settings.PEPEUNIT_TOKEN.encode()
    }

    url = f'{settings.PEPEUNIT_URL}/pepeunit/api/v1/units/firmware/tgz/{get_unit_uuid(settings.PEPEUNIT_TOKEN)}'
    
    print('start')

    r = mrequests.get(url=url, headers=headers)

    filename = 'update.tgz'
    filepath = f'/tmp/{filename}'

    print(filepath)

    if r.status_code == 200:
        r.save(filepath, buf=bytearray(256))
        print(f".tgz saved to {filepath}")
    else:
        print(f"Request failed. Status: {r.status_code}")

    r.close()
    
    tmp_update_path = '/update/'
    os.mkdir(tmp_update_path[:-1])
    with open(filepath, 'rb') as tgz:

        tar_file = deflate.DeflateIO(tgz, deflate.AUTO, 9)
        unpack_tar = tarfile.TarFile(fileobj=tar_file)
        
        print('start save files')
        
        for unpack_file in unpack_tar:

            print(unpack_file.size, unpack_file.name, unpack_file.type)

            if unpack_file.type != tarfile.DIRTYPE and not '@PaxHeader' in unpack_file.name:

                out_filepath = tmp_update_path + unpack_file.name[2:]

                print(out_filepath)

                makedirs(out_filepath)

                subf = unpack_tar.extractfile(unpack_file)

                with open(out_filepath, "wb") as outf:
                    
                    shutil.copyfileobj(subf, outf)

                    outf.close()

    os.remove(filepath)
    
    copy_directory('/update', '')

    shutil.rmtree('/update')

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

    mqttClient.set_callback(sub_cb)
    mqttClient.connect()

    print(gc.mem_free(), gc.mem_alloc())

    unit_topics = get_unit_topics()

    for input_topic in unit_topics['input_topic']:
        mqttClient.subscribe(f'input/{unit_uuid}/{input_topic}')
    
    for input_topic in unit_topics['input_base_topic']:
        mqttClient.subscribe(f'input_base/{unit_uuid}/{input_topic}')

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
