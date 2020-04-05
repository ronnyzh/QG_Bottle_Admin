# -*- coding:utf-8 -*-
# !/usr/bin/python

"""

     背包道具模型

"""
from common.log import log_debug
from web_db_define import *
from datetime import *
from bag.bag_config import bag_redis
from red_envelope_db_define import *

import time
import json
import random

def getItemListInfo():
    item_ids = bag_redis.smembers(ITEM_ID_SET)
    data = []
    for item_id in item_ids:
        dic = bag_redis.hgetall(ITEM_ATTRS%item_id)
        data.append(dic)

    res = json.dumps({"count":len(data),"data":data})
    return res

def changeIsDelete(item_id,ci):
    bag_redis.hset(ITEM_ATTRS%item_id,'is_delete',ci)

def changeIsGoods(item_id,ig):
    bag_redis.hset(ITEM_ATTRS%item_id,'is_goods',ig)

def changeCanUse(item_id,cu):
    bag_redis.hset(ITEM_ATTRS%item_id,'can_use',cu)

def changeBagShow(item_id,bs):
    bag_redis.hset(ITEM_ATTRS%item_id,'bag_show',bs)

def getModifyItemInfo(item_id):
    return bag_redis.hgetall(ITEM_ATTRS%item_id)

def getItemTtileAndId():
    item_ids = bag_redis.smembers(ITEM_ID_SET)
    data = []
    for item_id in item_ids:
        title = bag_redis.hget(ITEM_ATTRS%item_id,'title')
        dic = {
            'title':title,
            'id':item_id
        }
        data.append(dic)

    return data


# 元宝当天信息
def get_redbag_info(redis,selfUid,startDate,endDate):
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
        #if bag_redis.exists(RED_ENVELOPE_DAY_INFO % (dateStr,)):
        info1 = bag_redis.hgetall(RED_ENVELOPE_DAY_INFO % (dateStr,))
        info = {}

        info['date'] = dateStr
        info['day_join_num'] = info1.get('playerCount',0)
        info['day_round'] = info1.get('gameRound',0) if info1.get('gameRound',0) else 0
        info['day_send_redbag'] =round( ( int(info1.get('30',0)) + int(info1.get('60',0)) + int(info1.get('120',0)) ) / 100.0 , 2)
        info['day_send_vcoin'] = int(info1.get('3',0)) + int(info1.get('6',0)) + int(info1.get('12',0)) # 当天发放元宝
        #info['day_send_vcoin'] = bag_redis.get('vcoin:present:date:%s:sum'%dateStr)
        info['day_present_redbag'] = info1.get('baselive_goldingot',0)
        info['day_room_fee'] = info1.get('roomCharge',0) if info1.get('roomCharge',0) else 0
        info['b_robot_change'] = info1.get('B',0)
        info['d_robot_change'] = info1.get('D',0)
        info['diamond_to_vcoin_num'] = 0 #info1.get('playerCount',0)
        r2c = bag_redis.get("redbag2cash:date:%s"%dateStr)
        # vcn = bag_redis.get("buy:vcoin:date:%s"%dateStr)
        info['player_claim_redbag_cash'] = r2c if r2c else 0#info1.get('playerCount',0)
        # info['vcoin_charge_num'] = vcn if vcn else 0 #info1.get('playerCount',0)
        # info['charge_order_num'] = 0 #info1.get('playerCount',0)

        res.append(info)
        endDate -= deltaTime
    return {"count": 1, "data": res}

def get_redbag_sum_info():
    res = [bag_redis.hgetall("redbag:sum:info")]
    return json.dumps({"count": 1, "data": res})


def get_exchange_info():
    course_ids = bag_redis.smembers('currency:change:course:set')
    data = []
    for cid in course_ids:
        dic = bag_redis.hgetall("currency:change:course:%s:hesh"%cid)
        dic['cid'] = cid
        data.append(dic)
    return json.dumps({"count":len(data),"data":data})