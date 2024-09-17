import gc
import os
import time
import binascii
import json
import machine
import esp

def get_unit_uuid(token: str):
    data = token.split('.')[1].encode()
    return json.loads(binascii.a2b_base64(data + (len(data) % 4) * b'=').decode('utf-8'))['uuid']

def get_unit_schema():
    with open('schema.json', 'r') as f:
        return json.loads(f.read())

def get_unit_state(ifconfig, settings):

    gc.collect()
    
    state_dict = {
        'ifconfig': ifconfig,
        'millis': time.ticks_ms(),
        'mem_free': gc.mem_free(),
        'mem_alloc': gc.mem_alloc(),
        'freq': machine.freq(),
        'statvfs': os.statvfs('/'),
        'commit_version': settings.COMMIT_VERSION
    }

    return json.dumps(state_dict)

def get_topic_split(topic):
    return tuple(topic.split('/'))

def search_topic_in_schema(schema_dict: dict, node_uuid: str) -> tuple[str, str]:

    for topic_type in schema_dict.keys():
        for topic_name in schema_dict[topic_type].keys():
            for topic in schema_dict[topic_type][topic_name]:
                if topic.find(node_uuid) >= 0:
                    return (topic_type, topic_name)

    raise ValueError
