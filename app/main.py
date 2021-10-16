from flask import Flask, jsonify, render_template
import redis
import json

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
