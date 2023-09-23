import uos
import binascii

from ucryptolib import aes

from config import settings


def aes_add_padding(data: str) -> str:
    return data+chr(16-len(data)%16)*(16-len(data)%16)


def aes_del_padding(data):
    return data[:-data[-1]]


def aes_encode(data: str) -> str:
    """
    data: any utf-8 str
    return: (base64 str - iv)."base64 str - encrypted data)
    """
    key = binascii.a2b_base64(settings.SYNC_ENCRYPT_KEY)
    iv = uos.urandom(16)

    MODE_CBC = 2
    aes_cipher = aes(key, MODE_CBC, iv)

    iv_base64_str = binascii.b2a_base64(iv).decode()

    return f'{iv_base64_str[:-1]}.{binascii.b2a_base64(aes_cipher.encrypt(aes_add_padding(data))).decode()}'


def aes_decode(data: str) -> str:
    """
    data: (base64 str - iv).base64 str - encrypted data)
    return: decode aes utf-8 str
    """
    key = binascii.a2b_base64(settings.SYNC_ENCRYPT_KEY)
    iv = binascii.a2b_base64(data.split('.')[0].encode())

    MODE_CBC = 2
    aes_cipher = aes(key, MODE_CBC, iv)

    return aes_del_padding(aes_cipher.decrypt(binascii.a2b_base64(data.split('.')[1].encode()))).decode('utf-8')
