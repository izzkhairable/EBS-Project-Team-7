import os
import redis
import json
import requests
import datetime
from requests.auth import HTTPBasicAuth

def getBearerToken(authUrl, clientId, clientSecret):
    callUrl = authUrl
    request_body = {'grant_type': 'client_credentials', 'response_type': 'token', 'client_id': clientId, 'client_secret': clientSecret}
    response = requests.post(callUrl, data = request_body)
    print("Bearer token request status from server: " + str(response.status_code))
    data = json.loads(response.text)
    bToken = data["access_token"]
    return bToken
# Get (almost) all data of the "thing"
def getThingData(iotThingUrl, bToken, thingId):
    print("ThingID: " + thingId)
    callUrl = iotThingUrl + thingId + "')"
    headers = {'Authorization': 'Bearer ' + bToken}
    response = requests.get(callUrl, headers = headers)
    print("Thing data request status from server: " + str(response.status_code))
    data = json.loads(response.text)
    asg = data['_assignment']
    device = asg['_devices']
    for i in device:
        deviceId = i['_id']
        for j in i['_sensors']:
            sensorId = j['_id']
            sensorTypeId = j['_sensorTypeId']
    return (deviceId, sensorId, sensorTypeId)    

# Retrieve capabilities from SAP IoT device management (remaining data needed)
def getThingCapabilities(iotUrl, iotUser, iotPassword, iotTenant, sensorType):
    callUrl = iotUrl + iotTenant + "/sensorTypes/" + sensorType 
    response = requests.get(callUrl, auth = HTTPBasicAuth(iotUser, iotPassword))
    print("Capabilities request status from server: " + str(response.status_code))
    data = json.loads(response.text)
    capabilityList = data["capabilities"]
    commandCapabilityId = ""
    for capability in data["capabilities"]:
        if capability["type"] == "command":
            commandCapabilityId = capability["id"]
    return commandCapabilityId        

def main(event, context):
    clientSecret = os.getenv('CLIENTSECRET')
    clientId = os.environ.get('CLIENTID')
    authUrl = os.environ.get('AUTHENTICATIONURL')
    iotUrl = os.environ.get('IOTMGMTURL')
    iotUser = os.environ.get('IOTUSER')
    iotPassword = os.environ.get('IOTPASSWORD')
    iotTenant = os.environ.get('IOTTENANT')
    iotThingUrl = os.environ.get('IOTTHINGURL')
    redisHost = os.environ.get('REDISHOST')
    redisPort = os.environ.get('REDISPORT')
    redisPassword = os.environ.get('REDISPASSWORD')
    redisDb = os.environ.get('REDISDBNO')    
    r = redis.Redis(host=redisHost, port = redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)
    #event = {'data': {'thingId': '38ED5BF550EE4CC6AD2BE9A7BE7111A4', 'thingCoordinate': '1.3050856285437102, 103.93210128266621'}}
    thingId = event["data"]["thingID"]
    coordinate = event["data"]["thingCoordinate"]

    bearerToken = getBearerToken(authUrl, clientId, clientSecret)
    (deviceId, sensorId, sensorTypeId) = getThingData(iotThingUrl, bearerToken, thingId)
    commandCapabilityId = getThingCapabilities(iotUrl, iotUser, iotPassword, iotTenant, sensorTypeId)
    dataset = {"thingId": thingId, "deviceId": deviceId, "sensorId": sensorId, "commandCapabilityId": commandCapabilityId, "coordinate": coordinate }

    deviceFound = 0
    for device in r.lrange('devices', 0, -1):
        device = json.loads(device)
        if device['thingId'] == thingId:
            deviceFound = deviceFound + 1          

    #We check if this Thing ID and the Thing Data are stored in Redis, if not, we push. If already exist, we check if anything else has changed, such as the coordinates, then we delete old data and replace it with new data.
    if deviceFound == 0:
        r.rpush('devices', json.dumps(dataset))
    else:
        # dataset = {"thingId": thingId, "deviceId": deviceId, "sensorId": sensorId, "commandCapabilityId": commandCapabilityId, "coordinate": "1314" }
        for ind in range(len(r.lrange('devices', 0, -1))):
            device = json.loads(r.lrange('devices', 0, -1)[ind])
            if device['thingId'] == thingId:
                if device != dataset:
                    r.lrem('devices', 1, r.lrange('devices', 0, -1)[ind])
                    r.rpush('devices', json.dumps(dataset))

    if len(r.lrange(thingId, -1, -1)) == 1: 
        prev_date = json.loads(r.lrange(thingId, -1, -1)[0])['datetime']
        min_diff = (datetime.datetime.now() - prev_date).total_seconds()/60
        if min_diff >= 30: #If the most recent event was logged more than 30 minutes ago, we log again. If not, don't log, because too recent.. 
            r.rpush(thingId, '{"event": "strong_wave", "datetime": "' + str(datetime.datetime.now()) + '"}')
    else:
        r.rpush(thingId, '{"event": "strong_wave", "datetime": "' + str(datetime.datetime.now()) + '"}')

    for wave_event in r.lrange(thingId, 0, -1): #We want get rid of all data older than 30 days..
        the_time = datetime.datetime.strptime(json.loads(wave_event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
        if (datetime.datetime.now() - the_time).days >= 30:
            r.lpop(thingId)

# thingId = '38ED5BF550EE4CC6AD2BE9A7BE7111A4'    
# redisHost = 'localhost'
# redisPort = '6379'
# redisPassword = ''
# redisDb = 0
# r = redis.Redis(host=redisHost, port = redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)
# r.flushall()


# if r.lrange(thingId, -1, -1) == 1: 
#     prev_date = json.loads(r.lrange(thingId, -1, -1)[0])['datetime']
#     min_diff = (datetime.datetime.now() - prev_date).total_seconds()/60
#     if min_diff >= 30: #If the most recent event was logged more than 30 minutes ago, we log again. 
#         r.rpush(thingId, '{"event": "strong_wave", "datetime": "' + str(datetime.datetime.now()) + '"}')
# else:
#     r.rpush(thingId, '{"event": "strong_wave", "datetime": "' + str(datetime.datetime.now()) + '"}')


# r.rpush(thingId, '{"event": "strong_wave", "datetime": "' + str(datetime.datetime.strptime('2021-09-13 18:34:18.988434', '%Y-%m-%d %H:%M:%S.%f')) + '"}')
# r.rpush(thingId, '{"event": "strong_wave", "datetime": "' + str(datetime.datetime.strptime('2021-09-14 18:34:18.988434', '%Y-%m-%d %H:%M:%S.%f')) + '"}')
# r.rpush(thingId, '{"event": "strong_wave", "datetime": "' + str(datetime.datetime.strptime('2021-09-15 18:34:18.988434', '%Y-%m-%d %H:%M:%S.%f')) + '"}')


# for wave_event in r.lrange(thingId, 0, -1): #We want get rid of all data older than 30 days..
#     the_time = datetime.datetime.strptime(json.loads(wave_event)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
#     if (datetime.datetime.now() - the_time).days >= 30:
#         r.lpop(thingId)

# print(r.lrange(thingId, 0, -1))