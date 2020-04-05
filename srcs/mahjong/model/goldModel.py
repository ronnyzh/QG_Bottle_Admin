# -*- coding:utf-8 -*-
# !/usr/bin/python

"""

     金币场数据模型

"""
import time
import json
import random
from common.log import log_debug
from gold_db_define import *
from web_db_define import *
import uuid
import copy
import redis
import traceback
import collections
from datetime import datetime, timedelta, date
from common.utilt import ServerPagination
from common.mysql_util import MysqlInterface
from common.mysql_lj_game import MysqlljgameInterface
from itertools import groupby


def get_uuid():
    return uuid.uuid4().hex


def getPrivateRedisInst(redisdb, gameid):
    """
        获取redis连接实例
    """
    try:
        if not redisdb.exists(GAME2REDIS % gameid):
            return None
        info = redisdb.hgetall(GAME2REDIS % gameid)
        ip = info['ip']
        passwd = info['passwd']
        port = int(info['port'])
        dbnum = int(info['num'])
        redisdb = redis.ConnectionPool(host=ip, port=port, db=dbnum, password=passwd)
        return redis.Redis(connection_pool=redisdb)
    except:
        traceback.print_exc()
        return None


def get_user_info(redis, account):
    """ 获取玩家信息"""
    info = {}
    user_table = redis.get(FORMAT_ACCOUNT2USER_TABLE % account)
    if not user_table:
        return info
    info = redis.hgetall(user_table)
    info['uid'] = user_table.split(':')[1]
    return info


def sendProtocolResult2Web(redis, _uuid, proto):
    """
        发送处理结果
    """
    redis.set(RESULT_GOLD_SERVICE_PROTOCOL % _uuid, json.dumps(proto))
    redis.expire(RESULT_GOLD_SERVICE_PROTOCOL % _uuid, 5)


def getProtocolResultFromGold(redis, _uuid, timeout=5):
    """ 
        gold server 结果消息返回
    """
    while timeout > 0:
        key = RESULT_GOLD_SERVICE_PROTOCOL % _uuid
        if redis.exists(key):
            return json.loads(redis.get(key))
        time.sleep(0.1)
        timeout = timeout - 0.1


def get_GoldGameList(redis):
    """
    获取金币场场次
    """
    res = []
    for gameid in PARTY_GOLD_GAME_LIST.keys():
        list = PARTY_GOLD_GAME_LIST.get(gameid, PARTY_GOLD_GAME_LIST.get('default'))
        data = copy.deepcopy(list)
        for item in data:
            if gameid == '555':
                item['gameName'] = '经典牛牛'
            elif gameid == '666':
                item['gameName'] = '欢乐牛牛'
            elif gameid == '556':
                item['gameName'] = '明牌牛牛'
            elif gameid == '444':
                item['gameName'] = '东胜麻将'
            elif gameid == '557':
                item['gameName'] = '欢乐拼点'
                # item['hasOwner'] = '1' # 支持好友开房
            elif gameid == '771':
                item['gameName'] = '廉江二人麻将'
            elif gameid == '772':
                item['gameName'] = '廉江四人麻将'

            online = redis.scard(GOLD_ONLINE_PLAYID_ACCOUNT_SET % (gameid, item['id']))
            item['online'] = online
        res.append({'gameid': gameid, 'config': data})
    return res


LIST_CACHE_MAXNUM = 10000
LIST_CACHE_TTL = 5 * 60


def get_user_field(redis, prredis, account):
    print(account)
    user_info = get_user_info(redis, account)
    if not user_info:
        return
    agentid = user_info['parentAg']
    reg_date = user_info['reg_date']
    last_login_date = user_info['last_login_date']
    uid = user_info['uid']
    gold = user_info.get('gold', '')
    roomcard = redis.get(USER4AGENT_CARD % (agentid, uid))
    gold_user_table = GOLD_USER_TABLE % account
    gold_dic = prredis.hgetall(gold_user_table)
    if not gold_dic:
        gold_dic['nickname'] = user_info['nickname']
        gold_dic['uid'] = uid
        gold_dic['agent'] = agentid
        gold_dic['account'] = account
    gold_dic['cur_diamond_num'] = roomcard
    gold_dic['first_log_date'] = reg_date
    gold_dic['last_log_date'] = last_login_date
    # gold_dic['buy_diamond_stream'] = 'buy_record?account=%s' % account
    gold_dic['buy_gold_stream'] = 'buy_record?account=%s' % account
    gold_dic['gold_record_stream'] = 'journal?account=%s' % account
    money = prredis.get(GOLD_BUY_RECORD_ACCOUNT_MOENY_SUM % account)
    if money:
        money = float(money) / 100
    gold_dic['buy_gold_num'] = money
    if not gold_dic.get('agent', ''):
        gold_dic['agent'] = agentid
    # 财富排行
    rank = prredis.zrevrank(GOLD_MONEY_RANK_WITH_AGENT_ZSET % gold_dic['agent'],
                            account)
    if rank != None:
        gold_dic['agent_wealth_rank'] = int(rank) + 1
    else:
        gold_dic['agent_wealth_rank'] = u'无'
    # 胜局排行
    rank = prredis.zrevrank(GOLD_WIN_RANK_WITH_AGENT_ZSET % gold_dic['agent'],
                            account)
    if rank != None:
        gold_dic['agent_win_rank'] = int(rank) + 1
    else:
        gold_dic['agent_win_rank'] = u'无'
    # 胜率
    win = prredis.llen(GOLD_RECORD_ACCOUNT_WIN_LIST % account)
    total = prredis.llen(GOLD_RECORD_ACCOUNT_TOTAL_LIST % account)
    if total:
        gold_dic['gold_win_rate'] = '%.2f' % (win / float(total) * 100 if total else 0)
    gold_dic['cur_gold_num'] = gold
    return gold_dic


def getGoldListInfos(redis, search, page_size, page_num):
    """
        获取金币场用户数据
    """
    prredis = getPrivateRedisInst(redis, MASTER_GAMEID)

    '''
    # 如果缓存存在则直接去缓存中取数据
    if not search and redis.exists('gold:data:cache'):
        data = redis.get('gold:data:cache')
        data_list = json.loads(data)
        count = len(data_list)
        return {'total': count, 'result': data_list}
    '''

    # 微信集合
    weixin_sets = prredis.smembers(GOLD_ACCOUNT_SET_TOTAL)
    weixin_sets = weixin_sets | redis.smembers(ACCOUNT4WEIXIN_SET)
    data_list = []
    if search:
        if search not in weixin_sets:
            return {'total': 0, 'result': []}
        gold_dic = get_user_field(redis, prredis, search)
        if gold_dic:
            data_list.append(gold_dic)
        return {'total': len(gold_dic), 'result': data_list}

    total_count = len(weixin_sets)
    weixin_sets = ServerPagination(weixin_sets, page_size, page_num)
    # 遍历微信集合，从对应表中取出数据字典放入data列表中

    for account in weixin_sets:
        gold_dic = get_user_field(redis, prredis, account)
        data_list.append(gold_dic)

    '''
    # 如果大于10000条数据做一个金币用户表data缓存
    if count >= LIST_CACHE_MAXNUM:
        data_cache = json.dumps(data_list)
        redis.set('gold:data:cache', data_cache)
        # 缓存5分钟
        redis.expire('gold:data:cache', LIST_CACHE_TTL) 
    '''
    data_list = sorted(data_list,key=lambda i:int(i['cur_gold_num']), reverse=True)
    return {'total': total_count, 'result': data_list}


