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
        'statvfs': os.statvfs('/')
    }

    return json.dumps(state_dict)

def makedirs(name, mode=0o777):
    ret = False
    s = ""
    comps = name.rstrip("/").split("/")[:-1]
    if comps[0] == "":
        s = "/"
    for c in comps:
        if s and s[-1] != "/":
            s += "/"
        s += c
        try:
            os.mkdir(s)
            ret = True
        except:
            pass
    return ret

def copy_file(from_path, to_path):
    with open(from_path, 'rb') as from_file:
        with open(to_path, 'wb') as to_file:
            CHUNK_SIZE = 256
            data = from_file.read(CHUNK_SIZE)
            while data:
                to_file.write(data)
                data = from_file.read(CHUNK_SIZE)
        to_file.close()
    from_file.close()

def copy_directory(from_path, to_path):
    for entry in os.ilistdir(from_path):
        if entry[1] == 0x4000:
            copy_directory(from_path + '/' + entry[0], to_path + '/' + entry[0])
        else:
            print(from_path, entry[0])
            copy_file(from_path + '/' + entry[0], to_path + '/' + entry[0])