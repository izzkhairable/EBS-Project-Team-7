import time
import os
import redis
import json
import datetime
import requests
import configparser
from requests.auth import HTTPBasicAuth


def main():

    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.read(['./config/data_removal_controller.cfg'])
    redisHost = config.get("redis", "redisHost")
    redisPort = int(config.get("redis", "redisPort"))
    redisPassword = config.get("redis", "redisPassword")
    redisDb = int(config.get("redis", "redisDb"))
    r = redis.Redis(host=redisHost, port=redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)

    if len(r.lrange('devices', 0, -1)) > 0:
        for thing in r.lrange('devices', 0, -1):
            current_thing = json.loads(thing)['thingId'] + 'DATACOLLECTION'
            for data in r.lrange(current_thing, 0, -1): #We want get rid of all data older than 30 days..
                the_time = datetime.datetime.strptime(json.loads(data)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
                if (datetime.datetime.now() - the_time).days >= 30:
                    r.lrem(current_thing, 1, data)

    time.sleep(20)

while True:
    main()
