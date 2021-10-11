import os
import redis
import json


def main(event, context):

    # redisHost = 'localhost'
    # redisPort = '6379'
    # redisPassword = ''
    # redisDb = 0
        # r = redis.Redis(host=redisHost, port = redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None)
    thingId = event["data"]["thingID"]
    # we want to use this thingId to get  device id, sensor id etc.. so can store it in redis. (continue coding from here later)
    print(thingId)

