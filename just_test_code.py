import redis

redisHost = 'localhost'
redisPort = '6379'
redisPassword = ''
redisDb = 0
commandUrl = 'https://a4042ecf-281e-4d4a-b721-c9b43461e188.eu10.cp.iot.sap/a4042ecf-281e-4d4a-b721-c9b43461e188/iot/core/api/v1/tenant/1954515505/devices/'
iotUser = 'smu-team07'
iotPassword = 'smuArmSAP#2021'

r = redis.Redis(host=redisHost, port=redisPort, db=int(
redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)

r.flushall()
thing1 = '{"thingId": "38ED5BF550EE4CC6AD2BE9A7BE7111A4", "deviceId": "dcac5d23-cf60-44ff-82e8-b1fb4fd69efb", "sensorId": "f1ff9a46-86f7-47ef-befb-ccb8a76b90a8", "commandCapabilityId": "24c65333-6630-46d2-b4b8-69ca3f3786df", "coordinate": {"lat": "1.3050856285437102", "lng": "103.93210128266621"}, "zone": "East Coast Park Zone 1"}'
thing2 = '{"thingId": "thingtwo", "deviceId": "dcac5d23-cf60-44ff-82e8-b1fb4fd69efb", "sensorId": "f1ff9a46-86f7-47ef-befb-ccb8a76b90a8", "commandCapabilityId": "24c65333-6630-46d2-b4b8-69ca3f3786df", "coordinate": {"lat": "1.3050856285437102", "lng": "103.93210128266621"}, "zone": "East Coast Park Zone 1"}'
thing3 = '{"thingId": "thingthree", "deviceId": "dcac5d23-cf60-44ff-82e8-b1fb4fd69efb", "sensorId": "f1ff9a46-86f7-47ef-befb-ccb8a76b90a8", "commandCapabilityId": "24c65333-6630-46d2-b4b8-69ca3f3786df", "coordinate": {"lat": "1.3050856285437102", "lng": "103.93210128266621"}, "zone": "East Coast Park Zone 1"}'


r.rpush('devices', thing1)
r.rpush('devices', thing2)
r.rpush('devices', thing3)


print(r.lrange('devices', 0, -1))