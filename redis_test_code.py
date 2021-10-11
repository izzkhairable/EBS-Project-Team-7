import redis
import json 
import datetime
from requests.auth import HTTPBasicAuth
import requests

def getBearerToken(authUrl, clientId, clientSecret):
    callUrl = authUrl
    request_body = {'grant_type': 'client_credentials', 'response_type': 'token', 'client_id': clientId, 'client_secret': clientSecret}
    response = requests.post(callUrl, data = request_body)
    print("Bearer token request status from server: " + str(response.status_code))
    data = json.loads(response.text)
    bToken = data["access_token"]
    return bToken

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


redisHost = 'localhost'
redisPort = '6379'
redisPassword = ''
redisDb = 0

r = redis.Redis(host=redisHost, port = redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)
#https://stackoverflow.com/questions/25745053/about-char-b-prefix-in-python3-4-1-client-connect-to-redis

r.flushall()

coordinate = '1.3050856285437102, 103.93210128266621'






r.rpush('devices', '{"device_id": "dcac5d23-cf60-44ff-82e8-b1fb4fd69efb", "sensor_id": "f1ff9a46-86f7-47ef-befb-ccb8a76b90a8", "cmd_capability_id": "24c65333-6630-46d2-b4b8-69ca3f3786df", "sensor_type_id": "49d0f4c3-b243-469a-8797-28a483458de2"}')

print(json.loads(r.lrange('devices' , 0, -1)[0]))


