import gc
import time
import binascii
import json
import machine
import esp

def get_unit_uuid(token: str):
    data = token.split('.')[1].encode()
    return json.loads(binascii.a2b_base64(data + (len(data) % 4) * b'=').decode('utf-8'))['uuid']

def get_unit_topics():
    with open('schema.json', 'r') as f:
        return json.loads(f.read())

def get_unit_state(ifconfig):

    gc.collect()
    
    state_dict = {
        'ifconfig': ifconfig,
        'millis': time.ticks_ms(),
        'mem_free': gc.mem_free(),
        'mem_alloc': gc.mem_alloc(),
        'freq': machine.freq(),
        'flash_size': esp.flash_size()
    }

    return json.dumps(state_dict)
