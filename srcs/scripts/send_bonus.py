# -*- coding:utf-8 -*-

"""
每日发送bonus给代理账号
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

# REFRESH_TIMES = ['00:00', '06:00', '12:00', '18:00']
# WAIT_SLEEP_TIME = 15
# SLEEP_TIME = 5 * 60 * 60 + 30 * 60

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
    redisdb = redis.ConnectionPool(host="172.18.176.177", port=6381, db=dbNum, password='168joyvick')
    return redis.Redis(connection_pool=redisdb)

def inner_send_mail(title,uid,body,awards):
    """
        内部发送邮件接口
    """

    bag_redis = redis.ConnectionPool(host="172.18.176.177", port=6381, db="2", password='168joyvick')
    email_id = uuid.uuid4().hex
    e_num = bag_redis.scard(USER_EMAIL_SET%uid)
    if e_num >= 50:
        return {"code":1,"msg":"mail num more than 50"}
    bag_redis.hmset(EMAIL_HASH%email_id,{"title":title,"body":body,"awards":awards,"send_time":datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'),"read":0,"timestamp":str(time.time())})
    bag_redis.sadd(USER_EMAIL_SET%uid,email_id)
    return {"code":0,"msg":"ok"}


def send_bonus():
    try:
        redis_cli = getInst(1)
        nowTime = datetime.now()
        nowHour = nowTime.strftime("%H:%M")
        nowDay = nowTime.strftime('%Y-%m-%d')
        addLog('on send_bonus time: %s %s'%(nowDay, nowHour))
        agents_members = redis_cli.smembers(AGENT_ID_TABLE)

        for agent in agents_members:
            agent_binding_table = AGENT_BINDING_TABLE % (agent)
            agent_table = AGENT_TABLE % (agent)

            if redis_cli.llen(agent_binding_table):
                if redis_cli.hexists(agent_table,'bonus'):
                    bonus = redis_cli.hget(agent_table,'bonus')
                    if bonus and bonus != '0':
                        title = '返送金币到账'
                        body = '昨天玩家充值所有返送%s金币已经到账' % bonus
                        # awards = '2,%s' % bonus
                        awards = ''
                        binding_list = redis_cli.lrange(agent_binding_table, 0, -1)
                        for i in binding_list:
                            uid = i.split('|')[0]
                            name, pre_gold = redis_cli.hmget(FORMAT_USER_TABLE % uid, 'name', 'gold')
                            redis_cli.hincrby(FORMAT_USER_TABLE % uid, 'gold', bonus)
                            result = inner_send_mail(title,uid,body,awards)
                            if result.get('code','') == 0:
                                addLog('代理ID[%s],玩家uid[%s]:发送金币奖励 %s' % (agent,uid, bonus))

                            if not pre_gold: pre_gold = 0
                            change = int(bonus)
                            strTime = nowTime.strftime('%Y-%m-%d %H:%M:%S')
                            data = {
                                'user_id': uid,
                                'name': name,
                                'createtime': strTime,
                                'pre_gold': pre_gold,
                                'changed': change,
                                'now_gold': int(pre_gold) + change,
                                'action': 5  # 0:GM赠送, 1:扣房费, 2:结算扣分, 3:每日领取 4:充值, 5:代理返利
                            }
                            MysqlInterface.insert('log_gold', **data)
                        redis_cli.hset(agent_table, 'bonus', 0)

    except Exception as e:
        addLog('%s' %traceback.format_exc())

if __name__ == '__main__':
    send_bonus()
