import time
import os
import redis
import json
import datetime
from imgurpython import ImgurClient
import requests
import configparser
from requests.auth import HTTPBasicAuth
import cv2
import imutils
import numpy as np
from urllib.request import urlopen

def url_to_image(url, readFlag=cv2.IMREAD_COLOR):
    resp = urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, readFlag)
    return image

def sendCommand(waveStatus):
    callUrl = commandUrl + currentDeviceId + '/commands'
    headers = {"Content-Type": "application/json"}
    body = '{ "capabilityId": "' + currentCommandCapabilityId + \
        '", "command": { "waveStatus": "' + waveStatus + \
        '"}, "sensorId": "' + currentSensorId + '" }'
    response = requests.post(
        callUrl, headers=headers, data=body, auth=HTTPBasicAuth(iotUser, iotPassword))
    data = json.loads(response.text)
    print("Sent command with response: " +
            str(response.status_code) + " / " + data['message'])

def detect(frame):
    bounding_box_cordinates, weights =  HOGCV.detectMultiScale(frame, winStride = (4, 4), padding = (8, 8), scale = 1.03)
    person = 0  
    for x,y,w,h in bounding_box_cordinates:
        person += 1
    return person

def humanDetector(args):
    return detectByPathImage(args, None)

def detectByPathImage(path, output_path):
    image = imutils.url_to_image(path)
    image = imutils.resize(image, width = min(800, image.shape[1])) 
    result_image = detect(image)
    if output_path is not None:
        cv2.imwrite(output_path, result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return result_image

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(['./config/led_controller.cfg'])
#[redis]
redisHost = 'localhost'
redisPort = '6379'
redisPassword = ''
redisDb = 0
#[sapiot]
commandUrl = 'https://a4042ecf-281e-4d4a-b721-c9b43461e188.eu10.cp.iot.sap/a4042ecf-281e-4d4a-b721-c9b43461e188/iot/core/api/v1/tenant/1954515505/devices/'
iotUser = 'iot-thing-user' # Common user, you can keep it!
iotPassword = 'SAPArm#01'
#[ipCam]
ipCamUrl = 'http://222.164.109.140:666/image.jpg'

#[imgur]
client_id = '3ef4beacee8d63c'
client_secret = '75640200bd814140c1e10fe3bd95ed65e9dd490d'
access_token = '8a06c8a86ac3ef93546cff4ea2cb42956cd60cf4'
refresh_token = '7e64f091f020ffc5486e9b6f8f97ce9b8ed2ad6e'
client_username = 'Darkdrium'
client = ImgurClient(client_id, client_secret, access_token, refresh_token)
upload_frequency_in_minutes = 5

#[led]
off_led_after_x_mins_of_no_wave = 30

#[beach_human_counter]
count_human_every_x_min = 5

#[event]
delete_event_data_older_than_x_days = 30

#[sensor_data]
delete_sensor_data_older_than_x_days = 1

#[beach_counter]
delete_beach_counter_data_older_than_x_days = 6

#[misc]
sleep_time = 1

r = redis.Redis(host=redisHost, port=redisPort, db=int(
    redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)

HOGCV = cv2.HOGDescriptor()
HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

if len(r.lrange('devices', 0, -1)) > 0:
    for thing in r.lrange('devices', 0, -1):
        current_thing, currentDeviceId, currentSensorId, currentCommandCapabilityId = json.loads(thing)['thingId'], json.loads(
            thing)['deviceId'], json.loads(thing)['sensorId'], json.loads(thing)['commandCapabilityId']
        eventKey = current_thing
        dataCollectionKey = current_thing + 'DATACOLLECTION'
        # We want get rid of all data older than 30 days..
        beachCounterKey = current_thing + 'POPULATION'
        zone = str(json.loads(thing)['zone'])

        imagelist = client.get_account_images(client_username, page=0)
        insertImage = False
        ipCamOnline = False

        try:
            response = requests.get(ipCamUrl, timeout=1)
            ipCamOnline = True
        except:
            # r.rpush(current_thing, "{\"event\": \"ipcam_offline\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")
            ipCamOnline = False
        
        checkOplaStatusUrl = commandUrl + currentDeviceId
        req = requests.get(checkOplaStatusUrl, auth=HTTPBasicAuth(iotUser, iotPassword))
        oplaOnline = False
        if req.status_code == 200:
            oplaOnline = json.loads(req.text)['online']

        
        if len(imagelist) > 0:
            min_diff = (datetime.datetime.now() - datetime.datetime.strptime(imagelist[0].title, '%Y-%m-%d %H:%M:%S.%f')).total_seconds()/60
            if min_diff >= upload_frequency_in_minutes:
                insertImage = True
            else:
                pass
        else:
            insertImage = True

        if insertImage == True and ipCamOnline == True:
            response = requests.get(ipCamUrl, timeout=1)
            file = open(os.path.dirname(os.path.abspath(__file__)) + "/image.png", "wb")
            file.write(response.content)
            file.close()
            client.upload_from_path(os.path.dirname(os.path.abspath(__file__)) + "/image.png", anon=False, config={'title':str(datetime.datetime.now()), 'description': zone}) 

        ipcam_last_offline = None
        ipcam_last_online = None
        for event in r.lrange(eventKey, 0, -1)[::-1]: 
            event_type = json.loads(event)["event"]
            event_time = datetime.datetime.strptime(
                json.loads(event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
            if event_type == "ipcam_offline":
                ipcam_last_offline = event
                break

        for event in r.lrange(eventKey, 0, -1)[::-1]: 
            event_type = json.loads(event)["event"]
            event_time = datetime.datetime.strptime(
                json.loads(event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
            if event_type == "ipcam_online":
                ipcam_last_online = event
                break
        if ipcam_last_online != None and ipcam_last_offline != None:
            if json.loads(ipcam_last_offline)["datetime"] < json.loads(ipcam_last_online)["datetime"]:
                if ipCamOnline:
                    pass
                else:
                    r.rpush(current_thing, "{\"event\": \"ipcam_offline\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")
            elif json.loads(ipcam_last_offline)["datetime"] > json.loads(ipcam_last_online)["datetime"]:
                if ipCamOnline:
                    r.rpush(current_thing, "{\"event\": \"ipcam_online\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")
                else:
                    pass
        elif ipcam_last_online != None and ipcam_last_offline == None:
            if ipCamOnline:
                pass
            else:
                r.rpush(current_thing, "{\"event\": \"ipcam_offline\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")
        elif ipcam_last_offline != None and ipcam_last_online == None:
            if ipCamOnline:
                r.rpush(current_thing, "{\"event\": \"ipcam_online\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")

            else:
                pass
        elif ipcam_last_offline == None and ipcam_last_online == None:
            if ipCamOnline:
                r.rpush(current_thing, "{\"event\": \"ipcam_online\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")
            else:
                r.rpush(current_thing, "{\"event\": \"ipcam_offline\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")


#####################

        opla_last_offline = None
        opla_last_online = None
        for event in r.lrange(eventKey, 0, -1)[::-1]: 
            event_type = json.loads(event)["event"]
            event_time = datetime.datetime.strptime(
                json.loads(event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
            if event_type == "opla_offline":
                opla_last_offline = event
                break

        for event in r.lrange(eventKey, 0, -1)[::-1]: 
            event_type = json.loads(event)["event"]
            event_time = datetime.datetime.strptime(
                json.loads(event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
            if event_type == "opla_online":
                opla_last_online = event
                break
        if opla_last_online != None and opla_last_offline != None:
            if json.loads(opla_last_offline)["datetime"] < json.loads(opla_last_online)["datetime"]:
                if oplaOnline:
                    pass
                else:
                    r.rpush(current_thing, "{\"event\": \"opla_offline\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")
            elif json.loads(opla_last_offline)["datetime"] > json.loads(opla_last_online)["datetime"]:
                if oplaOnline:
                    r.rpush(current_thing, "{\"event\": \"opla_online\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")
                else:
                    pass
        elif opla_last_online != None and opla_last_offline == None:
            if oplaOnline:
                pass
            else:
                r.rpush(current_thing, "{\"event\": \"opla_offline\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")
        elif opla_last_offline != None and opla_last_online == None:
            if oplaOnline:
                r.rpush(current_thing, "{\"event\": \"opla_online\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")

            else:
                pass
        elif opla_last_offline == None and opla_last_online == None:
            if oplaOnline:
                r.rpush(current_thing, "{\"event\": \"opla_online\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")
            else:
                r.rpush(current_thing, "{\"event\": \"opla_offline\", \"datetime\": \"" + str(datetime.datetime.now()) + "\", \"zone\": \"" + zone + "\"}")


######################


        for data in r.lrange(beachCounterKey, 0, -1): 
            the_time = datetime.datetime.strptime(json.loads(data)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
            if (datetime.datetime.now() - the_time).days >= delete_beach_counter_data_older_than_x_days:
                r.lrem(beachCounterKey, 1, data)

        for event in r.lrange(eventKey, 0, -1):
            the_time = datetime.datetime.strptime(
                json.loads(event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
            event_type = json.loads(event)["event"]
            if (datetime.datetime.now() - the_time).days >= delete_event_data_older_than_x_days:
                r.lrem(eventKey, 1, event)
        # We want get rid of all data older than 30 days..

        for data in r.lrange(dataCollectionKey, 0, -1):
            the_time = datetime.datetime.strptime(
                json.loads(data)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
            if (datetime.datetime.now() - the_time).days >= delete_sensor_data_older_than_x_days:
                r.lrem(dataCollectionKey, 1, data)
            else:
                break
        # if len(r.lrange(dataCollectionKey, 0, -1)) > 0:
        #     latest_sensor_data = json.loads(r.lrange(dataCollectionKey, -1, -1)[0]) 
        #     data_collection_list = r.lrange(dataCollectionKey, 0, -1)
        #     total_temperature_for_current_day = 0
        #     total_no_of_data_for_current_day = 0
        #     total_temperature_for_current_month = 0
        #     total_no_of_data_for_current_month = 0
        #     for index in range(0, len(data_collection_list)):  
        #         jsonobj = json.loads(data_collection_list[index])
        #         eventdate = datetime.datetime.strptime(jsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')
        #         eventyear = eventdate.year
        #         eventmonth = eventdate.month
        #         eventday = eventdate.day
        #         previousjsonobj = json.loads(data_collection_list[index-1])
        #         previouseventdate = datetime.datetime.strptime(previousjsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')
        #         if index > 0 and index < len(data_collection_list)-1: #if we between 2nd to 2nd last item
        #             if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month):
        #                 total_temperature_for_current_month+=jsonobj['ambientTemperature']
        #                 total_no_of_data_for_current_month+=1
        #                 if eventday == previouseventdate.day:
        #                     total_temperature_for_current_day+=jsonobj['ambientTemperature']
        #                     total_no_of_data_for_current_day+=1
        #                 else:
        #                     r.rpush(current_thing + 'DAILYSENSORDATA', json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
        #                     total_temperature_for_current_day = jsonobj['ambientTemperature']
        #                     total_no_of_data_for_current_day = 1
        #             else:
        #                 r.rpush(current_thing + 'DAILYSENSORDATA', json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
        #                 total_temperature_for_current_day = jsonobj['ambientTemperature']
        #                 total_no_of_data_for_current_day = 1
        #                 r.rpush(current_thing + 'MONTHLYSENSORDATA', json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_month/total_no_of_data_for_current_month}))
        #                 total_temperature_for_current_month = jsonobj['ambientTemperature']
        #                 total_no_of_data_for_current_month = 1
        #         elif index == len(data_collection_list)-1: #if we are at the last item
        #             if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month):
        #                 total_temperature_for_current_month+=jsonobj['ambientTemperature']
        #                 total_no_of_data_for_current_month+=1
        #                 r.rpush(current_thing + 'MONTHLYSENSORDATA', json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_month/total_no_of_data_for_current_month}))

        #                 if eventday == previouseventdate.day:
        #                     total_temperature_for_current_day+=jsonobj['ambientTemperature']
        #                     total_no_of_data_for_current_day+=1
        #                     r.rpush(current_thing + 'DAILYSENSORDATA', json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
        #                 else:
        #                     r.rpush(current_thing + 'DAILYSENSORDATA', json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
        #                     total_temperature_for_current_day = jsonobj['ambientTemperature']
        #                     total_no_of_data_for_current_day = 1
        #                     r.rpush(current_thing + 'DAILYSENSORDATA', json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
        #             else:
        #                 r.rpush(current_thing + 'DAILYSENSORDATA', json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
        #                 total_temperature_for_current_day = jsonobj['ambientTemperature']
        #                 total_no_of_data_for_current_day = 1
        #                 r.rpush(current_thing + 'DAILYSENSORDATA', json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
        #                 r.rpush(current_thing + 'MONTHLYSENSORDATA', json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_month/total_no_of_data_for_current_month}))
        #                 total_temperature_for_current_month = jsonobj['ambientTemperature']
        #                 total_no_of_data_for_current_month = 1
        #                 r.rpush(current_thing + 'MONTHLYSENSORDATA', json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_month/total_no_of_data_for_current_month}))
        #         elif index == 0: #if we are at the first item
        #             total_temperature_for_current_day+=jsonobj['ambientTemperature']
        #             total_no_of_data_for_current_day+=1
        #             total_temperature_for_current_month+=jsonobj['ambientTemperature']
        #             total_no_of_data_for_current_month+=1
        #         r.lrem(dataCollectionKey, 1, data_collection_list[index])
        


        for event in r.lrange(eventKey, 0, -1)[::-1]: 
            event_type = json.loads(event)["event"]
            event_time = datetime.datetime.strptime(
                json.loads(event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
            if event_type == "strong_wave":
                min_diff = (datetime.datetime.now() -
                            event_time).total_seconds()/60
                if min_diff > off_led_after_x_mins_of_no_wave:  # IF THE MOST RECENT EVENT IS MORE 30 MINUTES AGO, SEND THE COMMAND TO DEVICE ALERT THAT THERE'S NO LONGER WAVE!!!
                    sendCommand("close")
                # IF THE MOST RECENT EVENT IS LESS THAN 30 MINUTES AGO, SEND THE COMMAND TO DEVICE ALERT OF WAVE EVENT.
                elif min_diff <= off_led_after_x_mins_of_no_wave:
                    sendCommand("activate")
                break

        # if len(r.lrange(eventKey, 0, -1)) > 0:
        #     data = json.loads(r.lrange(eventKey, 0, -1)[-1])
        #     event_type = data["event"]
        #     event_time = datetime.datetime.strptime(data["datetime"], '%Y-%m-%d %H:%M:%S.%f')
        #     if event_type == "strong_wave":
        #         min_diff = (datetime.datetime.now() - event_time).total_seconds()/60
        #         if min_diff > off_led_after_x_mins_of_no_wave:
        #             sendCommand("close")
        #         elif min_diff <= off_led_after_x_mins_of_no_wave:
        #             sendCommand("activate")

        if len(r.lrange(beachCounterKey, 0, -1)) > 0:
            data = r.lrange(beachCounterKey, -1, -1)[0]
            time_recorded = datetime.datetime.strptime(
                json.loads(data)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
            min_diff = (datetime.datetime.now() - time_recorded).total_seconds()/60
            if min_diff >= count_human_every_x_min and ipCamOnline:
                HOGCV = cv2.HOGDescriptor()
                HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
                count = humanDetector(ipCamUrl)
                current_datetime = datetime.datetime.now()
                r.rpush(beachCounterKey, "{\"datetime\": \"" + str(current_datetime) + "\", \"people_count\": " + str(count) + "}")
            else:
                pass
        else:
            if ipCamOnline:
                HOGCV = cv2.HOGDescriptor()
                HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
                count = humanDetector(ipCamUrl)
                current_datetime = datetime.datetime.now()
                r.rpush(beachCounterKey, "{\"datetime\": \"" + str(current_datetime) + "\", \"people_count\": " + str(count) + "}")

#print events
# print(r.lrange('38ED5BF550EE4CC6AD2BE9A7BE7111A4', 0, -1))
# print(r.lrange('38ED5BF550EE4CC6AD2BE9A7BE7111AZ', 0, -1))
#print daily 
print("daily data")
print(r.lrange('38ED5BF550EE4CC6AD2BE9A7BE7111A4DAILYSENSORDATA', 0, -1))
#print monthly
print("monthly data")
print(r.lrange('38ED5BF550EE4CC6AD2BE9A7BE7111A4MONTHLYSENSORDATA', 0, -1))

#print sensor
print("sensor data")
print(len(r.lrange('38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION', 0, -1)))
