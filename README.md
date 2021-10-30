# EBS Team 7 Beach Monitoring System

## This repo consist code for:

#### 1) Beach Monitoring Web Portal (frontend)

#### 2) Flask Application for Kyma Pods


docker build -t darrenho1994/beach-monitoring-system-flask-app:latest -f Dockerfile .

docker push darrenho1994/beach-monitoring-system-flask-app

kubectl config set-context --current --namespace=smu-team07 

kubectl apply -f ./deployment.yaml


How to access pod files:
1. kubectl exec --stdin --tty redis-9f99b7fd6-vh588	 -- /bin/bash 

2. type redis-cli

3. auth kPppOZp2hC

4. select 0


keys * (to search alll keys in my db)

FLUSHALL (to DELETE KEYS FROM ALL DATABASE)

FLUSHDB (to delete keys of the selected Redis Database) < use this


REDIS LIST OF DATABASE:
devices
1) "{\"thingId\": \"38ED5BF550EE4CC6AD2BE9A7BE7111A4\", \"deviceId\": \"dcac5d23-cf60-44ff-82e8-b1fb4fd69efb\", \"sensorId\": \"f1ff9a46-86f7-47ef-befb-ccb8a76b90a8\", \"commandCapabilityId\": \"24c65333-6630-46d2-b4b8-69ca3f3786df\", \"coordinate\": {\"lat\": \"1.3050856285437102\", \"lng\": \"103.93210128266621\"}, \"zone\": \"East Coast Park Zone 1\"}"

38ED5BF550EE4CC6AD2BE9A7BE7111A4
1) "{\"event\": \"strong_wave\", \"datetime\": \"2021-10-23 18:14:52.989580\", \"zone\": \"East Coast Park Zone 1\"}"


38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION
1) "{\"datetime\": \"2021-10-23 18:11:12.808428\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 24.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 59, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}"
2) "{\"datetime\": \"2021-10-23 18:12:17.172217\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 24.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}"
3) "{\"datetime\": \"2021-10-23 18:13:17.829322\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 24.0, \"ambientPressure\": 101.0, \"ambientLight\": 0, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}"
4) "{\"datetime\": \"2021-10-23 18:14:26.111993\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 25.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 58, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}"
5) "{\"datetime\": \"2021-10-23 18:15:27.841542\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 25.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 59, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}"
6) "{\"datetime\": \"2021-10-23 18:16:27.887971\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 25.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 60, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}"


38ED5BF550EE4CC6AD2BE9A7BE7111A4POPULATION
1) "{\"datetime\": \"2021-10-24 13:32:22.091528\", \"people_count\": 0}"
2) "{\"datetime\": \"2021-10-24 13:37:25.670296\", \"people_count\": 0}"
3) "{\"datetime\": \"2021-10-24 13:42:29.376065\", \"people_count\": 0}"
4) "{\"datetime\": \"2021-10-24 14:05:04.475641\", \"people_count\": 0}"
5) "{\"datetime\": \"2021-10-24 14:10:07.984202\", \"people_count\": 0}"
6) "{\"datetime\": \"2021-10-24 14:21:53.574388\", \"people_count\": 0}"
7) "{\"datetime\": \"2021-10-24 14:26:57.173634\", \"people_count\": 0}"
8) "{\"datetime\": \"2021-10-24 14:49:36.509912\", \"people_count\": 1}"
9) "{\"datetime\": \"2021-10-24 14:59:39.579794\", \"people_count\": 0}"
10) "{\"datetime\": \"2021-10-24 15:16:56.498443\", \"people_count\": 0}"
11) "{\"datetime\": \"2021-10-24 15:19:16.181271\", \"people_count\": 0}"
12) "{\"datetime\": \"2021-10-24 15:24:19.718675\", \"people_count\": 0}"
13) "{\"datetime\": \"2021-10-24 15:29:23.476751\", \"people_count\": 0}"
14) "{\"datetime\": \"2021-10-24 15:34:27.285244\", \"people_count\": 0}"
15) "{\"datetime\": \"2021-10-24 15:39:30.978977\", \"people_count\": 0}"
16) "{\"datetime\": \"2021-10-24 15:44:48.701382\", \"people_count\": 0}"

RPUSH 38ED5BF550EE4CC6AD2BE9A7BE7111A4DATACOLLECTION "{\"datetime\": \"2021-09-22 18:16:27.887971\", \"zone\": \"East Coast Park Zone 1\", \"ambientTemperature\": 25.0, \"ambientPressure\": 101.0, \"ambientLight\": 252, \"ambientHumidity\": 60, \"gyroscopeX\": 1.0, \"gyroscopeY\": -3.0, \"gyroscopeZ\": -1.0}"