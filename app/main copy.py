from flask import Flask, jsonify, render_template
from imgurpython import ImgurClient
import redis
import json
import requests
import configparser
import cv2
import datetime
import imutils
import numpy as np
import os
from requests.auth import HTTPBasicAuth
from urllib.request import urlopen

#https://data-flair.training/blogs/python-project-real-time-human-detection-counting/
HOGCV = cv2.HOGDescriptor()
HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
def url_to_image(url, readFlag=cv2.IMREAD_COLOR):
    resp = urlopen(url) #https://newbedev.com/how-can-i-read-an-image-from-an-internet-url-in-python-cv2-scikit-image-and-mahotas
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, readFlag)
    return image

def detect(frame):
    bounding_box_cordinates, weights =  HOGCV.detectMultiScale(frame, winStride = (4, 4), padding = (8, 8), scale = 1.03)
    person = 0
    
    for x,y,w,h in bounding_box_cordinates:
        # cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        # cv2.putText(frame, f'person {person}', (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
        person += 1
    # cv2.putText(frame, 'Status : Detecting ', (40,40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,0,0), 2)
    # cv2.putText(frame, f'Total Persons : {person}', (40,70), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,0,0), 2)
    # cv2.imshow('output', frame)
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

app = Flask(__name__)

config = configparser.ConfigParser(inline_comment_prefixes="#")
config.read(['./config/flaskapp.cfg'])

# # #[redis]
# redisHost = config.get("redis", "redisHost")
# redisPort = int(config.get("redis", "redisPort"))
# redisPassword = config.get("redis", "redisPassword")
# redisDb = int(config.get("redis", "redisDb"))
# r = redis.Redis(host=redisHost, port=redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)

# # #[imgur]
# client_id = config.get("imgur", "client_id")
# client_secret = config.get("imgur", "client_secret")
# access_token = config.get("imgur", "access_token")
# refresh_token = config.get("imgur", "refresh_token")
# client = ImgurClient(client_id, client_secret, access_token, refresh_token)

# #[ipCam]
# ipCamUrl = config.get("ipCam", "ipCamUrl")

# #[worldweatheronline]
# apiKey = config.get("worldweatheronline", "apiKey")


ipCamUrl = 'https://imagesvc.meredithcorp.io/v3/mm/image?url=https%3A%2F%2Fstatic.onecms.io%2Fwp-content%2Fuploads%2Fsites%2F38%2F2014%2F11%2F12220214%2Fshutterstock_159281780.jpg'
# ipCamUrl = 'http://222.164.109.140:666/image.jpg'
redisHost = 'localhost'
redisPort = '6379'
redisPassword = ''
redisDb = 0
r = redis.Redis(host=redisHost, port=redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)

client_id = '3ef4beacee8d63c'
client_secret = '75640200bd814140c1e10fe3bd95ed65e9dd490d'
access_token = '8a06c8a86ac3ef93546cff4ea2cb42956cd60cf4'
refresh_token = '7e64f091f020ffc5486e9b6f8f97ce9b8ed2ad6e'
client = ImgurClient(client_id, client_secret, access_token, refresh_token)

apiKey = '16293d33ab954ad0ae1193626211710'

@app.route("/", methods=["GET"])
def main():
    things_data_list_dict = []
    events_data_list_dict = []
    for thing in r.lrange('devices', 0, -1):
        thingJSON = json.loads(thing)
        commandUrl = 'https://a4042ecf-281e-4d4a-b721-c9b43461e188.eu10.cp.iot.sap/a4042ecf-281e-4d4a-b721-c9b43461e188/iot/core/api/v1/tenant/1954515505/devices/' + thingJSON['deviceId']
        req = requests.get(commandUrl, auth=HTTPBasicAuth('smu-team07', 'smuArmSAP#2021'))
        onlineStatus = False
        if req.status_code == 200:
            onlineStatus = json.loads(req.text)['online']
        status = ""
        if onlineStatus == False:
            status = "offline"
        else:
            status = "online"
        things_data_list_dict.append(
            {
                "thingId": thingJSON["thingId"],
                "deviceId": thingJSON["deviceId"],
                "sensorId": thingJSON["sensorId"],
                "commandCapabilityId": thingJSON["commandCapabilityId"],
                "coordinate": {
                    "lat": thingJSON["coordinate"]["lat"],
                    "lng": thingJSON["coordinate"]["lng"]
                },
                "zone": thingJSON["zone"],
                "status": status
            }
        )
        if len(r.lrange(thingJSON["thingId"], 0, -1)) > 0:
            for event in r.lrange(thingJSON["thingId"], 0, -1):
                eventJSON = json.loads(event)
                events_data_list_dict.append(
                    {
                        "event": eventJSON["event"],
                        "datetime": eventJSON["datetime"],
                        "zone": eventJSON["zone"]
                    }
                )

    return render_template(
        "homepage.html",
        # things_data=things_data_list_dict,
        # events_data=events_data_list_dict,
        things_data_json=json.dumps(things_data_list_dict),
        events_data_json=json.dumps(events_data_list_dict),
    )

