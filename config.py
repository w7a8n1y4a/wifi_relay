import json

class BaseConfig:
    """ Config variables """
    
    WIFI_SSID = ''
    WIFI_PASS = ''
    PEPEUNIT_URL = ''
    PEPEUNIT_TOKEN = ''
    SYNC_ENCRYPT_KEY = ''
    SECRET_KEY = ''

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

with open('env.json', 'r') as f:
    jsonenv = json.loads(f.read())

settings = BaseConfig(**jsonenv)
