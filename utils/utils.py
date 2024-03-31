import binascii
import json

def get_unit_uuid(token: str):
    data = token.split('.')[1].encode()
    return json.loads(binascii.a2b_base64(data + (len(data) % 4) * b'=').decode('utf-8'))['uuid']
