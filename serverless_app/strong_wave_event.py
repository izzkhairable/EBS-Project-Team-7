import os
import redis
import json
import requests
import datetime
from requests.auth import HTTPBasicAuth


def main(event, context):
    redisHost = os.environ.get('REDISHOST')
    redisPort = os.environ.get('REDISPORT')
    redisPassword = os.environ.get('REDISPASSWORD')
    redisDb = os.environ.get('REDISDBNO')
    r = redis.Redis(host=redisHost, port=redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)
    thingId = event["data"]["thingID"]
    thingLatitude = event["data"]["thingLatitude"]
    thingLongitude = event["data"]["thingLongitude"]
    thingZone = event["data"]["thingZone"]
    
    #### Logging of strong wave event happens here #####
    strong_wave_record_count = 0
    if len(r.lrange(thingId, 0, -1)) > 0:
        for event in r.lrange(thingId, 0, -1)[::-1]:
            jsonobj = json.loads(event)
            if jsonobj['event'] == 'strong_wave':
                strong_wave_record_count+=1
                prev_date = datetime.datetime.strptime(jsonobj['datetime'], '%Y-%m-%d %H:%M:%S.%f')
                min_diff = (datetime.datetime.now() - prev_date).total_seconds()/60
                if min_diff >= 30:  # If the most recent event was logged more than 30 minutes ago, we log again. If not, don't.
                    r.rpush(thingId, '{"event": "strong_wave", "datetime": "' +
                            str(datetime.datetime.now()) + '", "zone": "' + thingZone + '"}')
                break
        if strong_wave_record_count == 0:
            r.rpush(thingId, '{"event": "strong_wave", "datetime": "' +
                    str(datetime.datetime.now()) + '", "zone": "' + thingZone + '"}')            
    else: #If no event is found for the ThingID, it means it's our first time logging, so just ahead and log right away
        r.rpush(thingId, '{"event": "strong_wave", "datetime": "' +
                    str(datetime.datetime.now()) + '", "zone": "' + thingZone + '"}')