# 金币场运营表
def getGoldOperateInfos(redis, selfUid, startDate, endDate, niuniu_type):
    prredis = getPrivateRedisInst(redis, MASTER_GAMEID)
    try:
        startDate = datetime.strptime(startDate, '%Y-%m-%d')
        endDate = datetime.strptime(endDate, '%Y-%m-%d')
    except:
        weekDelTime = timedelta(7)
        weekBefore = datetime.now() - weekDelTime
        startDate = weekBefore
        endDate = datetime.now()
    deltaTime = timedelta(1)
    res = []
    while startDate <= endDate:
        dateStr = endDate.strftime('%Y-%m-%d')
        gameid = '555'
        if niuniu_type == '1':
            gameid = '555'
        elif niuniu_type == '2':
            gameid = '556'
        elif niuniu_type == '3':
            gameid = '666'
        if prredis.exists(GOLD_OPERATE % (gameid, dateStr)):
            info = prredis.hgetall(GOLD_OPERATE % (gameid, dateStr))
            info['online_user_max'] = redis.hget(GOLD_ONLINE_MAX_ACCOUNT_TABLE % (gameid, dateStr), 'count')
            info['date'] = dateStr
            info['buy_gold_total'] = redis.get(DAILY_GOLD2_SUM % dateStr)
            info['buy_money'] = redis.get(DAILY_GOLD2_MONEY_SUM % dateStr)
            info['buy_money'] = float(info['buy_money']) / 100 if info['buy_money'] else 0
            info['buy_gold_count'] = redis.scard(DAILY_USER_GOLD2_SET % dateStr)
            info['buy_gold_people_num'] = 'buy_record_info?date=%s' % dateStr
            room_num = 0
            if datetime.now().strftime("%Y-%m-%d") == dateStr:
                info['online_user'] = redis.scard(GOLD_ONLINE_ACCOUNT_SET % gameid)
                for roomid in redis.smembers(GOLD_ONLINE_ROOM_SET % gameid):
                    room_table = ROOM2SERVER % roomid
                    pl_count = redis.hget(room_table, 'playerCount')
                    if not pl_count or pl_count <= '0':
                        continue
                    room_num += 1
                info['room_count'] = room_num
            res.append(info)
        endDate -= deltaTime
    return {"count": 1, "data": res}


# 金币场运营表在线人数及在线房间数
def getOnlineOperateInfos(redis):
    prredis = getPrivateRedisInst(redis, MASTER_GAMEID)
    # 总当前在线人数
    online_people_sum = redis.scard(GOLD_ONLINE_ACCOUNT_SET_TOTAL)
    # 当前在线房间数
    online_room_num = 0
    for roomid in redis.smembers(GOLD_ONLINE_ROOM_SET_TOTAL):
        room_table = ROOM2SERVER % roomid
        pl_count = redis.hget(room_table, 'playerCount')
        if not pl_count or pl_count == '0':
            continue
        online_room_num += 1
    # online_room_num = redis.scard(GOLD_ONLINE_ROOM_SET_TOTAL)
    # 当前玩家金币总数
    user_current_gold_sum = 0
    for account in prredis.smembers(GOLD_ACCOUNT_SET_TOTAL):
        user_table = redis.get(FORMAT_ACCOUNT2USER_TABLE % account)
        if not user_table:
            continue
        gold = redis.hget(user_table, 'gold')
        gold = int(gold) if gold else 0
        user_current_gold_sum += gold
    return online_people_sum, online_room_num, user_current_gold_sum


# 金币场在线AI总数及在线AI房间数
def getOnlineAIInfos(redis):
    online_ai_sum = 0
    cur_ai_gold_sum = 0
    online_ai_room_num_set = set()
    for key in redis.smembers('users:robot:accounts:set'):
        online, account, gold = redis.hmget(key, 'isOnline', 'account', 'gold')
        gold = int(gold) if gold else 0
        cur_ai_gold_sum += gold
        if online == '1':
            online_ai_sum += 1
            if redis.exists(GOLD_ROOM_ACCOUNT_KEY % account):
                online_ai_room_num_set.add(redis.get(GOLD_ROOM_ACCOUNT_KEY % account))
    return online_ai_sum, len(online_ai_room_num_set), cur_ai_gold_sum


# 金币场AI数据总表
def getGoldAIInfos(redis, selfUid, startDate, endDate, grade):
    prredis = getPrivateRedisInst(redis, MASTER_GAMEID)
    try:
        startDate = datetime.strptime(startDate, '%Y-%m-%d')
        endDate = datetime.strptime(endDate, '%Y-%m-%d')
    except:
        weekDelTime = timedelta(7)
        weekBefore = datetime.now() - weekDelTime
        startDate = weekBefore
        endDate = datetime.now()
    deltaTime = timedelta(1)
    res = []
    while startDate <= endDate:
        dateStr = endDate.strftime('%Y-%m-%d')
        info = {}
        join_ai_sum = prredis.scard(GOLD_AI_ACCOUNT_SET_BYDAY % dateStr)
        if join_ai_sum:
            ai_room_sum = prredis.scard(GOLD_AI_ROOM_SET_BYDAY % dateStr)
            ai_gold_sum = prredis.llen(GOLD_AI_RECORD_LIST_BYDAY % dateStr)
            info['date'] = dateStr
            info['join_ai_sum'] = join_ai_sum
            info['ai_room_sum'] = ai_room_sum
            info['ai_gold_sum'] = ai_gold_sum
            info['cur_ai_gold_num'] = redis.get('robot:gold:sum:%s' % dateStr)
            res.append(info)
        endDate -= deltaTime

    return {"count": len(res), "data": res}


def saveBuyGoldRecord(redis, account, data):
    """ 
        保存金币流水
    """
    try:
        if not redis.sismember(GOLD_ACCOUNT_SET_TOTAL, account):
            redis.sadd(GOLD_ACCOUNT_SET_TOTAL, account)
        prredis = getPrivateRedisInst(redis, MASTER_GAMEID)
        num = prredis.incr(GOLD_BUY_RECORD_COUNT_TABLE)
        record_key = GOLD_BUY_RECORD_TABLE % num
        pipe = prredis.pipeline()
        data['account'] = account
        pipe.hmset(record_key, data)
        pipe.expire(record_key, GOLD_ROOM_MAX_TIME)
        pipe.lpush(GOLD_BUY_RECORD_ACCOUNT_LIST % account, record_key)
        pipe.lpush(GOLD_BUY_RECORD_LIST_TOTAL, record_key)
        pipe.incr(GOLD_BUY_RECORD_ACCOUNT_GOLD_SUM % account, data['gold'])
        pipe.incr(GOLD_BUY_RECORD_ACCOUNT_MOENY_SUM % account, data['money'])
        pipe.execute()
        user_info = get_user_info(redis, account)
        if not user_info:
            return
        agentid = user_info['parentAg']
        gold = user_info['gold']
        prredis.zadd(GOLD_MONEY_RANK_WITH_AGENT_ZSET % agentid, account, gold)
    except Exception, ex:
        traceback.print_exc()


def player_add_gold(redis, account, gold):
    user_table = redis.get(FORMAT_ACCOUNT2USER_TABLE % account)
    if not user_table:
        return
    redis.hincrby(user_table, 'gold', gold)

    prredis = getPrivateRedisInst(redis, MASTER_GAMEID)
    user_info = get_user_info(redis, account)
    if not user_info:
        return
    agentid = user_info['parentAg']
    gold = user_info['gold']
    prredis.zadd(GOLD_MONEY_RANK_WITH_AGENT_ZSET % agentid, account, gold)

    return True


