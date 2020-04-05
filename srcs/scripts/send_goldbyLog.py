# -*- coding:utf-8 -*-

"""
给账号发金币
"""
import sys
sys.path.insert(0, '../server_common')
sys.path.insert(0, '../mahjong')

# from common import log_util
from web_db_define import *

import time
from datetime import datetime, timedelta, date
import redis
import traceback
import uuid
from common.mysql_util import MysqlInterface

REFRESH_TIMES = ['00:00', '06:00', '12:00', '18:00']
WAIT_SLEEP_TIME = 15
SLEEP_TIME = 5 * 60 * 60 + 30 * 60

def addLog(s):
    nowDay = datetime.now().strftime('%Y-%m-%d')
    nowTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    f = file('./log/%s.log'%(nowDay), 'a')
    print s
    f.write('%s: '%nowTime)
    f.write(str(s))
    f.write('\n')
    f.close()

def getInst(dbNum):
    redisdb = redis.ConnectionPool(host="127.0.0.1", port=6379, db=dbNum, password='Fkkg65NbRwQOnq01OGMPy5ZREsNUeURm')
    return redis.Redis(connection_pool=redisdb)


def send_gold(uids,gold=0):
    try:
        if not uids: return
        redis_conn = getInst(1)
        nowTime = datetime.now()
        nowHour = nowTime.strftime("%H:%M")
        nowDay = nowTime.strftime('%Y-%m-%d')
        addLog('on send_gold time: %s %s'%(nowDay, nowHour))
        for uid in uids:
            table = 'users:%s' %uid
            name,pre_gold = redis_conn.hmget(table, 'name', 'gold')
            redis_conn.hset(table,'gold',gold)
            addLog('send %s, %s OK' %(table,gold))

            if not pre_gold: pre_gold=0
            strTime = nowTime.strftime('%Y-%m-%d %H:%M:%S')
            data = {
                'user_id': uid,
                'name': name,
                'createtime': strTime,
                'pre_gold': pre_gold,
                'changed': gold,
                'now_gold': int(pre_gold) + gold,
                'action': 0  #0:GM赠送, 1:扣房费, 2:结算扣分, 3:每日领取 4:充值
            }

            MysqlInterface.insert('log_gold',**data)

    except Exception as e:
        addLog('%s' %traceback.format_exc())

if __name__ == '__main__':
    uids = [9,10]
    send_gold(uids,gold=100)

