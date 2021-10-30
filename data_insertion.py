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


r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-09-24 18:11:12.808428\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 31.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 59, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-09-25 18:11:12.808428\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 34.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 59, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")

r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-19 18:11:12.808428\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 31.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 59, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-19 19:12:17.172217\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 23.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-19 20:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 27.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-20 19:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 32.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-20 20:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 27.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-20 21:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 34.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-21 18:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 28.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-21 19:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 27.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-21 20:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 31.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")




# r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-22 18:11:12.808428\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 31.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 59, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
# r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-22 18:11:12.808428\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 31.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 59, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
# r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-22 19:12:17.172217\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 23.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
# r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-23 20:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 27.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
# r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-23 19:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 32.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
# r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-24 20:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 27.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
# r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-24 21:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 34.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
# r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-24 18:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 28.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
# r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-25 19:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 27.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")
# r.rpush("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", "{\"datetime\": \"2021-10-25 20:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 31.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}")


r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-29 20:16:53.115025\", \"people_count\": 1}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-29 20:21:59.716455\", \"people_count\": 0}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-30 04:50:50.787477\", \"people_count\": 0}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-30 04:55:56.830324\", \"people_count\": 0}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-30 05:01:01.437206\", \"people_count\": 0}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-30 05:22:19.132869\", \"people_count\": 0}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-30 05:27:29.604053\", \"people_count\": 0}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-30 05:32:34.096403\", \"people_count\": 0}")
r.rpush('38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION', "{\"datetime\": \"2021-10-30 06:19:52.119898\", \"people_count\": 0}")