def player_set_gold(redis, account, gold):
    user_table = redis.get(FORMAT_ACCOUNT2USER_TABLE % account)
    if not user_table:
        return
    redis.hset(user_table, 'gold', gold)

    prredis = getPrivateRedisInst(redis, MASTER_GAMEID)
    user_info = get_user_info(redis, account)
    if not user_info:
        return
    agentid = user_info['parentAg']
    gold = user_info['gold']
    prredis.zadd(GOLD_MONEY_RANK_WITH_AGENT_ZSET % agentid, account, gold)

    return True


def do_PlayerWelfareSign(redis, account):
    """ 
        签到接口
    """
    today = datetime.now().strftime("%Y-%m-%d")
    key = WELFARE_USER_SIGN % (account, today)
    if redis.exists(key):
        return
    gold = 2000
    if not player_add_gold(redis, account, gold):
        return
    redis.set(key, 1)
    return gold


def doPatchSign(redis, account, date):
    """ 
        补签接口
        补签需要消耗2张房卡
    """
    user_info = get_user_info(redis, account)
    uid = user_info['uid']
    agentid = user_info['parentAg']
    roomcard = redis.get(USER4AGENT_CARD % (agentid, uid))
    roomcard = int(roomcard) if roomcard else 0

    if roomcard < PATCH_SIGN_FEE:
        return {'code': 1, 'msg': "钻石不足"}

    month = datetime.strptime(date, '%Y-%m-%d').month
    key = WELFARE_USER_PATCH_SIGN % (account, month)

    if redis.sismember(key, date):
        return {'code': 1, 'msg': "已补签过"}

    times = redis.scard(key)
    # 每月补签次数是否达到上限
    if times and int(times) > PATCH_SIGN_MAX:
        return {'code': 1, 'msg': "当月补签已达上限"}
    redis.sadd(key, date)
    return {'code': 0, 'msg': "补签成功"}


def doWelfareById(redis, uid, account, id):
    """ 
        福利
    """
    today = datetime.now().strftime("%Y-%m-%d")
    if id == '2':
        playerCoin = redis.hget(FORMAT_USER_TABLE % uid, 'gold')
        playerCoin = playerCoin if playerCoin else 0
        if int(playerCoin) >= SIGN_LINE:
            return {'code': 1, 'msg': u'未达到低保线无法领取'}
        key = WELFARE_USER_INSURANCE % (account, today)
        if redis.llen(key) >= SIGN_MAX:
            return {'code': 1, 'msg': u'已经领取了 {0} 次'.format(SIGN_MAX)}
        redis.lpush(key, SIGN_COINNUM)
        player_add_gold(redis, account, SIGN_COINNUM)
    elif id == '1':
        # 新手礼包
        if redis.hget(GOLD_REWARD_NEW_PRESENT_HASH, account) == MESSION_STATUS_OVER:
            return {'code': 1, 'msg': u'您已领取，无法再次领取'}
        redis.hset(GOLD_REWARD_NEW_PRESENT_HASH, account, MESSION_STATUS_OVER)
    elif id == '0':
        # 每日首冲奖励
        if not redis.sismember(DAILY_USER_GOLD2_SET % today, account):
            return {'code': 1, 'msg': u'您今日还未完成首冲'}
        elif redis.hget(GOLD_REWARD_DAY_BUY_GOLD_HASH % today, account) == MESSION_STATUS_OVER:
            return {'code': 1, 'msg': u'您已领取，无法再次领取'}
        redis.hget(GOLD_REWARD_DAY_BUY_GOLD_HASH % today, account, MESSION_STATUS_OVER)

    return {'code': 0, 'msg': u'领取成功'}


def doSignRewardById(redis, uid, account, id):
    """ 
        签到奖励
    """
    today = datetime.now().strftime("%Y-%m-%d")
    if id == '0':
        # 七天奖励
        pass
    elif id == '1':
        # 十五天奖励
        pass
    elif id == '2':
        # 月奖励
        pass
    return {'code': 0, 'msg': u'领取成功'}


