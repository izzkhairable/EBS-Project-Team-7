import datetime

print((datetime.datetime.strptime('2021-11-04 08:23:05.968344', '%Y-%m-%d %H:%M:%S.%f') - datetime.datetime.strptime('2021-11-02 18:41:31.919250', '%Y-%m-%d %H:%M:%S.%f')).days)