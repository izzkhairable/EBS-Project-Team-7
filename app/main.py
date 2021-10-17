from flask import Flask, jsonify, render_template
from imgurpython import ImgurClient
import redis
import json

app = Flask(__name__)

client_id = '3ef4beacee8d63c'
client_secret = '75640200bd814140c1e10fe3bd95ed65e9dd490d'
access_token = '8a06c8a86ac3ef93546cff4ea2cb42956cd60cf4'
refresh_token = '7e64f091f020ffc5486e9b6f8f97ce9b8ed2ad6e'
client = ImgurClient(client_id, client_secret, access_token, refresh_token)

@app.route("/", methods=["GET"])
def main():
    # redisHost = 'redis'
    # redisPort = '6379'
    # redisPassword = 'kPppOZp2hC'
    # redisDb = 5

    redisHost = "localhost"
    redisPort = "6379"
    redisPassword = ""
    redisDb = 0

    r = redis.Redis(
        host=redisHost,
        port=redisPort,
        db=int(redisDb),
        password=redisPassword,
        socket_timeout=None,
        decode_responses=True,
    )
    r.flushall()

    r.lpush(
        "things-data",
        """{
    "thingId": "38ED5BF550EE4CC6AD2BE9A7BE7111A4", 
    "deviceId": "dcac5d23-cf60-44ff-82e8-b1fb4fd69efb", 
    "sensorId": "f1ff9a46-86f7-47ef-befb-ccb8a76b90a8", 
    "commandCapabilityId": "24c65333-6630-46d2-b4b8-69ca3f3786df", 
    "coordinate": {"lat":"1.3050856285437102", "lng":"103.93210128266621"},
    "zone":"East Coast Park Zone 1",
    "status":"online"
    }""",
    )

    r.lpush(
        "things-data",
        """{
    "thingId": "38ED5BF550EE4CC6AD2BE9A7BE7111A4", 
    "deviceId": "dcac5d23-cf60-44ff-82e8-b1fb4fd69efb", 
    "sensorId": "f1ff9a46-86f7-47ef-befb-ccb8a76b90a8", 
    "commandCapabilityId": "24c65333-6630-46d2-b4b8-69ca3f3786df", 
    "coordinate": {"lat":"1.3883761", "lng":"103.9787106"},
    "zone":"Changi Beach Zone 1",
    "status":"offline"
    }""",
    )

    r.lpush(
        "alerts-data",
        '{"event": "strong_wave", "datetime": "2021-10-12T22:02:29.735563Z", "zone":"East Coast Park Zone 1"}',
    )

    r.lpush(
        "alerts-data",
        '{"event": "wet_device", "datetime": "2021-10-12T21:02:29.735563Z", "zone":"East Coast Park Zone 1"}',
    )

    r.lpush(
        "alerts-data",
        '{"event": "strong_wave", "datetime": "2021-10-13T20:02:29.735563Z", "zone":"Changi Beach Zone 1"}',
    )

    list_things_json_strings = r.lrange("things-data", 0, -1)
    things_data_list_dict = []
    for json_string in list_things_json_strings:
        things_data_list_dict.append(json.loads(json_string))

    list_alerts_json_strings = r.lrange("alerts-data", 0, -1)
    events_data_list_dict = []
    for json_string in list_alerts_json_strings:
        events_data_list_dict.append(json.loads(json_string))

    return render_template(
        "homepage.html",
        things_data=things_data_list_dict,
        events_data=events_data_list_dict,
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
    first_image_to_display = 'https://flxt.tmsimg.com/assets/p185179_b_v8_ab.jpg'
    if len(item_list) > 0:
        first_image_to_display = json.loads(item_list[:-1].split('|')[0])['link']
        last_image_to_display = json.loads(item_list[:-1].split('|')[-1])['link']
    return render_template("dashboard.html", data=item_list[:-1], data2=first_image_to_display, data3=last_image_to_display)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
