from genericpath import getmtime
from imgurpython import ImgurClient
import datetime
import os
import shutil
client_id = '3ef4beacee8d63c'
client_secret = '75640200bd814140c1e10fe3bd95ed65e9dd490d'
access_token = '8a06c8a86ac3ef93546cff4ea2cb42956cd60cf4'
refresh_token = '7e64f091f020ffc5486e9b6f8f97ce9b8ed2ad6e'
client = ImgurClient(client_id, client_secret, access_token, refresh_token)

# Authorization flow, pin example (see docs for other auth types)
# ... redirect user to `authorization_url`, obtain pin (or code or token) ...
#https://github.com/Imgur/imgurpython

#https://python.hotexamples.com/examples/imgurpython/ImgurClient/get_account_images/python-imgurclient-get_account_images-method-examples.html
items = client.get_account_images('Darkdrium', page=0)
for item in items:
    print(item.link) #https://api.imgur.com/models/gallery_image
    print(datetime.datetime.fromtimestamp(item.datetime).strftime('%Y-%m-%d %H:%M:%S'))
    #https://www.tutorialspoint.com/How-to-convert-an-integer-into-a-date-object-in-Python


# albums = client.get_account_album_ids('Darkdrium')
# for j in albums:
#     print(j)

# a = client.upload_from_path('C:\\Users\\Darren Ho\\Desktop\\DAWG.jpg', anon=False, config={'title':str(datetime.datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d %H:%M:%S'))})
# print(a)



location = "C:\\Users\\Darren Ho\\Pictures\\Imgur"
fileList = os.listdir(location)

for file in fileList:
    current_file_path = location + "\\" + file
    current_file_datetime = datetime.datetime.fromtimestamp(os.path.getmtime(current_file_path)).strftime('%Y-%m-%d %H:%M:%S')
    client.upload_from_path(current_file_path, anon=False, config={'title':current_file_datetime}) 
    shutil.move(current_file_path, 'C:\\Users\\Darren Ho\\Pictures\\Archive\\' + file)
    
