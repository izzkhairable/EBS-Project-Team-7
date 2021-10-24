import requests
import time
from genericpath import getmtime
from imgurpython import ImgurClient
import datetime
import os
import shutil


def main():
    client_id = '3ef4beacee8d63c'
    client_secret = '75640200bd814140c1e10fe3bd95ed65e9dd490d'
    access_token = '8a06c8a86ac3ef93546cff4ea2cb42956cd60cf4'
    refresh_token = '7e64f091f020ffc5486e9b6f8f97ce9b8ed2ad6e'
    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    try:
        response = requests.get(
            'http://222.164.109.140:666/image.jpg', timeout=1)
        file = open(os.path.dirname(os.path.abspath(__file__)) + "/static/image/image.png", "wb")
        file.write(response.content)
        file.close()
        client.upload_from_path(os.path.dirname(os.path.abspath(__file__)) + "/static/image/image.png", anon=False, config={'title':str(datetime.datetime.now())}) 
    except:
        print(os.path.dirname(os.path.abspath(__file__)))
        print("hello")
    time.sleep(1)

while True:
    main()
