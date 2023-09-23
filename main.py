from ucryptolib import aes
from config import settings
import uos

def pad(m):
    return m+chr(16-len(m)%16)*(16-len(m)%16)

key = b'\xfb\xd0%T\xa8bn*:\xf0\xed\xe6\xb8}\xe5e\x86{#\xe80\xf7\xb4\xc1\x03/9]NKf\xcd'
iv = b'\xb4f\xd6~\x1eA\xfca\xcf\x93\xca\xe0z;\x88\r'

print(key, iv)

MODE_CBC = 2
cipher = aes(key, MODE_CBC, iv)

plain = "Text and text wtf. w7a8n1y4a Text and text wtf. w7a8n1y4aText and text wtf. w7a8n1y4a"
print(len(plain))
plain = pad(plain)
encrypted = cipher.encrypt(plain)
print(f"{str(encrypted)}")
  
decipher = aes(key, MODE_CBC, iv)
decrypted = decipher.decrypt(encrypted)
print(f"{decrypted.strip()}")
