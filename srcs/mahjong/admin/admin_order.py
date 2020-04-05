#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
   订单模块
"""


from bottle import *
from admin import admin_app
from config.config import STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,RES_VERSION
from common.utilt import *
from common import encrypt_util,log_util,web_util,json_util
from web_db_define import *
from datetime import datetime,timedelta
from model.orderModel import *
from model.agentModel import *
from common.weixin_util import *
import json
import hashlib
import random
import string

@admin_app.get('/order/buy')
def getBuyPage(redis,session):
    """
    购买钻石
    """
    curTime = datetime.now()
    lang    = getLang()

    selfAccount,selfId = session['account'],session['id']

    agentTable = AGENT_TABLE%(selfId)
    parent_id = redis.hget(agentTable,'parent_id')

    parentAg,type = redis.hmget(AGENT_TABLE%(parent_id),('account','type'))
    if not parentAg:
        parentAg = lang.TYPE_2_ADMINTYPE[1]

    info = {
                'title'               :       lang.CARD_BUY_ONLINE_TXT%(parentAg),
                'parentAccount'       :        parentAg,
                'backUrl'             :       '/admin/order/buy',
                'submitUrl'           :       '/admin/order/buy',
                'rechargeTypes'       :       ROOMCARD2TYPE['agent'],
                'STATIC_LAYUI_PATH'   :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'   :       STATIC_ADMIN_PATH
    }

    return template('admin_order_buy',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/order/buy')
@checkAccess
def do_BuyPage(redis,session):
    """
        购买钻石操作
    """
    lang = getLang()
    curTime = datetime.now()

    selfAccount,selfId = session['account'],session['id']
    parentAg  =  request.forms.get('parentAg','').strip()
    cardNums  =  request.forms.get('cardNums','').strip()
    present_card = request.forms.get('parent_card','').strip()
    passwd    =  request.forms.get('passwd','').strip()
    note      =  request.forms.get('note','').strip()

    #[print]
    print '[%s][orderBuy][info] selfAccount[%s] parentAg[%s] cardNums[%s] present_card[%s] passwd[%s] note[%s]'\
                %(curTime,selfAccount,parentAg,cardNums,present_card,passwd,note)

    try:
        if int(cardNums) <=0:
            return {'code':1,'msg':'充值的钻石数必须大于0.'}
    except:
        return {'code':1,'msg':'非法的钻石数.'}

    checkNullFields = [
            {'field':parentAg,'msg':lang.CARD_SALER_NOT_EXISTS},
            {'field':cardNums,'msg':lang.CARD_RECHARGE_NUMS_REQUEST},
            {'field':passwd,'msg':lang.CARD_RECHARGE_PASSWD_REQ}
    ]

    for check in checkNullFields:
        if not check['field']:
            return {'code':1,'msg':check['msg']}

    adminTable = AGENT_TABLE%(selfId)
    selfPasswd,selfRoomCard,type,parent_id = redis.hmget(adminTable,('passwd','roomcard','type','parent_id'))

    #验证代理密码
    if selfPasswd != hashlib.sha256(passwd).hexdigest():
        return {'code':1,'msg':lang.CARD_HANDLE_TIPS_TXT}

    #生成充值订单号
    orderNo = getOrderNo(selfId)

    orderInfo = {
            'orderNo'                :       orderNo,
            'cardNums'               :       cardNums,
            'card_present'           :       present_card,
            'applyAccount'           :       selfAccount,
            'status'                 :       0,
            'apply_date'             :       curTime.strftime('%Y-%m-%d %H:%M:%S'),
            'finish_date'            :       '',
            'type'                   :       0,
            'note'                   :       note,
            'saleAccount'            :       parentAg
    }

    if createOrder(redis,orderInfo):
        dateStr = curTime.strftime('%Y-%m-%d')
        pipe = redis.pipeline()
        #将订单写入购卡订单
        pipe.lpush(AGENT_BUY_ORDER_LIST%(selfId,dateStr),orderNo)
        pipe.lpush(AGENT_BUYPENDING_ORDER_LIST%(selfId,dateStr),orderNo)
        #将订单写入售卡订单
        pipe.lpush(AGENT_SALE_ORDER_LIST%(parent_id,dateStr),orderNo)
        pipe.lpush(AGENT_SALEPENDING_ORDER_LIST%(parent_id,dateStr),orderNo)

        pipe.execute()

        try:
            member = ''.join([random.choice(string.ascii_letters) for num in range(10)])
            redis.set("wx:order:%s:member" % orderInfo.get("orderNo"), member)

            # 发送公众号订单消息给上级代理
            openid_list = redis.smembers('wx:authorize:%s:openid:set' % parentAg)
            balance, type = redis.hmget(AGENT_TABLE % (redis.get(AGENT_ACCOUNT_TO_ID % parentAg)), ('roomcard', 'type'))
            if type == '0':
                balance = u'无限制'
            orderInfo['balance'] = balance
            for openid in openid_list:
                if not redis.hget("wx:authorize:%s:%s:push:hesh" % (openid, parentAg), 'notOrderPush'):
                    getWeixinOrderPush(redis, openid, orderInfo, type="saleAccount")

            # 发送公众号订单消息给自身
            openid_list = redis.smembers('wx:authorize:%s:openid:set' % selfAccount)
            balance, type = redis.hmget(AGENT_TABLE % (redis.get(AGENT_ACCOUNT_TO_ID % selfAccount)), ('roomcard', 'type'))
            orderInfo['balance'] = balance
            for openid in openid_list:
                if not redis.hget("wx:authorize:%s:%s:push:hesh" % (openid, selfAccount), 'notOrderPush'):
                    getWeixinOrderPush(redis, openid, orderInfo, type="applyAccount")

        except Exception as err:
            print(u'订单发送错误')

        return {'code':0,'msg':lang.CARD_APPLY_SUCCESS_TXT%(orderNo),'jumpUrl':BACK_PRE+'/order/buy/record'}

    return {'code':1,'msg':lang.CARD_APPLY_ERROR_TXT%(orderNo)}


@admin_app.get('/order/buy/record')
@checkAccess
def getBuyRecordPage(redis,session):
    """
        获取购买钻石记录
    """
    curTime = datetime.now()
    lang    = getLang()

    selfAccount,selfId = session['account'],session['id']
    isList = request.GET.get('list','').strip()
    startDate = request.GET.get('startDate','').strip()
    endDate   = request.GET.get('endDate','').strip()

    if not startDate or not endDate:
        #默认显示一周时间
        startDate,endDate = getDaya4Week()

    if isList:
        orders = getBuyOrdersById(redis,selfId,startDate,endDate)
        return json.dumps(orders)
    else:
        info = {
                    'title'               :       lang.CARD_BUY_RECORD_TXT,
                    'startDate'           :       startDate,
                    'endDate'             :       endDate,
                    'searchUrl'           :       BACK_PRE+'/order/buy/record?list=1',
                    'tableUrl'            :       BACK_PRE+'/order/buy/record?list=1',
                    'STATIC_LAYUI_PATH'   :       STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'   :       STATIC_ADMIN_PATH
        }

        return template('admin_order_buy_record',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/order/sale/record')
@checkAccess
def getSaleRecordPage(redis,session):
    """
        获取售卖钻石记录
    """
    curTime = datetime.now()
    lang    = getLang()

    selfAccount,selfId = session['account'],session['id']

    startDate = request.GET.get('startDate','').strip()
    endDate   = request.GET.get('endDate','').strip()
    parentAg = request.GET.get('parentAg', '').strip()
    play = request.GET.get('play', '').strip()

    if not startDate or not endDate:
        #默认显示一周时间
        startDate,endDate = getDaya4Week()

    isList = request.GET.get('list','').strip()

    if isList:
        orders = getSaleOrdersById(redis,selfId,startDate,endDate,parentAg,play)
        return json.dumps(orders)
    else:
        info = {
                    'title'               :       lang.CARD_SALE_RECORD_TXT,
                    'startDate'           :       startDate,
                    'endDate'             :       endDate,
                    'searchUrl'           :       BACK_PRE+'/order/sale/record?list=1',
                    'tableUrl'            :       BACK_PRE+'/order/sale/record?list=1',
                    'STATIC_LAYUI_PATH'   :       STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'   :       STATIC_ADMIN_PATH
        }

        return template('admin_order_sale_record',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/order/comfirm')
@checkLogin
def do_orderComfirm(redis,session):
    """
    代理订单确认
    """
    lang = getLang()
    curTime = datetime.now()
    dateStr = curTime.strftime('%Y-%m-%d')

    selfAccount,selfUid = session['account'],session['id']
    fields = ('orderNo','token')
    for field in fields:
        exec('%s = request.forms.get("%s","").strip()'%(field,field))

    try:
        log_debug('[try do_orderComfirm] orderNo[%s] token[%s] session_token[%s]'%(orderNo,token,session['comfirm_token']))
    except:
        return {'code':-300,'msg':'接口参数请求错误'}

    if session.get('comfirm_token') == None:
        return {'code':1,'msg':'不合法的操作!'}

    # if token != session['comfirm_token']:
    #     return {'code':0,'msg':'请勿重复确认订单','jumpUrl':BACK_PRE+'/order/sale/record'}

    orderTable = ORDER_TABLE%(orderNo)
    if not orderTable:
        return {'code':1,'msg':lang.CARD_ORDER_NOT_EXISTS%(orderNo)}

    applyAccount, cardNums, present_card, status, apply_date, saleAccount = \
        redis.hmget(orderTable, ('applyAccount', 'cardNums', 'card_present', 'status', 'apply_date', 'saleAccount'))

    buyerId = getAgentId(redis,applyAccount)

    buyerTable = AGENT_TABLE%(buyerId)
    salerTable = AGENT_TABLE%(selfUid)

    saleType,salerRoomCard = redis.hmget(AGENT_TABLE%(selfUid),('type','roomcard'))
    if not salerRoomCard:
        salerRoomCard = 0

    orderUpdateInfo = {
                'status'            :       1,
                'finish_date'       :       curTime.strftime('%Y-%m-%d %H:%M:%S')
    }

    #置空
    session['comfirm_token'] = None
    pipe = redis.pipeline()
    try:
        if int(saleType) not in [SYSTEM_ADMIN]:
            #如果不是系统管理员或总公司需要减去对应钻石
            if int(salerRoomCard) < int(cardNums):
                return {'code':4,'msg':lang.CARD_NOT_ENGOUGHT_TXT,'jumpUrl':BACK_PRE+'/order/buy'}
            pipe.hincrby(salerTable,'roomcard',-int(cardNums))

        pipe.hincrby(buyerTable,'roomcard',int(cardNums))
        #将订单从pendding移除
        pipe.lrem(AGENT_BUYPENDING_ORDER_LIST%(buyerId,dateStr),orderNo)
        pipe.lpush(AGENT_BUYSUCCESS_ORDER_LIST%(buyerId,dateStr),orderNo)
        #将订单写入售卡订单
        pipe.lrem(AGENT_SALEPENDING_ORDER_LIST%(selfUid,dateStr),orderNo)
        pipe.lpush(AGENT_SALESUCCESS_ORDER_LIST%(selfUid,dateStr),orderNo)
        #更改订单状态
        pipe.hmset(orderTable,orderUpdateInfo)

        #统计代理购卡
        if redis.exists(AGENT_BUY_CARD_DATE%(buyerId,dateStr)):
            pipe.hincrby(AGENT_BUY_CARD_DATE%(buyerId,dateStr),'cardNums',int(cardNums))
            pipe.hincrby(AGENT_BUY_CARD_DATE%(buyerId,dateStr),'totalNums',int(cardNums))
        else:
            try:
                his_total_nums = redis.get(AGENT_BUY_TOTAL%(buyerId))
                if not his_total_nums:
                    his_total_nums = 0
            except:
                his_total_nums = 0
            pipe.hmset(AGENT_BUY_CARD_DATE%(buyerId,dateStr),{'cardNums':int(cardNums),'date':dateStr,'totalNums':int(his_total_nums)+int(cardNums)})

        #统计代理售卡
        if redis.exists(AGENT_SALE_CARD_DATE%(selfUid,dateStr)):
            pipe.hincrby(AGENT_SALE_CARD_DATE%(selfUid,dateStr),'cardNums',int(cardNums))
            pipe.hincrby(AGENT_SALE_CARD_DATE%(selfUid,dateStr),'totalNums',int(cardNums))
        else:
            try:
                his_total_nums = redis.get(AGENT_SALE_TOTAL%(selfUid))
                if not his_total_nums:
                    his_total_nums = 0
            except:
                his_total_nums = 0
            pipe.hmset(AGENT_SALE_CARD_DATE%(selfUid,dateStr),{'cardNums':int(cardNums),'date':dateStr,'totalNums':int(his_total_nums)+int(cardNums)})
    except Exception,e:
        log_debug('[try order error] reason[%s]'%(e))
        return {'code':1,'msg':'订单确认失败.'}

    pipe.execute()

    redis.delete("wx:order:%s:member" % (orderNo))
    try:
        openid_list = redis.smembers('wx:authorize:%s:openid:set' % saleAccount)
        orderInfo = redis.hgetall(ORDER_TABLE % orderNo)
        balance, type = redis.hmget(AGENT_TABLE % (redis.get(AGENT_ACCOUNT_TO_ID % saleAccount)),
                                    ('roomcard', 'type'))
        if type == '0':
            balance = u'无限制'
        orderInfo['balance'] = balance
        for openid in openid_list:
            if not redis.hget("wx:authorize:%s:%s:push:hesh" % (openid, selfAccount), 'notOrderPush'):
                getWeixinOrderComfire(redis, openid, orderInfo)

        openid_list = redis.smembers('wx:authorize:%s:openid:set' % applyAccount)
        orderInfo = redis.hgetall(ORDER_TABLE % orderNo)
        balance, type = redis.hmget(AGENT_TABLE % (redis.get(AGENT_ACCOUNT_TO_ID % applyAccount)),
                                    ('roomcard', 'type'))
        if type == '0':
            balance = u'无限制'
        orderInfo['balance'] = balance
        for openid in openid_list:
            if not redis.hget("wx:authorize:%s:%s:push:hesh" % (openid, applyAccount), 'notOrderPush'):
                getWeixinOrderComfire(redis, openid, orderInfo, type="applyAccount")
    except Exception as err:
        print(u'订单发送错误')
    return {'code':0,'msg':lang.CARD_COMFIRM_SUCCESS_TXT%(orderNo),'jumpUrl':BACK_PRE+'/order/sale/record'}

@admin_app.get('/order/info')
def getOrderInfo(redis,session):
    """
    订单信息查询
    """
    curTime = datetime.now()
    lang    = getLang()
    fields = ('orderNo','backUrl','isAjax')
    for field in fields:
        exec('%s = request.GET.get("%s","").strip()'%(field,field))

    try:
        log_debug('[try getOrderInfo] orderNo[%s] backUrl[%s] isAjax[%s] is_xhr[%s]'%(orderNo,backUrl,isAjax,request.is_xhr))
    except:
        return {'code':-300,'msg':'接口参数错误'}

    orderTable = ORDER_TABLE%(orderNo)
    if not redis.exists(orderTable):
        print '[%s][order info] orderNo[%s] is not exists.'%(curTime,orderNo)
        return None

    cardNums,applyAccount,status,apply_date,finish_date,note,saleAccount = \
                        redis.hmget(orderTable,('cardNums','applyAccount','status','apply_date','finish_date','note','saleAccount'))

    submit_token = encrypt_util.to_sha256(orderNo)
    session['comfirm_token'] = submit_token
    orderInfo = {
            'title'                 :           lang.CARD_DETAIL_TXT%(orderNo),
            'orderNo'               :           orderNo,
            'cardNums'              :           cardNums,
            'applyAccount'          :           saleAccount,
            'status'                :           lang.COMFIRM_ALREADY_TXT if status=='1'  else lang.COMFIRM_NOT_TXT,
            'applyDate'             :           apply_date,
            'finishDate'            :           finish_date,
            'note'                  :           note,
            'token'                 :           submit_token,
            'rechargeAccount'       :           applyAccount
    }

    if request.is_xhr:
        return orderInfo

    return template('agent_orderInfo',info=orderInfo,RES_VERSION=RES_VERSION)

@admin_app.post('/order/cancel')
def do_orderCancel(redis,session):
    """
    取消订单
    """
    lang = getLang()
    curTime = datetime.now()
    dateStr = curTime.strftime('%Y-%m-%d')

    selfAccount,selfUid,selfType = session['account'],session['id'],session['type']

    orderNo = request.forms.get('orderNo','').strip()
    #print
    print '[%s][order cancel][info] orderNo[%s]'%(curTime,orderNo)

    orderTable = ORDER_TABLE % (orderNo)
    orderInfo = redis.hgetall(orderTable)
    orderInfo['applyId'] = selfUid
    orderInfo['dateStr'] = curTime.strftime('%Y-%m-%d %H:%M:%S')

    if not orderTable:
        print '[%s][order cancel][error] orderNo[%s] is not exists.'
        return {'code':1,'msg':lang.CARD_ORDER_NOT_EXISTS%(orderNo)}

    applyAccount, cardNums, present_card, status, saleAccount, apply_date = \
        redis.hmget(orderTable, ('applyAccount', 'cardNums', 'card_present', 'status', 'saleAccount', 'apply_date'))

    salerId = getAgentId(redis,saleAccount)

    buyerTable = AGENT_TABLE%(selfUid)
    salerTable = AGENT_TABLE%(salerId)

    pipe = redis.pipeline()

    try:
        #将订单从pendding移除
        pipe.lrem(AGENT_BUYPENDING_ORDER_LIST%(selfUid,dateStr),orderNo)
        pipe.lrem(AGENT_BUY_ORDER_LIST%(selfUid,dateStr),orderNo)
        #将订单写入售卡订单
        pipe.lrem(AGENT_SALE_ORDER_LIST%(salerId,dateStr),orderNo)
        pipe.lrem(AGENT_SALEPENDING_ORDER_LIST%(salerId,dateStr),orderNo)
        pipe.lrem(ORDER_LIST,orderNo)
        pipe.delete(orderTable)
        pipe.execute()
    except Exception,e:
        print '[%s][order cancel][error] orderNo[%s] reason[%s]'%(curTime,orderNo,e)
        return {'code':1,'msg':lang.CARD_CANCEL_ERROR_TXT}

    redis.delete("wx:order:%s:member" % (orderInfo.get("orderNo")))
    try:
        if selfAccount == saleAccount:
            openid_list = redis.smembers('wx:authorize:%s:openid:set' % saleAccount)
            balance, type = redis.hmget(AGENT_TABLE % (redis.get(AGENT_ACCOUNT_TO_ID % saleAccount)), ('roomcard', 'type'))
            if type == '0':
                balance = '无限制'
            orderInfo['balance'] = balance
            for openid in openid_list:
                if not redis.hget("wx:authorize:%s:%s:push:hesh" % (openid, saleAccount), 'notOrderPush'):
                    getWeixinOrderCancel(redis, openid, orderInfo)

            openid_list = redis.smembers('wx:authorize:%s:openid:set' % applyAccount)
            balance, type = redis.hmget(AGENT_TABLE % (redis.get(AGENT_ACCOUNT_TO_ID % applyAccount)),
                                        ('roomcard', 'type'))
            if type == '0':
                balance = '无限制'
            orderInfo['balance'] = balance
            for openid in openid_list:
                if not redis.hget("wx:authorize:%s:%s:push:hesh" % (openid, applyAccount), 'notOrderPush'):
                    getWeixinOrderCancel(redis, openid, orderInfo, type="applyAccount")
        if selfAccount == applyAccount:
            openid_list = redis.smembers('wx:authorize:%s:openid:set' % saleAccount)
            balance, type = redis.hmget(AGENT_TABLE % (redis.get(AGENT_ACCOUNT_TO_ID % saleAccount)),
                                        ('roomcard', 'type'))
            if type == '0':
                balance = '无限制'
            orderInfo['balance'] = balance
            for openid in openid_list:
                if not redis.hget("wx:authorize:%s:%s:push:hesh" % (openid, saleAccount), 'notOrderPush'):
                    getWeixinOrderCancel(redis, openid, orderInfo, agent_type=True)

            openid_list = redis.smembers('wx:authorize:%s:openid:set' % applyAccount)
            balance, type = redis.hmget(AGENT_TABLE % (redis.get(AGENT_ACCOUNT_TO_ID % applyAccount)),
                                        ('roomcard', 'type'))
            if type == '0':
                balance = '无限制'
            orderInfo['balance'] = balance
            for openid in openid_list:
                if not redis.hget("wx:authorize:%s:%s:push:hesh" % (openid, applyAccount), 'notOrderPush'):
                    getWeixinOrderCancel(redis, openid, orderInfo, type="applyAccount",  agent_type=True)
    except Exception as err:
        print(u'订单发送错误')
    return {'code':0,'msg':lang.CARD_CANCEL_SUCCESS_TXT%(orderNo),'jumpUrl':BACK_PRE+'/order/buy/record'}


@admin_app.post('/order/sale/cancel')
def do_orderCancel(redis,session):
    """
    取消订单
    """
    lang = getLang()
    curTime = datetime.now()
    dateStr = curTime.strftime('%Y-%m-%d')

    selfAccount,selfUid,selfType = session['account'],session['id'],session['type']

    orderNo = request.forms.get('orderNo','').strip()

    orderTable = ORDER_TABLE % (orderNo)
    orderInfo = redis.hgetall(orderTable)
    orderInfo['dateStr'] = curTime.strftime('%Y-%m-%d %H:%M:%S')
    #print
    print '[%s][order cancel][info] orderNo[%s]'%(curTime,orderNo)

    orderTable = ORDER_TABLE%(orderNo)
    if not orderTable:
        print '[%s][order cancel][error] orderNo[%s] is not exists.'
        return {'code':1,'msg':lang.CARD_ORDER_NOT_EXISTS%(orderNo)}

    applyAccount, cardNums, present_card, status, saleAccount, apply_date = \
        redis.hmget(orderTable, ('applyAccount', 'cardNums', 'card_present', 'status', 'saleAccount', 'apply_date'))

    buyerId = getAgentId(redis,applyAccount)

    buyerTable = AGENT_TABLE%(buyerId)
    salerTable = AGENT_TABLE%(selfUid)

    pipe = redis.pipeline()

    try:
        #将订单从pendding移除
        pipe.lrem(AGENT_BUYPENDING_ORDER_LIST%(buyerId,dateStr),orderNo)
        pipe.lrem(AGENT_BUY_ORDER_LIST%(buyerId,dateStr),orderNo)
        #将订单写入售卡订单
        pipe.lrem(AGENT_SALE_ORDER_LIST%(selfUid,dateStr),orderNo)
        pipe.lrem(AGENT_SALEPENDING_ORDER_LIST%(selfUid,dateStr),orderNo)
        pipe.lrem(ORDER_LIST,orderNo)
        pipe.delete(orderTable)
        pipe.execute()
    except Exception,e:
        print '[%s][order cancel][error] orderNo[%s] reason[%s]'%(curTime,orderNo,e)
        return {'code':1,'msg':lang.CARD_CANCEL_ERROR_TXT}

    redis.delete("wx:order:%s:member" % (orderInfo.get("orderNo")))
    try:
        openid_list = redis.smembers('wx:authorize:%s:openid:set' % saleAccount)
        balance, type = redis.hmget(AGENT_TABLE % (redis.get(AGENT_ACCOUNT_TO_ID % saleAccount)),
                                    ('roomcard', 'type'))
        if type == '0':
            balance = u'无限制'
        orderInfo['balance'] = balance
        for openid in openid_list:
            if not redis.hget("wx:authorize:%s:%s:push:hesh" % (openid, saleAccount), 'notOrderPush'):
                getWeixinOrderCancel(redis, openid, orderInfo)

        openid_list = redis.smembers('wx:authorize:%s:openid:set' % applyAccount)
        balance, type = redis.hmget(AGENT_TABLE % (redis.get(AGENT_ACCOUNT_TO_ID % applyAccount)),
                                    ('roomcard', 'type'))
        if type == '0':
            balance = u'无限制'
        orderInfo['balance'] = balance
        for openid in openid_list:
            if not redis.hget("wx:authorize:%s:%s:push:hesh" % (openid, applyAccount), 'notOrderPush'):
                getWeixinOrderCancel(redis, openid, orderInfo, type="applyAccount")
    except Exception as err:
        print(u'订单发送错误')

    return {'code':0,'msg':lang.CARD_CANCEL_SUCCESS_TXT%(orderNo),'jumpUrl':BACK_PRE+'/order/sale/record'}

@admin_app.get('/order/wechat/record')
@admin_app.get('/order/wechat/record/<action>')
def get_wechat_records(redis,session,action="HALL"):
    """
    获取微信售钻记录接口
    action通知是获取捕鱼还是棋牌
    """
    lang = getLang()
    action = action.upper()
    fields = ('isList','startDate','endDate','memberId','orederNo')
    for field in fields:
        exec('%s = request.GET.get("%s","").strip()'%(field,field))

    log_util.debug('[try get_wechat_records] get params isList[%s] startDate[%s] endDate[%s] memberId[%s] orderNo[%s] action[%s]'\
                        %(isList,startDate,endDate,memberId,orederNo,action))
    if isList:
        condition = {
                'startDate'         :       startDate,
                'endDate'           :       endDate,
                'memberId'          :       memberId,
                'orderNo'           :       orederNo
        }
        records = get_wechat_order_records(redis,session['id'],condition,action)
        return json.dumps(records,cls=json_util.CJsonEncoder)
    else:
        params = 'isList=1&startDate=%s&endDate=%s'%(startDate,endDate)
        info = {
                    'title'         :        lang.WECHAT_RECORD_TITLE if action =="HALL" else lang.WECHAT_FISH_RECORD_TITLE,
                    'tableUrl'      :        BACK_PRE+'/order/wechat/record/{}?{}'.format(action,params),
                    'searchUrl'     :        BACK_PRE+'/order/wechat/record/{}'.format(action),
                    'STATIC_LAYUI_PATH'   :       STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'   :       STATIC_ADMIN_PATH,
                    'startDate'     :        startDate,
                    'action'        :       action,
                    'endDate'       :        endDate
        }

        return template('admin_wechat_record',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/order/wechat/sale/record')
@admin_app.get('/order/wechat/sale/record/<action>')
def get_wechat_records(redis,session,action="HALL"):
    """
    获取微信售钻记录接口
    action通知是获取捕鱼还是棋牌
    """
    lang = getLang()
    action = action.upper()
    fields = ('isList','startDate','endDate','memberId','orederNo')
    for field in fields:
        exec('%s = request.GET.get("%s","").strip()'%(field,field))


    log_util.debug('[try get_wechat_records] get params isList[%s] startDate[%s] endDate[%s] memberId[%s] orderNo[%s] action[%s]'\
                        %(isList,startDate,endDate,memberId,orederNo,action))
    if isList:
        condition = {
                'startDate'         :       startDate,
                'endDate'           :       endDate,
                'memberId'          :       memberId,
                'orderNo'           :       orederNo
        }
        records = get_wechat_order_sale_records(redis,session['id'],condition,action)
        return json.dumps(records,cls=json_util.CJsonEncoder)
    else:
        params = 'isList=1&startDate=%s&endDate=%s'%(startDate,endDate)
        info = {
                    'title'         :        lang.WECHAT_SALE_CURRENCY_TITLE if action =="HALL" else lang.WECHAT_FISH_RECORD_TITLE,
                    'tableUrl'      :        BACK_PRE+'/order/wechat/sale/record/{}?{}'.format(action,params),
                    'searchUrl'     :        BACK_PRE+'/order/wechat/sale/record/{}'.format(action),
                    'STATIC_LAYUI_PATH'   :       STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'   :       STATIC_ADMIN_PATH,
                    'startDate'     :        startDate,
                    'action'        :       action,
                    'endDate'       :        endDate
        }

        return template('admin_wechat_sale_record',info=info,lang=lang,RES_VERSION=RES_VERSION)


@admin_app.get('/order/all')
@checkAccess
def getOrderAll(redis, session):
    """所有订单信息"""
    lang = getLang()
    curTime = datetime.now()

    isList = request.GET.get("islist", "").strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()

    if isList:
        orderlist = []
        # 商城订单
        startDate = datetime.strptime(startDate, '%Y-%m-%d')
        endDate = datetime.strptime(endDate, '%Y-%m-%d')
        deltaTime = timedelta(1)
        while startDate <= endDate:
            dateStr = endDate.strftime('%Y-%m-%d')
            dayOrderList = redis.lrange("dayOrder:%s:101:list" % (dateStr), 0, -1)
            if dayOrderList:
                for each in dayOrderList:
                    orderdict = redis.hgetall('orders:id:%s' % each)
                    if orderdict:
                        orderdict['orderNo'] = each
                        orderdict['money'] = round(float(orderdict['money']) * 0.01, 2)
                        orderdict['startTime'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                               time.localtime(float(orderdict.get('startTime'))))
                        orderdict['time'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                          time.localtime(float(orderdict.get('time'))))
                        endTime = orderdict.get('endTime', '')
                        if endTime:
                            orderdict['endTime'] = '%s-%s-%s %s:%s:%s' % (
                                endTime[:4], endTime[4:6], endTime[6:8], endTime[8:10], endTime[10:12], endTime[12:14])
                        orderdict['memberId'] = redis.get("users:account:%s" % (orderdict['account'])).split(':')[-1]
                        orderdict['parentId'] = redis.hget(AGENT_TABLE % (orderdict.get('groupId', '')), 'parent_id')
                        orderdict['op'] = u'查看'
                        orderdict['orderType'] = u'商城订单'
                        orderlist.append(orderdict)
            # 代理订单
            agentOrderList = redis.keys('agent:*:sale:order:%s' % (dateStr))
            if agentOrderList:
                for item in agentOrderList:
                    i = redis.lrange(item, 0, -1)
                    for each in i:
                        orderdict = redis.hgetall('orders:id:%s' % each)
                        orderdict['orderNo'] = each
                        orderdict['startTime'] = orderdict.get('apply_date')
                        orderdict['endTime'] = orderdict.get('finish_date')
                        orderdict['op'] = '查看'
                        orderdict['orderType'] = u'代理订单'
                        orderlist.append(orderdict)
            endDate -= deltaTime
        return json.dumps({'data': orderlist})
    else:
        info = {
            'title': '订单记录',
            'tableUrl': BACK_PRE + '/order/all?islist=1',
            'STATIC_LAYUI_PATH'   :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'   :       STATIC_ADMIN_PATH,
        }
        return template('admin_order_all', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/order/details')
@admin_app.get('/order/details/<orderNo>')
def getOrderDetails(redis, session, orderNo=None):
    """
    订单记录详情
    """
    lang = getLang()
    curTime = datetime.now()

    orderTable = redis.hgetall("orders:id:%s" % (orderNo))
    type = orderTable.get('type', '')

    # 代理
    if type in ['0', '1', '2']:
        # 购钻代理/玩家
        if u'玩家' in orderTable.get('applyAccount', ''):
            applyId = orderTable.get('applyAccount', '').split('(')[0]
            applyTable = redis.hgetall("users:%s" % (applyId))
            curClubList = ','.join(redis.smembers("club:account:%s:set" % (applyTable.get('account', ''))))
            playerClubList = ','.join(redis.smembers("club:players:accounts:%s:set" % (applyTable.get('account', ''))))
            online = redis.hgetall("user:%s:online" % (applyTable.get('account', '')))
            applyTable['curClubList'] = curClubList
            applyTable['playerClubList'] = playerClubList
            applyTable['online'] = online
            applyAgentTable = {}

        else:
            applyAgentId = redis.get(AGENT_ACCOUNT_TO_ID % (orderTable.get('applyAccount', '')))
            applyAgentTable = redis.hgetall("agents:id:%s" % (applyAgentId))
            applyAgentChildList = ','.join(redis.smembers('agents:id:%s:child' % (applyAgentId)))
            applyAgentTable['members'] = getAgentMembers(redis, applyAgentId)
            applyAgentTable['allMembers'] = getAgentAllMembers(redis, applyAgentId)
            applyAgentTable['todayroomCard'] = getAgentRoomByDay(redis, applyAgentId, curTime.strftime('%Y-%m-%d'))
            applyAgentTable['agentChild'] = applyAgentChildList
            applyTable = {}

        # 售钻代理
        saleAgentId = redis.get(AGENT_ACCOUNT_TO_ID % (orderTable.get('saleAccount', '')))
        saleAgentTable = redis.hgetall("agents:id:%s" % (saleAgentId))
        saleAgentChildList = ','.join(redis.smembers('agents:id:%s:child' % (saleAgentId)))
        saleAgentTable['members'] = getAgentMembers(redis, saleAgentId)
        saleAgentTable['allMembers'] = getAgentAllMembers(redis, saleAgentId)
        saleAgentTable['todayroomCard'] = getAgentRoomByDay(redis, saleAgentId, curTime.strftime('%Y-%m-%d'))
        saleAgentTable['agentChild'] = saleAgentChildList

        # 购钻与售钻相关的订单
        try:
            applySaleOrder = []
            allSaleOrderList = redis.keys('agent:%s:sale:order:*' % (saleAgentId))
            for each in allSaleOrderList:
                for i in redis.lrange(each, 0, -1):
                    order = redis.hgetall('orders:id:%s' % (i))
                    apply = order.get('applyAccount', '').split('(')[0]
                    if applyId == apply:
                        applySaleOrder.append(order)
        except Exception as err:
            applySaleOrder = []
            allSaleOrderList = redis.keys('agent:%s:sale:order:*' % (saleAgentId))
            for each in allSaleOrderList:
                for i in redis.lrange(each, 0, -1):
                    order = redis.hgetall('orders:id:%s' % (i))
                    apply = redis.get(AGENT_ACCOUNT_TO_ID % (order.get('applyAccount', '')))
                    if applyAgentId == apply:
                        applySaleOrder.append(order)

        info = {
            'title': '订单信息[%s]' % (orderNo),
            'backUrl': '/admin/order/all',
            'STATIC_LAYUI_PATH'   :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'   :       STATIC_ADMIN_PATH,
            'userTable': {},
            'orderTable': orderTable,
            'applyTable': applyTable,
            'applyAgentTable': applyAgentTable,
            'applyType': {'0': '超级管理员', '1': '一级代理', '2': '二级代理'}.get(applyAgentTable.get('type'), ''),
            'saleAgentTable': saleAgentTable,
            'saleType': {'0': '超级管理员', '1': '一级代理', '2': '二级代理'}.get(saleAgentTable.get('type'), ''),
            'applySaleOrder': applySaleOrder,
            'goodsTable': {},
            'aType': session.get('type', ''),
            'type': 'sale',
        }
    # 商城
    else:
        # 玩家个人信息
        account = orderTable.get("account", "")
        memberId = redis.get('users:account:%s' % account)[-1]
        userTable = redis.hgetall(redis.get("users:account:%s" % account))
        userTable['memberId'] = memberId

        # 对玩家的订单进行整理
        goodsTable = redis.hgetall('goods:id:%s' % (orderTable.get('num', '')))
        orderTable['orderNo'] = orderNo
        orderTable['startTime'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                time.localtime(float(orderTable.get('startTime'))))
        orderTable['time'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                           time.localtime(float(orderTable.get('time'))))
        endTime = orderTable.get('endTime', '')
        if endTime:
            orderTable['endTime'] = '%s-%s-%s %s:%s:%s' % (
                endTime[:4], endTime[4:6], endTime[6:8], endTime[8:10], endTime[10:12], endTime[12:14])
        if 'groupId' in orderTable:
            orderTable['groupId'] = orderTable['groupId']
            parentId = redis.hget('agents:id:%s' % (orderTable['groupId']), 'parent_id')
            if parentId:
                orderTable['parentId'] = parentId

        # 玩家的购钻订单
        saleOrderList = []
        orderList = redis.keys('agent:*:sale:order:*')
        for each in orderList:
            saleOrderList.extend(redis.lrange(each, 0, -1))
        if saleOrderList:
            saleOrderList = [redis.hgetall("orders:id:%s" % (i)) for i in saleOrderList if
                             u'%s(玩家)' % (memberId) == str(redis.hget("orders:id:%s" % (i), 'applyAccount')).encode(
                                 'utf-8')]
        else:
            saleOrderList = []
        saleOrderList.sort(reverse=True)

        # 商城订单
        userAccount = account
        wechatSaleOrder, faildWechatSale = [], []
        for each in redis.smembers('playerOrder:%s:101:set' % (userAccount)):
            if redis.exists("orders:id:%s" % (each)):
                orderWechatTable = redis.hgetall("orders:id:%s" % (each))
                orderWechatTable['orderNo'] = each
                orderWechatTable['startTime'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                              time.localtime(float(orderWechatTable.get('startTime'))))
                orderWechatTable['time'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                         time.localtime(float(orderWechatTable.get('time'))))
                endTime = orderWechatTable.get('endTime', '')
                if endTime:
                    orderWechatTable['endTime'] = '%s-%s-%s %s:%s:%s' % (
                        endTime[:4], endTime[4:6], endTime[6:8], endTime[8:10], endTime[10:12], endTime[12:14])
                if each == orderNo:
                    orderWechatTable['orderNo'] = '%s(本订单)' % (each)
                wechatSaleOrder.append(orderWechatTable)
            else:
                faildWechatSale.append({'orderNo': each, 'type': 'faild'})
        # 成功商城订单
        successWechatSale = [each for each in wechatSaleOrder if each.get("type") == 'successful']
        # 过期商城订单
        pendingWechatSale = [each for each in wechatSaleOrder if each.get("type") == 'pending']

        info = {
            'title': '订单信息[%s]' % (orderNo),
            'backUrl': '/admin/order/all',
            'STATIC_LAYUI_PATH'   :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'   :       STATIC_ADMIN_PATH,
            'userTable': userTable,
            'orderTable': orderTable,
            'goodsTable': goodsTable,
            'wechatSaleOrder': wechatSaleOrder,  # 商城总订单
            'successWechatSale': successWechatSale,  # 商城成功订单
            'pendingWechatSale': pendingWechatSale,  # 商城挂起订单
            'faildWechatSale': faildWechatSale,  # 商城失败订单
            'saleOrderList': saleOrderList,  # 购钻总订单
            'goods0List': redis.lrange('goods:type:0:list', 0, -1),
            'goods2List': redis.lrange('goods:type:2:list', 0, -1),
            'aType': session.get('type', ''),
            'type': 'wechat',
        }

    return template('admin_order_details', info=info, lang=lang, RES_VERSION=RES_VERSION)



