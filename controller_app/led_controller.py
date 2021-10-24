import time
import os
import redis
import json
import datetime
import requests
import configparser
from requests.auth import HTTPBasicAuth


def main():
    def sendCommand(waveStatus):
        callUrl = commandUrl + currentDeviceId + '/commands'
        headers = { "Content-Type": "application/json" }
        body = '{ "capabilityId": "' + currentCommandCapabilityId +'", "command": { "waveStatus": "' + waveStatus + '"}, "sensorId": "' + currentSensorId + '" }'
        response = requests.post(callUrl,headers=headers, data=body, auth=HTTPBasicAuth(iotUser, iotPassword))
        data = json.loads(response.text)
        print("Sent command with response: " + str(response.status_code) + " / " + data['message'])

    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.read(['./config/led_controller.cfg'])
    redisHost = config.get("redis", "redisHost")
    redisPort = int(config.get("redis", "redisPort"))
    redisPassword = config.get("redis", "redisPassword")
    redisDb = int(config.get("redis", "redisDb"))
    commandUrl = config.get("sapiot", "commandUrl")
    iotUser = config.get("sapiot", "iotUser")
    iotPassword = config.get("sapiot", "iotPassword").replace("'","")
    r = redis.Redis(host=redisHost, port=redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)

    if len(r.lrange('devices', 0, -1)) > 0:
        for thing in r.lrange('devices', 0, -1):
            current_thing, currentDeviceId, currentSensorId, currentCommandCapabilityId = json.loads(thing)['thingId'], json.loads(thing)['deviceId'], json.loads(thing)['sensorId'], json.loads(thing)['commandCapabilityId']
            for event in r.lrange(current_thing, 0, -1): #We want get rid of all data older than 30 days..
                the_time = datetime.datetime.strptime(json.loads(event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
                event_type = json.loads(event)["event"]
                if (datetime.datetime.now() - the_time).days >= 30:
                    r.lrem(current_thing, 1, event)
            for event in r.lrange(current_thing, 0, -1)[::-1]:
                event_type = json.loads(event)["event"]  
                event_time = datetime.datetime.strptime(json.loads(event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
                if event_type == "strong_wave":
                    min_diff = (datetime.datetime.now() - event_time).total_seconds()/60  
                    if min_diff > 30: ## IF THE MOST RECENT EVENT IS MORE 30 MINUTES AGO, SEND THE COMMAND TO DEVICE ALERT THAT THERE'S NO LONGER WAVE!!! 
                        sendCommand("close")
                    elif min_diff <= 30: ## IF THE MOST RECENT EVENT IS LESS THAN 30 MINUTES AGO, SEND THE COMMAND TO DEVICE ALERT OF WAVE EVENT. 
                        sendCommand("activate")
                    break

    time.sleep(20)

while True:
    main()



######BELOW ARE TEST CODES############

# def sendCommand(waveStatus):
#     callUrl = commandUrl + currentDeviceId + '/commands'
#     headers = { "Content-Type": "application/json" }
#     body = '{ "capabilityId": "' + currentCommandCapabilityId +'", "command": { "waveStatus": "' + waveStatus + '"}, "sensorId": "' + currentSensorId + '" }'
#     response = requests.post(callUrl,headers=headers, data=body, auth=HTTPBasicAuth(iotUser, iotPassword))
#     data = json.loads(response.text)
#     print("Sent command with response: " + str(response.status_code) + " / " + data['message'])



# redisHost = 'localhost'
# redisPort = '6379'
# redisPassword = ''
# redisDb = 0
# commandUrl = 'https://a4042ecf-281e-4d4a-b721-c9b43461e188.eu10.cp.iot.sap/a4042ecf-281e-4d4a-b721-c9b43461e188/iot/core/api/v1/tenant/1954515505/devices/'
# iotUser = 'smu-team07'
# iotPassword = 'smuArmSAP#2021'

# r = redis.Redis(host=redisHost, port=redisPort, db=int(
# redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)

# r.flushall()
# thing1 = '{"thingId": "38ED5BF550EE4CC6AD2BE9A7BE7111A4", "deviceId": "dcac5d23-cf60-44ff-82e8-b1fb4fd69efb", "sensorId": "f1ff9a46-86f7-47ef-befb-ccb8a76b90a8", "commandCapabilityId": "24c65333-6630-46d2-b4b8-69ca3f3786df", "coordinate": {"lat": "1.3050856285437102", "lng": "103.93210128266621"}, "zone": "East Coast Park Zone 1"}'
# thing2 = '{"thingId": "69ED5BF550EE4CC6AD2BE9A7BE7111B7", "deviceId": "asca5161-cf60-44ff-82e8-512b4fas9sab", "sensorId": "g9ez5i16-86f7-47ef-befb-ccb8a76z16g9", "commandCapabilityId": "24c65333-6630-46d2-b4b8-69ca3f3786df", "coordinate": {"lat": "1.3050856285437102", "lng": "103.93210128266621"}, "zone": "East Coast Park Zone 2"}'

# r.rpush('devices', thing1)
# r.rpush('devices', thing2)

# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4', '{"event": "strong_wave", "datetime": "2021-08-24 22:02:29.735563", "zone": "East Coast Park Zone 1"}')
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4', '{"event": "strong_wave", "datetime": "2021-09-16 22:02:29.735563", "zone": "East Coast Park Zone 1"}')
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4', '{"event": "strong_wave", "datetime": "2021-10-11 22:02:29.735563", "zone": "East Coast Park Zone 1"}')
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4', '{"event": "strong_wave", "datetime": "2021-10-12 22:02:29.735563", "zone": "East Coast Park Zone 1"}')

# r.rpush('69ED5BF550EE4CC6AD2BE9A7BE7111B7', '{"event": "strong_wave", "datetime": "2021-08-24 22:02:29.735563", "zone": "East Coast Park Zone 2"}')
# r.rpush('69ED5BF550EE4CC6AD2BE9A7BE7111B7', '{"event": "strong_wave", "datetime": "2021-09-16 22:02:29.735563", "zone": "East Coast Park Zone 2"}')
# r.rpush('69ED5BF550EE4CC6AD2BE9A7BE7111B7', '{"event": "strong_wave", "datetime": "2021-10-11 22:02:29.735563", "zone": "East Coast Park Zone 2"}')
# r.rpush('69ED5BF550EE4CC6AD2BE9A7BE7111B7', '{"event": "strong_wave", "datetime": "2021-10-12 22:02:29.735563", "zone": "East Coast Park Zone 2"}')


# if len(r.lrange('devices', 0, -1)) > 0:
#     for thing in r.lrange('devices', 0, -1):
#         current_thing, currentDeviceId, currentSensorId, currentCommandCapabilityId = json.loads(thing)['thingId'], json.loads(thing)['deviceId'], json.loads(thing)['sensorId'], json.loads(thing)['commandCapabilityId']
#         for event in r.lrange(current_thing, 0, -1): #We want get rid of all data older than 30 days..
#             the_time = datetime.datetime.strptime(json.loads(event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
#             event_type = json.loads(event)["event"]
#             if (datetime.datetime.now() - the_time).days >= 30:
#                 r.lrem(current_thing, 1, event)
#         for event in r.lrange(current_thing, 0, -1)[::-1]:
#             event_type = json.loads(event)["event"]  
#             event_time = datetime.datetime.strptime(json.loads(event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
#             if event_type == "strong_wave":
#                 min_diff = (datetime.datetime.now() - event_time).total_seconds()/60  
#                 if min_diff > 30: ## IF THE MOST RECENT EVENT IS MORE 30 MINUTES AGO, SEND THE COMMAND TO DEVICE ALERT THAT THERE'S NO LONGER WAVE!!! 
#                     sendCommand("close")
#                 elif min_diff <= 30: ## IF THE MOST RECENT EVENT IS LESS THAN 30 MINUTES AGO, SEND THE COMMAND TO DEVICE ALERT OF WAVE EVENT. 
#                     sendCommand("activate")
#                 break

    
#print(r.lrange('devices', 0, -1))
#print(r.lrange('38ED5BF550EE4CC6AD2BE9A7BE7111A4', 0, -1))
#print(r.lrange('69ED5BF550EE4CC6AD2BE9A7BE7111B7', 0, -1))

# 1. Connect to Redis

# 2. Loop through each Thing in the "devices" array

# 3. Within each Thing, get rid of all events that are 30 days or older (remove from Redis "event" array)

# 4. 