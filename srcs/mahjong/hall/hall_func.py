#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    this is Description
"""

from bottle import response,request
import inspect
from web_db_define import *
from wechat.wechatData import *
from common.install_plugin import *
from datetime import datetime,timedelta
from config.config import *
from common.log import *
from common import log_util,convert_util
from model.agentModel import *
import time
import uuid
import xml.dom.minidom
import md5
import hashlib
import urllib2
import urllib
import socket
import redis
from common.mysql_util import MysqlInterface

#支付配置常量
TYPE_2_CARS = {

    '1'             :           10,
    '2'             :           20,
    '3'             :           30
}

CHECK_WAIT = 0
CHECK_SUCCESS = 1

SHOP_OPEN = 0
SHOP_CLOSE = 1

ACCESS_TOKEN_API =  'AccessToken:api'
ACCESS_TOKEN_JSAPI =  'AccessToken:jsapi'
def getRedisInst(redisHost,dbNum,port=6381,pwd="168joyvick"):
    """
    获取redis连接实例
    params:
        redisHost   :  redis主机地址
        dbNum        :  数据库编号
        port         :  端口号,默认6379
        pwd          :  密码,默认Fkkg65NbRwQOnq01OGMPy5ZREsNUeURm
    return:
        redis实例
    """
    #global redisdb
    redisdb = redis.ConnectionPool(host=redisHost, port=port, db=dbNum, password=pwd)
    return redis.Redis(connection_pool=redisdb)


def __coinReformat(coin):
    return round(float(coin)/100, 2)

def getDefaultRoomCard(redis,groupId,userId,lastGroup=None):
    """
    获取用户的房卡数
    传入参数: redis,groupId(公会ID),userId(玩家ID),lastGroup(是否第一次)
    返回参数:默认房卡
    """
    provinceAgId = getTopAgentId(redis,groupId)
    defaultCard = redis.get(USER4AGENT_CARD%(provinceAgId, userId))
    log_util.debug('[getDefaultRoomCard] groupId[%s] userId[%s] defaultCards[%s]'%(provinceAgId,userId,defaultCard))
    if not defaultCard:
        if lastGroup:
            #如果不是第一次加公会则返回当前的卡，没有则是0
            defaultCard = redis.get(USER4AGENT_CARD%(groupId, userId))
            if not defaultCard:
                return 0
            return defaultCard
        #如果是第一次则赠送默认房卡
        defaultCard = redis.hget(AGENT_TABLE%(provinceAgId),'defaultRoomCard')
        if not defaultCard:
            defaultCard = 0
    log_util.debug('[getDefaultRoomCard] return defaultCard[%s] groupId[%s]'%(defaultCard,groupId))
    return defaultCard


def getUserByAccount(redis, account):
    """
    通过account获取玩家数据
    """
    account2user_table = FORMAT_ACCOUNT2USER_TABLE%(account)
    userTable = redis.get(account2user_table)
    return userTable


def getInfoBySid(redis,sid):
    """
    通过Sid获取SessionTable, account, uid, verfiySid信息
    """
    SessionTable = FORMAT_USER_HALL_SESSION%(sid)

    # 判断SID是否生效
    if not SessionTable:
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR')
        redis.hincrby("access:number:ip:hset", client_ip, 1)
        print(u"远程地址:%s 头部：%s" % (client_ip, request.headers))
        if not client_ip or client_ip == "183.60.133.160":
            return None, None, None, None
        number = redis.hget("access:number:ip:hset", client_ip)
        number = int(number) if number else 0
        if number >= 3:
            redis.sadd("remote:disbled:ip:set", client_ip)
        return None, None, None, None

    account,uid = redis.hmget(SessionTable, ('account','uid'))
    verfiySid   = redis.get(FORMAT_USER_PLATFORM_SESSION%(uid))
    curTime = getNowTime()
    log_util.debug('[%s][SessionTable][info] account[%s] sessionKey[%s] verfiyKey[%s]'%(curTime,account,sid,verfiySid))
    return SessionTable, account, uid, verfiySid

def getlastMonth():
    now_time=datetime.now()
    totdaytime=(now_time.strftime("%Y-%m")) #获取后一天
    totdaytimeList=totdaytime.split('-')
    year=int(totdaytimeList[0])
    month=int(totdaytimeList[1])
    if month>1:
        lastmonth=month-1
        lastyear=year
    else:
        lastmonth=12
        lastyear=year-1
    return  '%s-%s'%(lastyear,lastmonth)

def getOrderNonceStr():
    nonceStr = ''
    for count in xrange(MAX_RANDOM_STR_COUNT):
        nonceStr += random.choice(RANDOM_STR_LIST)
    return nonceStr

def getOrderNonceStr4TX():
    nonceStr = ''
    for count in xrange(32):
        nonceStr += random.choice(RANDOM_STR_LIST)
    return nonceStr

def getXMLMessage(url, data): #支付用接口
    socket.setdefaulttimeout(WAIT_WEB_TIME)
    xmlDict = {}
    req = urllib2.Request(url = url, headers={'Content-Type':'text/xml'},data = data )
    Message = urllib2.urlopen(req)
    data = Message.read()

    xmlDict = transXml2Dict(data)
    return xmlDict


def gen_sign(params):
    """
        签名生成函数

        :param params: 参数，dict 对象
        :param key: API 密钥
        :return: sign string
    """

    param_list = []
    for k in sorted(params.keys()):
        v = params.get(k)
        if not v:
            # 参数的值为空不参与签名
            continue
        param_list.append('{0}={1}'.format(k, v))

    # 在最后拼接 key
    param_list.append('key={}'.format(MCH_KEY))
    # 用 & 连接各 k-v 对，然后对字符串进行 MD5 运算
    return md5.new('&'.join(param_list)).hexdigest().upper()

def gen_sign4TX(params):
    """
        签名生成函数

        :param params: 参数，dict 对象
        :param key: API 密钥
        :return: sign string
    """

    param_list = []
    for k in sorted(params.keys()):
        v = params.get(k)
        if not v:
            # 参数的值为空不参与签名
            continue
        param_list.append('{0}={1}'.format(k, v))

    # 在最后拼接 key
    param_list.append('key={}'.format(MCH_KEY_TX))
    # 用 & 连接各 k-v 对，然后对字符串进行 MD5 运算
    return md5.new('&'.join(param_list)).hexdigest().upper()

def gen_sign4WXConfig(params):
    """
        签名生成函数

        :param params: 参数，dict 对象
        :return: sign string
    """

    param_list = []
    for k in sorted(params.keys()):
        v = params.get(k)
        if not v:
            # 参数的值为空不参与签名
            continue
        param_list.append('{0}={1}'.format(k, v))
    # 用 & 连接各 k-v 对，然后对字符串进行 MD5 运算
    return hashlib.sha1('&'.join(param_list)).hexdigest()

def gen_nonce_str():
    """
        生成随机字符串，有效字符a-zA-Z0-9

        :return: 随机字符串
    """
    return ''.join(str(uuid.uuid4()).split('-'))

def transDict2Xml(data):
    """
        将 dict 对象转换成微信支付交互所需的 XML 格式数据
    """

    xml = []
    for k in sorted(data.keys()):
        v = data.get(k)
        if not v.startswith('<![CDATA['):
            v = '<![CDATA[{}]]>'.format(v)
        xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(xml))

def transXml2Dict(data):
    """
        解析微信返回的xml
    """
    dom = xml.dom.minidom.parseString(data)
    root = dom.documentElement
    xmlDict = {}
    for child in root.childNodes:
        print child
        result = dom.getElementsByTagName(child.nodeName)
        if result == []:
            continue
        result = result[0].childNodes[0].nodeValue
        xmlDict[child.nodeName] = result

    return xmlDict

def para_filter(params):
    """
        过滤参数
    """
    return {key: params[key]
            for key in params
            if key.lower() not in {'sign'} and params[key]}

def checkSign(params):
    """
        验证签名
    """
    if 'sign' not in params:
        return False
    wx_sign = params['sign']
    filter_params = para_filter(params)
    sign = gen_sign(filter_params)
    sign4TX = gen_sign4TX(filter_params)
    return wx_sign == sign or wx_sign == sign4TX

def response2Wechat(resultCode,Msg):
    """
        返回结果给微信
    """

    item = {
        'return_code'       :       resultCode,
        'return_msg'        :       Msg
    }

    return transDict2Xml(item)

def verfiyRcvDatas(redis,params):
    """
        校验支付数据
    """
    curTime = datetime.now()
    orderTable = ORDER_TABLE%(params['out_trade_no'])
    if not redis.exists(orderTable):
        log_util.debug('[%s][wechatPay][error] orderNo[%s] is not exists.'%(curTime,params['out_trade_no']))
        return False

    updateInfo = {
            'money'         :       params['total_fee'],
            'endTime'       :       params['time_end'],
            'currency'      :       params['fee_type'],
            'orderNum'      :       params['transaction_id'],
            'type'          :       'successful',
    }

    pipe = redis.pipeline()
    try:
        log_util.debug('[%s][wechatPay][info] update orderInfo[%s] success.'\
                                    %(curTime,updateInfo))
        pipe.hmset(orderTable,updateInfo)
        pipe.srem(PENDING_ORDER,orderTable)
        pipe.sadd(SUCCEED_ORDER,orderTable)
        pipe.persist(orderTable)
        pipe.execute()
    except:
        log_util.debug('[%s][wechatPay][error] update orderInfo[%s] error.'%(curTime,updateInfo))
        return False

    return True

def countRateOfAgent(redis,agentId,roomcardNumber,unitPrice,lowerRate=0):

    log_util.debug('[HALLFUNC][countRateOfAgent][info] agentId[%s] roomcard[%s] unitPrice[%s]'%(agentId,roomcardNumber,unitPrice))

    curTime = datetime.now()
    date = curTime.strftime("%Y-%m-%d")
    parentTable = AGENT_TABLE%(agentId)
    parentType,parentrate,parentId = redis.hmget(parentTable,('type','shareRate','parent_id'))

    if parentType == '0':
        AGENT_RATE_TABLE = AGENT_COMPAY_RATE_DATE%(agentId,date)
    else:
        AGENT_RATE_TABLE =AGENT_RATE_DATE%(agentId,parentrate,unitPrice,date)

    log_util.debug('[HALLFUNC][countRateOfAgent][info] agentId[%s] parentId[%s] parentrate[%s] parentId[%s] agentRateTable[%s]'\
                                %(agentId,parentId,parentrate,parentId,AGENT_RATE_TABLE))

    pipe = redis.pipeline()
    pipe.hincrby(AGENT_RATE_TABLE,'number',amount=roomcardNumber)
    pipe.hset(AGENT_RATE_TABLE,'unitPrice',unitPrice)
    pipe.hset(AGENT_RATE_TABLE,'rate',parentrate)
    if parentType == '0':
        RemainPrice = float(unitPrice) - float(lowerRate)
        if RemainPrice > 0:
            pipe.hincrbyfloat(AGENT_RATE_TABLE, 'rateTotal', amount=RemainPrice * roomcardNumber)
    else:
        remainPrice = float(unitPrice) -  float(lowerRate)
        if remainPrice <= 0:
            countRateOfAgent(redis,parentId,roomcardNumber,unitPrice,lowerRate)
        else:
            parent1Type, parent1Rate = redis.hmget( AGENT_TABLE % (parentId), ('type', 'shareRate'))
            if parent1Type !='0':
                if parentrate > parent1Rate:
                    parentrate = parent1Rate

            if not parentrate:
                parentrate = 0.00

            firstRemainPrice = float(unitPrice) - float(parentrate)
            if firstRemainPrice <=0:
                Rate = float(unitPrice) - float(lowerRate)
                pipe.hincrbyfloat(AGENT_RATE_TABLE,'rateTotal',amount=Rate*roomcardNumber)
                pipe.hincrbyfloat(AGENT_RATE_TABLE, 'meAndNextTotal', amount=float(unitPrice)*roomcardNumber)
                countRateOfAgent(redis,parentId,roomcardNumber,unitPrice,parentrate)
            else :
                Rate = float(parentrate)
                pipe.hincrbyfloat(AGENT_RATE_TABLE,'rateTotal',amount=Rate*roomcardNumber)
                pipe.hincrbyfloat(AGENT_RATE_TABLE, 'meAndNextTotal', amount=float(parentrate) * roomcardNumber)
                pipe.hincrbyfloat(AGENT_RATE_TABLE, 'superRateTotal', amount=firstRemainPrice*roomcardNumber)
                countRateOfAgent(redis,parentId,roomcardNumber,unitPrice,parentrate)
    pipe.execute()

def getCardMoney(redis,groupId):
    """
    会员购卡单价
    """
    AgentTable = AGENT_TABLE%(groupId)
    unitPrice,parentId,atype=redis.hmget(AgentTable,'unitPrice','parent_id','type')
    log_util.debug('[HALLFUNC][getCardMoney][info] groupId[%s] price[%s]'%(groupId,unitPrice))
    if atype in ['2','3']:
        return getCardMoney(redis,parentId)

    return unitPrice


def addGold2Merber(redis, account, money, num, present_card):
    """
        玩家增加金币
        redis: 
        account: 账号
        money:  购买金额
        num:  购买金币数
        present_card: 赠送金币
    """
    if not present_card:
        present_card = 0
    try:
        present_card = int(present_card)
    except:
        present_card = 0

    now = datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    ymd = now.strftime("%Y-%m-%d")
    user_table = redis.get(FORMAT_ACCOUNT2USER_TABLE % account)
    if not user_table:
        return
    uid = user_table.split(':')[1]
    name, pre_gold, parentAg = redis.hmget(FORMAT_USER_TABLE % uid, ('account', 'gold', 'parentAg'))

    exclude = [658502] #排除列表的公会玩家，不赠送赠送金币
    if int(parentAg) in exclude:
        present_card = 0

    pipe = redis.pipeline()
    pipe.hincrby(FORMAT_USER_TABLE % uid, 'gold', (int(num) + present_card))

    # 每天购买金币的用户集合，用来统计每天购买人数
    pipe.sadd(DAILY_USER_GOLD2_SET % ymd, account)
    # 添加充值金币数到每天总金币数表
    pipe.incrby(DAILY_GOLD2_SUM % ymd, num)
    # 每人每天购买金币总数
    pipe.incrby(DAILY_ACCOUNT_GOLD2_SUM % (account, ymd), num)
    # 每人每天购买金额总数
    pipe.incrby(DAILY_ACCOUNT_GOLD2_MONEY_SUM % (account, ymd), money)
    # 将充值金额数增加到每日充值金额表
    pipe.incrby(DAILY_GOLD2_MONEY_SUM % ymd, money)
    pipe.execute()

    #存放奖励
    try:
        bonus = int(int(num) * 0.04)
        parentAg = redis.hget(FORMAT_USER_TABLE % uid, 'parentAg')  #市级
        redis.hincrby(AGENT_TABLE % (parentAg), 'bonus', bonus)
        parent2Ag = redis.get(AGENT2PARENT % parentAg) #省级
        redis.hincrby(AGENT_TABLE % (parent2Ag), 'bonus', bonus)
    except:
        print 'bonus error: num is %s , %s' % (num,e)

    try:
        # 记录mysql_log
        if not pre_gold: pre_gold = 0
        curTime = datetime.now()
        strTime = curTime.strftime('%Y-%m-%d %H:%M:%S')
        changed = int(num) + present_card
        data = {
            'user_id': uid,
            'name': name,
            'createtime': strTime,
            'pre_gold': pre_gold,
            'changed': changed,
            'now_gold': int(pre_gold) + changed,
            'action': 4  # 1:扣房费, 2:结算扣分, 3:每日领取, 4:充值
        }
        MysqlInterface.insert('log_gold', **data)
    except:
        print 'mysql insert error.'

    from model.goldModel import saveBuyGoldRecord
    saveBuyGoldRecord(redis, account, {'gold': num, 'money': money, 'date': date})
    return redis.hget(FORMAT_USER_TABLE % uid, 'gold')


def addRoomCard2Member4Type2(redis, curTime, orderTable, memberAccount):
    gold, money, present_card = redis.hmget(orderTable, ('roomCards', 'money', 'presentCards'))
    addGold2Merber(redis, memberAccount, money, gold, present_card)

def addRoomCard2Member(redis,transNo):
    """
        会员增加房卡
    """
    curTime = datetime.now()
    orderTable = ORDER_TABLE%(transNo)
    if not redis.exists(orderTable):
        log_util.debug('[%s][wechatPay][error] orderNo[%s] is not exists.'%(curTime,params['out_trade_no']))
        return False

    goodid, memberAccount = redis.hmget(orderTable, ('num', 'account'))
    rType = redis.hget(GOODS_TABLE % goodid, 'type')
    rType = int(rType) if rType else None
    if rType == 2:
        addRoomCard2Member4Type2(redis, curTime, orderTable, memberAccount)
        return

    cardNums,present_card = redis.hmget(orderTable,('roomCards','presentCards'))
    if not present_card:
        present_card = 0
    try:
        present_card = int(present_card)
    except:
        present_card = 0

    #chargeNums = TYPE_2_CARS[rType]
    account2user_table = FORMAT_ACCOUNT2USER_TABLE%(memberAccount) #从账号获得账号信息，和旧系统一样
    userTable = redis.get(account2user_table)
    groupId = redis.hget(userTable, 'parentAg')
    try:
        redis.hset(orderTable, 'groupId', groupId)
    except Exception,error:
        print '[addRoomCard2Member] [ERROR] %s'%(error)
    #会员ID
    id = userTable.split(':')[1]

    pipe = redis.pipeline()
    pipe.incrby(USER4AGENT_CARD%(groupId, id),(int(cardNums)+present_card))
    #记录充值卡总额
    if not redis.exists(USER4AGENT_RECHARGE%(groupId,id)):
        pipe.set(USER4AGENT_RECHARGE%(groupId,id),0)
    pipe.incrby(USER4AGENT_RECHARGE%(groupId, id),int(cardNums))
    CardMoney = getCardMoney(redis,groupId)
    log_util.debug('[%s][wechatPay] recharge CardMoney[%s]'%(curTime,CardMoney))
    #计算分成金额
    countRateOfAgent(redis,groupId,int(cardNums),CardMoney)
    log_util.debug('[%s][wechatPay] recharge roomcards[%s] to account[%s] success'%(curTime,cardNums,memberAccount))
    roomCards = pipe.execute()[0]

    pipe = redis.pipeline()
    ymd = datetime.now().strftime("%Y-%m-%d")
    useDatas = [int(cardNums), 4, roomCards]
    useStr = ';'.join(map(str, useDatas))
    pipe.lpush(PLAYER_DAY_USE_CARD%(id, ymd), useStr)
    pipe.expire(PLAYER_DAY_USE_CARD%(id, ymd), SAVE_PLAYER_DAY_USE_CARD_TIME)
    pipe.execute()
    #发送消息给服务端
    # sendProtocol2GameService(redis,MAHJONG_GAMEID,HEAD_SERVICE_PROTOCOL_MEMBER_REFRESH%(memberAccount))

def getNowTime():
    """
        获取现在时间
    """
    return datetime.now()

def getDaya4Month():
    """
        返回一个星期时间
    """
    weekDelTime = timedelta(30)
    weekBefore = datetime.now()-weekDelTime
    startDate = weekBefore
    endDate   = datetime.now()

    return startDate.strftime('%Y-%m-%d 00:00:00'),endDate.strftime('%Y-%m-%d 23:59:59')
APPIDWEB = 'wx3825bd03f79e6c58'
SECRETWEB = '10ae9133ff4917228c947655d42cb54c'
def getJsapiTicket(redis, account):
    curTime = datetime.now()
    errMsg = ''
    access_token = redis.get(ACCESS_TOKEN_API)
    log_util.debug('[%s][getJsapiTicket][info] access_token [%s]' % (curTime, access_token))
    if not access_token:
        access_token,errMsg = get_access_token(redis)
        if errMsg:
            return '',errMsg
        jsapi_ticket, errMsg = get_jsapi_ticket(redis, access_token)
        return jsapi_ticket,errMsg
    else:
        jsapi_ticket = redis.get(ACCESS_TOKEN_JSAPI)
        log_util.debug('[%s][getJsapiTicket][info] jsapi_ticket [%s]' % (curTime, jsapi_ticket))
        if not jsapi_ticket:
            jsapi_ticket, errMsg = get_jsapi_ticket(redis,access_token)
        return jsapi_ticket, errMsg

def get_jsapi_ticket(redis,access_token):
    curTime = datetime.now()
    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi' % (access_token)
    message = getUrlMessage(url)
    log_util.debug('[%s][getJsapiTicket][info] message [%s]' % (curTime,message))
    errMsg = ''
    jsapi_ticket = ''
    if message['errcode'] !=0:
        log_util.debug('[%s][getJsapiTicket][info] ACCESS_TOKEN_JSAPI message:%s' % (curTime,message))
        errMsg = message['errmsg']
    else:
        pipe = redis.pipeline()
        pipe.set(ACCESS_TOKEN_JSAPI,message['ticket'])
        # pipe.expire(ACCESS_TOKEN_JSAPI, message['expires_in'])
        pipe.expire(ACCESS_TOKEN_JSAPI, 6000)
        pipe.execute()
        jsapi_ticket = message['ticket']
    return jsapi_ticket,errMsg

def get_access_token(redis):
    curTime = datetime.now()
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (APPIDWEB, SECRETWEB)
    message = getUrlMessage(url)
    errMsg = ''
    access_token = ''
    log_util.debug('[%s][get_access_token][info] ACCESS_TOKEN_API message:%s' % (curTime, message))
    if 'errcode' in message:
        errMsg = message['errmsg']
    else:
        pipe = redis.pipeline()
        pipe.set(ACCESS_TOKEN_API,message['access_token'])
        # pipe.expire(ACCESS_TOKEN_API, message['expires_in'])
        pipe.expire(ACCESS_TOKEN_API, 6000)
        pipe.execute()
        access_token = message['access_token']
    return access_token,errMsg

def del_access_jsapi_token(redis):
    pipe = redis.pipeline()
    pipe.set(ACCESS_TOKEN_API,'')
    pipe.set(ACCESS_TOKEN_JSAPI,'')
    pipe.execute()


from functools import wraps
import time

def write_timeLog(name, time):

    with open("timeit.log", "a") as f:
        f.write("%s: %s\n" % (name, time))
    print("%s-%s\n" % (name, time))


def fn_performance(fn):
    def wrapper(real_fn):
        @wraps(real_fn)
        def function_timer(*args, **kwargs):
            t0 = time.time()

            result = real_fn(*args, **kwargs)

            t1 = time.time()

            fn(real_fn, t1-t0)
            return result
        return function_timer
    return wrapper


class RetryExecute(Exception):
    pass


def retry_execute(count):
    def wrapper(fn):
        @wraps(fn)
        def execute(*args, **kwargs):
            for _ in range(count):
                try:
                    return fn(*args, **kwargs)
                except RetryExecute:
                    continue
        return execute
    return wrapper

def return_code_error(*args, **kwargs):

    return {"code": 1, "msg": "你的请求过快"}


def retry_insert_number(time=2, count=15):

    def __wrapper__(fn):
        @wraps(fn)
        def execute(redis, session, *args, **kwargs):
            print(fn, redis, session)
            rule = request.urlparts.path
            method = request.route.method
            ip = request.environ.get('HTTP_X_FORWARDED_FOR') or request.remote_addr

            if method == "GET":
                sid = request.params.get('sid','').strip()
                params = dict(request.params)
            else:
                sid = request.forms.get("sid", '').strip()
                params = dict(request.forms)
            print(u"%s开始访问%s 使用方法：%s, 请求参数:%s" % (ip, rule, method, params))
            accessTable = "web:access:rule:%s:method:%s:ip:%s:number"%(rule, method, ip)
            accessAllTable = "web:access:ip:%s:number"%(ip)

            redis.incrby(accessAllTable, 1)
            redis.incrby(accessTable, 1)

            ttlAll = redis.pttl(accessAllTable)
            ttlTable = redis.pttl(accessTable)
            if not ttlAll:
                redis.expire(accessAllTable, 1)
            else:
                redis.pexpire(accessAllTable, int(ttlAll))

            if not ttlTable:
                redis.expire(accessTable, time)
            else:
                redis.pexpire(accessTable, int(ttlTable))

            number = redis.get(accessTable)
            number = int(number) if number else 0
            allNumber = redis.get(accessAllTable)
            allNumber = int(allNumber) if allNumber else 0

            print(u"IP：%s 访问接口 %s 次数:%s 总次数:%s, TTL(%s, %s)" % (ip, rule, number, allNumber, ttlTable, ttlAll))
            if allNumber >= count:
                redis.hincrby("access:number:allIp:hset", ip, 5)
                total = redis.hget("access:number:allIp:hset", ip)
                total = int(total) if total else 0
                redis.sadd("remote:disbled:ip:set", ip)
                if sid:
                    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
                    #redis.sadd("remove:disbled:userid:set",
                    #           "总接口访问过于频繁, user_id=%s" % (uid)
                    #           )
                    redis.hset("remote:disbled:user:hset",
                               ip, uid
                               )
            if number >= count:
                redis.hincrby("access:number:ip:hset", ip, 5)
                total = redis.hget("access:number:ip:hset", ip)
                total = int(total) if total else 0
                if total > 15:
                    redis.sadd("remote:disbled:ip:set", ip)
                    if sid:
                        SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
                        #redis.sadd("remove:disbled:userid:set",
                        #"用户访问%s频率过快, user_id=%s" % (rule, uid)
                        #)
                        redis.hset("remote:disbled:user:hset",
                                    ip, uid
                                   )
                return return_code_error(*args, **kwargs)

            args = list(args)
            args.append(redis)
            args.append(session)
            args = tuple(args)
            return fn(*args, **kwargs)
        return execute
    return __wrapper__


