import binascii
import json

def get_unit_uuid(token: str):
    return json.loads(binascii.a2b_base64(token.split('.')[1].encode() + b"=").decode('utf-8'))['uuid']