daily_data_list = []
monthly_data_list = []
if len(r.lrange("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", 0, -1)) > 0:
    latest_sensor_data = json.loads(r.lrange("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", -1, -1)[0]) 
    data_collection_list = r.lrange("38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION", 0, -1)[::-1]
    total_temperature_for_current_day = 0
    total_no_of_data_for_current_day = 0
    total_temperature_for_current_month = 0
    total_no_of_data_for_current_month = 0
    for index in range(0, len(data_collection_list)):  
        jsonobj = json.loads(data_collection_list[index])
        eventdate = datetime.datetime.strptime(jsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')
        eventyear = eventdate.year
        eventmonth = eventdate.month
        eventday = eventdate.day
        previousjsonobj = json.loads(data_collection_list[index-1])
        previouseventdate = datetime.datetime.strptime(previousjsonobj["datetime"], '%Y-%m-%d %H:%M:%S.%f')
        if index > 0 and index < len(data_collection_list)-1: #if we between 2nd to 2nd last item
            if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month):
                total_temperature_for_current_month+=jsonobj['ambientTemperature']
                total_no_of_data_for_current_month+=1
                if eventday == previouseventdate.day:
                    total_temperature_for_current_day+=jsonobj['ambientTemperature']
                    total_no_of_data_for_current_day+=1
                else:
                    daily_data_list.append(json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
                    total_temperature_for_current_day = jsonobj['ambientTemperature']
                    total_no_of_data_for_current_day = 1
            else:
                daily_data_list.append(json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
                total_temperature_for_current_day = jsonobj['ambientTemperature']
                total_no_of_data_for_current_day = 1
                monthly_data_list.append(json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_month/total_no_of_data_for_current_month}))
                total_temperature_for_current_month = jsonobj['ambientTemperature']
                total_no_of_data_for_current_month = 1
        elif index == len(data_collection_list)-1: #if we are at the last item
            if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month):
                total_temperature_for_current_month+=jsonobj['ambientTemperature']
                total_no_of_data_for_current_month+=1
                monthly_data_list.append(json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_month/total_no_of_data_for_current_month}))

                if eventday == previouseventdate.day:
                    total_temperature_for_current_day+=jsonobj['ambientTemperature']
                    total_no_of_data_for_current_day+=1
                    daily_data_list.append(json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
                else:
                    daily_data_list.append(json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
                    total_temperature_for_current_day = jsonobj['ambientTemperature']
                    total_no_of_data_for_current_day = 1
                    daily_data_list.append(json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
            else:
                daily_data_list.append(json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
                total_temperature_for_current_day = jsonobj['ambientTemperature']
                total_no_of_data_for_current_day = 1
                daily_data_list.append(json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_day/total_no_of_data_for_current_day}))
                monthly_data_list.append(json.dumps({"date": str(previouseventdate), "temp": total_temperature_for_current_month/total_no_of_data_for_current_month}))
                total_temperature_for_current_month = jsonobj['ambientTemperature']
                total_no_of_data_for_current_month = 1
                monthly_data_list.append(json.dumps({"date": str(eventdate), "temp": total_temperature_for_current_month/total_no_of_data_for_current_month}))
        elif index == 0: #if we are at the first item
            total_temperature_for_current_day+=jsonobj['ambientTemperature']
            total_no_of_data_for_current_day+=1
            total_temperature_for_current_month+=jsonobj['ambientTemperature']
            total_no_of_data_for_current_month+=1
        print(total_no_of_data_for_current_month)
print(daily_data_list)
print(monthly_data_list)
# a = None
# print(a == None)
# print(a is None)
# print(datetime.datetime.now() > datetime.datetime.strptime("2021-10-30 14:10:07.984202", '%Y-%m-%d %H:%M:%S.%f'))

daily_visitor_history_count = []
monthly_visitor_history_count = []
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
                    daily_visitor_history_count.append({"date": str(previouseventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day}) 
                    total_number_of_people_for_current_day = jsonobj['people_count']
                    total_no_of_data_for_current_day = 1
            else:
                daily_visitor_history_count.append({"date": str(previouseventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day})
                total_number_of_people_for_current_day = jsonobj['people_count']
                total_no_of_data_for_current_day = 1
                monthly_visitor_history_count.append({"date": str(previouseventdate), "count": total_number_of_people_for_current_month/total_no_of_data_for_current_month}) 
                total_number_of_people_for_current_month = jsonobj['people_count']
                total_no_of_data_for_current_month = 1
        elif index == len(dailyPopulationList)-1: #if we are at the last item
            if (eventyear == previouseventdate.year and eventmonth == previouseventdate.month):
                total_number_of_people_for_current_month+=jsonobj['people_count']
                total_no_of_data_for_current_month+=1
                monthly_visitor_history_count.append({"date": str(eventdate), "count": total_number_of_people_for_current_month/total_no_of_data_for_current_month})

                if eventday == previouseventdate.day:
                    total_number_of_people_for_current_day+=jsonobj['people_count']
                    total_no_of_data_for_current_day+=1
                    daily_visitor_history_count.append({"date": str(eventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day}) 
                else:
                    daily_visitor_history_count.append({"date": str(previouseventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day})
                    total_number_of_people_for_current_day = jsonobj['people_count']
                    total_no_of_data_for_current_day = 1
                    daily_visitor_history_count.append({"date": str(eventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day})
            else:
                daily_visitor_history_count.append({"date": str(previouseventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day})
                total_number_of_people_for_current_day = jsonobj['people_count']
                total_no_of_data_for_current_day = 1
                daily_visitor_history_count.append({"date": str(eventdate), "count": total_number_of_people_for_current_day/total_no_of_data_for_current_day})
                monthly_visitor_history_count.append({"date": str(previouseventdate), "count": total_number_of_people_for_current_month/total_no_of_data_for_current_month})
                total_number_of_people_for_current_month = jsonobj['people_count']
                total_no_of_data_for_current_month = 1
                monthly_visitor_history_count.append({"date": str(eventdate), "count": total_number_of_people_for_current_month/total_no_of_data_for_current_month})
        elif index == 0: #if we are at the first item
            total_number_of_people_for_current_day+=jsonobj['people_count']
            total_no_of_data_for_current_day+=1
            total_number_of_people_for_current_month+=jsonobj['people_count']
            total_no_of_data_for_current_month+=1

print(daily_visitor_history_count)
print(monthly_visitor_history_count)

