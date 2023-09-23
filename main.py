from utils.aes import aes_encode, aes_decode

from config import settings

text = "One two three four five six seven aht neun zein elf zwoelf"

print(text)
cypher = aes_encode(text)
print(cypher)
decrypt = aes_decode(cypher)
print(decrypt)
