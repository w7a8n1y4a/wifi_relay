from ucryptolib import aes
from config import settings
import uos

key = b'\xe1\xac<p\xaa.\x15\x03\x16\xa9\x1fq\x98Lw:\xa3;\xdb\x04\xb6\x8d*\xc3\x8e\xd5(\xfd\x17\xcbP$'
iv = b'!\xb2>\\^\xb0Q\xf7\x87\x93\x02\xc2\x8b\xc3\xb5y'

print(key, iv)

MODE_CBC = 2
cipher = aes(key, MODE_CBC, iv)

plain = "Text and text wtf. w7a8n1y4a"
print(plain)

padded = plain + " " * (16 - len(plain) % 16)
print(len(padded))
encrypted = cipher.encrypt(padded)
print(f"{str(encrypted)}")
  
decipher = aes(key, MODE_CBC, iv)
decrypted = decipher.decrypt(encrypted)
print(f"{decrypted.strip()}")
