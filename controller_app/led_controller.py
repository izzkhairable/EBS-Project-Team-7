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

def main():
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

    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.read(['./config/led_controller.cfg'])
    #[redis]
    redisHost = config.get("redis", "redisHost")
    redisPort = int(config.get("redis", "redisPort"))
    redisPassword = config.get("redis", "redisPassword")
    redisDb = int(config.get("redis", "redisDb"))
    #[sapiot]
    commandUrl = config.get("sapiot", "commandUrl")
    iotUser = config.get("sapiot", "iotUser")
    iotPassword = config.get("sapiot", "iotPassword").replace("'", "")
    #[ipCam]
    ipCamUrl = config.get("ipCam", "ipCamUrl")

    #[imgur]
    client_id = config.get("imgur", "client_id")
    client_secret = config.get("imgur", "client_secret")
    access_token = config.get("imgur", "access_token")
    refresh_token = config.get("imgur", "refresh_token")
    client_username = config.get("imgur", "client_username")
    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    upload_frequency_in_minutes = int(config.get("imgur", "upload_frequency_in_minutes"))

    #[led]
    off_led_after_x_mins_of_no_wave = int(config.get("led", "off_led_after_x_mins_of_no_wave"))
    
    #[beach_human_counter]
    count_human_every_x_min = int(config.get("beach_human_counter", "count_human_every_x_min"))

    #[event]
    delete_event_data_older_than_x_days = int(config.get("event", "delete_event_data_older_than_x_days"))

    #[sensor_data]
    delete_sensor_data_older_than_x_days = int(config.get("sensor_data", "delete_sensor_data_older_than_x_days"))

    #[beach_counter]
    delete_beach_counter_data_older_than_x_days = int(config.get("beach_counter", "delete_beach_counter_data_older_than_x_days"))

    #[misc]
    sleep_time = int(config.get("misc", "sleep_time"))

    r = redis.Redis(host=redisHost, port=redisPort, db=int(
        redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)

    HOGCV = cv2.HOGDescriptor()
    HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

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
    time.sleep(sleep_time)
while True:
    main()