def getJournal(redis, account):
    """

    """
    prredis = getPrivateRedisInst(redis, MASTER_GAMEID)
    res = []
    for table in prredis.lrange(GOLD_RECORD_ACCOUNT_TOTAL_LIST % account, 0, -1):
        info = prredis.hgetall(table)
        if not info.get('start_time', ''):
            continue
        info['rid'] = table.split(':')[4]
        info['start_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(info['start_time']) / 1000))
        info['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(info['end_time']) / 1000))
        res.append(info)
    return res


def getBuyGoldRecord(redis, account):
    """
        
    """
    prredis = getPrivateRedisInst(redis, MASTER_GAMEID)
    res = []
    for table in prredis.lrange(GOLD_BUY_RECORD_ACCOUNT_LIST % account, 0, -1):
        info = prredis.hgetall(table)
        info['money'] = float(info['money']) / 100
        res.append(info)
    return res


def getBuyGoldAccounts(redis, date):
    """

    """
    res = []
    for account in redis.smembers(DAILY_USER_GOLD2_SET % date):
        info = {}
        info['date'] = date
        info['gold'] = redis.get(DAILY_ACCOUNT_GOLD2_SUM % (account, date))
        money = redis.get(DAILY_ACCOUNT_GOLD2_MONEY_SUM % (account, date))
        info['money'] = float(money) / 100
        info['account'] = account
        res.append(info)
    return res


GOLD_RANK_CACHE = 'gold:rank:cache:%s'


def first_day_of_week():
    """ 
        获取本周第一天
    """
    return date.today() - timedelta(days=date.today().weekday())


def get_gold_week_win_rank(redis, groupid):
    first = first_day_of_week()
    last = first + timedelta(7)
    keys = []
    while first <= last:
        keys.append(GOLD_WIN_RANK_WITH_AGENT_ZSET_BYDAY % (groupid, first.strftime("%Y-%m-%d")))
        first += timedelta(1)
    redis.zunionstore('gold:win:rank:%s:thisweek:zset' % groupid, keys, aggregate='MAX')
    return redis.zrevrange('gold:win:rank:%s:thisweek:zset' % groupid, 0, 10 - 1, True)


def get_gold_rank(redis, groupid, account):
    """
        获取排行榜        
    """
    sortby = 'week'

    prredis = getPrivateRedisInst(redis, MASTER_GAMEID)
    today = datetime.now().strftime("%Y-%m-%d")

    # if redis.exists(GOLD_RANK_CACHE % account):
    #     return json.loads(redis.get(GOLD_RANK_CACHE % account))

    res = {}
    res['gold_rank'] = []
    res['win_rank'] = []
    my_user_info = get_user_info(redis, account)

    # 财富排行榜
    rank = 0
    try:
        for _account, value in prredis.zrevrange(GOLD_MONEY_RANK_WITH_AGENT_ZSET % groupid, 0, 10 - 1, True):
            rank += 1
            value = int(value)
            user_info = get_user_info(redis, _account)
            if not user_info:
                continue
            res['gold_rank'].append({'rank': rank, 'nickname': user_info['nickname'], 'value': value,
                                     'account': _account, 'headImgUrl': user_info['headImgUrl']})

        myrank = prredis.zrevrank(GOLD_MONEY_RANK_WITH_AGENT_ZSET % groupid, account)
        myvalue = prredis.zscore(GOLD_MONEY_RANK_WITH_AGENT_ZSET % groupid, account)
        if my_user_info and myrank != None:
            res['gold_rank'].append({'rank': int(myrank) + 1, 'nickname': my_user_info['nickname'], 'value': myvalue,
                                     'account': account, 'headImgUrl': my_user_info['headImgUrl'], 'self': '1'})
        else:
            res['gold_rank'].append({'nickname': my_user_info['nickname'],
                                     'account': account, 'headImgUrl': my_user_info['headImgUrl'], 'self': '1'})
    except Exception as err:
        return {}
    # 胜局排行榜
    rank = 0
    for _account, value in get_gold_week_win_rank(prredis, groupid):
        rank += 1
        value = int(value)
        user_info = get_user_info(redis, _account)
        if not user_info:
            continue
        res['win_rank'].append({'rank': rank, 'nickname': user_info['nickname'], 'value': value,
                                'desc': '本周胜局', 'account': _account, 'headImgUrl': user_info['headImgUrl']})
    myrank = prredis.zrevrank('gold:win:rank:%s:thisweek:zset' % groupid, account)
    myvalue = prredis.zscore('gold:win:rank:%s:thisweek:zset' % groupid, account)
    if my_user_info and myrank != None:
        res['win_rank'].append({'rank': int(myrank) + 1, 'nickname': my_user_info['nickname'], 'value': myvalue,
                                'desc': '本周胜局', 'account': account, 'headImgUrl': my_user_info['headImgUrl'],
                                'self': '1'})
    else:
        res['win_rank'].append({'nickname': my_user_info['nickname'],
                                'account': account, 'headImgUrl': my_user_info['headImgUrl'], 'self': '1'})
    redis.set(GOLD_RANK_CACHE % account, json.dumps(res))
    redis.expire(GOLD_RANK_CACHE % account, 300)
    return res


def first_day_of_month():
    """ 
        获取本月第一天
    """
    day = date.today().strftime('%d')
    day = int(day)
    return date.today() - timedelta(days=day - 1)


def get_welfare_info(redis, account):
    today = datetime.now().strftime("%Y-%m-%d")
    first = first_day_of_month()
    last = date.today() - timedelta(days=1)
    res = copy.deepcopy(WELFARE_CONFIG)
    res['date'] = today
    res['signed'] = []
    res['unsinged'] = []
    # 今天是否签到
    if redis.exists(WELFARE_USER_SIGN % (account, today)):
        res['issigned'] = 1
    else:
        res['issigned'] = 0

    while first <= last:
        if redis.exists(WELFARE_USER_SIGN % (account, first)):
            res['signed'].append(first.strftime('%d'))
        elif redis.sismember(WELFARE_USER_PATCH_SIGN % (account, first.strftime("%m")), first.strftime('%Y-%m-%d')):
            res['signed'].append(first.strftime('%d'))
        else:
            res['unsinged'].append(first.strftime('%d'))
        first += timedelta(1)

    # 七天奖励
    if not redis.exists(GOLD_WELFARE_SIGN_7DAYS):
        res['rewardlist'][0]['status'] = MESSION_STATUS_NO
    elif redis.hget(GOLD_WELFARE_SIGN_7DAYS, account) == MESSION_STATUS_OVER:
        res['rewardlist'][0]['status'] = MESSION_STATUS_OVER
    else:
        res['rewardlist'][0]['status'] = MESSION_STATUS_OK

    # 十五天奖励
    if not redis.exists(GOLD_WELFARE_SIGN_15DAYS):
        res['rewardlist'][0]['status'] = MESSION_STATUS_NO
    elif redis.hget(GOLD_WELFARE_SIGN_15DAYS, account) == MESSION_STATUS_OVER:
        res['rewardlist'][0]['status'] = MESSION_STATUS_OVER
    else:
        res['rewardlist'][0]['status'] = MESSION_STATUS_OK

    # 月奖励
    if not redis.exists(GOLD_WELFARE_SIGN_MONTH):
        res['rewardlist'][0]['status'] = MESSION_STATUS_NO
    elif redis.hget(GOLD_WELFARE_SIGN_MONTH, account) == MESSION_STATUS_OVER:
        res['rewardlist'][0]['status'] = MESSION_STATUS_OVER
    else:
        res['rewardlist'][0]['status'] = MESSION_STATUS_OK

    # 每日首冲奖励
    if not redis.sismember(DAILY_USER_GOLD2_SET % today, account):
        res['messionlist'][0]['status'] = MESSION_STATUS_NO
        res['messionlist'][0]['parent_mode'] = CHECK_MALL
    else:
        if redis.hget(GOLD_REWARD_DAY_BUY_GOLD_HASH % today, account) == MESSION_STATUS_OVER:
            res['messionlist'][0]['status'] = MESSION_STATUS_OVER
        else:
            res['messionlist'][0]['status'] = MESSION_STATUS_OK

    # 新手礼包
    if redis.hget(GOLD_REWARD_NEW_PRESENT_HASH, account) == MESSION_STATUS_OVER:
        res['messionlist'][1]['status'] = MESSION_STATUS_OVER
    else:
        res['messionlist'][1]['status'] = MESSION_STATUS_OK

    # 破产补助
    key = WELFARE_USER_INSURANCE % (account, today)
    if not redis.exists(WELFARE_USER_INSURANCE % (account, today)):
        res['messionlist'][2]['status'] = MESSION_STATUS_OK
    else:
        if redis.llen(key) >= SIGN_MAX:
            res['messionlist'][2]['status'] = MESSION_STATUS_OVER
        else:
            res['messionlist'][2]['status'] = MESSION_STATUS_OK

    return res


GOLD_ACTION = {
    1: "扣房费", 2: "结算扣分", 3: "每日领取", 4: "充值"
}


def get_gold_log(startDate, endDate, uid=''):
    '''
    mysql金币流水
    :return: []
    '''
    res = []
    try:
        startDate = '%s %s' % (startDate, '00:00:00')
        endDate = '%s %s' % (endDate, '23:59:59')
        sql = '''select user_id,name,game_id,isRobot,createtime,pre_gold,changed,now_gold,action from log_gold
                 where createtime between '%s' and '%s'
        ''' % (startDate, endDate)
        print sql
        results = MysqlInterface.select(sql, fetchmany=True)
        if results:
            for i in results:
                info = {}
                info['user_id'] = i[0]
                info['name'] = i[1]
                info['game_id'] = i[2]
                info['isRobot'] = i[3]
                info['createtime'] = i[4].strftime("%Y-%m-%d %H:%M:%S")
                info['pre_gold'] = i[5]
                info['changed'] = i[6]
                info['now_gold'] = i[7]
                info['action'] = GOLD_ACTION.get(i[8], i[8])
                res.append(info)

    except Exception as e:
        print e

    return {"count": len(res), "data": res}


def get_gold_amount(startDate, endDate, pageSize, pageNumber, searchText, redis=redis):
    """
    返回 mysql - amount 显示'机器人表'各项数据
    :param startDate: starttime-> 2018-07-12
    :param endDate: endtime-> 2018-07-19
    :param pageSize:
    :param pageNumber:
    :param searchText:
    :param limit:
    :param redis:
    :return: {"count": len(res), "data": res}
    """
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    res = []
    if pageNumber:
        pageNumber = (pageNumber - 1) * int(pageSize)

    try:
        if searchText:
            sql = """select id, userId, userTable, resultId, preBalance, afterBalance, balance, type, status, level, create_time, update_time  from amount where userId='%s' and create_time >='%s' and create_time <='%s' order by create_time desc limit %s,%s""" \
                  % (searchText, startDate, endDate, pageNumber, pageSize)
            results = MysqlljgameInterface.select(sql, fetchmany=False)

            sql = """select count(1) from amount where userId='%s' and create_time >= '%s' and create_time <='%s'""" \
                  % (searchText, startDate, endDate)
            count = MysqlljgameInterface.select(sql, fetchmany=False)
        else:
            sql = """select id, userId, userTable, resultId, preBalance, afterBalance, balance, type, status, level, create_time, update_time  from amount where create_time >='%s' and create_time <='%s' order by create_time desc limit %s,%s""" \
                  % (startDate, endDate, pageNumber, pageSize)
            results = MysqlljgameInterface.select(sql, fetchmany=False)

            sql = """select count(1) from amount where  create_time >= '%s' and create_time <='%s'""" \
                  % (startDate, endDate)
            count = MysqlljgameInterface.select(sql, fetchmany=False)

        if results:
            num = 1
            for i in results:
                info = {}
                info['number'] = num
                num += 1
                info['userId'] = i[1]
                info['userTable'] = i[2]
                info['resultId'] = i[3]
                info['preBalance'] = i[4]
                info['afterBalance'] = i[5]
                info['balance'] = i[6]
                info['type'] = '机器人' if i[7] else '用户'  # 0=用户 1=机器人
                info['status'] = '失败' if i[8] else '成功'  # 状态 0=成功 1=失败
                info['level'] = i[9]
                info['create_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[10]))
                info['update_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[11]))
                res.append(info)

    except Exception as e:
        print e

    return {"count": count, "data": res}


def get_gold_amount_sumlist(redis):
    """
    返回mysql - amount 统计表中 '投放之前的金额(preBalanc),投放之后的金额(afterBalance),减少/增加的金额(balance)'的总数
    :param redis:
    :return:
    """
    res = []
    sql = """select sum(preBalance), sum(afterBalance), sum(balance) from amount"""
    results = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:
            info = {}
            info['preBalance'] = float(i[0]) if i[0] else 0
            info['afterBalance'] = float(i[1]) if i[1] else 0
            info['balance'] = float(i[2]) if i[2] else 0
            info['type'] = '机器人'
            res.append(info)
    return {"count": len(res), "data": res}


def get_gold_amount_daylist(redis, startDate, endDate):
    """
    返回 计算某一段时间内 mysql - amount 统计表中 '投放之前的金额(preBalanc),投放之后的金额(afterBalance),减少/增加的金额(balance)'的总数
    :param redis:
    :param startDate:
    :param endDate:
    :return:
    """
    res = []
    sql = """select sum(preBalance), sum(afterBalance), sum(balance) from amount where create_time >='%s' and create_time <='%s'
    """ \
          % (startDate, endDate)
    results = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:
            info = {}
            info['preBalance'] = float(i[0]) if i[0] else 0
            info['afterBalance'] = float(i[1]) if i[1] else 0
            info['balance'] = float(i[2]) if i[2] else 0
            info['type'] = '机器人'
            res.append(info)
    return {'data': res, 'count': len(res)}


def get_gold_amount_graphlist(redis,startDate, endDate, type, gameid):
    """
    返回统计图表数据
    计算某一段时间内 mysql - amount 统计表中 '投放之前的金额(preBalanc),投放之后的金额(afterBalance),减少/增加的金额(balance)'的总数
    :param redis:
    :param startDate:
    :param endDate:
    :return:
    """
    if gameid:
        sql = """select FROM_UNIXTIME(create_time,'%s'), sum(preBalance), sum(afterBalance), sum(balance) from amount where create_time>='%s' and create_time <='%s' and userId='%s'  GROUP BY from_unixtime(create_time,'%s') ORDER BY create_time asc """ \
              % (type, startDate, endDate, gameid, type)
        results = MysqlljgameInterface.select(sql, fetchmany=False)
    else:
        sql = """select FROM_UNIXTIME(create_time,'%s'), sum(preBalance), sum(afterBalance), sum(balance) from amount where create_time>='%s' and create_time <='%s'  GROUP BY from_unixtime(create_time,'%s') ORDER BY create_time asc """ \
              % (type, startDate, endDate, type)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

    graph_data = []
    if results:
        for i in results:
            info = {}
            if i[0] and ' ' in i[0]:
                a, b = i[0].split(' ')
                if ':' in b:
                    info['datetime'] = b + '\n' + a
                else:
                    info['datetime'] = b + ':00' + '\n' + a
            else:
                info['datetime'] = i[0]
            info['graph_preBalance'] = float(i[1]) if i[0] else 0
            info['graph_afterBalance'] = float(i[2]) if i[2] else 0
            info['graph_balance'] = float(i[3]) if i[3] else 0
            info['type'] = '机器人'
            graph_data.append(info)
    return {'graph_data': graph_data}


def get_gold_roomcost(startDate, endDate, pageSize, pageNumber, searchText, limit=True):
    """
    返回金币场房费流水
    :param startDate: starttime-> 2018-07-12
    :param endDate: starttime-> 2018-07-19
    :param uid: uid
    :return: {"count": len(res), "data": res}
    """
    res = []
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))
    if pageNumber:
        pageNumber = (pageNumber - 1) * int(pageSize)

    try:
        if searchText:
            sql = """select id, user_id, game_id, playid, pay_ment, is_robot, reason, create_time, update_time from roomCost where user_id='%s'  and  create_time >= '%s' and create_time <= '%s' order by create_time desc limit %s,%s""" \
                  % (searchText, startDate, endDate, pageNumber, pageSize)
            results = MysqlljgameInterface.select(sql, fetchmany=False)

            sql = """select count(1) from roomCost where user_id='%s'  and create_time between '%s' and '%s'""" \
                  % (searchText, startDate, endDate)
            count = MysqlljgameInterface.select(sql, fetchmany=False)
        else:
            sql = """select id, user_id, game_id, playid, pay_ment, is_robot, reason, create_time, update_time from roomCost where create_time >= '%s' and create_time <= '%s' order by create_time desc limit %s,%s""" \
                  % (startDate, endDate, pageNumber, pageSize)
            results = MysqlljgameInterface.select(sql, fetchmany=False)

            sql_count = """select count(1) from roomCost where create_time between '%s' and '%s'""" \
                        % (startDate, endDate)
            count = MysqlljgameInterface.select(sql_count, fetchmany=False)

        if results:
            num = 1
            for i in results:
                info = {}
                info['number'] = num
                num += 1
                info['user_id'] = i[1]
                info['game_id'] = i[2]
                info['playid'] = PLAYTYPE(i[3])
                info['pay_ment'] = i[4]
                info['is_robot'] = '机器人' if i[5] else '用户'  # 0=用户 1=机器人
                info['reason'] = i[6]
                info['create_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[7])) if i[7] else ''
                info['update_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[8])) if i[8] else ''
                res.append(info)

    except Exception as e:
        print e

    return {"count": count, "data": res}


def get_gold_roomcost_sumlist(redis):
    """
    返回mysql - roomCost 统计表中 '房费(pay_ment)’ 的总数
    :param redis:
    :return:
    """
    res = []
    sql = """select sum(pay_ment),
    sum(
    if((is_robot=0),pay_ment,0)
    ),
    sum(
    if((is_robot=1),pay_ment,0)
    )
    from roomCost
    """
    results = MysqlljgameInterface.select(sql, fetchmany=False)
    if results:
        results = results[0][0:1], results[0][1:2], results[0][2:3]
        for i, y in enumerate(results):
            info = {}
            info['pay_ment'] = float(y[0]) if y[0] else 0
            info['type'] = ['用户和机器人', '用户', '机器人'][i]
            res.append(info)

    return {'data': res, 'count': len(res)}

def get_gold_roomcost_daylist(redis, startDate, endDate):
    """
    计算某一段时间内
    返回mysql - roomCost 统计表中 '房费(pay_ment)’ 的总数
    :param redis:
    :param startDate:
    :param endDate:
    :return:
    """
    res = []
    sql = """select sum(pay_ment),
    sum(
    if((is_robot=0),pay_ment,0)
    ),
    sum(
    if((is_robot=1),pay_ment,0)
    )
    from roomCost WHERE create_time >= '%s' and create_time <='%s'
    """ \
          % (startDate, endDate)

    results = MysqlljgameInterface.select(sql, fetchmany=False)
    if results:
        results = results[0][0:1], results[0][1:2], results[0][2:3]
        for i, y in enumerate(results):
            info = {}
            info['pay_ment'] = float(y[0]) if y[0] else 0
            info['type'] = ['用户和机器人', '用户', '机器人'][i]
            res.append(info)
    return {'data': res, 'count': len(res)}

def get_gold_roomcost_graphlist(redis, startDate, endDate, gametype, gameid):
    """
    返回 计算某一段时间内 mysql - roomCost 统计表中 '房费(pay_ment)’ 的总数
    :param redis:
    :param startDate:
    :param endDate:
    :return:
    """
    if gameid:
        sql = """select FROM_UNIXTIME(create_time,'%s'), sum(pay_ment),
                sum(
                if((is_robot=0),pay_ment,0)
                ),
                sum(
                if((is_robot=1),pay_ment,0)
                )
                from roomCost where user_id='%s' and create_time>='%s' and create_time <='%s'  GROUP BY from_unixtime(create_time,'%s') ORDER BY create_time
                """ \
              % (gametype, gameid, startDate, endDate, gametype)
    else:
        sql = """select FROM_UNIXTIME(create_time,'%s'), sum(pay_ment),
        sum(
        if((is_robot=0),pay_ment,0)
        ),
        sum(
        if((is_robot=1),pay_ment,0)
        )
        from roomCost where create_time>='%s' and create_time <='%s'  GROUP BY from_unixtime(create_time,'%s') ORDER BY create_time
        """ \
              % (gametype, startDate, endDate, gametype)
    results = MysqlljgameInterface.select(sql, fetchmany=False)

    graph_data = []
    if results:
        if None not in results[0]:
            for i in results:
                info = {}
                if i[0] and ' ' in i[0]:
                    a, b = i[0].split(' ')
                    if ':' in b:
                        info['datetime'] = b + '\n' + a
                    else:
                        info['datetime'] = b + ':00' + '\n' + a
                else:
                    info['datetime'] = i[0]
                info['graph_pre_balance'] = float(i[1])
                info['graph_user_pre_balance'] = float(i[2])
                info['graph_robot_pre_balance'] = float(i[3])
                graph_data.append(info)

    return {'graph_data': graph_data}

def get_gold_transorder(startDate, endDate, pageSize, pageNumber, searchText, limit=True, redis=redis):
    """
    返回 mysql - trans_order 显示'局数表'各项数据
    :param startDate: starttime-> 2018-07-12
    :param endDate: starttime-> 2018-07-19
    :param uid: uid
    :return: {"count": len(res), "data": res}
    """
    res = []
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))
    if pageNumber:
        pageNumber = (pageNumber - 1) * int(pageSize)

    try:
        if searchText:
            sql = "select id, user_id, trans_id, game_id, banker, room_id, playid, chair, status, tiles, reason,pre_balance, balance,betting_balance, after_balance, is_robot, create_time, update_time, is_deleted  from trans_order  where user_id='%s' and create_time>= '%s' and  create_time<='%s' order by create_time desc limit %s,%s"
            sql = sql % (searchText, startDate, endDate, pageNumber, pageSize)
            results = MysqlljgameInterface.select(sql, fetchmany=False)

            sql = "select count(1)  from trans_order  where user_id='%s' and create_time>= '%s' and  create_time<='%s'"
            sql = sql % (searchText, startDate, endDate)
            count = MysqlljgameInterface.select(sql, fetchmany=False)
        else:
            sql = "select id, user_id, trans_id, game_id, banker, room_id, playid, chair, status, tiles, reason, \
            pre_balance, balance,betting_balance, after_balance, is_robot, create_time, update_time, is_deleted  from trans_order where create_time >='%s' and create_time <= '%s' order by create_time desc limit %s,%s"
            sql = sql % (startDate, endDate, pageNumber, pageSize)
            results = MysqlljgameInterface.select(sql, fetchmany=False)

            sql = "select count(1)  from trans_order where create_time >='%s' and create_time <= '%s' order by create_time"
            sql = sql % (startDate, endDate)
            count = MysqlljgameInterface.select(sql, fetchmany=False)

        if results:
            num = 1
            for i in results:
                info = {}
                info['number'] = num
                num += 1
                info['user_id'] = i[1]
                info['sum_prebalance'] = 100
                info['trans_id'] = i[2]
                info['game_id'] = i[3]
                info['banker'] = '庄家' if i[4] else '闲家'
                info['room_id'] = i[5]
                info['playid'] = PLAYTYPE(i[6])
                info['chair'] = i[7]
                info['status'] = '正常' if i[8] else '异常'
                info['tiles'] = i[9]
                info['reason'] = i[10]
                info['pre_balance'] = i[11]
                info['balance'] = i[12]
                info['betting_balance'] = i[13]
                info['after_balance'] = i[14]
                info['is_robot'] = '机器人' if i[15] else '用户'
                info['create_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[16])) if i[16] else ''
                info['update_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[17])) if i[17] else ''
                info['is_deleted'] = i[18]
                gameid = redis.lindex("game:gold:gameid:%s:list" % (i[3]), 0)
                info['gameName'] = redis.hmget("game:gold:gameid:%s:id:%s" % (i[3], gameid), "gameName")
                res.append(info)

    except Exception as e:
        print e

    return {"count": count, "data": res}

def get_gold_transorder_sumlist(redis):
    """
    mysql - trans_order 统计表中'pre_balance,balance,after_balance'中的总数据
    :param redis:
    :return:
    """
    res = []
    sql = """select sum(pre_balance), sum(balance), sum(after_balance),
    sum(
    if((is_robot=0),pre_balance,0)
    ),
    sum(
    if((is_robot=0),balance,0)
    ),
    sum(
    if((is_robot=0),after_balance,0)
    ),
    sum(
    if((is_robot=1),pre_balance,0)
    ),
    sum(
    if((is_robot=1),balance,0)
    ),
    sum(
    if((is_robot=1),after_balance,0)
    )
    from trans_order
    """
    results = MysqlljgameInterface.select(sql, fetchmany=False)
    if results:
        results = results[0][0:3], results[0][3:6], results[0][6:9]
        for i, y in enumerate(results):
            info = {}
            info['pre_balance'] = float(y[0]) if y[0] else 0
            info['balance'] = float(y[1]) if y[1] else 0
            info['after_balance'] = float(y[2]) if y[2] else 0
            info['type'] = ['用户和机器人', '用户', '机器人'][i]
            res.append(info)
    return {'data': res, 'count': len(res)}

def get_gold_transorder_daylist(redis, startDate, endDate):
    """
    返回计算某一段时间内
    mysql - trans_order 统计表中'pre_balance,balance,after_balance'中的总数据
    :param redis:
    :param startDate:
    :param endDate:
    :return:
    """
    res = []
    sql = """select sum(pre_balance), sum(balance), sum(after_balance),
    sum(
    if((is_robot=0),pre_balance,0)
    ),
    sum(
    if((is_robot=0),balance,0)
    ),
    sum(
    if((is_robot=0),after_balance,0)
    ),
    sum(
    if((is_robot=1),pre_balance,0)
    ),
    sum(
    if((is_robot=1),balance,0)
    ),
    sum(
    if((is_robot=1),after_balance,0)
    )
    from trans_order  where create_time >= '%s' and create_time <= '%s' 
    """ \
          % (startDate, endDate)
    results = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        results = results[0][0:3], results[0][3:6], results[0][6:9]
        for i, y in enumerate(results):
            info = {}
            info['pre_balance'] = float(y[0]) if y[0] else 0
            info['balance'] = float(y[1]) if y[1] else 0
            info['after_balance'] = float(y[2]) if y[2] else 0
            info['type'] = ['用户和机器人', '用户', '机器人'][i]
            res.append(info)
    return {'data': res, 'count': len(res)}

def get_gold_transorder_graphlist(redis, startDate, endDate, gameid, gametype):
    """
    返回统计图表数据
    计算某一段时间内 mysql - trans_order 统计表中'pre_balance,balance,after_balance'中的总数据
    :param redis:
    :param startDate:
    :param endDate:
    :return:
    """
    if gameid:
        sql = """select from_unixtime(create_time,'%s'), sum(pre_balance), sum(balance), sum(after_balance),
                sum(
                if((is_robot=0),pre_balance,0)
                ),
                sum(
                if((is_robot=0),balance,0)
                ),
                sum(
                if((is_robot=0),after_balance,0)
                ),
                sum(
                if((is_robot=1),pre_balance,0)
                ),
                sum(
                if((is_robot=1),balance,0)
                ),
                sum(
                if((is_robot=1),after_balance,0)
                )
                from trans_order where user_id='%s' and create_time>='%s' and create_time<='%s' GROUP BY from_unixtime(create_time,'%s')
                """ % (gametype, gameid, startDate, endDate, gametype)
    else:
        sql = """select from_unixtime(create_time,'%s'), sum(pre_balance), sum(balance), sum(after_balance),
        sum(
        if((is_robot=0),pre_balance,0)
        ),
        sum(
        if((is_robot=0),balance,0)
        ),
        sum(
        if((is_robot=0),after_balance,0)
        ),
        sum(
        if((is_robot=1),pre_balance,0)
        ),
        sum(
        if((is_robot=1),balance,0)
        ),
        sum(
        if((is_robot=1),after_balance,0)
        )
        from trans_order where create_time>='%s' and create_time<='%s' GROUP BY from_unixtime(create_time,'%s')
        """ % (gametype, startDate, endDate, gametype)
    results = MysqlljgameInterface.select(sql, fetchmany=False)

    graph_data = []
    if results:
        if None not in results[0]:
            for i in results:
                info = {}
                if i[0] and ' ' in i[0]:
                    a, b = i[0].split(' ')
                    if ':' in b:
                        info['datetime'] = b + '\n' + a
                    else:
                        info['datetime'] = b + ':00' + '\n' + a
                else:
                    info['datetime'] = i[0]
                info['graph_pre_balance'] = float(i[1])
                info['graph_balance'] = float(i[2])
                info['graph_after_balance'] = float(i[3])
                info['graph_user_pre_balance'] = float(i[4])
                info['graph_user_balance'] = float(i[5])
                info['graph_user_after_balance'] = float(i[6])
                info['graph_root_pre_balance'] = float(i[7])
                info['graph_root_balance'] = float(i[8])
                info['graph_robot_after_balance'] = float(i[9])
                graph_data.append(info)
    return {'graph_data': graph_data}

def get_gold_transorder_id(redis, trans_id):
    """
    返回金币场-局数表中同一局数下的数据
    :param redis:
    :param trans_id:
    :return:
    """
    res = []
    try:
        sql = "select id, user_id, trans_id, game_id, banker, room_id, playid, chair, status, tiles, reason,pre_balance, balance,betting_balance, after_balance, is_robot, create_time, update_time, is_deleted  from trans_order where trans_id='%s' order by create_time desc" % (trans_id)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        if results:
            num = 1
            for i in results:
                info = {}
                info['number'] = num
                num += 1
                info['user_id'] = i[1]
                info['trans_id'] = i[2]
                info['game_id'] = i[3]
                info['banker'] = '庄家' if i[4] else '闲家'
                info['room_id'] = i[5]
                info['playid'] = PLAYTYPE(i[6])
                info['chair'] = i[7]
                info['status'] = '正常' if i[8] else '异常'
                info['tiles'] = i[9]
                info['reason'] = i[10]
                info['pre_balance'] = i[11]
                info['balance'] = i[12]
                info['betting_balance'] = i[13]
                info['after_balance'] = i[14]
                info['is_robot'] = '机器人' if i[15] else '用户'
                info['create_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[16])) if i[16] else ''
                info['update_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[17])) if i[17] else ''
                info['is_deleted'] = i[18]
                res.append(info)

    except Exception as e:
        print e

    return {"count": len(res), "data": res}

def get_gold_game_day(redis, startDate, endDate):
    """
    统计每日金币场游戏人数在线
    :param redis:
    :return:
    """
    res = []
    sql = """SELECT fromTime, SUM(userCount) AS userCount, COUNT(user_id),game_id, pre_balance, balance, after_balance
    FROM (SELECT FROM_UNIXTIME(create_time,'%Y-%m-%d') AS fromTime, COUNT(user_id) AS userCount, user_id, game_id ,
    SUM(pre_balance) AS pre_balance, SUM(balance) AS balance,SUM(after_balance) AS after_balance
    FROM trans_order WHERE is_robot='0' GROUP BY  FROM_UNIXTIME(create_time,'%Y-%m-%d'),game_id,user_id) AS a GROUP BY fromTime,game_id ORDER BY fromTime desc
    """
    report = MysqlljgameInterface.select(sql, fetchmany=False)
    if report:
        sum = 1
        for i in report:
            info = {}
            if startDate <= i[0] <= endDate:
                info['number'] = sum
                sum += 1
                info['create_time'] = i[0]
                info['count'] = float(i[1])
                info['single_count'] = float(i[2])
                info['game_id'] = i[3]
                gameid = redis.lindex("game:gold:gameid:%s:list" % (i[3]), 0)
                info['gamename'] = redis.hmget("game:gold:gameid:%s:id:%s" % (i[3], gameid), "gameName")
                info['pre_balance'] = float(i[4])
                info['balance'] = float(i[5])
                info['after_balance'] = float(i[6])
                res.append(info)
    return {'data': res, 'count': len(res)}

def get_gold_game_daylist(redis, game_id, startDate):
    """
    返回获取金币场同一局数下的玩家列表
    :param redis:
    :param gameid:
    :param startDate:
    :return:
    """
    res = []
    sql = """select id, user_id, game_id, sum(pre_balance), sum(balance) , sum(after_balance), from_unixtime(create_time,'%%Y-%%m-%%d'),count(*) from trans_order where game_id='%s' and is_robot='0' and  from_unixtime(create_time,'%%Y-%%m-%%d')='%s' GROUP BY user_id  ORDER BY create_time desc """ \
          % (game_id, startDate)
    report = MysqlljgameInterface.select(sql, fetchmany=False)
    if report:
        sum = 1

        for i in report:
            info = {}
            info['number'] = sum
            sum += 1
            info['id'] = i[0]
            info['user_id'] = i[1]
            info['game_id'] = i[2]
            gameid = redis.lindex("game:gold:gameid:%s:list" % (i[2]), 0)
            info['gamename'] = redis.hmget("game:gold:gameid:%s:id:%s" % (i[2], gameid), "gameName")
            info['pre_balance'] = float(i[3])
            info['balance'] = float(i[4])
            info['after_balance'] = float(i[5])
            info['create_time'] = i[6]
            info['count'] = i[7]
            res.append(info)
    return {'data': res, 'count':len(res)}

def get_gold_game_sumlist(redis):
    """
    返回统计每日金币场游戏人数在线总数据
    :param redis:
    :return:
    """
    res = []
    sql = """SELECT  game_id, SUM(userCount) AS userCount, COUNT(user_id)
    FROM (SELECT 
     COUNT(user_id) AS userCount, user_id, game_id 
    FROM trans_order WHERE is_robot='0' GROUP BY FROM_UNIXTIME(create_time,'%Y-%m-%d'),game_id,user_id) AS a GROUP BY game_id
    """
    results = MysqlljgameInterface.select(sql, fetchmany=False)
    if results:
        for i in results:
            info = {}
            gamelist = redis.lrange('game:gold:gameid:list', 0, -1)
            if str(i[0]) in gamelist:
                playid = redis.lindex('game:gold:gameid:%s:list' % (i[0]), 0)
                gamename = redis.hmget('game:gold:gameid:%s:id:%s' % (i[0], playid), 'gameName')
                info['gamename'] = gamename
            info['game_id'] = i[0] if i[0] else 0
            info['game_sum'] = float(i[1]) if i[1] else 0
            info['game_count'] = float(i[2]) if i[2] else 0
            res.append(info)
    return {'data': res, 'count':len(res)}

def get_gold_game_day_list(redis, startDate, endDate):
    """
    返回计算某一段时间内
    统计每日金币场游戏人数在线总数据
    :param redis:
    :param startDate:
    :param endDate:
    :return:
    """
    res = []
    sql = """SELECT  game_id, SUM(userCount) AS userCount, COUNT(user_id)
    FROM (SELECT 
     COUNT(user_id) AS userCount, user_id, game_id 
    FROM trans_order WHERE is_robot='0' and create_time>='%s' and create_time<='%s' GROUP BY FROM_UNIXTIME(create_time,'%%Y-%%m-%%d'),game_id,user_id) AS a GROUP BY game_id
    """ \
          % (startDate, endDate)
    results = MysqlljgameInterface.select(sql, fetchmany=False)
    if results:
        for i in results:
            info = {}
            gamelist = redis.lrange('game:gold:gameid:list', 0, -1)
            if str(i[0]) in gamelist:
                playid = redis.lindex('game:gold:gameid:%s:list' % (i[0]), 0)
                gamename = redis.hmget('game:gold:gameid:%s:id:%s' % (i[0], playid), 'gameName')
                info['gamename'] = gamename
            info['game_id'] = i[0] if i[0] else 0
            info['game_sum'] = float(i[1]) if i[1] else 0
            info['game_count'] = float(i[2]) if i[2] else 0
            res.append(info)
    return {'data': res, 'count': len(res)}


def PLAYTYPE(num):
    """
    返回数据报中对应的场次，
    {0:新手场, 1:初级场, 2:中级场， 3:高级场, 4:土豪场，5:至尊场}
    :param num:
    :return:
    """
    if num == 0:
        return '新手场'
    elif num == 1:
        return '初级场'
    elif num == 2:
        return '中级场'
    elif num == 3:
        return '高级场'
    elif num == 4:
        return '土豪场'
    elif num == 5:
        return '至尊场'
    else:
        return

def get_daily_reward(redis, uid):
    """
        领取50金币。 当身上少于50金币的情况下可以领取，每日只能4次, 每日6点重置
    """
    gold = redis.hget(FORMAT_USER_TABLE % uid, 'gold')
    try:
        if not gold: gold = 0
        if int(gold) < 50:
            daily_table = 'daily:uid:%s' % uid
            if redis.exists(daily_table):
                count = redis.hget(daily_table, 'count')
                if count == '4':
                    return {'code': 1, 'msg': u'每日只能领取4次', 'gold': gold}

            else:
                redis.hset(daily_table, 'count', 0)

                # 设置key过期时间
                today = datetime.today()
                today = today.replace(hour=0, minute=0, second=0, microsecond=0)
                delta = timedelta(1, 3600 * 6)
                tomorrow = today + delta
                ts = int(time.mktime(tomorrow.timetuple()))
                redis.expireat(daily_table, ts)

            redis.hincrby(FORMAT_USER_TABLE % uid, 'gold', 50)
            redis.hincrby(daily_table, 'count', 1)
            now_gold = redis.hget(FORMAT_USER_TABLE % uid, 'gold')
            try:
                # 记录log
                name = redis.hget(FORMAT_USER_TABLE % uid, 'account')
                curTime = datetime.now()
                strTime = curTime.strftime('%Y-%m-%d %H:%M:%S')
                data = {
                    'user_id': uid,
                    'name': name,
                    'createtime': strTime,
                    'pre_gold': gold,
                    'changed': 50,
                    'now_gold': int(gold) + 50,
                    'action': 3  # 1:扣房费, 2:结算扣分, 3:每日领取
                }
                MysqlInterface.insert('log_gold', **data)
            except:
                print 'mysql insert error.'

            return {'code': 0, 'msg': u'领取成功', 'gold': now_gold}

        else:
            return {'code': 2, 'msg': u'少于50金币才能领取', 'gold': gold}

    except Exception as e:
        print e

    return {'code': -1, 'msg': u'error'}


def GoldGameDict(redis):
    """
    返回金币场游戏字典
    :param redis:
    :param session:
    :return: {'经典牛牛':555,'廉江二人麻将':771}
    """
    namedict = {}
    gamelist = redis.lrange('game:gold:gameid:list', 0, -1)
    for i in gamelist:
        playid = redis.lindex('game:gold:gameid:%s:list' % (i), 0)
        gameName, = redis.hmget('game:gold:gameid:%s:id:%s' % (i, playid), 'gameName')
        namedict[gameName] = i
    return namedict


def Bonus_time():
    """
    获取当前时间在哪个段，{'0':一般,'1':'夜间','2':'黎明'}
    :return:
    """
    from datetime import datetime
    now = datetime.now().hour
    if now in range(10, 19):
        return '0'
    if now in range(19, 24) + range(0, 4):
        return '1'
    if now in range(4, 10):
        return '2'


def Bonus_number(func, online):
    """
    返回虚数加成人数，根据Bonus_time函数的时间段获取对应的加成人数
    :param func:
    :param online:
    :return:
    """
    import random
    now = func()
    tmp = None
    data = {
        '1': {'0': [150, 180], '1': [200, 250], '2': [14, 17]},
        '2': {'0': [120, 160], '1': [180, 220], '2': [13, 16]},
        '3': {'0': [100, 140], '1': [150, 200], '2': [11, 15]},
        '4': {'0': [80, 110],  '1': [120, 175], '2': [9, 14]},
        '5': {'0': [60, 105],  '1': [80, 140],  '2': [8, 13]},
        '6': {'0': [50, 100],  '1': [60, 120],  '2': [6, 10]},
        '7': {'0': [40, 85],   '1': [50, 100],  '2': [0, 0]},
    }
    if online:
        if online in range(1, 11):
            tmp = data.get('1')
        elif online in range(11, 26):
            tmp = data.get('2')
        elif online in range(26, 51):
            tmp = data.get('3')
        elif online in range(51, 101):
            tmp = data.get('4')
        elif online in range(101, 151):
            tmp = data.get('5')
        elif online in range(151, 201):
            tmp = data.get('6')
        else:
            tmp = data.get('7')
        now = tmp.get(now)
        online += random.randint(*now)
        return online
    return online