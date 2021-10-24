import os
import redis
import json
import requests
import datetime
from requests.auth import HTTPBasicAuth


def getBearerToken(authUrl, clientId, clientSecret):
    callUrl = authUrl
    request_body = {'grant_type': 'client_credentials', 'response_type': 'token',
                    'client_id': clientId, 'client_secret': clientSecret}
    response = requests.post(callUrl, data=request_body)
    print("Bearer token request status from server: " + str(response.status_code))
    data = json.loads(response.text)
    bToken = data["access_token"]
    return bToken

def getThingData(iotThingUrl, bToken, thingId):
    print("ThingID: " + thingId)
    callUrl = iotThingUrl + thingId + "')"
    headers = {'Authorization': 'Bearer ' + bToken}
    response = requests.get(callUrl, headers=headers)
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

def getThingCapabilities(iotUrl, iotUser, iotPassword, iotTenant, sensorType):
    callUrl = iotUrl + iotTenant + "/sensorTypes/" + sensorType
    response = requests.get(callUrl, auth=HTTPBasicAuth(iotUser, iotPassword))
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
    r = redis.Redis(host=redisHost, port=redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)
    thingId = event["data"]["thingID"]
    thingLatitude = event["data"]["thingLatitude"]
    thingLongitude = event["data"]["thingLongitude"]
    thingZone = event["data"]["thingZone"]
    bearerToken = getBearerToken(authUrl, clientId, clientSecret)
    (deviceId, sensorId, sensorTypeId) = getThingData(iotThingUrl, bearerToken, thingId)
    commandCapabilityId = getThingCapabilities(iotUrl, iotUser, iotPassword, iotTenant, sensorTypeId)
    
    ambientTemperature = str(event["data"]["ambientTemperature"])
    ambientPressure = str(event["data"]["ambientPressure"])
    ambientLight = str(event["data"]["ambientLight"])
    ambientHumidity = str(event["data"]["ambientHumidity"])
    gyroscopeX = str(event["data"]["gyroscopeX"])
    gyroscopeY = str(event["data"]["gyroscopeY"])
    gyroscopeZ = str(event["data"]["gyroscopeZ"])
    
    #Check if the Thing ID already stored in Redis
    dataset = {"thingId": thingId, "deviceId": deviceId, "sensorId": sensorId, "commandCapabilityId": commandCapabilityId, "coordinate": {"lat": thingLatitude, "lng": thingLongitude}, "zone": thingZone}
    deviceFound = 0
    for device in r.lrange('devices', 0, -1):
        device = json.loads(device)
        if device['thingId'] == thingId:
            deviceFound = deviceFound + 1
    if deviceFound == 0: #If the ThingID along with the Thing Data are not found in Redis, we push it to Redis.
        r.rpush('devices', json.dumps(dataset))
    else: #If the ThingID along with the Thing Data are already found in Redis, we check if any of the Thing properties has changed, such as the coordinate, sensorID, etc.. 
        for ind in range(len(r.lrange('devices', 0, -1))):
            device = json.loads(r.lrange('devices', 0, -1)[ind])
            if device['thingId'] == thingId: #If the ThingID has some properties changed such as the coordinate, SensorID etc.. we delete the ThingID from Redis and add again (to update the ThingID and the properties)
                if device != dataset:
                    r.lrem('devices', 1, r.lrange('devices', 0, -1)[ind])
                    r.rpush('devices', json.dumps(dataset))

    #### Storing Data Here ####
    dataCollectionKey = thingId + 'DATACOLLECTION'
    if len(r.lrange(dataCollectionKey, -1, -1)) == 1: 
        prev_date = datetime.datetime.strptime(json.loads(r.lrange(dataCollectionKey, -1, -1)[0])['datetime'], '%Y-%m-%d %H:%M:%S.%f')
        min_diff = (datetime.datetime.now() - prev_date).total_seconds()/60
        if min_diff >= 1:  # If the most recent event was logged more than 1 minutes ago, we log again. If not, don't.
            r.rpush(dataCollectionKey, '{"datetime": "' + str(datetime.datetime.now()) + '", "zone": "' + thingZone + '", "ambientTemperature": ' + ambientTemperature + ', "ambientPressure": ' 
                    + ambientPressure + ', "ambientLight": ' + ambientLight + ', "ambientHumidity": ' + ambientHumidity + ', "gyroscopeX": ' + gyroscopeX
                    + ', "gyroscopeY": ' + gyroscopeY + ', "gyroscopeZ": ' + gyroscopeZ + '}')
    else: #If no event is found for the ThingID, it means it's our first time logging, so just ahead and log right away
        r.rpush(dataCollectionKey, '{"datetime": "' + str(datetime.datetime.now()) + '", "zone": "' + thingZone + '", "ambientTemperature": ' + ambientTemperature + ', "ambientPressure": ' 
                + ambientPressure + ', "ambientLight": ' + ambientLight + ', "ambientHumidity": ' + ambientHumidity + ', "gyroscopeX": ' + gyroscopeX
                + ', "gyroscopeY": ' + gyroscopeY + ', "gyroscopeZ": ' + gyroscopeZ + '}')



# redisHost = 'localhost'
# redisPort = '6379'
# redisPassword = ''
# redisDb = 0

# r = redis.Redis(host=redisHost, port=redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)
# thingId = '15049926'
# thingZone = 'USA'

# r.flushall()

# ambientTemperature = str(5)
# ambientPressure = str(5)
# ambientLight = str(5)
# ambientHumidity = str(5)
# gyroscopeX = str(5)
# gyroscopeY = str(5)
# gyroscopeZ = str(5)

# #### Storing Data Here ####
# dataCollectionKey = thingId + 'DATACOLLECTION'
# if len(r.lrange(dataCollectionKey, -1, -1)) == 1: 
#     prev_date = datetime.datetime.strptime(json.loads(r.lrange(dataCollectionKey, -1, -1)[0])['datetime'], '%Y-%m-%d %H:%M:%S.%f')
#     min_diff = (datetime.datetime.now() - prev_date).total_seconds()/60
#     if min_diff >= 1:  # If the most recent event was logged more than 1 minutes ago, we log again. If not, don't.
#         r.rpush(dataCollectionKey, '{"datetime": "' + str(datetime.datetime.now()) + '", "zone": "' + thingZone + '", "ambientTemperature": ' + ambientTemperature + ', "ambientPressure": ' 
#                 + ambientPressure + ', "ambientLight": ' + ambientLight + ', "ambientHumidity": ' + ambientHumidity + ', "gyroscopeX": ' + gyroscopeX
#                 + ', "gyroscopeY": ' + gyroscopeY + ', "gyroscopeZ": ' + gyroscopeZ + '}')
# else: #If no event is found for the ThingID, it means it's our first time logging, so just ahead and log right away
#     r.rpush(dataCollectionKey, '{"datetime": "' + str(datetime.datetime.now()) + '", "zone": "' + thingZone + '", "ambientTemperature": ' + ambientTemperature + ', "ambientPressure": ' 
#             + ambientPressure + ', "ambientLight": ' + ambientLight + ', "ambientHumidity": ' + ambientHumidity + ', "gyroscopeX": ' + gyroscopeX
#             + ', "gyroscopeY": ' + gyroscopeY + ', "gyroscopeZ": ' + gyroscopeZ + '}')


# print(dataCollectionKey)
# print(json.loads(r.lrange(dataCollectionKey, 0, -1)[0])['ambientTemperature'])