@app.route("/dashboard")
def dashboard():
    items = client.get_account_images('Darkdrium', page=0)
    item_list = ''
    for item in items:
        curr_item = '{"link": "' + item.link + '", "title": "' + item.title + '"}'
        item_list = item_list + curr_item + "|"
    # forecast_data = json.dumps(requests.get('http://api.worldweatheronline.com/premium/v1/marine.ashx?key=' + apiKey + '&format=json&q=1.3883761,103.9787106').json())
    forecast_data = json.dumps({
            "data": {
                "request": [
                    {
                        "type": "LatLon",
                        "query": "Lat 1.39 and Lon 103.98"
                    }
                ],
                "weather": [
                    {
                        "date": "2021-10-18",
                        "astronomy": [
                            {
                                "sunrise": "06:47 AM",
                                "sunset": "06:52 PM",
                                "moonrise": "05:23 PM",
                                "moonset": "04:59 AM",
                                "moon_phase": "Full Moon",
                                "moon_illumination": "90"
                            }
                        ],
                        "maxtempC": "29",
                        "maxtempF": "85",
                        "mintempC": "25",
                        "mintempF": "78",
                        "uvIndex": "7",
                        "hourly": [
                            {
                                "time": "0",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "7",
                                "windspeedKmph": "11",
                                "winddirDegree": "315",
                                "winddir16Point": "NW",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "82",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1009",
                                "pressureInches": "30",
                                "cloudcover": "42",
                                "HeatIndexC": "29",
                                "HeatIndexF": "84",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "8",
                                "WindGustKmph": "13",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "84",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "0.1",
                                "waterTemp_C": "23",
                                "waterTemp_F": "73",
                                "uvIndex": "1"
                            },
                            {
                                "time": "300",
                                "tempC": "25",
                                "tempF": "78",
                                "windspeedMiles": "2",
                                "windspeedKmph": "4",
                                "winddirDegree": "341",
                                "winddir16Point": "NNW",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0025_light_rain_showers_night.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "0.2",
                                "precipInches": "0.0",
                                "humidity": "84",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1009",
                                "pressureInches": "30",
                                "cloudcover": "81",
                                "HeatIndexC": "28",
                                "HeatIndexF": "82",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "25",
                                "WindChillF": "78",
                                "WindGustMiles": "10",
                                "WindGustKmph": "15",
                                "FeelsLikeC": "28",
                                "FeelsLikeF": "82",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "0.1",
                                "waterTemp_C": "23",
                                "waterTemp_F": "73",
                                "uvIndex": "1"
                            },
                            {
                                "time": "600",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "5",
                                "windspeedKmph": "8",
                                "winddirDegree": "153",
                                "winddir16Point": "SSE",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "80",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "40",
                                "HeatIndexC": "28",
                                "HeatIndexF": "83",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "7",
                                "WindGustKmph": "11",
                                "FeelsLikeC": "28",
                                "FeelsLikeF": "83",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "0.1",
                                "waterTemp_C": "23",
                                "waterTemp_F": "73",
                                "uvIndex": "1"
                            },
                            {
                                "time": "900",
                                "tempC": "28",
                                "tempF": "83",
                                "windspeedMiles": "7",
                                "windspeedKmph": "11",
                                "winddirDegree": "120",
                                "winddir16Point": "ESE",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0002_sunny_intervals.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "66",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "35",
                                "HeatIndexC": "31",
                                "HeatIndexF": "88",
                                "DewPointC": "21",
                                "DewPointF": "70",
                                "WindChillC": "28",
                                "WindChillF": "83",
                                "WindGustMiles": "18",
                                "WindGustKmph": "29",
                                "FeelsLikeC": "31",
                                "FeelsLikeF": "88",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "0.1",
                                "waterTemp_C": "23",
                                "waterTemp_F": "73",
                                "uvIndex": "7"
                            },
                            {
                                "time": "1200",
                                "tempC": "29",
                                "tempF": "85",
                                "windspeedMiles": "6",
                                "windspeedKmph": "10",
                                "winddirDegree": "144",
                                "winddir16Point": "SE",
                                "weatherCode": "353",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Light rain shower"
                                    }
                                ],
                                "precipMM": "1.0",
                                "precipInches": "0.0",
                                "humidity": "66",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1010",
                                "pressureInches": "30",
                                "cloudcover": "56",
                                "HeatIndexC": "33",
                                "HeatIndexF": "91",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "29",
                                "WindChillF": "85",
                                "WindGustMiles": "17",
                                "WindGustKmph": "28",
                                "FeelsLikeC": "33",
                                "FeelsLikeF": "91",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "0.1",
                                "waterTemp_C": "23",
                                "waterTemp_F": "73",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1500",
                                "tempC": "28",
                                "tempF": "82",
                                "windspeedMiles": "4",
                                "windspeedKmph": "6",
                                "winddirDegree": "23",
                                "winddir16Point": "NNE",
                                "weatherCode": "359",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0018_cloudy_with_heavy_rain.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Torrential rain shower"
                                    }
                                ],
                                "precipMM": "7.5",
                                "precipInches": "0.3",
                                "humidity": "77",
                                "visibility": "3",
                                "visibilityMiles": "1",
                                "pressure": "1009",
                                "pressureInches": "30",
                                "cloudcover": "58",
                                "HeatIndexC": "31",
                                "HeatIndexF": "88",
                                "DewPointC": "23",
                                "DewPointF": "74",
                                "WindChillC": "28",
                                "WindChillF": "82",
                                "WindGustMiles": "10",
                                "WindGustKmph": "16",
                                "FeelsLikeC": "31",
                                "FeelsLikeF": "88",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "23",
                                "waterTemp_F": "73",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1800",
                                "tempC": "27",
                                "tempF": "80",
                                "windspeedMiles": "7",
                                "windspeedKmph": "11",
                                "winddirDegree": "355",
                                "winddir16Point": "N",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "0.4",
                                "precipInches": "0.0",
                                "humidity": "80",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "82",
                                "HeatIndexC": "30",
                                "HeatIndexF": "86",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "27",
                                "WindChillF": "80",
                                "WindGustMiles": "13",
                                "WindGustKmph": "22",
                                "FeelsLikeC": "30",
                                "FeelsLikeF": "86",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "23",
                                "waterTemp_F": "73",
                                "uvIndex": "6"
                            },
                            {
                                "time": "2100",
                                "tempC": "27",
                                "tempF": "80",
                                "windspeedMiles": "6",
                                "windspeedKmph": "10",
                                "winddirDegree": "349",
                                "winddir16Point": "NNW",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "81",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1013",
                                "pressureInches": "30",
                                "cloudcover": "39",
                                "HeatIndexC": "30",
                                "HeatIndexF": "85",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "27",
                                "WindChillF": "80",
                                "WindGustMiles": "15",
                                "WindGustKmph": "24",
                                "FeelsLikeC": "30",
                                "FeelsLikeF": "85",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "23",
                                "waterTemp_F": "73",
                                "uvIndex": "1"
                            }
                        ]
                    },
                    {
                        "date": "2021-10-19",
                        "astronomy": [
                            {
                                "sunrise": "06:47 AM",
                                "sunset": "06:51 PM",
                                "moonrise": "06:05 PM",
                                "moonset": "05:43 AM",
                                "moon_phase": "Full Moon",
                                "moon_illumination": "97"
                            }
                        ],
                        "maxtempC": "29",
                        "maxtempF": "84",
                        "mintempC": "26",
                        "mintempF": "79",
                        "uvIndex": "7",
                        "hourly": [
                            {
                                "time": "0",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "4",
                                "windspeedKmph": "7",
                                "winddirDegree": "355",
                                "winddir16Point": "N",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "82",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "29",
                                "HeatIndexC": "29",
                                "HeatIndexF": "84",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "7",
                                "WindGustKmph": "12",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "84",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "1"
                            },
                            {
                                "time": "300",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "3",
                                "windspeedKmph": "4",
                                "winddirDegree": "23",
                                "winddir16Point": "NNE",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "84",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "25",
                                "HeatIndexC": "29",
                                "HeatIndexF": "84",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "7",
                                "WindGustKmph": "11",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "84",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "1"
                            },
                            {
                                "time": "600",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "10",
                                "windspeedKmph": "15",
                                "winddirDegree": "111",
                                "winddir16Point": "ESE",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "83",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1013",
                                "pressureInches": "30",
                                "cloudcover": "49",
                                "HeatIndexC": "29",
                                "HeatIndexF": "84",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "19",
                                "WindGustKmph": "30",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "84",
                                "sigHeight_m": "0.3",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "1"
                            },
                            {
                                "time": "900",
                                "tempC": "28",
                                "tempF": "83",
                                "windspeedMiles": "11",
                                "windspeedKmph": "18",
                                "winddirDegree": "108",
                                "winddir16Point": "ESE",
                                "weatherCode": "356",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0010_heavy_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Moderate or heavy rain shower"
                                    }
                                ],
                                "precipMM": "3.1",
                                "precipInches": "0.1",
                                "humidity": "69",
                                "visibility": "7",
                                "visibilityMiles": "4",
                                "pressure": "1014",
                                "pressureInches": "30",
                                "cloudcover": "75",
                                "HeatIndexC": "31",
                                "HeatIndexF": "88",
                                "DewPointC": "22",
                                "DewPointF": "71",
                                "WindChillC": "28",
                                "WindChillF": "83",
                                "WindGustMiles": "20",
                                "WindGustKmph": "33",
                                "FeelsLikeC": "31",
                                "FeelsLikeF": "88",
                                "sigHeight_m": "0.4",
                                "swellHeight_m": "0.2",
                                "swellHeight_ft": "0.7",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1200",
                                "tempC": "29",
                                "tempF": "84",
                                "windspeedMiles": "9",
                                "windspeedKmph": "14",
                                "winddirDegree": "87",
                                "winddir16Point": "E",
                                "weatherCode": "353",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Light rain shower"
                                    }
                                ],
                                "precipMM": "2.0",
                                "precipInches": "0.1",
                                "humidity": "69",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "80",
                                "HeatIndexC": "32",
                                "HeatIndexF": "90",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "29",
                                "WindChillF": "84",
                                "WindGustMiles": "10",
                                "WindGustKmph": "16",
                                "FeelsLikeC": "32",
                                "FeelsLikeF": "90",
                                "sigHeight_m": "0.3",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1500",
                                "tempC": "26",
                                "tempF": "80",
                                "windspeedMiles": "6",
                                "windspeedKmph": "10",
                                "winddirDegree": "86",
                                "winddir16Point": "E",
                                "weatherCode": "353",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Light rain shower"
                                    }
                                ],
                                "precipMM": "2.1",
                                "precipInches": "0.1",
                                "humidity": "81",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1010",
                                "pressureInches": "30",
                                "cloudcover": "82",
                                "HeatIndexC": "29",
                                "HeatIndexF": "85",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "80",
                                "WindGustMiles": "11",
                                "WindGustKmph": "18",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "85",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1800",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "7",
                                "windspeedKmph": "11",
                                "winddirDegree": "56",
                                "winddir16Point": "NE",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "1.3",
                                "precipInches": "0.1",
                                "humidity": "81",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "77",
                                "HeatIndexC": "29",
                                "HeatIndexF": "85",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "9",
                                "WindGustKmph": "14",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "85",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "6"
                            },
                            {
                                "time": "2100",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "8",
                                "windspeedKmph": "12",
                                "winddirDegree": "39",
                                "winddir16Point": "NE",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "80",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1013",
                                "pressureInches": "30",
                                "cloudcover": "28",
                                "HeatIndexC": "29",
                                "HeatIndexF": "84",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "19",
                                "WindGustKmph": "30",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "84",
                                "sigHeight_m": "0.3",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "1"
                            }
                        ]
                    },
                    {
                        "date": "2021-10-20",
                        "astronomy": [
                            {
                                "sunrise": "06:47 AM",
                                "sunset": "06:51 PM",
                                "moonrise": "06:46 PM",
                                "moonset": "06:25 AM",
                                "moon_phase": "Waning Gibbous",
                                "moon_illumination": "97"
                            }
                        ],
                        "maxtempC": "27",
                        "maxtempF": "81",
                        "mintempC": "25",
                        "mintempF": "77",
                        "uvIndex": "7",
                        "hourly": [
                            {
                                "time": "0",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "5",
                                "windspeedKmph": "8",
                                "winddirDegree": "78",
                                "winddir16Point": "ENE",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "81",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "33",
                                "HeatIndexC": "29",
                                "HeatIndexF": "83",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "7",
                                "WindGustKmph": "11",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "83",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "21",
                                "waterTemp_F": "70",
                                "uvIndex": "1"
                            },
                            {
                                "time": "300",
                                "tempC": "26",
                                "tempF": "78",
                                "windspeedMiles": "9",
                                "windspeedKmph": "15",
                                "winddirDegree": "100",
                                "winddir16Point": "E",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "83",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "47",
                                "HeatIndexC": "28",
                                "HeatIndexF": "83",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "78",
                                "WindGustMiles": "16",
                                "WindGustKmph": "26",
                                "FeelsLikeC": "28",
                                "FeelsLikeF": "83",
                                "sigHeight_m": "0.3",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "21",
                                "waterTemp_F": "70",
                                "uvIndex": "1"
                            },
                            {
                                "time": "600",
                                "tempC": "27",
                                "tempF": "80",
                                "windspeedMiles": "16",
                                "windspeedKmph": "26",
                                "winddirDegree": "75",
                                "winddir16Point": "ENE",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "79",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1013",
                                "pressureInches": "30",
                                "cloudcover": "34",
                                "HeatIndexC": "30",
                                "HeatIndexF": "85",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "27",
                                "WindChillF": "80",
                                "WindGustMiles": "23",
                                "WindGustKmph": "36",
                                "FeelsLikeC": "30",
                                "FeelsLikeF": "85",
                                "sigHeight_m": "0.6",
                                "swellHeight_m": "0.2",
                                "swellHeight_ft": "0.7",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "21",
                                "waterTemp_F": "70",
                                "uvIndex": "1"
                            },
                            {
                                "time": "900",
                                "tempC": "27",
                                "tempF": "81",
                                "windspeedMiles": "12",
                                "windspeedKmph": "20",
                                "winddirDegree": "30",
                                "winddir16Point": "NNE",
                                "weatherCode": "353",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Light rain shower"
                                    }
                                ],
                                "precipMM": "1.7",
                                "precipInches": "0.1",
                                "humidity": "75",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1014",
                                "pressureInches": "30",
                                "cloudcover": "74",
                                "HeatIndexC": "30",
                                "HeatIndexF": "87",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "27",
                                "WindChillF": "81",
                                "WindGustMiles": "23",
                                "WindGustKmph": "38",
                                "FeelsLikeC": "30",
                                "FeelsLikeF": "87",
                                "sigHeight_m": "0.5",
                                "swellHeight_m": "0.3",
                                "swellHeight_ft": "1.0",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "21",
                                "waterTemp_F": "70",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1200",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "10",
                                "windspeedKmph": "16",
                                "winddirDegree": "20",
                                "winddir16Point": "NNE",
                                "weatherCode": "353",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Light rain shower"
                                    }
                                ],
                                "precipMM": "1.1",
                                "precipInches": "0.0",
                                "humidity": "81",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "82",
                                "HeatIndexC": "29",
                                "HeatIndexF": "85",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "16",
                                "WindGustKmph": "25",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "85",
                                "sigHeight_m": "0.4",
                                "swellHeight_m": "0.2",
                                "swellHeight_ft": "0.7",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "1.9",
                                "waterTemp_C": "21",
                                "waterTemp_F": "70",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1500",
                                "tempC": "25",
                                "tempF": "78",
                                "windspeedMiles": "4",
                                "windspeedKmph": "7",
                                "winddirDegree": "28",
                                "winddir16Point": "NNE",
                                "weatherCode": "353",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Light rain shower"
                                    }
                                ],
                                "precipMM": "0.5",
                                "precipInches": "0.0",
                                "humidity": "87",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "87",
                                "HeatIndexC": "28",
                                "HeatIndexF": "82",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "25",
                                "WindChillF": "78",
                                "WindGustMiles": "12",
                                "WindGustKmph": "19",
                                "FeelsLikeC": "28",
                                "FeelsLikeF": "82",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.2",
                                "swellHeight_ft": "0.7",
                                "swellDir": "40",
                                "swellDir16Point": "NE",
                                "swellPeriod_secs": "3.3",
                                "waterTemp_C": "21",
                                "waterTemp_F": "70",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1800",
                                "tempC": "25",
                                "tempF": "77",
                                "windspeedMiles": "5",
                                "windspeedKmph": "8",
                                "winddirDegree": "319",
                                "winddir16Point": "NW",
                                "weatherCode": "119",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0003_white_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "87",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "66",
                                "HeatIndexC": "28",
                                "HeatIndexF": "82",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "25",
                                "WindChillF": "77",
                                "WindGustMiles": "10",
                                "WindGustKmph": "17",
                                "FeelsLikeC": "28",
                                "FeelsLikeF": "82",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "40",
                                "swellDir16Point": "NE",
                                "swellPeriod_secs": "3.4",
                                "waterTemp_C": "21",
                                "waterTemp_F": "70",
                                "uvIndex": "6"
                            },
                            {
                                "time": "2100",
                                "tempC": "25",
                                "tempF": "77",
                                "windspeedMiles": "6",
                                "windspeedKmph": "10",
                                "winddirDegree": "290",
                                "winddir16Point": "WNW",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "85",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1013",
                                "pressureInches": "30",
                                "cloudcover": "62",
                                "HeatIndexC": "28",
                                "HeatIndexF": "82",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "25",
                                "WindChillF": "77",
                                "WindGustMiles": "17",
                                "WindGustKmph": "28",
                                "FeelsLikeC": "28",
                                "FeelsLikeF": "82",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "40",
                                "swellDir16Point": "NE",
                                "swellPeriod_secs": "3.4",
                                "waterTemp_C": "21",
                                "waterTemp_F": "70",
                                "uvIndex": "1"
                            }
                        ]
                    },
                    {
                        "date": "2021-10-21",
                        "astronomy": [
                            {
                                "sunrise": "06:46 AM",
                                "sunset": "06:51 PM",
                                "moonrise": "07:28 PM",
                                "moonset": "07:08 AM",
                                "moon_phase": "Waning Gibbous",
                                "moon_illumination": "90"
                            }
                        ],
                        "maxtempC": "29",
                        "maxtempF": "84",
                        "mintempC": "25",
                        "mintempF": "77",
                        "uvIndex": "6",
                        "hourly": [
                            {
                                "time": "0",
                                "tempC": "25",
                                "tempF": "77",
                                "windspeedMiles": "6",
                                "windspeedKmph": "10",
                                "winddirDegree": "283",
                                "winddir16Point": "WNW",
                                "weatherCode": "119",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0003_white_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "85",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "69",
                                "HeatIndexC": "28",
                                "HeatIndexF": "82",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "25",
                                "WindChillF": "77",
                                "WindGustMiles": "13",
                                "WindGustKmph": "21",
                                "FeelsLikeC": "28",
                                "FeelsLikeF": "82",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "50",
                                "swellDir16Point": "NE",
                                "swellPeriod_secs": "3.4",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            },
                            {
                                "time": "300",
                                "tempC": "25",
                                "tempF": "77",
                                "windspeedMiles": "4",
                                "windspeedKmph": "6",
                                "winddirDegree": "305",
                                "winddir16Point": "NW",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "84",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "52",
                                "HeatIndexC": "28",
                                "HeatIndexF": "82",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "25",
                                "WindChillF": "77",
                                "WindGustMiles": "7",
                                "WindGustKmph": "11",
                                "FeelsLikeC": "28",
                                "FeelsLikeF": "82",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "50",
                                "swellDir16Point": "NE",
                                "swellPeriod_secs": "3.3",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            },
                            {
                                "time": "600",
                                "tempC": "26",
                                "tempF": "78",
                                "windspeedMiles": "7",
                                "windspeedKmph": "11",
                                "winddirDegree": "197",
                                "winddir16Point": "SSW",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "81",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "31",
                                "HeatIndexC": "28",
                                "HeatIndexF": "82",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "26",
                                "WindChillF": "78",
                                "WindGustMiles": "8",
                                "WindGustKmph": "13",
                                "FeelsLikeC": "28",
                                "FeelsLikeF": "82",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "50",
                                "swellDir16Point": "NE",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            },
                            {
                                "time": "900",
                                "tempC": "28",
                                "tempF": "83",
                                "windspeedMiles": "7",
                                "windspeedKmph": "11",
                                "winddirDegree": "98",
                                "winddir16Point": "E",
                                "weatherCode": "353",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Light rain shower"
                                    }
                                ],
                                "precipMM": "1.1",
                                "precipInches": "0.0",
                                "humidity": "65",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1013",
                                "pressureInches": "30",
                                "cloudcover": "87",
                                "HeatIndexC": "31",
                                "HeatIndexF": "88",
                                "DewPointC": "21",
                                "DewPointF": "70",
                                "WindChillC": "28",
                                "WindChillF": "83",
                                "WindGustMiles": "16",
                                "WindGustKmph": "25",
                                "FeelsLikeC": "31",
                                "FeelsLikeF": "88",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "50",
                                "swellDir16Point": "NE",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1200",
                                "tempC": "29",
                                "tempF": "84",
                                "windspeedMiles": "9",
                                "windspeedKmph": "14",
                                "winddirDegree": "56",
                                "winddir16Point": "ENE",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0002_sunny_intervals.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "66",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1010",
                                "pressureInches": "30",
                                "cloudcover": "25",
                                "HeatIndexC": "32",
                                "HeatIndexF": "89",
                                "DewPointC": "22",
                                "DewPointF": "71",
                                "WindChillC": "29",
                                "WindChillF": "84",
                                "WindGustMiles": "15",
                                "WindGustKmph": "24",
                                "FeelsLikeC": "32",
                                "FeelsLikeF": "89",
                                "sigHeight_m": "0.3",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "7"
                            },
                            {
                                "time": "1500",
                                "tempC": "27",
                                "tempF": "81",
                                "windspeedMiles": "6",
                                "windspeedKmph": "9",
                                "winddirDegree": "33",
                                "winddir16Point": "NNE",
                                "weatherCode": "353",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Light rain shower"
                                    }
                                ],
                                "precipMM": "1.2",
                                "precipInches": "0.0",
                                "humidity": "75",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1009",
                                "pressureInches": "30",
                                "cloudcover": "67",
                                "HeatIndexC": "30",
                                "HeatIndexF": "86",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "27",
                                "WindChillF": "81",
                                "WindGustMiles": "8",
                                "WindGustKmph": "13",
                                "FeelsLikeC": "30",
                                "FeelsLikeF": "86",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1800",
                                "tempC": "27",
                                "tempF": "80",
                                "windspeedMiles": "6",
                                "windspeedKmph": "10",
                                "winddirDegree": "32",
                                "winddir16Point": "NNE",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "0.1",
                                "precipInches": "0.0",
                                "humidity": "77",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "62",
                                "HeatIndexC": "29",
                                "HeatIndexF": "85",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "27",
                                "WindChillF": "80",
                                "WindGustMiles": "9",
                                "WindGustKmph": "15",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "85",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "6"
                            },
                            {
                                "time": "2100",
                                "tempC": "27",
                                "tempF": "80",
                                "windspeedMiles": "6",
                                "windspeedKmph": "10",
                                "winddirDegree": "16",
                                "winddir16Point": "NNE",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "78",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "42",
                                "HeatIndexC": "29",
                                "HeatIndexF": "85",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "27",
                                "WindChillF": "80",
                                "WindGustMiles": "6",
                                "WindGustKmph": "10",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "85",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            }
                        ]
                    },
                    {
                        "date": "2021-10-22",
                        "astronomy": [
                            {
                                "sunrise": "06:46 AM",
                                "sunset": "06:51 PM",
                                "moonrise": "08:10 PM",
                                "moonset": "07:51 AM",
                                "moon_phase": "Waning Gibbous",
                                "moon_illumination": "83"
                            }
                        ],
                        "maxtempC": "29",
                        "maxtempF": "84",
                        "mintempC": "25",
                        "mintempF": "78",
                        "uvIndex": "7",
                        "hourly": [
                            {
                                "time": "0",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "4",
                                "windspeedKmph": "6",
                                "winddirDegree": "338",
                                "winddir16Point": "NNW",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "81",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1010",
                                "pressureInches": "30",
                                "cloudcover": "44",
                                "HeatIndexC": "29",
                                "HeatIndexF": "84",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "7",
                                "WindGustKmph": "11",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "84",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "1"
                            },
                            {
                                "time": "300",
                                "tempC": "25",
                                "tempF": "78",
                                "windspeedMiles": "1",
                                "windspeedKmph": "2",
                                "winddirDegree": "111",
                                "winddir16Point": "ESE",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0025_light_rain_showers_night.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "1.4",
                                "precipInches": "0.1",
                                "humidity": "85",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1010",
                                "pressureInches": "30",
                                "cloudcover": "71",
                                "HeatIndexC": "28",
                                "HeatIndexF": "82",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "25",
                                "WindChillF": "78",
                                "WindGustMiles": "7",
                                "WindGustKmph": "11",
                                "FeelsLikeC": "28",
                                "FeelsLikeF": "82",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "1"
                            },
                            {
                                "time": "600",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "5",
                                "windspeedKmph": "8",
                                "winddirDegree": "171",
                                "winddir16Point": "S",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "82",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "27",
                                "HeatIndexC": "29",
                                "HeatIndexF": "84",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "11",
                                "WindGustKmph": "18",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "84",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "1"
                            },
                            {
                                "time": "900",
                                "tempC": "28",
                                "tempF": "82",
                                "windspeedMiles": "4",
                                "windspeedKmph": "6",
                                "winddirDegree": "147",
                                "winddir16Point": "SSE",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "1.3",
                                "precipInches": "0.1",
                                "humidity": "68",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "83",
                                "HeatIndexC": "31",
                                "HeatIndexF": "87",
                                "DewPointC": "21",
                                "DewPointF": "71",
                                "WindChillC": "28",
                                "WindChillF": "82",
                                "WindGustMiles": "17",
                                "WindGustKmph": "28",
                                "FeelsLikeC": "31",
                                "FeelsLikeF": "87",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1200",
                                "tempC": "29",
                                "tempF": "84",
                                "windspeedMiles": "5",
                                "windspeedKmph": "8",
                                "winddirDegree": "79",
                                "winddir16Point": "E",
                                "weatherCode": "353",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Light rain shower"
                                    }
                                ],
                                "precipMM": "0.8",
                                "precipInches": "0.0",
                                "humidity": "66",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1010",
                                "pressureInches": "30",
                                "cloudcover": "72",
                                "HeatIndexC": "32",
                                "HeatIndexF": "89",
                                "DewPointC": "22",
                                "DewPointF": "71",
                                "WindChillC": "29",
                                "WindChillF": "84",
                                "WindGustMiles": "14",
                                "WindGustKmph": "22",
                                "FeelsLikeC": "32",
                                "FeelsLikeF": "89",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1500",
                                "tempC": "29",
                                "tempF": "84",
                                "windspeedMiles": "6",
                                "windspeedKmph": "9",
                                "winddirDegree": "47",
                                "winddir16Point": "NE",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "1.6",
                                "precipInches": "0.1",
                                "humidity": "66",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1009",
                                "pressureInches": "30",
                                "cloudcover": "76",
                                "HeatIndexC": "32",
                                "HeatIndexF": "89",
                                "DewPointC": "22",
                                "DewPointF": "71",
                                "WindChillC": "29",
                                "WindChillF": "84",
                                "WindGustMiles": "19",
                                "WindGustKmph": "31",
                                "FeelsLikeC": "32",
                                "FeelsLikeF": "89",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1800",
                                "tempC": "28",
                                "tempF": "82",
                                "windspeedMiles": "6",
                                "windspeedKmph": "9",
                                "winddirDegree": "348",
                                "winddir16Point": "NNW",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "1.2",
                                "precipInches": "0.0",
                                "humidity": "74",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "70",
                                "HeatIndexC": "30",
                                "HeatIndexF": "87",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "28",
                                "WindChillF": "82",
                                "WindGustMiles": "6",
                                "WindGustKmph": "9",
                                "FeelsLikeC": "30",
                                "FeelsLikeF": "87",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "6"
                            },
                            {
                                "time": "2100",
                                "tempC": "27",
                                "tempF": "80",
                                "windspeedMiles": "7",
                                "windspeedKmph": "12",
                                "winddirDegree": "337",
                                "winddir16Point": "NNW",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "78",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "33",
                                "HeatIndexC": "30",
                                "HeatIndexF": "85",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "27",
                                "WindChillF": "80",
                                "WindGustMiles": "14",
                                "WindGustKmph": "23",
                                "FeelsLikeC": "30",
                                "FeelsLikeF": "85",
                                "sigHeight_m": "0.3",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "72",
                                "uvIndex": "1"
                            }
                        ]
                    },
                    {
                        "date": "2021-10-23",
                        "astronomy": [
                            {
                                "sunrise": "06:46 AM",
                                "sunset": "06:51 PM",
                                "moonrise": "08:55 PM",
                                "moonset": "08:35 AM",
                                "moon_phase": "Waning Gibbous",
                                "moon_illumination": "76"
                            }
                        ],
                        "maxtempC": "29",
                        "maxtempF": "84",
                        "mintempC": "26",
                        "mintempF": "79",
                        "uvIndex": "7",
                        "hourly": [
                            {
                                "time": "0",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "6",
                                "windspeedKmph": "9",
                                "winddirDegree": "340",
                                "winddir16Point": "NNW",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "80",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "24",
                                "HeatIndexC": "29",
                                "HeatIndexF": "84",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "6",
                                "WindGustKmph": "10",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "84",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            },
                            {
                                "time": "300",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "1",
                                "windspeedKmph": "1",
                                "winddirDegree": "105",
                                "winddir16Point": "ESE",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0025_light_rain_showers_night.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "1.6",
                                "precipInches": "0.1",
                                "humidity": "81",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1010",
                                "pressureInches": "30",
                                "cloudcover": "86",
                                "HeatIndexC": "29",
                                "HeatIndexF": "84",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "8",
                                "WindGustKmph": "13",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "84",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            },
                            {
                                "time": "600",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "5",
                                "windspeedKmph": "8",
                                "winddirDegree": "169",
                                "winddir16Point": "SSE",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "80",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "30",
                                "HeatIndexC": "29",
                                "HeatIndexF": "84",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "6",
                                "WindGustKmph": "9",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "84",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            },
                            {
                                "time": "900",
                                "tempC": "28",
                                "tempF": "83",
                                "windspeedMiles": "4",
                                "windspeedKmph": "6",
                                "winddirDegree": "228",
                                "winddir16Point": "SW",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "2.3",
                                "precipInches": "0.1",
                                "humidity": "65",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "75",
                                "HeatIndexC": "31",
                                "HeatIndexF": "87",
                                "DewPointC": "21",
                                "DewPointF": "70",
                                "WindChillC": "28",
                                "WindChillF": "83",
                                "WindGustMiles": "11",
                                "WindGustKmph": "17",
                                "FeelsLikeC": "31",
                                "FeelsLikeF": "87",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1200",
                                "tempC": "29",
                                "tempF": "84",
                                "windspeedMiles": "4",
                                "windspeedKmph": "6",
                                "winddirDegree": "165",
                                "winddir16Point": "SSE",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "1.9",
                                "precipInches": "0.1",
                                "humidity": "62",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1010",
                                "pressureInches": "30",
                                "cloudcover": "72",
                                "HeatIndexC": "32",
                                "HeatIndexF": "89",
                                "DewPointC": "21",
                                "DewPointF": "70",
                                "WindChillC": "29",
                                "WindChillF": "84",
                                "WindGustMiles": "13",
                                "WindGustKmph": "20",
                                "FeelsLikeC": "32",
                                "FeelsLikeF": "89",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1500",
                                "tempC": "29",
                                "tempF": "83",
                                "windspeedMiles": "3",
                                "windspeedKmph": "5",
                                "winddirDegree": "182",
                                "winddir16Point": "S",
                                "weatherCode": "353",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Light rain shower"
                                    }
                                ],
                                "precipMM": "1.2",
                                "precipInches": "0.0",
                                "humidity": "67",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1009",
                                "pressureInches": "30",
                                "cloudcover": "89",
                                "HeatIndexC": "31",
                                "HeatIndexF": "89",
                                "DewPointC": "22",
                                "DewPointF": "71",
                                "WindChillC": "29",
                                "WindChillF": "83",
                                "WindGustMiles": "14",
                                "WindGustKmph": "23",
                                "FeelsLikeC": "31",
                                "FeelsLikeF": "89",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1800",
                                "tempC": "28",
                                "tempF": "82",
                                "windspeedMiles": "5",
                                "windspeedKmph": "8",
                                "winddirDegree": "235",
                                "winddir16Point": "SW",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "2.0",
                                "precipInches": "0.1",
                                "humidity": "71",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "74",
                                "HeatIndexC": "30",
                                "HeatIndexF": "87",
                                "DewPointC": "22",
                                "DewPointF": "71",
                                "WindChillC": "28",
                                "WindChillF": "82",
                                "WindGustMiles": "16",
                                "WindGustKmph": "26",
                                "FeelsLikeC": "30",
                                "FeelsLikeF": "87",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "6"
                            },
                            {
                                "time": "2100",
                                "tempC": "27",
                                "tempF": "81",
                                "windspeedMiles": "7",
                                "windspeedKmph": "11",
                                "winddirDegree": "294",
                                "winddir16Point": "WNW",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0025_light_rain_showers_night.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "0.2",
                                "precipInches": "0.0",
                                "humidity": "73",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "85",
                                "HeatIndexC": "30",
                                "HeatIndexF": "85",
                                "DewPointC": "22",
                                "DewPointF": "71",
                                "WindChillC": "27",
                                "WindChillF": "81",
                                "WindGustMiles": "16",
                                "WindGustKmph": "26",
                                "FeelsLikeC": "30",
                                "FeelsLikeF": "85",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            }
                        ]
                    },
                    {
                        "date": "2021-10-24",
                        "astronomy": [
                            {
                                "sunrise": "06:46 AM",
                                "sunset": "06:51 PM",
                                "moonrise": "09:42 PM",
                                "moonset": "09:22 AM",
                                "moon_phase": "Last Quarter",
                                "moon_illumination": "69"
                            }
                        ],
                        "maxtempC": "29",
                        "maxtempF": "84",
                        "mintempC": "26",
                        "mintempF": "79",
                        "uvIndex": "6",
                        "hourly": [
                            {
                                "time": "0",
                                "tempC": "27",
                                "tempF": "80",
                                "windspeedMiles": "9",
                                "windspeedKmph": "14",
                                "winddirDegree": "300",
                                "winddir16Point": "WNW",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0025_light_rain_showers_night.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "0.5",
                                "precipInches": "0.0",
                                "humidity": "76",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "88",
                                "HeatIndexC": "29",
                                "HeatIndexF": "85",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "27",
                                "WindChillF": "80",
                                "WindGustMiles": "18",
                                "WindGustKmph": "29",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "85",
                                "sigHeight_m": "0.3",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            },
                            {
                                "time": "300",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "7",
                                "windspeedKmph": "12",
                                "winddirDegree": "279",
                                "winddir16Point": "W",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0025_light_rain_showers_night.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "0.1",
                                "precipInches": "0.0",
                                "humidity": "81",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1009",
                                "pressureInches": "30",
                                "cloudcover": "89",
                                "HeatIndexC": "29",
                                "HeatIndexF": "83",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "8",
                                "WindGustKmph": "13",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "83",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            },
                            {
                                "time": "600",
                                "tempC": "26",
                                "tempF": "79",
                                "windspeedMiles": "13",
                                "windspeedKmph": "22",
                                "winddirDegree": "238",
                                "winddir16Point": "WSW",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "81",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "27",
                                "HeatIndexC": "29",
                                "HeatIndexF": "84",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "79",
                                "WindGustMiles": "22",
                                "WindGustKmph": "36",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "84",
                                "sigHeight_m": "0.5",
                                "swellHeight_m": "0.2",
                                "swellHeight_ft": "0.7",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            },
                            {
                                "time": "900",
                                "tempC": "28",
                                "tempF": "83",
                                "windspeedMiles": "9",
                                "windspeedKmph": "14",
                                "winddirDegree": "252",
                                "winddir16Point": "WSW",
                                "weatherCode": "176",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0009_light_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Patchy rain possible"
                                    }
                                ],
                                "precipMM": "1.1",
                                "precipInches": "0.0",
                                "humidity": "65",
                                "visibility": "9",
                                "visibilityMiles": "5",
                                "pressure": "1012",
                                "pressureInches": "30",
                                "cloudcover": "78",
                                "HeatIndexC": "31",
                                "HeatIndexF": "87",
                                "DewPointC": "21",
                                "DewPointF": "70",
                                "WindChillC": "28",
                                "WindChillF": "83",
                                "WindGustMiles": "9",
                                "WindGustKmph": "15",
                                "FeelsLikeC": "31",
                                "FeelsLikeF": "87",
                                "sigHeight_m": "0.3",
                                "swellHeight_m": "0.2",
                                "swellHeight_ft": "0.7",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "3.2",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1200",
                                "tempC": "29",
                                "tempF": "84",
                                "windspeedMiles": "4",
                                "windspeedKmph": "7",
                                "winddirDegree": "333",
                                "winddir16Point": "NNW",
                                "weatherCode": "116",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0002_sunny_intervals.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Partly cloudy"
                                    }
                                ],
                                "precipMM": "0.0",
                                "precipInches": "0.0",
                                "humidity": "67",
                                "visibility": "10",
                                "visibilityMiles": "6",
                                "pressure": "1009",
                                "pressureInches": "30",
                                "cloudcover": "55",
                                "HeatIndexC": "33",
                                "HeatIndexF": "91",
                                "DewPointC": "22",
                                "DewPointF": "72",
                                "WindChillC": "29",
                                "WindChillF": "84",
                                "WindGustMiles": "12",
                                "WindGustKmph": "19",
                                "FeelsLikeC": "33",
                                "FeelsLikeF": "91",
                                "sigHeight_m": "0.1",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "190",
                                "swellDir16Point": "S",
                                "swellPeriod_secs": "2.0",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "7"
                            },
                            {
                                "time": "1500",
                                "tempC": "29",
                                "tempF": "83",
                                "windspeedMiles": "7",
                                "windspeedKmph": "11",
                                "winddirDegree": "34",
                                "winddir16Point": "NNE",
                                "weatherCode": "356",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0010_heavy_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Moderate or heavy rain shower"
                                    }
                                ],
                                "precipMM": "5.4",
                                "precipInches": "0.2",
                                "humidity": "72",
                                "visibility": "7",
                                "visibilityMiles": "4",
                                "pressure": "1008",
                                "pressureInches": "30",
                                "cloudcover": "65",
                                "HeatIndexC": "32",
                                "HeatIndexF": "90",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "29",
                                "WindChillF": "83",
                                "WindGustMiles": "10",
                                "WindGustKmph": "15",
                                "FeelsLikeC": "32",
                                "FeelsLikeF": "90",
                                "sigHeight_m": "0.2",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "190",
                                "swellDir16Point": "S",
                                "swellPeriod_secs": "2.0",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "6"
                            },
                            {
                                "time": "1800",
                                "tempC": "27",
                                "tempF": "81",
                                "windspeedMiles": "11",
                                "windspeedKmph": "18",
                                "winddirDegree": "289",
                                "winddir16Point": "WNW",
                                "weatherCode": "356",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0010_heavy_rain_showers.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Moderate or heavy rain shower"
                                    }
                                ],
                                "precipMM": "6.7",
                                "precipInches": "0.3",
                                "humidity": "78",
                                "visibility": "7",
                                "visibilityMiles": "4",
                                "pressure": "1010",
                                "pressureInches": "30",
                                "cloudcover": "60",
                                "HeatIndexC": "30",
                                "HeatIndexF": "86",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "27",
                                "WindChillF": "81",
                                "WindGustMiles": "23",
                                "WindGustKmph": "36",
                                "FeelsLikeC": "30",
                                "FeelsLikeF": "86",
                                "sigHeight_m": "0.4",
                                "swellHeight_m": "0.1",
                                "swellHeight_ft": "0.3",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "2.0",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "6"
                            },
                            {
                                "time": "2100",
                                "tempC": "26",
                                "tempF": "80",
                                "windspeedMiles": "12",
                                "windspeedKmph": "20",
                                "winddirDegree": "286",
                                "winddir16Point": "WNW",
                                "weatherCode": "356",
                                "weatherIconUrl": [
                                    {
                                        "value": "http://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0026_heavy_rain_showers_night.png"
                                    }
                                ],
                                "weatherDesc": [
                                    {
                                        "value": "Moderate or heavy rain shower"
                                    }
                                ],
                                "precipMM": "5.7",
                                "precipInches": "0.2",
                                "humidity": "80",
                                "visibility": "7",
                                "visibilityMiles": "4",
                                "pressure": "1011",
                                "pressureInches": "30",
                                "cloudcover": "78",
                                "HeatIndexC": "29",
                                "HeatIndexF": "85",
                                "DewPointC": "23",
                                "DewPointF": "73",
                                "WindChillC": "26",
                                "WindChillF": "80",
                                "WindGustMiles": "21",
                                "WindGustKmph": "34",
                                "FeelsLikeC": "29",
                                "FeelsLikeF": "85",
                                "sigHeight_m": "0.5",
                                "swellHeight_m": "0.2",
                                "swellHeight_ft": "0.7",
                                "swellDir": "80",
                                "swellDir16Point": "E",
                                "swellPeriod_secs": "2.0",
                                "waterTemp_C": "22",
                                "waterTemp_F": "71",
                                "uvIndex": "1"
                            }
                        ]
                    }
                ]
            }
        }
)
    
    HOGCV = cv2.HOGDescriptor()
    HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    count = humanDetector(ipCamUrl)
    latest_sensor_data = ''
    daily_sensor_list = ''
    monthly_sensor_list = ''

    if len(r.lrange("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", 0, -1)) > 0:
        latest_sensor_data = json.loads(r.lrange("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", -1, -1)[0]) 
        dailySensorList = r.lrange('38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION', 0, -1)[::-1]
        total_temperature_for_current_day = 0
        total_humidity_for_current_day = 0
        total_pressure_for_current_day = 0
        total_intensity_for_current_day = 0
        total_no_of_data_for_current_day = 0
        total_temperature_for_current_month = 0
        total_humidity_for_current_month = 0
        total_pressure_for_current_month = 0
        total_intensity_for_current_month = 0
        total_no_of_data_for_current_month = 0

        for index in range(0, len(dailySensorList)):
            jsonobj = json.loads(dailySensorList[index])
            eventdate = datetime.datetime.strptime(jsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')
            eventyear = eventdate.year
            eventmonth = eventdate.month
            eventday = eventdate.day
            previousjsonobj = json.loads(dailySensorList[index-1])
            previouseventdate = datetime.datetime.strptime(previousjsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')

            if index > 0 and index < len(dailySensorList)-1: #if we between 2nd to 2nd last item
                if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month):
                    total_temperature_for_current_month+=jsonobj['ambientTemperature']
                    total_humidity_for_current_month+=jsonobj['ambientHumidity']
                    total_pressure_for_current_month+=jsonobj['ambientPressure']
                    total_intensity_for_current_month+=jsonobj['ambientLight']
                    total_no_of_data_for_current_month+=1
                    if eventday == previouseventdate.day:
                        total_temperature_for_current_day+=jsonobj['ambientTemperature']
                        total_humidity_for_current_day+=jsonobj['ambientHumidity']
                        total_pressure_for_current_day+=jsonobj['ambientPressure']
                        total_intensity_for_current_day+=jsonobj['ambientLight']

                        total_no_of_data_for_current_day+=1
                    else:
                        daily_sensor_list+=json.dumps({"date": str(previouseventdate), "ambientTemperature": total_temperature_for_current_day/total_no_of_data_for_current_day, "ambientHumidity": total_humidity_for_current_day/total_no_of_data_for_current_day, "ambientPressure": total_pressure_for_current_day/total_no_of_data_for_current_day, "ambientLight": total_intensity_for_current_day/total_no_of_data_for_current_day}) + '|'
                        total_temperature_for_current_day = jsonobj['ambientTemperature']
                        total_humidity_for_current_day = jsonobj['ambientHumidity']
                        total_pressure_for_current_day = jsonobj['ambientPressure']
                        total_intensity_for_current_day = jsonobj['ambientLight']

                        total_no_of_data_for_current_day = 1
                else:
                    daily_sensor_list+=json.dumps({"date": str(previouseventdate), "ambientTemperature": total_temperature_for_current_day/total_no_of_data_for_current_day, "ambientHumidity": total_humidity_for_current_day/total_no_of_data_for_current_day, "ambientPressure": total_pressure_for_current_day/total_no_of_data_for_current_day, "ambientLight": total_intensity_for_current_day/total_no_of_data_for_current_day}) + '|'
                    total_temperature_for_current_day = jsonobj['ambientTemperature']
                    total_humidity_for_current_day = jsonobj['ambientHumidity']
                    total_pressure_for_current_day = jsonobj['ambientPressure']
                    total_intensity_for_current_day = jsonobj['ambientLight']

                    total_no_of_data_for_current_day = 1
                    monthly_sensor_list+=json.dumps({"date": str(previouseventdate), "ambientTemperature": total_temperature_for_current_month/total_no_of_data_for_current_month, "ambientHumidity": total_humidity_for_current_day/total_no_of_data_for_current_month, "ambientPressure": total_pressure_for_current_day/total_no_of_data_for_current_month, "ambientLight": total_intensity_for_current_day/total_no_of_data_for_current_month}) + '|'
                    total_temperature_for_current_month = jsonobj['ambientTemperature']
                    total_humidity_for_current_month = jsonobj['ambientHumidity']
                    total_pressure_for_current_month = jsonobj['ambientPressure']
                    total_intensity_for_current_month = jsonobj['ambientLight']

                    total_no_of_data_for_current_month = 1
            elif index == len(dailySensorList)-1: #if we are at the last item
                if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month):
                    total_temperature_for_current_month+=jsonobj['ambientTemperature']
                    total_humidity_for_current_month+=jsonobj['ambientHumidity']
                    total_pressure_for_current_month+=jsonobj['ambientPressure']
                    total_intensity_for_current_month+=jsonobj['ambientLight']

                    total_no_of_data_for_current_month+=1
                    monthly_sensor_list+=json.dumps({"date": str(eventdate), "ambientTemperature": total_temperature_for_current_month/total_no_of_data_for_current_month, "ambientHumidity": total_humidity_for_current_day/total_no_of_data_for_current_month, "ambientPressure": total_pressure_for_current_day/total_no_of_data_for_current_month, "ambientLight": total_intensity_for_current_day/total_no_of_data_for_current_month}) + '|'

                    if eventday == previouseventdate.day:
                        total_temperature_for_current_day+=jsonobj['ambientTemperature']
                        total_humidity_for_current_day+= jsonobj['ambientHumidity']
                        total_pressure_for_current_day+= jsonobj['ambientPressure']
                        total_intensity_for_current_day+= jsonobj['ambientLight']
                        total_no_of_data_for_current_day+=1
                        daily_sensor_list+=json.dumps({"date": str(eventdate), "ambientTemperature": total_temperature_for_current_day/total_no_of_data_for_current_day, "ambientHumidity": total_humidity_for_current_day/total_no_of_data_for_current_day, "ambientPressure": total_pressure_for_current_day/total_no_of_data_for_current_day, "ambientLight": total_intensity_for_current_day/total_no_of_data_for_current_day}) + '|'
                    else:
                        daily_sensor_list+=json.dumps({"date": str(previouseventdate), "ambientTemperature": total_temperature_for_current_day/total_no_of_data_for_current_day, "ambientHumidity": total_humidity_for_current_day/total_no_of_data_for_current_day, "ambientPressure": total_pressure_for_current_day/total_no_of_data_for_current_day, "ambientLight": total_intensity_for_current_day/total_no_of_data_for_current_day}) + '|'
                        total_temperature_for_current_day = jsonobj['ambientTemperature']
                        total_humidity_for_current_day = jsonobj['ambientHumidity']
                        total_pressure_for_current_day = jsonobj['ambientPressure']
                        total_intensity_for_current_day = jsonobj['ambientLight']
                        total_no_of_data_for_current_day = 1
                        daily_sensor_list+=json.dumps({"date": str(eventdate), "ambientTemperature": total_temperature_for_current_day/total_no_of_data_for_current_day, "ambientHumidity": total_humidity_for_current_day/total_no_of_data_for_current_day, "ambientPressure": total_pressure_for_current_day/total_no_of_data_for_current_day, "ambientLight": total_intensity_for_current_day/total_no_of_data_for_current_day}) + '|'
                else:
                    daily_sensor_list+=json.dumps({"date": str(previouseventdate), "ambientTemperature": total_temperature_for_current_day/total_no_of_data_for_current_day, "ambientHumidity": total_humidity_for_current_day/total_no_of_data_for_current_day, "ambientPressure": total_pressure_for_current_day/total_no_of_data_for_current_day, "ambientLight": total_intensity_for_current_day/total_no_of_data_for_current_day}) + '|'
                    total_temperature_for_current_day = jsonobj['ambientTemperature']
                    total_humidity_for_current_day = jsonobj['ambientHumidity']
                    total_pressure_for_current_day = jsonobj['ambientPressure']
                    total_intensity_for_current_day = jsonobj['ambientLight']
                    total_no_of_data_for_current_day = 1
                    daily_sensor_list+=json.dumps({"date": str(eventdate), "ambientTemperature": total_temperature_for_current_day/total_no_of_data_for_current_day, "ambientHumidity": total_humidity_for_current_day/total_no_of_data_for_current_day, "ambientPressure": total_pressure_for_current_day/total_no_of_data_for_current_day, "ambientLight": total_intensity_for_current_day/total_no_of_data_for_current_day}) + '|'
                    monthly_sensor_list+=json.dumps({"date": str(previouseventdate), "ambientTemperature": total_temperature_for_current_month/total_no_of_data_for_current_month, "ambientHumidity": total_humidity_for_current_day/total_no_of_data_for_current_month, "ambientPressure": total_pressure_for_current_day/total_no_of_data_for_current_month, "ambientLight": total_intensity_for_current_day/total_no_of_data_for_current_month}) + '|'
                    total_temperature_for_current_month = jsonobj['ambientTemperature']
                    total_humidity_for_current_month = jsonobj['ambientHumidity']
                    total_pressure_for_current_month = jsonobj['ambientPressure']
                    total_intensity_for_current_month = jsonobj['ambientLight']

                    total_no_of_data_for_current_month = 1
                    monthly_sensor_list+=json.dumps({"date": str(eventdate), "ambientTemperature": total_temperature_for_current_month/total_no_of_data_for_current_month, "ambientHumidity": total_humidity_for_current_day/total_no_of_data_for_current_month, "ambientPressure": total_pressure_for_current_day/total_no_of_data_for_current_month, "ambientLight": total_intensity_for_current_day/total_no_of_data_for_current_month}) + '|'
            elif index == 0: #if we are at the first item
                total_temperature_for_current_day+=jsonobj['ambientTemperature']
                total_humidity_for_current_day+= jsonobj['ambientHumidity']
                total_pressure_for_current_day+= jsonobj['ambientPressure']
                total_intensity_for_current_day+= jsonobj['ambientLight']
                total_no_of_data_for_current_day+=1
                
                total_temperature_for_current_month+=jsonobj['ambientTemperature']
                total_humidity_for_current_month+=jsonobj['ambientHumidity']
                total_pressure_for_current_month+=jsonobj['ambientPressure']
                total_intensity_for_current_month+=jsonobj['ambientLight']
                total_no_of_data_for_current_month+=1



    daily_visitor_history_count = ''
    monthly_visitor_history_count = ''
    if len(r.lrange('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', 0, -1)) > 0:
        dailyPopulationList = r.lrange('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', 0, -1)[::-1]
        total_number_of_people_for_current_day = 0
        total_no_of_data_for_current_day = 0
        total_number_of_people_for_current_month = 0
        total_no_of_data_for_current_month = 0

        for index in range(0, len(dailyPopulationList)):
            jsonobj = json.loads(dailyPopulationList[index])
            eventdate = datetime.datetime.strptime(jsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')
            eventyear = eventdate.year
            eventmonth = eventdate.month
            eventday = eventdate.day
            previousjsonobj = json.loads(dailyPopulationList[index-1])
            previouseventdate = datetime.datetime.strptime(previousjsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')

            if index > 0 and index < len(dailyPopulationList)-1: #if we between 2nd to 2nd last item
                if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month):
                    total_number_of_people_for_current_month+=jsonobj['people_count']
                    total_no_of_data_for_current_month+=1
                    if eventday == previouseventdate.day:
                        total_number_of_people_for_current_day+=jsonobj['people_count']
                        total_no_of_data_for_current_day+=1
                    else:
                        daily_visitor_history_count+=json.dumps({"date": str(previouseventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day}) + '|'
                        total_number_of_people_for_current_day = jsonobj['people_count']
                        total_no_of_data_for_current_day = 1
                else:
                    daily_visitor_history_count+=json.dumps({"date": str(previouseventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day}) + '|'
                    total_number_of_people_for_current_day = jsonobj['people_count']
                    total_no_of_data_for_current_day = 1
                    monthly_visitor_history_count+=json.dumps({"date": str(previouseventdate), "count": total_number_of_people_for_current_month/total_no_of_data_for_current_month}) + '|'
                    total_number_of_people_for_current_month = jsonobj['people_count']
                    total_no_of_data_for_current_month = 1
            elif index == len(dailyPopulationList)-1: #if we are at the last item
                if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month):
                    total_number_of_people_for_current_month+=jsonobj['people_count']
                    total_no_of_data_for_current_month+=1
                    monthly_visitor_history_count+=json.dumps({"date": str(eventdate), "count": total_number_of_people_for_current_month/total_no_of_data_for_current_month}) + '|'

                    if eventday == previouseventdate.day:
                        total_number_of_people_for_current_day+=jsonobj['people_count']
                        total_no_of_data_for_current_day+=1
                        daily_visitor_history_count+=json.dumps({"date": str(eventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day}) + '|'
                    else:
                        daily_visitor_history_count+=json.dumps({"date": str(previouseventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day}) + '|'
                        total_number_of_people_for_current_day = jsonobj['people_count']
                        total_no_of_data_for_current_day = 1
                        daily_visitor_history_count+=json.dumps({"date": str(eventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day}) + '|'
                else:
                    daily_visitor_history_count+=json.dumps({"date": str(previouseventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day}) + '|'
                    total_number_of_people_for_current_day = jsonobj['people_count']
                    total_no_of_data_for_current_day = 1
                    daily_visitor_history_count+=json.dumps({"date": str(eventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day}) + '|'
                    monthly_visitor_history_count+=json.dumps({"date": str(previouseventdate), "count": total_number_of_people_for_current_month/total_no_of_data_for_current_month}) + '|'
                    total_number_of_people_for_current_month = jsonobj['people_count']
                    total_no_of_data_for_current_month = 1
                    monthly_visitor_history_count+=json.dumps({"date": str(eventdate), "count": total_number_of_people_for_current_month/total_no_of_data_for_current_month}) + '|'
            elif index == 0: #if we are at the first item
                total_number_of_people_for_current_day+=jsonobj['people_count']
                total_no_of_data_for_current_day+=1
                total_number_of_people_for_current_month+=jsonobj['people_count']
                total_no_of_data_for_current_month+=1
            
    try:
        response = requests.get(
            ipCamUrl, timeout=10)
        file = open(os.path.dirname(os.path.abspath(__file__)) + "/static/image/image.png", "wb")
        file.write(response.content)
        file.close()
    except:
        print("Your ipCamUrl must be down.")
    return render_template("dashboard.html", daily_sensor_list=daily_sensor_list[:-1], monthly_visitor_history_count=monthly_visitor_history_count[:-1], daily_visitor_history_count=daily_visitor_history_count[:-1], people_count=count, data=item_list[:-1], forecast_data=forecast_data, next_day_forecast=json.dumps(json.loads(forecast_data)["data"]["weather"][0]), latest_sensor_data=json.dumps(latest_sensor_data))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
