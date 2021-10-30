import redis
import datetime
import json
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

r.rpush("devices", "{\"thingId\": \"38ED5BF550EE4CC6AD2BE9A7BE7111A4\", \"deviceId\": \"dcac5d23-cf60-44ff-82e8-b1fb4fd69efb\", \"sensorId\": \"f1ff9a46-86f7-47ef-befb-ccb8a76b90a8\", \"commandCapabilityId\": \"24c65333-6630-46d2-b4b8-69ca3f3786df\", \"coordinate\": {\"lat\": \"1.3050856285437102\", \"lng\": \"103.93210128266621\"}, \"zone\": \"East Coast Park Zone 1\"}")
r.rpush("devices", "{\"thingId\": \"38ED5BF550EE4CC6AD2BE9A7BE7111AZ\", \"deviceId\": \"dcac5d23-cf6z0-44ff-82e8-b1fb4fd69efb\", \"sensorId\": \"f1ff9a46-86f7-47ef-befb-ccb8a76b90a8\", \"commandCapabilityId\": \"24c65333-6630-46d2-b4b8-69ca3f3786df\", \"coordinate\": {\"lat\": \"1.3843981451960123\", \"lng\": \"104.00170223087149\"}, \"zone\": \"Changi Beach Zone 1\"}")

r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4", "{\"event\": \"strong_wave\", \"datetime\": \"2021-10-23 18:14:52.989580\", \"zone\": \"East Coast Park Zone 1\"}")

r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-24 18:11:12.808428\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 31.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 59, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-24 19:12:17.172217\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 23.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-24 20:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 27.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-24 21:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 24.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-25 19:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 32.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-25 20:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 27.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-25 21:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 34.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-25 22:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 21.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-26 18:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 28.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-26 19:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 27.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-26 20:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 31.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-26 21:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 24.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-27 18:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 26.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-27 19:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 34.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-27 20:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 31.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-27 21:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 27.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")

r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-19 13:32:22.091528\", \"people_count\": 3}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-19 13:37:25.670296\", \"people_count\": 8}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-19 13:42:29.376065\", \"people_count\": 5}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-20 14:05:04.475641\", \"people_count\": 18}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-20 14:10:07.984202\", \"people_count\": 2}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-20 14:21:53.574388\", \"people_count\": 7}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-21 14:26:57.173634\", \"people_count\": 16}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-21 13:32:22.091528\", \"people_count\": 3}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-21 13:37:25.670296\", \"people_count\": 8}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-22 13:42:29.376065\", \"people_count\": 15}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-22 14:05:04.475641\", \"people_count\": 8}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-22 14:10:07.984202\", \"people_count\": 12}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-23 14:21:53.574388\", \"people_count\": 7}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-23 14:26:57.173634\", \"people_count\": 15}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-24 14:21:53.574388\", \"people_count\": 7}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-24 14:26:57.173634\", \"people_count\": 9}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-24 16:32:22.091528\", \"people_count\": 3}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-25 13:32:22.091528\", \"people_count\": 12}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-25 15:32:22.091528\", \"people_count\": 8}")

data_list = []

if len(r.lrange("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", 0, -1)) > 0:
    latest_sensor_data = json.loads(r.lrange("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", -1, -1)[0]) 
    data_collection_list = r.lrange("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", 0, -1)[::-1]
    total_temperature_for_current_day = 0
    total_no_of_data_for_current_day = 0
    for index in range(0, len(data_collection_list)):
        jsonobj = json.loads(data_collection_list[index])
        eventdate = datetime.datetime.strptime(jsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')
        eventyear = eventdate.year
        eventmonth = eventdate.month
        eventday = eventdate.day
        previousjsonobj = json.loads(data_collection_list[index-1])
        previouseventdate = datetime.datetime.strptime(previousjsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')

        if index > 0 and index < len(data_collection_list)-1: #if we between 2nd to 2nd last item
            if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month and eventday == previouseventdate.day):
                total_temperature_for_current_day+=jsonobj['ambientTemperature']
                total_no_of_data_for_current_day+=1
            else:
                data_list.append(json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
                total_temperature_for_current_day = jsonobj['ambientTemperature']
                total_no_of_data_for_current_day = 1
        elif index == len(data_collection_list)-1: #if we are at the last item
            if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month and eventday == previouseventdate.day):
                total_temperature_for_current_day+=jsonobj['ambientTemperature']
                total_no_of_data_for_current_day+=1
                data_list.append(json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
            else:
                data_list.append(json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
                total_temperature_for_current_day = jsonobj['ambientTemperature']
                total_no_of_data_for_current_day = 1
                data_list.append(json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
        elif index == 0: #if we are at the first item
            total_temperature_for_current_day+=jsonobj['ambientTemperature']
            total_no_of_data_for_current_day+=1

print(data_list)

# a = None
# print(a == None)
# print(a is None)
# print(datetime.datetime.now() > datetime.datetime.strptime("2021-10-30 14:10:07.984202", '%Y-%m-%d %H:%M:%S.%f'))