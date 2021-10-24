import cv2
import imutils
import numpy as np
import os
import configparser
import redis
import json
import datetime
import time
from urllib.request import urlopen


# config = configparser.ConfigParser(inline_comment_prefixes="#")
# config.read(['./config/led_controller.cfg'])
# redisHost = config.get("redis", "redisHost")
# redisPort = int(config.get("redis", "redisPort"))
# redisPassword = config.get("redis", "redisPassword")
# redisDb = int(config.get("redis", "redisDb"))
def url_to_image(url, readFlag=cv2.IMREAD_COLOR):
    resp = urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, readFlag)
    return image

def main():
    # redisHost = 'localhost'
    # redisPort = '6379'
    # redisPassword = ''
    # redisDb = 0
    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.read(['./config/human_counter_controller.cfg'])
    redisHost = config.get("redis", "redisHost")
    redisPort = int(config.get("redis", "redisPort"))
    redisPassword = config.get("redis", "redisPassword")
    redisDb = int(config.get("redis", "redisDb"))
    ipCamUrl = config.get("ipCam", "ipCamUrl")
    r = redis.Redis(host=redisHost, port=redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)

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
            current_thing = json.loads(thing)['thingId'] + 'POPULATION'
            for data in r.lrange(current_thing, 0, -1): #We want get rid of all data older than 6 days..
                the_time = datetime.datetime.strptime(json.loads(data)["datetime"], '%Y-%m-%d %H:%M:%S.%f')
                if (datetime.datetime.now() - the_time).days >= 6:
                    r.lrem(current_thing, 1, data)


    HOGCV = cv2.HOGDescriptor()
    HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    count = humanDetector(ipCamUrl)
    current_datetime = datetime.datetime.now()
    r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"" + str(current_datetime) + "\", \"people_count\": " + str(count) + "}")
    time.sleep(300)

while True:
    main()
# redisHost = 'localhost'
# redisPort = '6379'
# redisPassword = ''
# redisDb = 0
# r = redis.Redis(
#     host=redisHost,
#     port=redisPort,
#     db=int(redisDb),
#     password=redisPassword,
#     socket_timeout=None,
#     decode_responses=True,
# )

# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-23 03:00:00.000000\", \"people_count\": 5}")
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-23 06:00:00.000000\", \"people_count\": 8}")
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-23 12:00:00.000000\", \"people_count\": 7}")
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-23 18:00:00.000000\", \"people_count\": 4}")

# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-24 03:00:00.000000\", \"people_count\": 12}")
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-24 06:00:00.000000\", \"people_count\": 3}")
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-24 12:00:00.000000\", \"people_count\": 9}")
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-24 18:00:00.000000\", \"people_count\": 7}")

# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-25 03:00:00.000000\", \"people_count\": 11}")
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-25 06:00:00.000000\", \"people_count\": 9}")
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-25 12:00:00.000000\", \"people_count\": 5}")
# r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-25 18:00:00.000000\", \"people_count\": 8}")

# dailyPopulationList = r.lrange('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', 0, -1)[::-1]
# outcome = ''
# number_of_people_for_current_day = 0
# for index in range(0, len(dailyPopulationList)):
#     jsonobj = json.loads(dailyPopulationList[index])
#     eventdate = datetime.datetime.strptime(jsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')
#     eventyear = eventdate.year
#     eventmonth = eventdate.month
#     eventday = eventdate.day
#     previousjsonobj = json.loads(dailyPopulationList[index-1])
#     previouseventdate = datetime.datetime.strptime(previousjsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')

#     if index > 0 and index < len(dailyPopulationList)-1:
#         if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month and eventday == previouseventdate.day):
#             number_of_people_for_current_day+=jsonobj['people_count']
#         else:
#             outcome+= json.dumps({"date": str(previouseventdate), "count": number_of_people_for_current_day}) + "|"
#             number_of_people_for_current_day = jsonobj['people_count']
#     elif index == len(dailyPopulationList)-1:
#         if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month and eventday == previouseventdate.day):
#             number_of_people_for_current_day+=jsonobj['people_count']
#             outcome+= json.dumps({"date": str(eventdate), "count": number_of_people_for_current_day}) + "|"
#         else:
#             outcome+= json.dumps({"date": str(previouseventdate), "count": number_of_people_for_current_day}) + "|"
#             number_of_people_for_current_day = jsonobj['people_count']
#             outcome+= json.dumps({"date": str(eventdate), "count": jsonobj['people_count']}) + "|"
#     elif index == 0:
#         number_of_people_for_current_day+=jsonobj['people_count']


# print(outcome)