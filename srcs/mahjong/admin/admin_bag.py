#coding:utf-8
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    背包
"""
from bottle import *
from admin import admin_app
from config.config import STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,RES_VERSION
from common.utilt import *
from common.log import *
from datetime import datetime
from web_db_define import *
from access_module import *
from common import encrypt_util,convert_util,json_util,web_util
from bag.bag_config import bag_redis
from model.bagModel import *

import json
import uuid

@admin_app.get('/bag/create/item')
@checkAccess
def createItem(redis,session):

    lang    = getLang()

    info = {
            'title'                  :       '创建道具',
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
            'submitUrl'              :       BACK_PRE + "/bag/create/item"
    }

    return template('admin_bag_create_item',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=0)

@admin_app.post('/bag/create/item')
@checkAccess
def createItem(redis,session):

    lang    = getLang()

    item_id = request.forms.get('item_id', '').strip()
    title = request.forms.get('title', '').strip()
    des = request.forms.get('des', '').strip()
    icon = request.forms.get('icon', '').strip()
    price = request.forms.get('price', '').strip()
    times = request.forms.get('times', '').strip()
    days = request.forms.get('days', '').strip()
    unit = request.forms.get('unit', '').strip()
    can_reward = request.forms.get('can_reward', '').strip()

    info = {
        'title'                  :       '创建道具',
        'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
        'submitUrl'              :       BACK_PRE + "/bag/create/item"
    }

    if not title or not item_id or not des:
        return template('admin_bag_create_item',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=2)

    for iid in bag_redis.smembers(ITEM_ID_SET):
        if item_id == iid:
            return template('admin_bag_create_item',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=3)

    bag_redis.hmset(ITEM_ATTRS%item_id,{
        "item_id":item_id,
        "title":title,
        "des":des,
        "is_delete":0,
        "price":price,
        "is_goods":1,
        "days":days,
        "times":times,
        "bag_show":1,
        "unit":unit,
        "can_reward":can_reward,
    })

    bag_redis.sadd(ITEM_ID_SET,item_id)
    return template('admin_bag_create_item',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=1)

@admin_app.get('/bag/list')
@checkAccess
def getCurOnline(redis,session):
    """
        道具列表
    """
    lang    =  getLang()
    isList  =  request.GET.get('list','').strip()

    if isList:
        return getItemListInfo()
    else:
        info = {
                'title'                  :           '道具列表',
                'listUrl'                :           BACK_PRE+'/bag/list?list=1',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_bag_list',info=info,lang=lang,RES_VERSION=RES_VERSION,op_res=0)

@admin_app.get('/bag/item/changeI')
@checkAccess
def DeleteItem(redis,session):
    """
        删除或恢复道具
    """

    lang    =  getLang()
    item_id  =  request.GET.get('item_id','').strip()
    ci  =  request.GET.get('ci','').strip()

    changeIsDelete(item_id,ci)

    info = {
        'title'                  :           '道具列表',
        'listUrl'                :           BACK_PRE+'/bag/list?list=1',
        'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    return template('admin_bag_list',info=info,lang=lang,RES_VERSION=RES_VERSION,op_res=1)

@admin_app.get('/bag/item/isgoods')
@checkAccess
def DeleteItem(redis,session):
    """
        设定道具是否可在商城购买
    """

    lang    =  getLang()
    item_id  =  request.GET.get('item_id','').strip()
    ig  =  request.GET.get('ig','').strip()

    changeIsGoods(item_id,ig)

    info = {
        'title'                  :           '道具列表',
        'listUrl'                :           BACK_PRE+'/bag/list?list=1',
        'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    return template('admin_bag_list',info=info,lang=lang,RES_VERSION=RES_VERSION,op_res=1)

@admin_app.get('/bag/item/can_use')
@checkAccess
def canUseItem(redis,session):
    """
        设定道具是否使用
    """

    lang    =  getLang()
    item_id  =  request.GET.get('item_id','').strip()
    cu  =  request.GET.get('cu','').strip()

    changeCanUse(item_id,cu)

    info = {
        'title'                  :           '道具列表',
        'listUrl'                :           BACK_PRE+'/bag/list?list=1',
        'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    return template('admin_bag_list',info=info,lang=lang,RES_VERSION=RES_VERSION,op_res=1)

@admin_app.get('/bag/item/modify')
@checkAccess
def itemModify(redis,session):
    """
        修改道具信息
    """

    lang    =  getLang()
    item_id  =  request.GET.get('item_id','').strip()

    dic =  getModifyItemInfo(item_id)

    info = {
        'title'                  :           '修改道具信息',
        'submitUrl'              :           BACK_PRE + "/bag/item/modify",
        'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    return template('admin_bag_item_modify',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=0,**dic)

@admin_app.post('/bag/item/modify')
@checkAccess
def itemModify(redis,session):

    lang    = getLang()

    item_id = request.forms.get('item_id', '').strip()
    title = request.forms.get('title', '').strip()
    des = request.forms.get('des', '').strip()
    icon = request.forms.get('icon', '').strip()
    price = request.forms.get('price', '').strip()
    times = request.forms.get('times', '').strip()
    days = request.forms.get('days', '').strip()
    unit = request.forms.get('unit', '').strip()
    can_reward = request.forms.get('can_reward', '').strip()

    dic =  getModifyItemInfo(item_id)

    info = {
        'title'                  :       '创建道具',
        'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
        'submitUrl'              :       BACK_PRE + "/bag/item/modify",
    }

    if not title or not item_id or not des:
        return template('admin_bag_item_modify',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=2,**dic)

    bag_redis.hmset(ITEM_ATTRS%item_id,{
        "item_id":item_id,
        "title":title,
        "des":des,
        "price":price,
        "times":times,
        "days":days,
        "unit":unit,
        "can_reward":can_reward,
    })

    return template('admin_bag_item_modify',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=1,**dic)

@admin_app.get('/bag/send/mail')
@checkAccess
def send_mail(redis,session):
    """
        发送邮件页面
    """

    lang    = getLang()

    items = getItemTtileAndId()

    info = {
            'title'                  :       '发送邮件',
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
            'submitUrl'              :       BACK_PRE + "/bag/send/mail"
    }

    return template('admin_bag_send_mail',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=0,items=items)

@admin_app.post('/bag/send/mail')
@checkAccess
def send_mail(redis,session):
    """
        发送邮件接口
    """
    lang    = getLang()
    title = request.forms.get('title', '').strip()
    uid = request.forms.get('uid', '').strip()
    body = request.forms.get('body', '').strip()

    items = getItemTtileAndId()

    info = {
        'title'                  :       '发送邮件',
        'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
        'submitUrl'              :       BACK_PRE + "/bag/send/mail"
    }

    item_ids = bag_redis.smembers(ITEM_ID_SET)
    e_num = bag_redis.scard(USER_EMAIL_SET % uid)
    if int(e_num) >= 50:
        return template('admin_bag_send_mail',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=3,items=items)

    a_list = []
    for item_id in item_ids:
        num = request.forms.get('item'+item_id, '').strip()
        if num:
            a_member = item_id+","+num
            a_list.append(a_member)

    if a_list:
        awards = "|".join(a_list)
    else:
        awards = ""

    email_id = uuid.uuid4().hex
    bag_redis.hmset(EMAIL_HASH%email_id,{"title":title,"body":body,"awards":awards,"send_time":datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'),"read":0,"timestamp":str(time.time())})
    bag_redis.sadd(USER_EMAIL_SET%uid,email_id)

    return template('admin_bag_send_mail',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=1,items=items)

@admin_app.get('/bag/vcoin/day')
@checkAccess
def getVcoinDay(redis,session):
    """
    当天元宝信息
    """
    curTime  = datetime.now()
    lang     = getLang()

    fields = ('isList','id','startDate','endDate','date')
    for field in fields:
        exec("%s = request.GET.get('%s','').strip()"%(field,field))

    if date:
        endDate = date

    if not id:
        id = session['id']

    if isList:
        selfUid = id
        report = get_redbag_info(redis,selfUid,startDate,endDate)
        return json.dumps(report)
    else:
        """ 返回模板信息 """
        info = {
                    'title'                  :       '元宝当天信息',
                    'listUrl'                :       BACK_PRE+'/bag/vcoin/day?isList=1',
                    'searchTxt'              :       '',
                    'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
        }

    return template('admin_bag_vcoin_day',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/bag/vcoin/sum')
def getVcoinDay(redis,session):
    """
         元宝总表
    """
    lang    =  getLang()
    isList  =  request.GET.get('list','').strip()

    if isList:
        return get_redbag_sum_info()
    else:
        info = {
                'title'                  :           '元宝总表',
                'listUrl'                :           BACK_PRE+'/bag/vcoin/sum?list=1',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_bag_vcoin_sum',info=info,lang=lang,RES_VERSION=RES_VERSION,op_res=0)

@admin_app.get('/bag/exchange/list')
@checkAccess
def getCurOnline(redis,session):
    """
        商城兑换列表
    """
    lang    =  getLang()
    isList  =  request.GET.get('list','').strip()

    if isList:
        return get_exchange_info()
    else:
        info = {
            'title'                  :           '商城兑换列表',
            'listUrl'                :           BACK_PRE+'/bag/exchange/list?list=1',
            'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_bag_exchange_list',info=info,lang=lang,RES_VERSION=RES_VERSION,op_res=0)

@admin_app.get('/bag/create/exchange')
@checkAccess
def createItem(redis,session):
    '''
        创建兑换套餐
    :param redis:
    :param session:
    :return:
    '''

    lang    = getLang()

    info = {
            'title'                  :       '创建兑换套餐',
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
            'submitUrl'              :       BACK_PRE + "/bag/create/exchange"
    }

    return template('admin_bag_create_exchange',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=0)

@admin_app.post('/bag/create/exchange')
@checkAccess
def createItem(redis,session):
    '''
        创建兑换套餐
    :param redis:
    :param session:
    :return:
    '''

    lang    = getLang()

    cid = request.forms.get('cid', '').strip()
    name = request.forms.get('name', '').strip()
    cost_type = request.forms.get('cost_type', '').strip()
    cost = request.forms.get('cost', '').strip()
    gain_type = request.forms.get('gain_type', '').strip()
    gain = request.forms.get('gain', '').strip()
    cost_title = request.forms.get('cost_title', '').strip()
    gain_title = request.forms.get('gain_title', '').strip()

    info = {
        'title'                  :       '创建兑换套餐',
        'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
        'submitUrl'              :       BACK_PRE + "/bag/create/exchange"
    }

    if not all([cid,name,cost_type,cost,gain_type,gain]):
        return template('admin_bag_create_exchange',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=2)

    if cid in bag_redis.smembers("currency:change:course:set"):
        return template('admin_bag_create_exchange',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=3)

    bag_redis.hmset("currency:change:course:%s:hesh"%cid,{
        "name":name,
        "cost":cost,
        "cost_type":cost_type,
        "gain":gain,
        "gain_type":gain_type,
        "cost_title":cost_title,
        "gain_title":gain_title
    })

    bag_redis.sadd("currency:change:course:set",cid)
    return template('admin_bag_create_exchange',info=info,lang=lang,RES_VERSION=RES_VERSION,post_res=1)

@admin_app.get('/bag/exchange/del')
@checkAccess
def DeleteItem(redis,session):
    """
        删除兑换套餐
    """

    lang    =  getLang()
    cid =  request.GET.get('cid','').strip()

    bag_redis.srem("currency:change:course:set",cid)
    bag_redis.delete("currency:change:course:%s:hesh"%cid)

    info = {
        'title'                  :           '商城兑换列表',
        'listUrl'                :           BACK_PRE+'/bag/exchange/list?list=1',
        'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    return template('admin_bag_exchange_list',info=info,lang=lang,RES_VERSION=RES_VERSION,op_res=0)

@admin_app.get('/bag/exchange/modify')
@checkAccess
def exchangeModify(redis,session):
    """
        修改兑换套餐
    """

    lang    =  getLang()
    cid =  request.GET.get('cid','').strip()
    dic = bag_redis.hgetall("currency:change:course:%s:hesh"%cid)

    info = {
        'title'                  :           '修改兑换套餐',
        'submitUrl'              :           BACK_PRE + "/bag/exchange/modify",
        'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    return template('admin_bag_exchange_modify',info=info,lang=lang,RES_VERSION=RES_VERSION,cid=cid,post_res=0,**dic)

@admin_app.post('/bag/exchange/modify')
@checkAccess
def createItem(redis,session):
    '''
        修改兑换套餐
    '''

    lang    = getLang()

    cid = request.forms.get('cid', '').strip()
    name = request.forms.get('name', '').strip()
    cost_type = request.forms.get('cost_type', '').strip()
    cost = request.forms.get('cost', '').strip()
    gain_type = request.forms.get('gain_type', '').strip()
    gain = request.forms.get('gain', '').strip()
    cost_title = request.forms.get('cost_title', '').strip()
    gain_title = request.forms.get('gain_title', '').strip()
    big_type_id = request.forms.get('big_type_id', '').strip()
    big_type_title = request.forms.get('big_type_title', '').strip()

    info = {
        'title'                  :           '商城兑换列表',
        'listUrl'                :           BACK_PRE+'/bag/exchange/list?list=1',
        'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    bag_redis.hmset("currency:change:course:%s:hesh"%cid,{
        "name":name,
        "cost":cost,
        "cost_type":cost_type,
        "gain":gain,
        "gain_type":gain_type,
        "cost_title":cost_title,
        "gain_title":gain_title,
        "big_type_title":big_type_title,
        "big_type_id":big_type_id,
    })

    return template('admin_bag_exchange_list',info=info,lang=lang,RES_VERSION=RES_VERSION,op_res=1)


@admin_app.get('/bag/item/bag_show')
@checkAccess
def canUseItem(redis,session):
    """
        设定道具是否使用
    """

    lang    =  getLang()
    item_id  =  request.GET.get('item_id','').strip()
    bs  =  request.GET.get('bs','').strip()

    changeBagShow(item_id,bs)

    info = {
        'title'                  :           '道具列表',
        'listUrl'                :           BACK_PRE+'/bag/list?list=1',
        'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    return template('admin_bag_list',info=info,lang=lang,RES_VERSION=RES_VERSION,op_res=1)