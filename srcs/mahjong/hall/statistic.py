import redis
import datetime

cushion_redis = redis.Redis(host="172.18.10.17",port=6888,db=9, password="Fkkg65NbRwQOnq01OGMPy5ZREsNUeURm")
CUSHION_QUEUE = 'task:redis:mysql:queue'

def dig_login_times(user_id):
    cur_time = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
    value = "dig_hall_login:" + str(user_id) + "|" + cur_time
    cushion_redis.rpush(CUSHION_QUEUE,value)
