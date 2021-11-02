import os
import redis
import json
import requests
import datetime
from requests.auth import HTTPBasicAuth
from twilio.rest import Client


def main(event, context):
    redisHost = os.environ.get('REDISHOST')
    redisPort = os.environ.get('REDISPORT')
    redisPassword = os.environ.get('REDISPASSWORD')
    redisDb = os.environ.get('REDISDBNO')
    r = redis.Redis(host=redisHost, port=redisPort, db=int(
        redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)
    thingId = event["data"]["thingID"]
    thingLatitude = event["data"]["thingLatitude"]
    thingLongitude = event["data"]["thingLongitude"]
    thingZone = event["data"]["thingZone"]

    account_sid = os.environ.get('ACCOUNTSID')
    auth_token = os.environ.get('AUTHTOKEN')
    from_no = os.environ.get('FROMNO')
    to_no = os.environ.get('TONO')

    client = Client(account_sid, auth_token)

    #### Logging of strong wave event happens here #####
    wet_device_record_count = 0
    if len(r.lrange(thingId, 0, -1)) > 0:
        for event in r.lrange(thingId, 0, -1)[::-1]:
            jsonobj = json.loads(event)
            if jsonobj['event'] == 'wet_device':
                wet_device_record_count += 1
                prev_date = datetime.datetime.strptime(
                    jsonobj['datetime'], '%Y-%m-%d %H:%M:%S.%f')
                min_diff = (datetime.datetime.now() -
                            prev_date).total_seconds()/60
                # If the most recent event was logged more than 6 hours, we log again. If not, don't.
                if min_diff >= 360:
                    r.rpush(thingId, '{"event": "wet_device", "datetime": "' +
                            str(datetime.datetime.now()) + '", "zone": "' + thingZone + '"}')
                    message = client.messages \
                        .create(
                            body="Water detected in float buoy for Thing ID: " + thingId + " in " + thingZone,
                            from_=from_no,
                            to=to_no
                        )
                    print(message.sid)
                break
        if wet_device_record_count == 0:
            r.rpush(thingId, '{"event": "wet_device", "datetime": "' +
                    str(datetime.datetime.now()) + '", "zone": "' + thingZone + '"}')
            message = client.messages \
                .create(
                    body="Water detected in float buoy for Thing ID: " + thingId + " in " + thingZone,
                    from_=from_no,
                    to=to_no
                )
            print(message.sid)

redisHost = 'localhost'
redisPort = 6379
redisPassword = ''
redisDb = 0
r = redis.Redis(host=redisHost, port=redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)
thingId = "38ED5BF550EE4CC6AD2BE9A7BE7111A4"
thingZone = "East Coast Park Zone 1"

account_sid = 'AC0a38e4d918e7c1e3e64ba772018512d9'
auth_token = 'aab6a1ee1d105739257b1ca079c0385e'
from_no = "+16627802933"
to_no = "+6592375375"


client = Client(account_sid, auth_token)

#### Logging of strong wave event happens here #####
wet_device_record_count = 0
if len(r.lrange(thingId, 0, -1)) > 0:
    for event in r.lrange(thingId, 0, -1)[::-1]:
        jsonobj = json.loads(event)
        if jsonobj['event'] == 'wet_device':
            wet_device_record_count += 1
            prev_date = datetime.datetime.strptime(
                jsonobj['datetime'], '%Y-%m-%d %H:%M:%S.%f')
            min_diff = (datetime.datetime.now() -
                        prev_date).total_seconds()/60
            # If the most recent event was logged more than 6 hours, we log again. If not, don't.
            if min_diff >= 360:
                r.rpush(thingId, '{"event": "wet_device", "datetime": "' +
                        str(datetime.datetime.now()) + '", "zone": "' + thingZone + '"}')
                message = client.messages \
                    .create(
                        body="Water detected in float buoy for Thing ID: " + thingId + " in " + thingZone,
                        from_=from_no,
                        to=to_no
                    )
                print(message.sid)
            break
    if wet_device_record_count == 0:
        r.rpush(thingId, '{"event": "wet_device", "datetime": "' +
                str(datetime.datetime.now()) + '", "zone": "' + thingZone + '"}')
        message = client.messages \
            .create(
                body="Water detected in float buoy for Thing ID: " + thingId + " in " + thingZone,
                from_=from_no,
                to=to_no
            )
        print(message.sid)

print(r.lrange('38ED5BF550EE4CC6AD2BE9A7BE7111A4', 0, -1))