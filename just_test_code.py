from os import stat
import requests
url = "http://222.164.109.140:666/image.jpg"

try:
    status_code = requests.get(url, timeout=3)
except:
    status_code = "offline"
print(status_code)