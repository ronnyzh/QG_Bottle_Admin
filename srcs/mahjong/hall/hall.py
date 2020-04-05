#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    微信模块(登录大厅验证,微信支付)
"""

from bottle import request, Bottle, abort, redirect, response, template,static_file
from web_db_define import *
import mahjong_pb2
import poker_pb2
import replay4proto_pb2
from talk_data import sendTalkData
from wechat.wechatData import *
from common.install_plugin import install_redis_plugin,install_session_plugin
from hall_func import *
from common.log import *
from common import log_util,web_util
from config.config import *
from datetime import datetime
from model.goodsModel import *
from model.hallModel import *
from model.protoclModel import sendProtocol2GameService
from model.mailModel import *
from model.agentModel import getTopAgentId
from model.userModel import get_user_open_auth
from model.gameModel import get_game_info
import time
import urllib2
import json
import random
import md5
import re
from urlparse import urlparse
#from .statistic import dig_login_times
from pyinapp import *
ACCEPT_NUM_BASE = 198326
ACCEPT_TT = [md5.new(str(ACCEPT_NUM_BASE+i)).hexdigest() for i in xrange(10)]

#wechatApp
hall_app = Bottle()

#安装插件
install_redis_plugin(hall_app)
install_session_plugin(hall_app)

GAMEID2COUNT_PLAYER_PER_SERVER = {
    1       :   30,
    2       :   0,
    3       :   150,
    4       :   150,
    101     :   300,
}

"""
    亲友圈
"""
import club

"""
    金币场导入
"""
import hall_gold
from model.gold_db_define import GOLD_GAMEID_SET, PARTY_TYPE_GOLD, GOLD_ROOM_DATA


def remote_disbaled(redis):
    
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR')
    redis.hincrby("access:number:ip:hset", client_ip, 1)
    print(u"远程地址:%s 头部：%s" % (client_ip, request.headers))
    if not client_ip or client_ip == "183.60.133.160":
        return
    number = redis.hget("access:number:ip:hset", client_ip)
    number = int(number) if number else 0
    if number >= 15:
        redis.sadd("remote:disbled:ip:set", client_ip)
        # sendRemoveIpaddr(client_ip)
    return 

@hall_app.get('/getHallServer')
@web_util.allow_cross_request
@retry_insert_number()
def do_getHallServer(redis,session):
    """
    获取大厅server地址
    """
    tt = request.forms.get('tt','').strip()

    Servers = []
    serverList = redis.smembers(FORMAT_HALL_SERVICE_SET)
    for server in serverList:
        Servers.append(server)

    if Servers:
        return {'code':0,'serverList':Servers}

    return {'code':-1,'msg':'服务器列表为空'}

@hall_app.get('/getHallVersion')
@web_util.allow_cross_request
@retry_insert_number()
def getHallVersion(redis,session):
    """
    """
    HALL2VERS = getHotSettingAll(redis)
    HALL2VERS['hotUpdateURL'] = HALL2VERS['hotUpdateURL']+"/"+HALL2VERS['packName']
    return HALL2VERS

@hall_app.post('/login')
#@fn_performance(lambda x, y: write_timeLog("login", y))
@web_util.allow_cross_request
@retry_insert_number(time=1, count=4)
def do_hallLogin(redis,session):
    """
    大厅登录接口
    """

    tt = request.forms.get('tt', '').strip()
    curTime = datetime.now()
    ip = request.remote_addr
    getIp = request['REMOTE_ADDR']
    _account = request.forms.get('account', '').strip()
    clientType = request.forms.get('clientType', '').strip()
    groupId = request.forms.get('groupId','').strip()
    RoomId = request.forms.get('rid','').strip()
    tta = request.forms.get('ttA','').strip()
    ttc = request.forms.get('ttC','').strip()
    newgroupid=''
    # if not RoomId:
    #     RoomId='123456'   
    tta = request.forms.get('ttA', '').strip()
    ttc = request.forms.get('ttC', '').strip()

    if redis.exists("request:TTA:%s" % tta):
        return #{'code': -1, 'msg': '无效TTA。'}

    newgroupid = ''
    # if not RoomId:
    #     RoomId='123456'
    m1 = md5.new()
    m1.update(tta)
    getttc = m1.hexdigest()
    ttb = getttc[1:4]
    m2 = md5.new()
    m2.update(tta + ttb)
    getttc1 = m2.hexdigest()
    if not (ttc == getttc1):
        return #{'code': -1, 'msg': 'tta%s ttc%s' % (tta, getttc1)}
    redis.setex("request:TTA:%s" % tta, '', 1800)

    # if not RoomId:
    #     RoomId='123456'
    if not clientType:
        clientType = 0
    passwd = request.forms.get('passwd', '').strip()
    type = request.forms.get('type', '').strip() #登录类型
    type = int(type)

    log_debug('hallLogin ip[%s] getIp[%s] groupId[%s]'%(ip,getIp,groupId))
    try:
        print '[on login]account[%s] clientType[%s] passwd[%s] type[%s]'%(_account, clientType, passwd, type)
    except Exception as e:
        print 'print error File', e

    login_pools = redis.smembers(FORMAT_LOGIN_POOL_SET)
    #log_debug('[LOGIN][url:/hall/login] account[%s] login_pools[%s]'%(_account,login_pools))

    if _account in login_pools:
        log_debug('[LOGIN][url:/hall/login] account[%s] is already login.'%(_account))
        return
    #默认公会号
    NEW_NOTICE=1 #是否启用新广播
    dgid='658502'
    DEFAULT_GID='658502'#默认公会暂不开放
    defaultgid=''
    roomCardClub='400'#开亲友圈需要钻石数
    redis.sadd(FORMAT_LOGIN_POOL_SET,_account)
    #log_debug('[LOGIN][url:/hall/login] account[%s] login_pools[%s]'%(_account,login_pools))
    reAccount, rePasswd = onReg(redis, _account, passwd, type, ip)
    #log_debug('[wechat onReg][info] reAccount[%s] rePasswd[%s]'%(reAccount, rePasswd))
    ACTIVITIVE_SWITCH=0#风车转盘开关
    if reAccount:
        if type:
            realAccount = redis.get(WEIXIN2ACCOUNT%(reAccount))
        else:
            realAccount = reAccount
        #读取昵称和group_id
        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(realAccount)
        userTable = redis.get(account2user_table)
        id = userTable.split(':')[1]
        #dig_login_times(user_id=id)
        #if type==3 and groupId:
           # redis.set(WAIT_JOIN_GAME_GROUPID_PLAYERS%id,groupId)
           # redis.expire(WAIT_JOIN_GAME_GROUPID_PLAYERS%id,6000000)
           # groupId=''
        if RoomId:
            redis.set(WAIT_JOIN_GAME_ROOMID_PLAYERS%id,RoomId)
            redis.expire(WAIT_JOIN_GAME_ROOMID_PLAYERS%id,600)
        if redis.exists(UNIONID2GROUP%reAccount):
            unionId = reAccount
            needJoinGroup = redis.get(UNIONID2GROUP%unionId)
            adminTable = AGENT_TABLE%(needJoinGroup)
            if redis.exists(adminTable):
                agValid, auto_check, groupType = redis.hmget(adminTable, ('valid', 'auto_check', 'type'))
                if agValid == '1' and groupType != '1':
                    if not auto_check:
                        auto_check = CHECK_SUCCESS
                    pipe = redis.pipeline()
                    if auto_check == CHECK_SUCCESS:
                        pipe.hset(FORMAT_USER_TABLE%(id), 'parentAg', needJoinGroup)
                        pipe.sadd(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(needJoinGroup), id)
                    pipe.lpush(JOIN_GROUP_LIST%(needJoinGroup), id)
                    pipe.set(JOIN_GROUP_RESULT%(id), '%s:%s:%s'%(needJoinGroup, auto_check, curTime.strftime('%Y-%m-%d %H:%M:%S')))
                    pipe.execute()
        account, name, ag, loginIp, loginDate, picUrl, gender,valid,headImgUrl = redis.hmget(userTable, ('account', 'nickname', 'parentAg', 'lastLoginIp', 'lastLoginDate', 'picUrl', 'gender','valid','headImgUrl'))

        agentTable = AGENT_TABLE%(ag)
        isTrail,shop = redis.hmget(agentTable,('isTrail','recharge'))
        if not isTrail:
            isTrail = 0
        if not shop:
            shop = SHOP_OPEN
        shop = int(shop)
        if int(valid) == 0:
            #冻结后不能登录
            redis.srem(FORMAT_LOGIN_POOL_SET,_account)
            return {'code':105,'msg':'该帐号被冻结,请与客服联系'}

        print '[hall][login]before ag[%s] groupId[%s]'%(ag,groupId)
        if not ag and groupId and redis.exists(AGENT_TABLE%(groupId)):
            #移除之前的公会ID
            redis.srem(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(ag),id)
            ag = groupId
            #将公会ID放入代理ID
            redis.sadd(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(ag),id)
            #设置公会
            redis.hset(userTable,'parentAg',ag)
        if (not (type==3)):
        #会话信息

            sid = md5.new(str(id)+str(time.time())).hexdigest()
            SessionTable = FORMAT_USER_HALL_SESSION%(sid)
            if redis.exists(SessionTable):
                print "[%s][hall][login][error] account[%s] sid[%s] is existed."%(curTime,realAccount,sid)
                redis.srem(FORMAT_LOGIN_POOL_SET,account)
                return {'code':-1, 'msg':'链接超时'}

            #同一账号不能同时登录
            redis.set(FORMAT_USER_PLATFORM_SESSION%(id),sid)

            #更新登录IP和登陆日期
            redis.hmset(userTable, {'lastLoginIp':request.remote_addr, 'lastLoginDate':datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
                    'lastLoginClientType':clientType})

            #记录session信息
            session['member_id'] = id
            session['member_account'] = account
            session['member_lastIp'] = loginIp
            session['member_lastDate'] = loginDate
            session['session_key']  = sid
            pipe = redis.pipeline()
            pipe.hmset(SessionTable, {'account':account,'uid':id,'sid':sid,'loginIp':ip})
            pipe.expire(SessionTable, 60*40)
            pipe.execute()
        urlRes = urlparse(request.url)
        serverIp = ''
        serverPort = 0
        gameid = 0
        exitPlayerData = EXIT_PLAYER%(realAccount)
        print '[hall][login]exitPlayerData[%s]'%(exitPlayerData)
        if redis.exists(exitPlayerData):
            serverIp, serverPort, game = redis.hmget(exitPlayerData, ('ip', 'port', 'game'))
            print '[hall][login]exitPlayerData get succed, ip[%s], serverPort[%s], game[%s]'%(serverIp, serverPort, game)
            serverIp = urlRes.netloc.split(':')[0]
            gameid = redis.hget(ROOM2SERVER%(game), 'gameid')
            try:
                int(gameid)
            except:
                serverIp = ''
                serverPort = 0
                gameid = 0
                redis.delete(exitPlayerData)
                print '[hall][login][delete] exitPlayerData[%s]'%(exitPlayerData)
        if redis.sismember(ONLINE_ACCOUNTS_TABLE, realAccount):
            print '[hall][login]get ONLINE_ACCOUNTS_TABLE succed'
            # for key in redis.keys(FORMAT_CUR_USER_GAME_ONLINE%(realAccount)):
            key = FORMAT_CUR_USER_GAME_ONLINE%(realAccount)
            if key:
                serviceTag, gameNum = redis.hmget(key, ('serviceTag', 'game'))
                if gameNum:
                    # continue
                    serverIp = serviceTag.split(':')[1]
                    serverPort = serviceTag.split(':')[2]
                    gameid = redis.hget(ROOM2SERVER%(gameNum), 'gameid')
                    serverIp = urlRes.netloc.split(':')[0]
                    try:
                        int(gameid)
                    except:
                        serverIp = ''
                        serverPort = 0
                        gameid = 0
                        redis.srem(ONLINE_ACCOUNTS_TABLE, realAccount)
                        print '[hall][login][delete] ONLINE_ACCOUNTS_TABLE[%s]'%(realAccount)
        if not ag or ag == dgid: #没有公会 或者公会是默认公会
            defaultgid=DEFAULT_GID
            if (not (type == 3)):
                wait_group = WAIT_JOIN_GAME_GROUPID_PLAYERS%id
                ngId = redis.get(wait_group)
                if ngId:
                    defaultgid=ngId
                redis.set(wait_group, '')

        userInfo = {'name':name,'isTrail':int(isTrail),'shop':int(shop),'group_id':ag,'account':reAccount, 'passwd':rePasswd,'uid':id,'group_id_auto':defaultgid,'headImgUrl':headImgUrl,'group_id_default':dgid ,'OnA':ACTIVITIVE_SWITCH, 'notice_open':NEW_NOTICE ,'roomCardClub':roomCardClub, 'salvage':50}
        joinNum = ''
        id = userTable.split(':')[1]

        # 没有公会则加入默认公会
        func_join_default_group(redis,id)

        joinMessage = redis.get(JOIN_GROUP_RESULT%(id))
        if joinMessage:
            joinMessage = joinMessage.split(':')
            joinNum = int(joinMessage[0])
            joinResult = int(joinMessage[1])
            userInfo['applyId'] = joinNum
            if joinResult == 1:
                redis.delete(JOIN_GROUP_RESULT%(id))

        key = redis.get(ACCOUNT2WAIT_JOIN_PARTY_TABLE%account)
        # for key in redis.keys(WAIT_JOIN_PARTY_ROOM_PLAYERS%('*', '*', '*')):
        if key:
            if account in redis.lrange(key, 0, -1):
                try:
                    gameId, serviceTag = redis.get('account:%s:wantServer'%account).split(',')
                    message = HEAD_SERVICE_PROTOCOL_NOT_JOIN_PARTY_ROOM%(account, ag)
                    redis.lpush(FORMAT_SERVICE_PROTOCOL_TABLE%(gameId, serviceTag), message)
                except:
                    print '[account wantServer][%s]'%(redis.get('account:%s:wantServer'%account))
                redis.lrem(key, account)
        if serverIp:
            urlRes = urlparse(request.url)
            domain = urlRes.netloc.split(':')[0]

            if redis.sismember(GOLD_GAMEID_SET, gameid):
                gameInfo = {'ip': domain, 'port': int(serverPort), 'gameid': gameid, 'isParty': PARTY_TYPE_GOLD}
            else:
                gameInfo = {'ip':domain, 'port':int(serverPort), 'gameid':gameid}

            gameState = {}
            gameTable = GAME_TABLE%(gameid)
            if redis.exists(gameTable):
                name, webTag, version,packName = redis.hmget(gameTable, ('name', 'web_tag', 'version','pack_name'))
                gameState[gameid] = {
                    'id'                :           gameid,
                    'name'              :           name,
                    'web_tag'           :           webTag,
                    'version'           :           version,
                    'downloadUrl'       :           packName
                }

            if joinNum:
                redis.srem(FORMAT_LOGIN_POOL_SET,_account)
                return {'code':0, 'sid':sid, 'userInfo':userInfo,\
                    'gameInfo':gameInfo, 'joinResult':joinResult, 'gameState':gameState}
            redis.srem(FORMAT_LOGIN_POOL_SET,_account)
            return {'code':0, 'sid':sid, 'userInfo':userInfo, 'gameInfo':gameInfo, 'gameState':gameState}
        else:
            if joinNum:
                redis.srem(FORMAT_LOGIN_POOL_SET,_account)
                return {'code':0, 'sid':sid, 'userInfo':userInfo, 'joinResult':joinResult}
            redis.srem(FORMAT_LOGIN_POOL_SET,account)
            if (not (type==3)):
                return {'code':0, 'sid':sid, 'userInfo':userInfo}
            else:
                print 'webchatlogin3'
    else: #失败
        redis.srem(FORMAT_LOGIN_POOL_SET,_account)
        return {'code':101, 'msg':'账号或密码错误或者微信授权失败'}

# 加入默认公会
def func_join_default_group(redis,id):

    if redis.hget(FORMAT_USER_TABLE % (id),'parentAg'):
        return

    groupId = "658502"
    pipe = redis.pipeline()
    pipe.hset(FORMAT_USER_TABLE % (id), 'parentAg', groupId)
    pipe.sadd(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE % (groupId), id)
    pipe.lpush(JOIN_GROUP_LIST % (groupId), id)
    auto_check = '1'
    pipe.set(JOIN_GROUP_RESULT % (id), '%s:%s:%s' % (groupId, auto_check, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    pipe.execute()

@hall_app.post('/joinGroup')
@web_util.allow_cross_request
@retry_insert_number()
def do_joinGroup(redis,session):
    """
    加入公会接口
    """
    curTime = datetime.now()
    sid  =  request.forms.get('sid','').strip()
    groupId = request.forms.get('groupId','').strip()


    #print
    print '[%s][joinGroup][info] groupId[%s] sid[%s]'%(curTime,groupId,sid)

    adminTable = AGENT_TABLE%(groupId)

    # SessionTable = FORMAT_USER_HALL_SESSION%(sid)
    # account,uid = redis.hmget(SessionTable, ('account','uid'))
    # verfiySid   = redis.get(FORMAT_USER_PLATFORM_SESSION%(uid))
    print 'do_joinGroup'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    try:
        print '[on joinGroup]account[%s] sid[%s] groupId[%s]'%(account, sid, groupId)
    except Exception as e:
        print 'print error File', e

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        print '[%s][HALL][url:/joinGroup][info] code[%s] sid[%s] groupId[%s] verfiySid[%s]'%(curTime,-4,sid,groupId,verfiySid)
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}

    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        print '[%s][HALL][url:/joinGroup][info] code[%s] sid[%s] groupId[%s] userTable[%s]'%(curTime,-5,sid,groupId,userTable)
        return {'code':-5,'msg':'该用户不存在'}

    if not (redis.exists(adminTable)):
        print '[%s][HALL][url:/joinGroup][info] code[%s] sid[%s] groupId[%s] adminTable[%s]'%(curTime,-1,sid,groupId,adminTable)
        return {'code':-1, 'msg':'加入公会失败, 公会不存在'}

    agValid,auto_check = redis.hmget(adminTable,('valid','auto_check'))
    if not auto_check:
        auto_check = CHECK_SUCCESS
    auto_check = int(auto_check)
    if agValid != '1':
        print  '[JoinRoom][info] agentId[%s] has freezed. valid[%s] '%(groupId,agValid)
        return {'code':-7,'msg':'该公会已被冻结,不能申请加入'}

    type = redis.hget(adminTable, 'type')
    if int(type) == 1:
        print '[%s][HALL][url:/joinGroup][info] code[%s] sid[%s] groupId[%s] type[%s]'%(curTime,-1,sid,groupId,type)
        return {'code':-1, 'msg':'加入公会失败，不能直接加入总公司。'}

    id = userTable.split(':')[1]

    #自动退出当前公会
    groupId4old = redis.hget(userTable, 'parentAg')
    adminTable4Old = AGENT_TABLE%(groupId4old)
    if redis.exists(adminTable4Old) and redis.exists(userTable):
        tryExitGroup(redis, userTable, account, id, groupId4old)

    #如果存在,绑定
    pipe = redis.pipeline()
    if auto_check == CHECK_SUCCESS:
        pipe.hset(FORMAT_USER_TABLE%(id),'parentAg',groupId)
        pipe.sadd(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(groupId), id)
    pipe.lpush(JOIN_GROUP_LIST%(groupId), id)
    pipe.set(JOIN_GROUP_RESULT%(id), '%s:%s:%s'%(groupId,auto_check,curTime.strftime('%Y-%m-%d %H:%M:%S')))
    pipe.execute()
    return {'code':0, 'msg':'等待公会确认中'}

@hall_app.post('/cancleJoinGroup')
@web_util.allow_cross_request
@retry_insert_number()
def do_cancleJoin(redis,session):
    """
    取消加入公会
    """
    curTime = datetime.now()
    sid  =  request.forms.get('sid','').strip()
    groupId = request.forms.get('groupId','').strip()

    print 'do_canclejoinGroup'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}

    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}

    id = userTable.split(':')[1]
    pipe = redis.pipeline()
    try:
        joinMessage = redis.get(JOIN_GROUP_RESULT%(id))
        if joinMessage:
            joinMessage = joinMessage.split(':')
            joinNum = int(joinMessage[0])
            pipe.lrem(JOIN_GROUP_LIST%(joinNum),id)
            pipe.delete(JOIN_GROUP_RESULT%(id))
    except:
        print '[%s][cancleJoin][error] id[%s] cancle join error.  reason[%s]'%(curTime,id,e)
        return {'code':-1,'msg':'取消加入公会失败'}

    pipe.execute()
    return {'code':0}

@hall_app.post('/checkjoinGroup')
@web_util.allow_cross_request
@retry_insert_number()
def do_checkjoinGroup(redis,session):
    curTime = datetime.now()
    sid  =  request.forms.get('sid','').strip()

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    log_util.debug('[try checkjoinGroup]account[%s] sid[%s]'%(account, sid))

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}

    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}
    id = userTable.split(':')[1]
    ag,lastGroup = redis.hmget(userTable, ('parentAg','lastGroup'))
    agentTable = AGENT_TABLE%(ag)
    joinNum = '000000'
    joinMessage = redis.get(JOIN_GROUP_RESULT%(id))
    log_util.debug('joinMessage[%s] ag[%s]'%(joinMessage,ag))
    #删除玩家所有的message
    deleteAllMsg(redis,id)
    #将当前的代理发布的公告塞进玩家ID
    pushAgentMsg2User(redis,ag,id)
    if joinMessage:
        joinMessage = joinMessage.split(':')
        joinNum = joinMessage[0]
        joinResult = int(joinMessage[1])
        # redis.delete(JOIN_GROUP_RESULT%(id))

    if joinResult:
        if lastGroup:
            lastGroupAdmin = AGENT_TABLE%(lastGroup)
            lastParentAg = getTopAgentId(redis,lastGroup)
            nowParentAg  = getTopAgentId(redis,ag)
            log_util.debug('[try checkjoinGroup] lastParent[%s] nowParent[%s] groupId[%s] card[%s] lastGroup[%s] card[%s]'\
                        %(lastParentAg,nowParentAg,ag,redis.get(USER4AGENT_CARD%(ag,id)),lastGroup,redis.get(USER4AGENT_CARD%(lastGroup,id))))

            if lastParentAg == nowParentAg:
                defaultCard = redis.get(USER4AGENT_CARD%(lastGroup,id))
            else:
                defaultCard = getDefaultRoomCard(redis,ag,id,lastGroup)
        else:
            defaultCard = getDefaultRoomCard(redis,ag,id)

        if not defaultCard:
            defaultCard = 0

        log_util.debug('[try checkjoinGroup] ag[%s] defaultCard[%s]'%(ag,defaultCard))
        redis.set(USER4AGENT_CARD%(ag, id),int(defaultCard))
        redis.hset(userTable,'baseScore','[1]')
    if not joinMessage:
        ag = redis.hget(userTable, 'parentAg')
        if ag:
            return {'code':0, 'joinResult':1, 'group_id':ag}
        else:
            return {'code':0, 'joinResult':0}
    if joinResult != 2:
        return {'code':0, 'joinResult':joinResult, 'group_id':joinNum}
    else:
        return {'code':0, 'joinResult':joinResult, 'msg':'加入公会失败', 'group_id':joinNum}

@hall_app.get('/extendSession')
@web_util.allow_cross_request
@retry_insert_number()
def do_extendSession(redis,session):
    """
    游戏中延长session有效时间接口
    """



    ip = web_util.get_ip()
    api_path = request.path
    log_util.debug('user ip[%s] remove_ip[%s] path[%s]'%(ip,request['REMOTE_ADDR'],request.path))
    sid = request.GET.get('sid','').strip()

    # 获取访问记录
    get_num = redis.get("request:_inExtends:%s" % sid)
    # 获取再2秒内请求的次数
    get_num = int(get_num) if get_num else 0
    # 如果这个次数大于3的话就直接反回
    if get_num > 5:
        return {"code": -1, "msg": "你的请求过快。"}
    # 否则我就记录起来并且数量加1
    get_num += 1
    redis.setex("request:_inExtends:%s" % sid, get_num, 2)

    SessionTable = FORMAT_USER_HALL_SESSION%(sid)
    if not redis.exists(SessionTable):
        return {'code':1}

    extendSession(redis,session,SessionTable)
    return {'code':0}


@hall_app.post('/game_version')
@web_util.allow_cross_request
@retry_insert_number()
def get_version(redis, session):
    """
        获取特定游戏的版本号
    """
    sid = request.forms.get('sid', '').strip()
    gameid = request.forms.get('gameid', '').strip()

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    if verfiySid and sid != verfiySid:
        return {'code': -4,'msg': '账号已在其他地方登录', 'osid': sid}

    if not redis.exists(SessionTable):
        return {'code':-3, 'msg':'sid 超时'}

    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}
    picUrl, gender, groupId, isVolntExitGroup, maxScore,baseScore,user_open_auth= \
                        redis.hmget(userTable, ('headImgUrl', 'sex', 'parentAg', 'isVolntExitGroup', 'maxScore','baseScore','open_auth'))

    if not groupId:
        return {'code':-7, 'msg':'您已被移出公会，请重新加入公会'}

    game_table = GAME_TABLE % gameid
    if not redis.exists(game_table):
        return {'code': -7, 'msg': '该游戏不存在'}
    name, webTag, version,packName,game_sort = redis.hmget(game_table, ('name', 'web_tag', 'version','pack_name','game_sort'))
    res = {
        'id'                :           gameid,
        'name'              :           name,
        'web_tag'           :           webTag,
        'version'           :           version,
        'downloadUrl'       :           packName,
    }
    return {'code': 0, 'data': res}


@hall_app.post('/new_refresh')
@web_util.allow_cross_request
@retry_insert_number()
def get_version(redis, session):
    """
        刷新请求金币和钻石
    """
    sid = request.forms.get('sid', '').strip()
    gameid = request.forms.get('gameid', '').strip()

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    if verfiySid and sid != verfiySid:
        return {'code': -4,'msg': '账号已在其他地方登录', 'osid': sid}

    if not redis.exists(SessionTable):
        return {'code':-3, 'msg':'sid 超时'}

    do_sessionExpire(redis, session, SessionTable, 60 * 60)

    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}
    picUrl, gender, groupId, isVolntExitGroup, maxScore,baseScore,user_open_auth= \
                        redis.hmget(userTable, ('headImgUrl', 'sex', 'parentAg', 'isVolntExitGroup', 'maxScore','baseScore','open_auth'))

    if not groupId:
        return {'code': -7, 'msg': '您已被移出公会，请重新加入公会'}

    uid = userTable.split(':')[1]
    roomCard = redis.get(USER4AGENT_CARD % (groupId, uid))
    roomCard = int(roomCard) if roomCard else 0
    gold = redis.hget(FORMAT_USER_TABLE % uid, 'gold')
    gold = int(gold) if gold else 0
    res = {'roomCard': roomCard, 'gold': gold}
    return {'code': 0, 'data': res}


@hall_app.post('/refresh')
@web_util.allow_cross_request
@retry_insert_number()
def do_Refresh(redis,session):
    """
    刷新接口
    """
    curTime = datetime.now()
    ip = web_util.get_ip()
    sid = request.forms.get('sid','').strip()

    # 获取访问记录
    get_num = redis.get("request:_in:%s" % sid)
    # 获取再2秒内请求的次数
    get_num = int(get_num) if get_num else 0
    # 如果这个次数大于5的话就直接反回
    if get_num >= 5:
        return {"code": -1, "msg": "你的请求过快。"}
    # 否则我就记录起来并且数量加1
    get_num += 1
    redis.setex("request:_in:%s" % sid,get_num, 2)

    if not sid:
        remote_disbaled(redis)

    print 'do_Refresh'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    try:
        print '[on refresh]account[%s] sid[%s]'%(account, sid)
    except Exception as e:
        print 'print error File', e

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}

    if not redis.exists(SessionTable):
        remote_disbaled(redis)
        return {'code':-3, 'msg':'sid 超时'}


    #refresh session
    do_sessionExpire(redis,session,SessionTable,60*60)

    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}
    picUrl, gender, groupId, isVolntExitGroup, maxScore,baseScore,user_open_auth,rank,oldrank= \
                        redis.hmget(userTable, ('headImgUrl', 'sex', 'parentAg', 'isVolntExitGroup', 'maxScore','baseScore','open_auth','rank','oldrank'))

    if not groupId:
        return {'code':-7, 'msg':'您已被移出公会，请重新加入公会'}

    adminTable = AGENT_TABLE%(groupId)
    isTrail,shop,agent_open_auth = redis.hmget(adminTable,('isTrail','recharge','open_auth'))
    if not isTrail:
        isTrail = 0
    if not shop:
        shop = SHOP_OPEN

    shop = int(shop)
    id = userTable.split(':')[1]
    roomCard = redis.get(USER4AGENT_CARD%(groupId, id))
    if not roomCard:
        roomCard = 0
    if not maxScore:
        maxScore = 1

    hasBroad = False
    if redis.exists(FORMAT_BROADCAST_LIST_TABLE):
        #有广播内容
        hasBroad = True

    # 加入玩家金币
    coin = redis.hget(FORMAT_USER_TABLE % uid, 'gold')
    coin = int(coin) if coin else 0

    maxScore = int(maxScore)
    #获取开房权限
    open_room = get_user_open_auth(redis,user_open_auth,agent_open_auth)
    userInfo = {'id':id, 'ip':ip,'open_room':open_room,'picUrl':picUrl, 'gender':gender,'isTrail':int(isTrail),'shop':int(shop),'roomCard':roomCard, 'maxScore':maxScore, 'coin': coin,'rank':rank,'oldrank':oldrank}

    gameInfo = get_game_info(redis, groupId, True)
    if not gameInfo:
        return {'code':-1,'msg':'游戏不存在.'}
    goodsInfo = get_dia_goods_list(redis,groupId)
    goldInfo = getHallGoodsList(redis, "2")
    goodsInfo.extend(goldInfo)
    lobbyInfo = getHotSettingAll(redis)
    lobbyInfo['hotUpdateURL'] = lobbyInfo['hotUpdateURL']+"/"+lobbyInfo['packName']

    # 获取创建亲友圈和加入亲友圈列表
    cur_list = list(redis.smembers(CLUB_ACCOUNT_LIST % account))
    cur_list.extend(list(redis.smembers(CLUB_PLAYER_TO_CLUB_LIST % account)))
    # 玩家最近进入亲友圈的临时存储
    club_number = redis.get(CLUB_PLAYER_INTO % account)
    room_list, cur_online, cur_openplay, cur_member = [], 0, 0, 0
    if cur_list:
        if club_number:
            if club_number not in cur_list:
                cur_online_number = cur_list[0]
            else:
                cur_online_number = club_number
        else:
            cur_online_number = cur_list[0]
        # 获取首个亲友圈ID、公会信息，然后对应房间所属（亲友圈会更换公会）
        cur_online_account = redis.hget(CLUB_ATTR % cur_online_number, "club_user")
        cur_online_usertable = redis.get(FORMAT_ACCOUNT2USER_TABLE % cur_online_account)
        cur_online_agent = redis.hget(cur_online_usertable, "parentAg")
        # 获取首个亲友圈下的每个包房的房间列表
        # for other_create_room in redis.keys("otherCreate:Room:%s:%s:*:set" % (cur_online_agent, cur_online_number)):
        #     room_list.extend(redis.smembers(other_create_room))
        # # 计算每个房间的在线人数总和
        # for roomid in room_list:
        #     room2server_table = ROOM2SERVER % roomid
        #     if redis.exists(room2server_table):
        #         ag, club_number = redis.hmget(room2server_table, ("ag", "club_number"))
        #         if ag == cur_online_agent and club_number == cur_online_number:
        #             cur_openplay += 1
        #             cur_online += int(redis.hget(room2server_table, "playerCount"))
        # # 获取亲友圈会员总数，+1包括创建人
        # cur_member = redis.scard(CLUB_PLAYER_LIST % cur_online_number) + 1
    # log_debug('[try doRefresh] userInfo[%s] gameInfo[%s] goodsInfo[%s]'%(userInfo,gameInfo,goodsInfo))
    return {'code':0,'lobbyInfo':lobbyInfo,'hasBroad':hasBroad,'userInfo':userInfo,'goodsInfo':goodsInfo,'gameInfo':gameInfo, 'baseScore':map(int,eval(baseScore)) if baseScore else DEFAULT_BASE_SCORE}

@hall_app.post('/getGameID')
@web_util.allow_cross_request
@retry_insert_number()
def do_getGameID(redis,session):
    """
    由房间号获得gameid
    """
    sid = request.forms.get('sid', '').strip()
    roomid = request.forms.get('roomid','').strip()
    gameid, club_number = redis.hmget(ROOM2SERVER%(roomid), 'gameid', "club_number")
    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
    
    print '[on getGameID]club_number[%s] gameid[%s]' % (club_number, gameid)
    if club_number:
        ownerAccount = redis.hget("club:attribute:%s:hash" % club_number, "club_user")
        clubAccounts = redis.smembers("club:players:%s:set" % club_number)
        print '[on getGameID]ownerAccount[%s] clubAccounts[%s]' % (ownerAccount, clubAccounts)
        if ownerAccount != account and account not in clubAccounts:
            return {"code": -1, "msg": "你不是该亲友圈成员。"}

    try:
        print '[on getGameID]roomid[%s] gameid[%s]'%(roomid, gameid)
    except Exception as e:
        print 'print error File', e

    if not gameid:
        return {'code':-1, 'msg':'未找到房间'}
    else:
        return {'code':0, 'gameid':gameid}


@hall_app.post('/getRoomSetting')
@web_util.allow_cross_request
@retry_insert_number()
def do_getRoomSetting(redis,session):
    """
    获取创建房间设置信息
    """
    curTime = datetime.now()
    sid = request.forms.get('sid','').strip()


    #return
    print 'do_getRoomSetting'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    try:
        print '[on getRoomSetting]sid[%s] account[%s]'%(sid, account)
    except Exception as e:
        print 'print error File', e

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}

    if not redis.exists(SessionTable):
        return {'code':-3, 'msg':'sid 超时'}
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}

    groupId = redis.hget(userTable, 'parentAg')

    gameIdList = get_game_info(redis,groupId)
    if not gameIdList:
        return {'code':-1}
    gameDatas = []
    gameIdList = [gameid for gameid in gameIdList if gameid[0] not in redis.smembers(GOLD_GAMEID_SET)]
    for gameId in gameIdList:
        gameId = convert_util.to_int(gameId[0])
        gameTable = GAME_TABLE%(gameId)
        gameName,relationOpts,relationAndOpts, other_info, gameType = redis.hmget(gameTable,('name','dependSetting','dependAndSetting', 'other_info', 'gameType'))
        gameType = int(gameType) if gameType else 0
        try:
            gameRuleUrl = redis.hget(gameTable,'template_url')
            if not gameRuleUrl:
                gameRuleUrl = '/intro/game_0.html'
        except:
            gameRuleUrl = '/intro/game_0.html'

        optionType = 1
        ruleLists = []
        # ruleLists.append({'title': "房费", 'list': ["房主支付", "代开房间"], 'Dependencies': [], 'message': [], 'type': 1, 'row': ""})
        roomCardsDatas = []
        for index, data in enumerate(redis.lrange(USE_ROOM_CARDS_RULE%(gameId), 0, -1)):
            datas = data.split(':')
            name, cards = datas[0], datas[1]
            # roomCardsDatas.append({'name':name, 'cards':int(cards)})
            roomCardsDatas.append({'name':name, 'cards':int(index)})
        rows = 0
        for ruleNum in redis.lrange(GAME2RULE%(gameId), 0, -1):
            ruleTile, ruleType, rule, message,depend= redis.hmget(GAME2RULE_DATA%(gameId, ruleNum), ('title', 'type', 'rule', 'message','depend'))
            try:
                message = message.split(',')
            except:
                message = []
            ruleDataList = rule.split(',')
            ruleData = {'type':int(ruleType), 'title':ruleTile, 'list':ruleDataList,'Dependencies':[], 'message':message,'rows':rows}
            if redis.hexists(GAME2RULE_DATA%(gameId, ruleNum), 'row'):
                ruleData['row'] = redis.hget(GAME2RULE_DATA%(gameId, ruleNum), 'row')
            if depend:
                dependsDatas = redis.hget(GAME2RULE_DATA%(gameId, ruleNum), 'depend').split(';')
                for depend in dependsDatas:
                    if depend == '0':
                        """
                        type:3 为空
                        """
                        ruleData['Dependencies'].append({'type':3,'list':[]})
                    else:
                        subInfo = depend.split('|')
                        ruleData['Dependencies'].append({'type':int(subInfo[0]),'list':subInfo[1].split(',')})
            rows+=1
            ruleLists.append(ruleData)

        if relationOpts:
            #或选项
            relationOpts = eval(relationOpts)
        else:
            relationOpts = {}

        if relationAndOpts:
            #与选项
            relationAndOpts = eval(relationAndOpts)
        else:
            relationAndOpts = {}

        gameDatas.append({'name':gameName,'relationOptsAnd':relationAndOpts,'relationOptsOr':relationOpts,'optionType':optionType, 'gameId':gameId,'ruleUrl':gameRuleUrl,'optionsData':ruleLists, 'cardUseDatas':roomCardsDatas, 'other_info':other_info, "gameType": gameType})

    # print '[getRoomSetting][info] gameId[%s] gameRule[%s]'%(gameIdList,gameDatas)

    return {'code':0,'setting':gameDatas}


@hall_app.post('/joinRoom')
@web_util.allow_cross_request
@retry_insert_number()
def do_joinRoom(redis,session):
    """
    加入房间接口
    """
    roomid = request.forms.get('roomid','').strip()
    sid = request.forms.get('sid','').strip()
    print 'do_joinRoom'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    try:
        print '[on joinRoom]sid[%s] account[%s] roomid[%s]'%(sid, account, roomid)
    except Exception as e:
        print 'print error File', e

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}

    redis.hmset(SessionTable,
        {
            'action'   :   0,
            'roomid'    :   roomid,
        }
    )
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}
    groupId, maxScore = redis.hmget(userTable, ('parentAg', 'maxScore'))
    agentTable = AGENT_TABLE%(groupId)
    agValid = redis.hget(agentTable,'valid')
    if agValid != '1':
        print  '[JoinRoom][info] agentId[%s] has freezed. valid[%s] '%(groupId,agValid)
        return {'code':-7,'msg':'该公会已被冻结,不能创建或加入该公会的房间'}
    if not maxScore:
        maxScore = 1

    print '[join game][info] groupId[%s] roomid[%s]'%(groupId, roomid)
    ip, port, ag, gameid, playerCount, maxPlayer, baseScore, club_number = redis.hmget(ROOM2SERVER%(roomid), ('ip', 'port', 'ag', 'gameid', 'playerCount', 'maxPlayer', 'baseScore', "club_number"))
    print '[join game][info] ip[%s] port[%s] ag[%s] gameid[%s] playerCount[%s] maxPlayer[%s] maxScore[%s] baseScore[%s]'\
                        %(ip, port, ag, gameid, playerCount, maxPlayer,maxScore,baseScore)
    print '[join game]club_number[%s] gameid[%s]' % (club_number, gameid)
    if club_number:
        if club_number in redis.smembers('club:banPlay:set'):
            return {"code": 1, 'msg': "禁止娱乐"}

        if account in redis.smembers('club:banPlayer:%s:set' % club_number):
            return {"code": 1, 'msg': "禁止娱乐"}
        ownerAccount = redis.hget("club:attribute:%s:hash" % club_number, "club_user")
        clubAccounts = redis.smembers("club:players:%s:set" % club_number)
        print '[join game]ownerAccount[%s] clubAccounts[%s]' % (ownerAccount, clubAccounts)
        if ownerAccount != account and account not in clubAccounts:
            return {"code": 1, "msg": "你不是该亲友圈成员。"}
        signTable = "club:userbanList:%s:hset" % club_number
        users = redis.lrange("room2accountList:roomId:%s:list" % roomid, 0, -1)
        allBanList = set()

        curUserBanList = redis.hget(signTable, uid)
        if not curUserBanList:
            curUserBanList = set()
        else:
            curUserBanList = eval(curUserBanList)

        for _user in users:
            _userTable = redis.get("users:account:%s" % _user)
            _user_id = _userTable.split(":")[-1]
            if _user_id in curUserBanList:
                return {"code": 1, "msg": "房间有不能与你同台的玩家,请阁下更换其它房间"}

            banList = redis.hget(signTable, _user_id)
            if not banList:
                banList = set()
            else:
                banList = eval(banList)
            allBanList |= banList
        print(u"禁止的用户：%s , 当前用户:%s" % (allBanList, uid))
        if uid in allBanList:
            return {"code": 1, "msg": "房间有不能与你同台的玩家,请阁下更换其它房间"}
    if not ip:
        return {'code':-2, 'msg':'房间已解散'}

    if redis.exists(GOLD_ROOM_DATA % (gameid, roomid)):
        return {'code': -2, 'msg': '您没有权限进入'}

    if int(maxScore) < int(baseScore):
        return {'code':-1, 'msg':'底分不足'}
    try:
        hidden = int(redis.hget(ROOM2SERVER%(roomid), 'hidden'))
    except:
        hidden = 1
    key = redis.get(ACCOUNT2WAIT_JOIN_PARTY_TABLE%account)
    # for key in redis.keys(WAIT_JOIN_PARTY_ROOM_PLAYERS%('*', '*', '*')):
    if key:
        if account in redis.lrange(key, 0, -1):
            try:
                game, serviceTag = redis.get('account:%s:wantServer'%account).split(',')
                message = HEAD_SERVICE_PROTOCOL_NOT_JOIN_PARTY_ROOM%(account, ag)
                redis.lpush(FORMAT_SERVICE_PROTOCOL_TABLE%(game, serviceTag), message)
            except:
                print '[account wantServer][%s]'%(redis.get('account:%s:wantServer'%account))
            redis.lrem(key, account)

    # if account in waitJoinPlayers:
        # return {'code':-1, 'msg':'等待加入游戏中'}
    if int(playerCount) == int(maxPlayer):
        return {'code':-1, 'msg':'房间已满'}
    # print 'hidden %s groupId %s ag %s'%(hidden,groupId,ag)
    if (hidden==0) and (int(groupId) != int(ag)):
        return {'code':-1, 'msg':'不能进入其它公会的公会房间'}

    urlRes = urlparse(request.url)
    domain = urlRes.netloc.split(':')[0]

    if redis.sismember(GOLD_GAMEID_SET, gameid):
        return {'code': 0, 'ip': domain, 'port': port, 'gameid': gameid, 'isParty': PARTY_TYPE_GOLD}
    if club_number:
        clubTochatroom_key = "club:replay:to:chatroom:%s:hash" % roomid
        if redis.exists(clubTochatroom_key):
            if not redis.hexists(clubTochatroom_key, account):
                redis.hmset("club:replay:to:chatroom:%s:hash" % roomid, {account: 0})
    return {'code':0, 'ip' : domain, 'port' : port, 'gameid':gameid}

@hall_app.post('/notJoinPartyRoom')
@web_util.allow_cross_request
@retry_insert_number()
def do_NotJoinPartyRoom(redis,session):
    """
    取消加入娱乐模式房间
    """
    sid = request.forms.get('sid','').strip()
    print 'do_NotJoinPartyRoom'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    try:
        print '[on notJoinPartyRoom]sid[%s] account[%s]'%(sid, account)
    except Exception as e:
        print 'print error File', e

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        return {'code':-3, 'msg':'sid 超时'}
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}
    ag = redis.hget(userTable, 'parentAg')
    ag = 1

    account2waitTable = ACCOUNT2WAIT_JOIN_PARTY_TABLE%account
    if redis.exists(account2waitTable):
        redis.rpush(CANCEL_JOIN_PARTY_ROOM_PLAYERS, account)
    return {'code':0}

    """
    for key in redis.keys(WAIT_JOIN_PARTY_ROOM_PLAYERS%('*', '*', '*')):
        if account in redis.lrange(key, 0, -1):
            try:
                gameId, serviceTag = redis.get('account:%s:wantServer'%account).split(',')
                message = HEAD_SERVICE_PROTOCOL_NOT_JOIN_PARTY_ROOM%(account, ag)
                redis.lpush(FORMAT_SERVICE_PROTOCOL_TABLE%(gameId, serviceTag), message)
            except:
                print '[account wantServer][%s]'%(redis.get('account:%s:wantServer'%account))
            redis.lrem(key, account)
    return {'code':0}
    """

@hall_app.post('/joinPartyRoom')
@web_util.allow_cross_request
@retry_insert_number()
def do_JoinPartyRoom(redis,session):
    """
    加入娱乐模式房间
    """
    gameId = request.forms.get('gameid','').strip()
    gameId = int(gameId)
    # gameId = 6
    sid = request.forms.get('sid','').strip()
    print 'do_JoinPartyRoom'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    try:
        print '[on joinPartyRoom]sid[%s] account[%s] gameId[%s]'%(sid, account, gameId)
    except Exception as e:
        print 'print error File', e

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        return {'code':-3, 'msg':'sid 超时'}
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}
    ag = redis.hget(userTable, 'parentAg')
    ag = 1
    # if ag == '427011':
        # gameId = 5
    # if ag == '437673':
        # gameId = 1
    # if ag == '523806':
        # gameId = 6

    rule = '[0,0,[0],1]'
    gameTable = GAME_TABLE%(gameId)
    if not redis.exists(gameTable):
        return {'code':-1, 'msg':'gameId 不存在'}

    partyPlayerCount = redis.hget(gameTable, 'party_player_count')
    if not partyPlayerCount or int(partyPlayerCount)<=0:
        return {'code':-1, 'msg':'玩家个数少于1个'}
    exitPlayerData = EXIT_PLAYER%(account)
    if redis.exists(exitPlayerData):
        return {'code' : 0}
    maxPlayers = int(partyPlayerCount)
    waitJoinList = WAIT_JOIN_PARTY_ROOM_PLAYERS%(ag, gameId, rule)
    if redis.exists(waitJoinList) and account in redis.lrange(waitJoinList, 0, -1):
        return {'code' : 0}
    # saveStr = '%s,%s,%s'%(ag, gameId, rule)
    pipe = redis.pipeline()
    pipe.rpush(waitJoinList, account)
    pipe.set(ACCOUNT2WAIT_JOIN_PARTY_TABLE%account, waitJoinList)
    pipe.set(PARTY_ACCOUNT2PLAYER_COUNT%account, maxPlayers)
    pipe.expire(PARTY_ACCOUNT2PLAYER_COUNT%account, 10 * 60)
    pipe.execute()
    return {'code' : 0}


    """
    reservedServers = []
    serverList = redis.lrange(FORMAT_GAME_SERVICE_SET%(gameId), 0, -1)
    for serverTable in serverList:
        playerCount = redis.hincrby(serverTable, 'playerCount', 0)
        # if countPlayerLimit and playerCount >= countPlayerLimit:
            # continue
        _, _, _, currency, ipData, portData = serverTable.split(':')
        reservedServers.append((currency, ipData, portData))

    if reservedServers:
        waitJoinList = WAIT_JOIN_PARTY_ROOM_PLAYERS%(ag, gameId)
        if redis.exists(waitJoinList) and account in redis.lrange(waitJoinList, 0, -1):
            return {'code' : 0}
        currency, serverIp, serverPort = reservedServers[0]
        serviceTag = '%s:%s:%s'%(currency, serverIp, serverPort)
        message = HEAD_SERVICE_PROTOCOL_JOIN_PARTY_ROOM%(account, ag)
        redis.lpush(FORMAT_SERVICE_PROTOCOL_TABLE%(gameId, serviceTag), message)
        redis.lpush(waitJoinList, account)
        saveStr = '%s,%s'%(gameId, serviceTag)
        redis.set('account:%s:wantServer'%account, saveStr)
        redis.expire('account:%s:wantServer'%account, 10 * 60)
        return {'code' : 0}
    else:
        return {'code' : -1, 'msg' : '服务器维护中'}
    """

@hall_app.post('/checkJoinPartyRoom')
@web_util.allow_cross_request
@retry_insert_number()
def do_CheckJoinPartyRoom(redis,session):
    """
    确认加入娱乐模式结果
    """
    sid = request.forms.get('sid','').strip()
    print 'do_CheckJoinPartyRoom'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}

    if not redis.exists(SessionTable):
        return {'code':-3, 'msg':'sid 超时'}

    userTable = getUserByAccount(redis, account)
    ag = redis.hget(userTable, 'parentAg')
    ag = 1
    maxPlayers = 4
    if redis.exists(PARTY_ACCOUNT2PLAYER_COUNT%account):
        maxPlayers = redis.get(PARTY_ACCOUNT2PLAYER_COUNT%account)
    if not maxPlayers:
        return {'code':-1, 'msg':'娱乐模式配置错误，加入失败'}
    maxPlayers = int(maxPlayers)
    redis.delete(PARTY_ACCOUNT2PLAYER_COUNT%account)

    isMatched = IS_MATCH_FINISHED%(account)
    exitPlayerData = EXIT_PLAYER%(account)
    if redis.exists(exitPlayerData):
        serverIp, serverPort, game = redis.hmget(exitPlayerData, ('ip', 'port', 'game'))
        urlRes = urlparse(request.url)
        domain = urlRes.netloc.split(':')[0]
        gameid = redis.hget(ROOM2SERVER%(game), 'gameid')
        redis.delete(isMatched)
        return {'code':0, 'ip' : domain, 'port' : serverPort, 'gameid':gameid}
    else:
        key = redis.get(ACCOUNT2WAIT_JOIN_PARTY_TABLE%account)
        # for key in redis.keys(WAIT_JOIN_PARTY_ROOM_PLAYERS%(ag, '*', '*')):
        if key:
            waitJoinList = redis.lrange(key, 0, -1)
            if account in waitJoinList:
                # if key.split(':')[-2] == '5':
                    # maxPlayers = 5
                waitPlayers = len(waitJoinList)
                print '[check join party] account[%s] waitPlayers[%s]'%(account,waitPlayers)
                return {'code':0, 'maxPlayers':maxPlayers, 'waitPlayers':waitPlayers}

    if redis.exists(isMatched) and not redis.get(isMatched):
        return {'code':0, 'maxPlayers':maxPlayers, 'waitPlayers':maxPlayers}
    return {'code':-1, 'msg':'未申请加入娱乐模式'}

@hall_app.post('/createRoom')
@web_util.allow_cross_request
@retry_insert_number()
def do_CreateRoom(redis,session):
    """
    创建房间接口
    """
    # tt = request.forms.get('tt', '').strip()
    # if tt not in ACCEPT_TT:
        # print "try getServer: get faild, code[1]."
        # return {'code' : -1}
    gameId = request.forms.get('gameid','').strip()    
    rule = request.forms.get('rule','').strip()
    sid = request.forms.get('sid','').strip()
    hidden = request.forms.get('hidden','').strip()

    print 'do_CreateRoom'    
    if not gameId or len(gameId)<1:
        return
    if not sid or len(sid)<1:
        remote_disbaled(redis)
        return
    if not rule or len(rule)<1:
        return
    if not hidden or len(hidden)<1:
        return    
    try:
        gameId = int(gameId)
    except Exception as e:
        print 'gameID error File', e
        return
    if not gameId :
        return
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    try:
        print '[on createRoom]sid[%s] account[%s] gameId[%s] rule[%s] hidden[%s]'%(sid, account, gameId, rule, hidden)
    except Exception as e:
        print 'print error File', e
        return 

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        remote_disbaled(redis)
        return {'code':-3, 'msg':'sid 超时'}

    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}
    ag, maxScore,user_open_auth = redis.hmget(userTable, ('parentAg', 'maxScore','open_auth'))
    adminTable = AGENT_TABLE%(ag)
    agValid,agent_open_auth = redis.hmget(adminTable,('valid','open_auth'))
    #获取是否有权限开房
    open_room = get_user_open_auth(redis,user_open_auth,agent_open_auth)
    if agValid != '1':
        print  '[CraeteRoom][info] agentId[%s] has freezed. valid[%s] '%(ag,agValid)
        return {'code':-7,'msg':'该公会已被冻结,不能创建或加入该公会的房间'}

    # 目前只有欢乐拼点支持好友开房
    if str(gameId) in redis.smembers(GOLD_GAMEID_SET) and str(gameId) != '557':
        return {'code': -1, 'msg': '该游戏不能通过代开房间或房主开房启动'}

    id = userTable.split(':')[1]
    roomCards = redis.get(USER4AGENT_CARD%(ag, id))
    if not maxScore:
        maxScore = 1
    params = eval(rule)

    isOther = params[0]
    try:
        isOther = int(isOther)
    except:
        pass
    del params[0]
    print params

    if params[-1] > maxScore:
        params[-1] = maxScore
    needRoomCards = int(params[-2])

    for index, data in enumerate(redis.lrange(USE_ROOM_CARDS_RULE%(gameId), 0, -1)):
        datas = data.split(':')
        name, cards = datas[0], datas[1]
        try:
            playCount = int(datas[2])
        except:
            playCount = 0
        # if int(cards) == needRoomCards:
            # break
        if int(index) == needRoomCards:
            needRoomCards = int(cards)
            params[-2] = needRoomCards
            break
        playCount = -1
    if playCount < 0:
        return {'code':-1,'msg':'房间规则已修改，请重新加载创房页面'}
    params.insert(-2, playCount)

    rule = str(params)

    if int(roomCards) < needRoomCards:
        return {'code':-6,'msg':'钻石不足'}
    print '[do_CreateRoom][info] roomCards[%s] needRoomCards[%s]'%(roomCards, needRoomCards)

    if not isOther:

        key = redis.get(ACCOUNT2WAIT_JOIN_PARTY_TABLE%account)
        # for key in redis.keys(WAIT_JOIN_PARTY_ROOM_PLAYERS%('*', '*', '*')):
        if key:
            if account in redis.lrange(key, 0, -1):
                try:
                    game, serviceTag = redis.get('account:%s:wantServer'%account).split(',')
                    message = HEAD_SERVICE_PROTOCOL_NOT_JOIN_PARTY_ROOM%(account, ag)
                    redis.lpush(FORMAT_SERVICE_PROTOCOL_TABLE%(game, serviceTag), message)
                except:
                    print '[account wantServer][%s]'%(redis.get('account:%s:wantServer'%account))
                redis.lrem(key, account)
        # if account in waitJoinPlayers:
            # return {'code':-1, 'msg':'等待加入游戏中'}


    countPlayerLimit = 30
    gameTable = GAME_TABLE%(gameId)
    maxRoomCount = redis.hget(gameTable,'maxRoomCount')
    if maxRoomCount:
        countPlayerLimit = int(maxRoomCount) * 4

    reservedServers = []
    serverList = redis.lrange(FORMAT_GAME_SERVICE_SET%(gameId), 0, -1)
    for serverTable in serverList:
        playerCount = redis.hincrby(serverTable, 'playerCount', 0)
        roomCount = redis.hincrby(serverTable, 'roomCount', 0)
        if not playerCount:
            playerCount = 0
        if not roomCount:
            roomCount = 0
        playerCount = int(playerCount)
        roomCount = int(roomCount)
        countPlayerLimit = int(countPlayerLimit)
        if countPlayerLimit and (playerCount >= countPlayerLimit or roomCount >= countPlayerLimit/4):
            continue
        _, _, _, currency, ipData, portData = serverTable.split(':')
        reservedServers.append((currency, ipData, portData))

    if reservedServers:
        currency, serverIp, serverPort = reservedServers[0]
        ruleText = getRuleText(rule, gameId, redis)
        if isOther:
            if open_room == 0:#没有代开权限
                return {'code':-1000,'msg':'没有代开房间权限'}

            params = eval(rule)
            params.append(int(hidden))
            rule = str(params)
            protocolStr = HEAD_SERVICE_PROTOCOL_CREATE_OTHER_ROOM%(account, ag, rule, ruleText)
            redis.rpush(FORMAT_SERVICE_PROTOCOL_TABLE%(gameId, '%s:%s:%s'%(currency, serverIp, serverPort)), protocolStr)
            return {'code':0, 'msg':'房间开启成功', 'ip':'', 'port':''}

        redis.hmset(SessionTable,
            {
                'action'   :   1,
                'rule'     :   rule,
                'ruleText' :   ruleText,
                'hidden'   :   hidden,
            }
        )
        urlRes = urlparse(request.url)
        domain = urlRes.netloc.split(':')[0]

        if redis.sismember(GOLD_GAMEID_SET, gameId):
            return {'code': 0, 'ip': domain, 'port': serverPort, 'isParty': PARTY_TYPE_GOLD}
        return {'code': 0, 'ip' : domain, 'port' : serverPort}
    else:
        return {'code':-1, 'msg':'服务器忙碌或维护中'}

@hall_app.post('/getRoomList')
@web_util.allow_cross_request
@retry_insert_number()
def do_getRoomList(redis,session):
    """
    获取房间列表
    """
    sid  =  request.forms.get('sid','').strip()

    if not sid:
        remote_disbaled(redis)
        return {"code": 1, "msg": "参数错误没有SID"}

    print 'do_getRoomList'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    try:
        print '[on getRoomList]sid[%s] account[%s]'%(sid, account)
    except Exception as e:
        print 'print error File', e

    print 'account'
    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        remote_disbaled(redis)
        return {'code':-3, 'msg':'sid 超时'}
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}

    id = userTable.split(':')[1]
    maxScore,userBaseScore = redis.hmget(userTable,('maxScore','baseScore'))
    print maxScore,userBaseScore
    if not userBaseScore:
        userBaseScore = DEFAULT_BASE_SCORE
    groupId = redis.hget(userTable, 'parentAg')
    print maxScore,userBaseScore
    if not maxScore:
        maxScore = 1
    try:
        roomLists = redis.smembers(AG2SERVER%(groupId))
    except:
        roomLists = []
    roomDatas = []
    for roomNum in roomLists:
        # print '[getRoomList][info] ROOM2SERVER[%s]'%ROOM2SERVER%(roomNum)
        gameName, dealer, playerCount, maxPlayer, gameid,baseScore, ruleText = redis.hmget(ROOM2SERVER%(roomNum), ('gameName', 'dealer', 'playerCount', 'maxPlayer', 'gameid','baseScore', 'ruleText'))
        if not baseScore:
            baseScore = 1
        print 'baseScore[%s],userBaseScore[%s]'%(baseScore,userBaseScore)
        try:
            hidden = int(redis.hget(ROOM2SERVER%(roomNum), 'hidden'))
        except:
            hidden = 0

        if isinstance(userBaseScore,str):
            userBaseScore = map(int,eval(userBaseScore))

        print userBaseScore
        if int(baseScore)!=1 and int(baseScore) not in userBaseScore:
            continue

        try:
            if int(playerCount) == int(maxPlayer) or hidden == 1:
                continue
        except:
            continue
        roomDatas.append({'gameName':gameName, 'dealer':dealer, 'playerCount':playerCount, 'maxPlayer':maxPlayer, 'roomNum':roomNum, 'gameid':gameid, 'ruleText':ruleText, 'baseScore':int(baseScore)})
    # print '[getRoomList][info] roomDatas[%s]'%roomDatas
    return {'code':0, 'roomData':roomDatas}

@hall_app.post('/getMyRoomList')
@web_util.allow_cross_request
@retry_insert_number()
def do_getMyRoomList(redis,session):
    """
    开给别人的房间列表
    """
    sid  =  request.forms.get('sid','').strip()
    print 'do_getRoomList'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    try:
        print '[on getMyRoomList]sid[%s] account[%s]'%(sid, account)
    except Exception as e:
        print 'print error File', e

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        return {'code':-3, 'msg':'sid 超时'}
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}

    account = redis.hget(SessionTable, 'account')
    otherRooms = MY_OTHER_ROOMS%account

    gameDatas = []
    type2gameDatas = {}
    for roomTable in redis.lrange(otherRooms, 0, -1):
        if not redis.exists(roomTable):
            redis.lrem(otherRooms, roomTable)
            continue
        roomId, name, gameType, minNum, maxNum, roomTime, rule, accountsStr, roomType, endTime, gameid, club_number = redis.hmget(roomTable,\
                ('roomId', 'name', 'gameType', 'minNum', 'maxNum', 'time', 'rule', 'accountList', 'roomType', 'endTime','gameid', "club_number"))
        print '[getMyRoomList] roomId[%s], name[%s], gameType[%s], minNum[%s], maxNum[%s], roomTime[%s], rule[%s], accountsStr[%s], roomType[%s], endTime[%s]'%(roomId, name, gameType, minNum, maxNum, roomTime, rule, accountsStr, roomType, endTime)
        if redis.hget(ROOM2SERVER % roomId, "club_number"):
            continue

        if club_number and club_number != '':
            continue

        try:
            gameType = int(gameType)
        except:
            redis.lrem(otherRooms, roomTable)
            continue
        try:
            roomType = int(roomType)
            if roomType:
                roomType = '好友'
            else:
                roomType = '公会'
            import time
            endTime = max(int(endTime) - int(time.time() * 1000), 0)
        except:
            roomType = ''
            endTime = 0
        try:
            if accountsStr:
                accountList = accountsStr.split(';')
            else:
                accountList = redis.lrange(ROOM2ACCOUNT_LIST%(roomId), 0, -1)
        except:
            accountList = []
        account2Data = []
        for playerAccount in accountList:
            account2user_table = FORMAT_ACCOUNT2USER_TABLE%(playerAccount)
            table = redis.get(account2user_table)
            nickname, headImgUrl = redis.hmget(table, ('nickname', 'headImgUrl'))
            account2Data.append({'nickname':nickname, 'headImgUrl':headImgUrl})
        if int(gameType) == 2:
            gameTypeStr = '已结束'
            maxPlayeCount = playerCount = 1
        elif int(gameType) == 1:
            gameTypeStr = '游戏中（%s/%s）'%(minNum, maxNum)
            maxPlayeCount = 1
            playerCount = 1
        else:
            gameTypeStr = '%s/%s'%(minNum, maxNum)
            maxPlayeCount = maxNum
            playerCount = minNum
        # gameDatas.append({'roomId':roomId, 'name':name, 'gameType':gameTypeStr, 'time':time, 'rule':rule,\
                # 'maxPlayeCount':maxPlayeCount, 'playerCount':playerCount})
        if not int(playerCount):
            if -1 not in type2gameDatas:
                type2gameDatas[-1] = []
            type2gameDatas[-1].append({'roomId':roomId, 'name':name, 'gameType':gameTypeStr, 'time':roomTime, 'rule':rule,\
                    'maxPlayeCount':maxPlayeCount, 'playerCount':playerCount, 'account2Data':account2Data,\
                    'roomType': roomType, 'endTime':endTime, 'gameid':gameid})
        else:
            if int(gameType) not in type2gameDatas:
                type2gameDatas[int(gameType)] = []
            type2gameDatas[int(gameType)].append({'roomId':roomId, 'name':name, 'gameType':gameTypeStr, 'time':roomTime, 'rule':rule,\
                    'maxPlayeCount':maxPlayeCount, 'playerCount':playerCount, 'account2Data':account2Data,\
                    'roomType': roomType, 'endTime':endTime, 'gameid':gameid})
    for i in xrange(4):
        index = i - 1
        if index in type2gameDatas:
            gameDatas.extend(type2gameDatas[index])
    return {'code':0, 'gameDatas':gameDatas}

@hall_app.post('/dissolveMyRoomList')
@web_util.allow_cross_request
@retry_insert_number()
def do_dissolveMyRoomList(redis,session):
    """
    解散我自己的房间
    """
    sid  =  request.forms.get('sid','').strip()
    roomId = request.forms.get('roomId','').strip()
    print 'do_getRoomList'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    try:
        print '[on dissolveMyRoomList]sid[%s] account[%s] roomId[%s]'%(sid, account, roomId)
    except Exception as e:
        print 'print error File', e

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        return {'code':-3, 'msg':'sid 超时'}
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}

    account = redis.hget(SessionTable, 'account')
    roomTable = ROOM2SERVER%(roomId)
    otherRooms = MY_OTHER_ROOMS%account
    otherRoomList = redis.lrange(otherRooms, 0, -1)
    roomIds = []
    for table in otherRoomList:
        roomIds.append(table.split(':')[-2])
    if roomId not in roomIds:
        return {'code':1,'msg':'无权限的房间'}
    try:
        gameId, playerCount, maxPlayer = redis.hmget(roomTable, ('gameid', 'playerCount', 'maxPlayer'))
        playerCount = int(playerCount)
        maxPlayer = int(maxPlayer)
    except:
        return {'code':1,'msg':'房间已解散或不存在'}
    if int(playerCount) == int(maxPlayer):
        return {'code':1,'msg':'房间内玩家已满，无法解散'}

    sendProtocol2GameService(redis, gameId,HEAD_SERVICE_PROTOCOL_DISSOLVE_ROOM%(roomId))
    return {'code':0,'msg':'房间解散成功'}

@hall_app.post('/exitGroup')
@web_util.allow_cross_request
@retry_insert_number()
def do_exitGroup(redis,session):
    """
    退出公会接口
    """
    sid  =  request.forms.get('sid','').strip()
    SessionTable = FORMAT_USER_HALL_SESSION%(sid)
    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}
    account = redis.hget(SessionTable, 'account')

    try:
        print '[on exitGroup]sid[%s] account[%s]'%(sid, account)
    except Exception as e:
        print 'print error File', e

    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}
    groupId,cards = redis.hmget(userTable, ('parentAg','roomCard'))
    id = userTable.split(':')[1]
    adminTable = AGENT_TABLE%(groupId)
    if redis.exists(adminTable) and redis.exists(userTable):
        tryExitGroup(redis, userTable, account, id, groupId)
        return {'code':0, 'msg':'退出公会成功'}
    else:
        return {'code':-1, 'msg':'退出公会失败'}

@hall_app.post('/getPlayHis')
@web_util.allow_cross_request
@retry_insert_number()
def do_getPlayHis(redis,session):
    """
    获得历史回放
    """
    sid = request.forms.get('sid','').strip()
    getAccount = request.forms.get('account','').strip()

    SessionTable = FORMAT_USER_HALL_SESSION%(sid)
    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}

    account = redis.hget(SessionTable, 'account')
    if getAccount:
        account = getAccount
    print '[do_getPlayHis] account[%s] getAccount[%s]'%(account, getAccount)

    playHisList = []
    LEN = 99
    timeRe = 'startTime:[0-9]+'
    roomRe = 'game:\w+'
    playHis = PLAYER_PLAY_ROOM%(account)
    data = redis.lrange(playHis, 0, LEN)
    for hisData in data:
        timeData = re.search(timeRe, hisData)
        timeData = timeData.group()
        time = timeData.split(':')[1]
        roomData = re.search(roomRe, hisData)
        roomData = roomData.group()
        num = roomData.split(':')[1]
        if redis.exists(hisData):
            game2room = GAME2ROOM%(num, time)
            dataTable = PLAY_GAME_DATA%(num, time)
            if redis.exists(dataTable):
                players, gameid, scoreData = redis.hmget(dataTable, ('player', 'gameid', 'score'))
                players = players.split(':')
                for gamePlayer in players:
                    if not gamePlayer:
                        continue
                    hisPlayer = gamePlayer.split(',')[1]
                    if hisPlayer == account:
                        side = int(gamePlayer.split(',')[0])
                        score = int(scoreData.split(':')[side])
                        name = redis.hget(GAME_TABLE%(gameid), 'name')
                        ownnerAccount = players[0].split(',')[1]
                        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(ownnerAccount)
                        table = redis.get(account2user_table)
                        ownnerNickname = redis.hget(table, 'nickname')
                        playHisList.append({'side':side, 'time':time, 'gameid':gameid, 'roomId':num, 'score':score,\
                                'name':name, 'ownner':ownnerNickname})
                        break
        else:
            redis.lrem(playHis, hisData)

    if not playHisList:
        return {'code':-1, 'msg':'没有回放数据'}
    else:
        return {'code':0, 'playHis':playHisList}

@hall_app.post('/getPlayHisData')
@web_util.allow_cross_request
@retry_insert_number()
def do_getPlayHisData(redis,session):
    sid = request.forms.get('sid','').strip()
    getAccount = request.forms.get('account','').strip()
    SessionTable = FORMAT_USER_HALL_SESSION%(sid)

    account = redis.hget(SessionTable, 'account')
    if getAccount:
        account = getAccount
    print '[do_getPlayHisData] account[%s] getAccount[%s]'%(account, getAccount)
    time = request.forms.get('time','').strip()
    num = request.forms.get('roomId','').strip()

    playHisList = []
    game2room = GAME2ROOM%(num, time)
    dataTable = PLAY_GAME_DATA%(num, time)
    if redis.exists(dataTable):
        players, gameid = redis.hmget(dataTable, ('player', 'gameid'))
        players = players.split(':')
        for gamePlayer in players:
            if not gamePlayer:
                continue
            hisPlayer = gamePlayer.split(',')[1]
            if hisPlayer == account:
                side = int(gamePlayer.split(',')[0])
                for roomData in redis.lrange(game2room, 0, -1):
                    time = roomData.split(':')[3]
                    roomData = GAME_ROOM_DATA%(num, time)
                    replayNum, scoreData = redis.hmget(roomData, ('actionData', 'score'))
                    score = int(scoreData.split(':')[side])
                    print 'give replay:account:%s,side:%s'%(account, side)
                    replayNum = replayNum + "%05d"%(int(gameid))
                    nicknameList = []
                    for playerAccountData in players:
                        playerAccount = playerAccountData.split(',')[1]
                        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(playerAccount)
                        table = redis.get(account2user_table)
                        playerNickname = redis.hget(table, 'nickname')
                        nicknameList.append(playerNickname)
                    playHisList.append({'side':side, 'time':time, 'gameid':gameid, 'replayNum':replayNum, 'roomId':num, 'score':score,\
                            'player':nicknameList})
    if not playHisList:
        return {'code':-1, 'msg':'没有回放数据'}
    else:
        playHisList.reverse()
        return {'code':0, 'playHis':playHisList}

@hall_app.post('/getPlayHisScore')
@web_util.allow_cross_request
@retry_insert_number()
def do_getPlayHisScore(redis,session):
    sid = request.forms.get('sid','').strip()
    SessionTable = FORMAT_USER_HALL_SESSION%(sid)

    gameStartTime = request.forms.get('time','').strip()
    roomId = request.forms.get('roomId','').strip()

    gamesData = PLAY_GAME_DATA%(roomId, gameStartTime)
    players, descs, scores, roomSettings, ownner = redis.hmget(gamesData, ('player', 'descs', 'score', 'roomSettings', 'ownner'))
    nicknames = []
    headImgUrls = []
    accounts = []
    ids = []
    players = players.split(':')
    if '|' not in descs:
        descs = []
    else:
        descs = descs.split('|')
    scores = scores.split(':')
    if roomSettings:
        roomSettings = roomSettings.split('|')
    else:
        roomSettings = []
    for player in players:
        account = player.split(',')[1]
        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(account)
        table = redis.get(account2user_table)
        id = table.split(':')[-1]
        nickname, headImgUrl = redis.hmget(table, ('nickname', 'headImgUrl'))
        headImgUrls.append(headImgUrl)
        nicknames.append(nickname)
        accounts.append(account)
        ids.append(id)
    datas = []
    try:
        ownner = int(ownner)
    except:
        ownner = 100
    for index in xrange(len(nicknames)):
        if descs:
            descsData = descs[index].split(',')
        else:
            descsData = []
        roomSetting = ''
        if roomSettings:
            roomSetting = roomSettings[index]
        datas.append({'nickname':nicknames[index], 'descs':descsData, 'score':scores[index],\
                'id':ids[index], 'account': accounts[index], 'headImgUrl':headImgUrls[index], 'roomSetting':roomSetting, 'isOwner':ownner == index})
    if datas:
        return {'code':0, 'scoreData':datas}
    else:
        return {'code':-1, 'msg':'回放已过期'}

@hall_app.post('/getReplay')
@web_util.allow_cross_request
@retry_insert_number()
def do_getReplay(redis,session):
    sid = request.forms.get('sid','').strip()
    SessionTable = FORMAT_USER_HALL_SESSION%(sid)

    account = redis.hget(SessionTable, 'account')
    replayNum = request.forms.get('replayNum','').strip()
    gameId = int(replayNum[-5:])
    replayNum = replayNum[:-5]
    side = request.forms.get('side','').strip()
    print 'get replay:account:%s,side:%s,replayNum:%s,gameId:%s'%(account, side, replayNum, gameId)

    try:
        redisIp, redisPort, redisNum, passwd = redis.hmget(GAME2REDIS4READ%(gameId), ('ip', 'port', 'num', 'passwd'))
        redisNum = int(redisNum)
        redis = getRedisInst(redisIp, redisNum, redisPort, passwd)
        print '[get Replay] get redis for read, ip[%s] port[%s]'%(redisIp, redisPort)
    except:
        redisIp, redisPort, redisNum, passwd = redis.hmget(GAME2REDIS%(gameId), ('ip', 'port', 'num', 'passwd'))
        redis = getRedisInst(redisIp, redisNum, redisPort, passwd)
        print '[get Replay] get redis for common, ip[%s] port[%s]'%(redisIp, redisPort)
    replayData = ''
    try:
        for data in redis.zrangebyscore(PLAYER_REPLAY_SET, int(replayNum), int(replayNum)):
            replayData = data
    except Exception as e:
        print 'get replay error[%s]'%(e)
    if replayData:
        replayData = packPrivaTeData(side, replayData)
        return str(replayData)
    else:
        return ''

@hall_app.post('/getVoiceData')
@web_util.allow_cross_request
@retry_insert_number()
def do_getVoiceData(redis,session):
    """
    开启语音服务时需调用此接口得到语音数据
    # post
    # request sample: http://<server>/entry/getVoiceData
    params:
        [tt]md5一个随机范围在198326-198335的数字做校验，简单规避爬虫等攻击尝试
        [ac]玩家账号
        [gameId]暂时无用，后续增加新游戏需要校验
    return:
        返回json:
            {
                "code"      :   #返回码，   0:校验通过，需要进一步检查errCode来得到语音API调用结果
                                            1:非法tt，客户端应提示服务器正在维护中，请稍后在进（等同于连接不上）
                                            2:ac账号非法，可能是未登录或无效账号
                "errCode"   :   语音API返回code，0为成功，可用authKey填充；其它code读取errStr信息
                "errStr"    :   语音API返回错误提示信息
                "authKey"   :   初始化key
            }
    """

    tt = request.forms.get('tt', '').strip()
    account = request.forms.get('ac', '').strip()
    gameId = request.forms.get('gameId', '').strip()
    print "getVoiceData: account[%s] gameId[%s] tt[%s]."%(account, gameId, tt)

    if tt not in ACCEPT_TT:
        return {'code':1}

    # realAccount = redis.get(UNIONID2ACCOUNT%(account))
    # if not realAccount:
        # realAccount = account
    # if redis.sismember(ONLINE_GAME_ACCOUNTS_TABLE%(MAHJONG_GAMEID), realAccount):
        # return {'code':2}

    authKey, errCode, errStr = sendTalkData()
    return {'code':0,'errCode':errCode,'errStr':errStr,'authKey':authKey}

@hall_app.post('/buyCard')
@web_util.allow_cross_request
@retry_insert_number()
def do_buyCard(redis,session):
    return
    """
    购买钻石
    """
    sid = request.forms.get('sid','').strip()
    cardNums = request.forms.get('cards','').strip()
    _type = request.forms.get('type', '').strip()
    print 'do_buyCard'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}

    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}
    groupId = redis.hget(userTable, 'parentAg')
    adminTable = AGENT_TABLE%(groupId)

    isTrail  = redis.hget(adminTable,'isTrail')

    #会员ID
    id = userTable.split(':')[1]
    pipe = redis.pipeline()
    pipe.incrby(USER4AGENT_CARD%(groupId, id),int(cardNums))
    cardMoney = getCardMoney(redis,groupId)

    log_util.debug('[HALL][url:/buyCard][info] account[%s] groupId[%s] isTrail[%s] cardNums[%s] cardMoney[%s]'%(account,groupId,isTrail,cardNums,cardMoney))

    # 金币场金币购买
    if _type == '2':
        money = 0
        flag = False
        for goodid in redis.lrange(GOODS_LIST, 0, -1):
            info = redis.hgetall(GOODS_TABLE % goodid)
            if info.get('cards', '0') == cardNums:
                money = int(float(info['price'])*100)
                flag = True
                break
        if not flag:
            return {'code': -1, 'msg': u'不存在此商品'}
        gold = addGold2Merber(redis, account, money, int(cardNums))
        return {'code': 0, 'msg': u'购买金币成功', 'gold': gold}

    if isTrail == '1':
        #试玩
        [roomCards] = pipe.execute()
        roomCard = redis.get(USER4AGENT_CARD % (groupId, id))
        return {'code':0,'msg':'购买钻石成功','roomCard':roomCard}

    try:
        log_util.debug('[HALL][url:/buyCard][error] cardNums[%s] cardMoney[%s]'%(cardNums,cardMoney))
        countRateOfAgent(redis,groupId,int(cardNums),cardMoney)
        roomCard = redis.get(USER4AGENT_CARD%(groupId, id))
    except Exception,e:
        log_util.debug('[HALL][url:/buyCard][error] Exception[%s]'%(e))
        return {'code':-1,'msg':'增加钻石失败'}

    [roomCards] = pipe.execute()

    # pipe = redis.pipeline()
    # ymd = datetime.now().strftime("%Y-%m-%d")
    # useDatas = [int(cardNums), 6, roomCards]
    # useStr = ';'.join(map(str, useDatas))
    # pipe.lpush(PLAYER_DAY_USE_CARD%(id, ymd), useStr)
    # pipe.expire(PLAYER_DAY_USE_CARD%(id, ymd), SAVE_PLAYER_DAY_USE_CARD_TIME)
    # pipe.execute()

    roomCard = redis.get(USER4AGENT_CARD % (groupId, id))
    return {'code':0,'msg':'购买钻石成功', 'roomCard':roomCard}

@hall_app.post('/getBroadcast')
@web_util.allow_cross_request
@retry_insert_number()
def do_getBroadcast(redis,session):
    """
    大厅广播
    """
    curTime  =  datetime.now()

    sid = request.forms.get('sid','').strip()

    print '[%s][hall getBroadcast][info] sid[%s]'%(curTime,sid)
    print 'do_getBroadcast'
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}

    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}
    groupId = redis.hget(userTable, 'parentAg')
    if redis.exists(FORMAT_BROADCAST_LIST_TABLE):
        broadcasts = getBroadcasts(redis,groupId)
    else:
        broadcasts = {'broadcasts':{}}

    return {'code':0,'data':broadcasts}

@hall_app.post('/notifyServer')
def do_paymentNotifyServer(redis):
    """
    微信支付
    """
    for k,v in request.forms.items():
        xml = k

    xml = xml.split('\n')
    xml = "".join(xml)

    curTime = datetime.now()
    print '[%s][wechatPay][info] recive from %s'%(curTime,request.remote_addr)

    #解析xml参数
    params = transXml2Dict(xml)
    print '[%s][wxPay][info] rcv params[%s].xml[%s]'%(curTime,params,xml)

    if not checkSign(params):
        #签名失败
        print '[%s][wechatPay][error] sign is not match.'%(curTime)
        return response2Wechat('FAIL','签名校验失败')
    if params['result_code'] != 'SUCCESS':
        print '[%s][wechatPay][error] result_code[%s] error'%(curTime,params['result_code'])
        return response2Wechat('FAIL','请求失败')
    if not verfiyRcvDatas(redis,params):
        print '[%s][wechatPay][error] data verfiy error.'%(curTime)
        return response2Wechat('FAIL','数据校验失败')

    addRoomCard2Member(redis,params['out_trade_no'])

    print '[%s][wechatPay] payment success!'%(curTime)
    #返回消息给微信
    return response2Wechat('SUCCESS','支付成功')

@hall_app.post('/onAppleStorePay')
@web_util.allow_cross_request
def do_onAppleStorePay(redis, session):
    """
    发起苹果商店支付接口
    """
    curTime = datetime.now()
    response.add_header('Access-Control-Allow-Origin', '*')
    # try:
    #     orderSwitch = int(redis.get(ORDER2WEIXIN_SWITCH))
    # except:
    #     orderSwitch = 0
    #
    # if not orderSwitch:
    #     return {'code':-1, 'msg':'暂未开放'}
    print 'do_onAppleStorePay'
    sid = request.forms.get('sid', '').strip()
    databytes = request.forms.get('data', '').strip()
    bundle_id = request.forms.get('bundle_id', '').strip()
    Sanbox = False

    databytes = databytes.replace(' ', '+')
    validator = AppStoreValidator(bundle_id, Sanbox)  # 确认支付

    try:
        purchases = validator.validate(databytes)

        productid = purchases[0].product_id
        transaction_id = purchases[0].transaction_id
        qty = purchases[0].quantity

        print 'applePay'
        SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)

        if verfiySid and sid != verfiySid:
            # session['member_account'],session['member_id'] = '',''
            return {'code': -4, 'msg': '账号已在其他地方登录', 'osid': sid}
        if not redis.exists(SessionTable):
            return {'code': -3, 'msg': 'sid 超时'}

        userTable = getUserByAccount(redis, account)
        if not redis.exists(userTable):
            return {'code': -5, 'msg': '该用户不存在'}
        groupId = redis.hget(userTable, 'parentAg')
        # 会员ID
        id = userTable.split(':')[1]
        cardNums = 0
        try:
            if not redis.exists(APP_PAY_ORDER_ITEM % (transaction_id)):
                # if redis.exists(GOODS_TABLE%(bundle_id)):
                #     cardNums = redis.hget(GOODS_TABLE%(bundle_id),'cards')
                print 'bundle_id %s' % bundle_id
                if bundle_id == 'com.qgmj.dx12':
                    cardNums = 12
                elif bundle_id == 'com.qgmj.dx50':
                    cardNums = 50
                else:
                    cardNums = 0

                redis.incrby(USER4AGENT_CARD % (groupId, id), int(cardNums))
                #     redis.set(APP_PAY_ORDER_ITEM%(transaction_id),productid)
                if cardNums:
                    date = curTime.strftime('%Y-%m-%d')
                    timestamp = int(time.time())
                    orderFields = {'account': account, 'groupId': groupId, 'money': float(cardNums) * 100,
                                   'name': '%s钻石' % cardNums, 'num': redis.lindex('goods:type:0:list', 0),
                                   'orderNum': transaction_id, 'roomCards': cardNums, 'time': timestamp,
                                   'startTime': timestamp, 'type': 'successful', 'payType': 'appleStorePay'}

                    pipe = redis.pipeline()
                    # 写入订单
                    pipe.lpush(ORDER_NUM_LIST, transaction_id) # 订单列表
                    pipe.lpush(DAY_ORDER % date, transaction_id) # 每日的订单列表
                    pipe.hmset(ORDER_TABLE % transaction_id, orderFields) # 订单详情表
                    pipe.expire(ORDER_TABLE % transaction_id, 62 * 24 * 60 * 60) # 订单详情表有效期

                    # 记录充值卡总额
                    if not redis.exists(USER4AGENT_RECHARGE % (groupId, uid)):
                        pipe.set(USER4AGENT_RECHARGE % (groupId, uid), 0)
                    pipe.incrby(USER4AGENT_RECHARGE % (groupId, uid), int(cardNums))

                    pipe.execute()
            else:
                return {'code': -8, 'msg': '交易ID[%s]已存在' % (transaction_id)}
        except:
            return {'code': -1, 'msg': '购买钻石失败'}

        CardMoney = getCardMoney(redis, groupId)
        countRateOfAgent(redis, groupId, int(cardNums), CardMoney)
        roomCard = redis.get(USER4AGENT_CARD % (groupId, id))
        return {'code': 0, 'msg': '购买钻石成功', 'roomCard': roomCard}

    except InAppValidationError as e:
        return {'code': -1, 'msg': '支付失败:%s' % (e)}

@hall_app.post('/onWeChatPay')
@web_util.allow_cross_request
@retry_insert_number()
def do_onWeChatPay(redis, session):
    """
    发起微信支付接口
    """
    curTime = datetime.now()

    try:
        orderSwitch = int(redis.get(ORDER2WEIXIN_SWITCH))
    except:
        orderSwitch = 0

    if not orderSwitch:
        return {'code':-1, 'msg':'暂未开放'}

    sid = request.forms.get('sid','').strip()
    goodsId   = request.forms.get('id','').strip()

    ip = request.remote_addr
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}

    userTable = getUserByAccount(redis, account)
    group_id  = redis.hget(userTable,'parentAg')

    # goodsId = redis.get(GOODS_NAME2NUM%(goodsName))
    goodsTable = GOODS_TABLE%(goodsId)
    cards,goodsName,present_card= redis.hmget(goodsTable,('cards','name','present_cards'))
    #判断金币价格
    goodsPrice = getGoodsMoney(redis,group_id,cards)
    if not redis.exists(goodsTable):
        print '[try goods][error] goods[%s] is not found.'%(goodsName)
        return {'code':-1, 'msg':'goods not found'}


    log_debug('[try goods] player cards[%s] goodsPrice[%s].'%(cards,goodsPrice))

    goodsId2OrderId = GOODS_NUM%(goodsId)
    orderIndex = redis.incr(goodsId2OrderId)
    if orderIndex >= 10000000000:
        redis.set(goodsId2OrderId, 0)
        orderIndex = redis.incr(goodsId2OrderId)
    outTradeNo = getOutTradeNo(goodsId, orderIndex)

    # data = (player, goodsBody, totalPrice, outTradeNo, goodsCount, goodsId, goodsName, goodsCards)
    # order2weixin(data) *data
    urlRes = urlparse(request.url)
    serverIp = urlRes.netloc.split(':')[0]

    nonceStr = getOrderNonceStr()
    signDict = {
        'sub_appid'         :       APPID,
        'mch_id'            :       MCH_ID,
        'nonce_str'         :       nonceStr,
        'body'              :       goodsName,
        'out_trade_no'      :       outTradeNo,
        'total_fee'         :       int(float(goodsPrice) * 100),
        'spbill_create_ip'  :       ip,
        'notify_url'        :       NOTIFY_URL%(serverIp),
        'trade_type'        :       TRADE_TYPE
    }

    #print payment params
    print '[%s][onWechatPay][info] payParams[%s]'%(curTime,signDict)

    # signList = packSignDict2List(signDict)
    # sign = getSign(signList)
    sign = gen_sign(signDict)

    orderStr = packSignDict2XML(signDict, sign)
    url = 'http://api.cmbxm.mbcloud.com/wechat/orders'
    resultDict = getXMLMessage(url, orderStr)
    print 'wxPay url[%s] data[%s] sign[%s] signDict[%s]'%(url, orderStr, sign, signDict)
    print 'resultDict:', resultDict

    if not resultDict:
        print '[%s][onWechatPay][error] resultDict[%s]'%(curTime,resultDict)
        return {'code':-1, 'msg':'微信支付失败'}
    if resultDict['return_code'] != 'SUCCESS':
        try:
            print '[%s][onWechatPay][error] resultDict[%s]'%(curTime,resultDict['return_msg'])
        except:
            pass
        return {'code':-1, 'msg':'微信支付未开启'}

    prepayID = resultDict['prepay_id']
    package = 'Sign=WXPay'
    timeStamp = int(time.time())
    signList = [
        'appid=%s'%(APPID),
        'partnerid=%s'%(MCH_ID),
        'prepayid=%s'%(prepayID),
        'package=%s'%(package),
        'noncestr=%s'%(nonceStr),
        'timeStamp=%s'%(timeStamp),
    ]
    sign = getSign(signList)

    pipe = redis.pipeline()
    # pipe.set(PENDING4ACCOUNT%(player.account, totalPrice, goodsBody), outTradeNo)
    orderTable = ORDER_TABLE%(outTradeNo)
    pipe.hmset(orderTable,
        {
            'time'         :       timeStamp,
            'sign'         :       sign,
            'nonceStr'     :       nonceStr,
            'prepayID'     :       prepayID,
            'name'         :       goodsName,
            'body'         :       "123",
            'money'        :       int(float(goodsPrice) * 100),
            'startTime'    :       timeStamp,
            'account'      :       account,
            'num'          :       goodsId,
            'type'         :       'pending',
            'roomCards'    :       cards,
            'presentCards' :       present_card
        }
    )
    pipe.sadd(PENDING_ORDER, outTradeNo)
    pipe.lpush(ORDER_NUM_LIST, outTradeNo)
    pipe.sadd(PLAYER_ORDER%(account), outTradeNo)

    pipe.lpush(DAY_ORDER%(curTime.strftime("%Y-%m-%d")), outTradeNo)
    pipe.lpush(DAY_PENDING_ORDER%(curTime.strftime("%Y-%m-%d")), outTradeNo)
    pipe.expire(orderTable, 1 * 60 * 60)
    pipe.execute()

    #发送成功信息
    app_prepay_info = eval(resultDict['app_prepay_info'])
    data = {'partnerId':app_prepay_info['partnerid'],'prepayID':app_prepay_info['prepayid'], 'nonceStr':app_prepay_info['noncestr'],'sign':app_prepay_info['paySign'], 'outTradeNo':outTradeNo, 'curTime':curTime.strftime("%Y-%m-%d %H:%M:%S"), 'timeStamp':app_prepay_info['timestamp'], 'sub_appid':resultDict['sub_appid'], 'app_prepay_info':resultDict['app_prepay_info']}

    print "[try order succeed] data", data
    print "[try order succeed] account[%s] outTradeNo[%s]."%(account, outTradeNo)
    return {'code':0, 'data':data}

@hall_app.post('/onWeChatPay4TX')
@web_util.allow_cross_request
def do_onWeChatPay4TX(redis, session):
    """
    发起微信支付接口
    """
    curTime = datetime.now()
    try:
        orderSwitch = int(redis.get(ORDER2WEIXIN_SWITCH))
    except:
        orderSwitch = 0

    if not orderSwitch:
        return {'code':-1, 'msg':'暂未开放'}

    sid = request.forms.get('sid','').strip()
    goodsId   = request.forms.get('id','').strip()
    sid       = request.forms.get('sid','').strip()

    ip = request.remote_addr

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}

    userTable = getUserByAccount(redis, account)
    group_id  = redis.hget(userTable,'parentAg')

    # goodsId = redis.get(GOODS_NAME2NUM%(goodsName))
    goodsTable = GOODS_TABLE%(goodsId)
    cards,goodsName,present_card= redis.hmget(goodsTable,('cards','name','present_cards'))

    rType, price = redis.hmget(goodsTable, 'type', 'price')
    rType = int(rType) if rType else 0
    if rType == 2:
        goodsPrice = float(price)
    else:
        #判断金币价格
        goodsPrice = getGoodsMoney(redis, group_id, cards)

    if not redis.exists(goodsTable):
        print '[try goods][error] goods[%s] is not found.'%(goodsName)
        return {'code':-1, 'msg':'goods not found'}


    log_debug('[try goods] player cards[%s] goodsPrice[%s].'%(cards,goodsPrice))

    goodsId2OrderId = GOODS_NUM%(goodsId)
    orderIndex = redis.incr(goodsId2OrderId)
    if orderIndex >= 10000000000:
        redis.set(goodsId2OrderId, 0)
        orderIndex = redis.incr(goodsId2OrderId)
    outTradeNo = getOutTradeNo(goodsId, orderIndex)

    # data = (player, goodsBody, totalPrice, outTradeNo, goodsCount, goodsId, goodsName, goodsCards)
    # order2weixin(data) *data
    urlRes = urlparse(request.url)
    serverIp = urlRes.netloc.split(':')[0]

    nonceStr = getOrderNonceStr4TX()
    signDict = {
        'appid'             :       APPID,
        'mch_id'            :       MCH_ID_TX,
        'nonce_str'         :       nonceStr,
        'body'              :       goodsName,
        'out_trade_no'      :       outTradeNo,
        'total_fee'         :       int(float(goodsPrice) * 100),        
        'spbill_create_ip'  :       ip,
        'notify_url'        :       NOTIFY_URL%('lj2.qianguisy.com'),
        'trade_type'        :       TRADE_TYPE
    }

    #print payment params
    print '[%s][onWechatPay][info] payParams[%s]'%(curTime,signDict)

    # signList = packSignDict2List(signDict)
    # sign = getSign4TX(signList)
    sign = gen_sign4TX(signDict)

    orderStr = packSignDict2XML(signDict, sign)
    url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    resultDict = getXMLMessage(url, orderStr)
    print 'wxPay url[%s] data[%s] sign[%s] signDict[%s]'%(url, orderStr, sign, signDict)
    print 'resultDict:', resultDict

    if not resultDict:
        print '[%s][onWechatPay][error] resultDict[%s]'%(curTime,resultDict)
        return {'code':-1, 'msg':'微信支付失败'}
    if resultDict['return_code'] != 'SUCCESS':
        try:
            print '[%s][onWechatPay][error] resultDict[%s]'%(curTime,resultDict['return_msg'])
        except:
            pass
        return {'code':-1, 'msg':'微信支付未开启'}

    prepayID = resultDict['prepay_id']
    package = 'Sign=WXPay'
    timeStamp = int(time.time())
    # signList = [
        # 'appid=%s'%(APPID),
        # 'partnerid=%s'%(MCH_ID_TX),
        # 'prepayid=%s'%(prepayID),
        # 'package=%s'%(package),
        # 'noncestr=%s'%(nonceStr),
        # 'timeStamp=%s'%(timeStamp),
    # ]
    signList = {'appid':APPID, 'partnerid':MCH_ID_TX, 'prepayid':prepayID, 'package':package, 'noncestr':nonceStr, 'timeStamp':timeStamp}
    sign = gen_sign4TX(signList)
    sign = '1'

    pipe = redis.pipeline()
    # pipe.set(PENDING4ACCOUNT%(player.account, totalPrice, goodsBody), outTradeNo)
    orderTable = ORDER_TABLE%(outTradeNo)
    pipe.hmset(orderTable,
        {
            'time'         :       timeStamp,
            'sign'         :       sign,
            'nonceStr'     :       nonceStr,
            'prepayID'     :       prepayID,
            'name'         :       goodsName,
            'body'         :       "123",
            'money'        :       int(float(goodsPrice) * 100),
            'startTime'    :       timeStamp,
            'account'      :       account,
            'num'          :       goodsId,
            'type'         :       'pending',
            'roomCards'    :       cards,
            'presentCards' :       present_card
        }
    )
    pipe.sadd(PENDING_ORDER, outTradeNo)
    pipe.lpush(ORDER_NUM_LIST, outTradeNo)
    pipe.sadd(PLAYER_ORDER%(account), outTradeNo)

    pipe.lpush(DAY_ORDER%(curTime.strftime("%Y-%m-%d")), outTradeNo)
    pipe.lpush(DAY_PENDING_ORDER%(curTime.strftime("%Y-%m-%d")), outTradeNo)
    pipe.expire(orderTable, 1 * 60 * 60)
    pipe.execute()

    #发送成功信息
    app_prepay_info = {'partnerid':MCH_ID_TX, 'prepayid':prepayID, 'noncestr':nonceStr, 'paySign':sign, 'timestamp':str(timeStamp), 'appid':APPID, 'package':'Sign=WXPay', }
    data = {'partnerId':str(MCH_ID_TX),'prepayID':str(prepayID), 'nonceStr':nonceStr,'sign':sign, 'outTradeNo':outTradeNo, 'curTime':curTime.strftime("%Y-%m-%d %H:%M:%S"), 'timeStamp':str(timeStamp), 'sub_appid':APPID, 'app_prepay_info':app_prepay_info}

    print "[try order succeed] data", data
    print "[try order succeed] account[%s] outTradeNo[%s]."%(account, outTradeNo)
    return {'code':0, 'data':data}

@hall_app.post('/checkOrder')
def do_checkOrder(redis, session):
    """
    检查微信支付是否成功接口
    """
    curTime = datetime.now()
    try:
        orderSwitch = int(redis.get(ORDER2WEIXIN_SWITCH))
    except:
        orderSwitch = 0

    if not orderSwitch:
        return {'code':-1, 'msg':'暂未开放'}

    outTradeNo = request.forms.get('outTradeNo','').strip()
    sid = request.forms.get('sid','').strip()

    SessionTable = FORMAT_USER_HALL_SESSION%(sid)
    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}
    account = redis.hget(SessionTable, 'account')
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}

    if not outTradeNo:
        return {'code':-1, 'msg':'outTradeNo不存在'}

    orderTable = ORDER_TABLE%(outTradeNo)
    if not redis.exists(SUCCEED_ORDER) or not redis.sismember(SUCCEED_ORDER, orderTable):
        return {'code':-9}

    if not orderTable:
        return {'code':-1, 'msg':'orderTable不存在'}

    roomCards = redis.hget(orderTable,('roomCards'))
    checkNum = redis.hincrby(orderTable, 'CheckNum', 1)

    groupId = redis.hget(userTable, 'parentAg')
    redis.hset(orderTable,'groupId',groupId)
    id = userTable.split(':')[1]

    roomCard = redis.get(USER4AGENT_CARD%(groupId, id))
    return {'code':0,'roomCard':roomCard}


@hall_app.get('/debugGetSetting')
@web_util.allow_cross_request
@retry_insert_number()
def do_getDebugOption(redis,session):
    """
    调试时获取游戏配置参数
    """
    curTime = datetime.now()
    gameId  = request.GET.get('gameId','').strip()

    if not gameId:
        return {'code':-1,'msg':'gameId is Empty!'}

    gameDatas = []
    gameId = int(gameId)
    gameTable = GAME_TABLE%(gameId)
    gameName,relationOpts,relationAndOpts = redis.hmget(gameTable,('name','dependSetting','dependAndSetting'))
    optionType = 1
    ruleLists = []
    roomCardsDatas = []
    for data in redis.lrange(USE_ROOM_CARDS_RULE%(gameId), 0, -1):
        datas = data.split(':')
        name, cards = datas[0], datas[1]
        roomCardsDatas.append({'name':name, 'cards':int(cards)})
    rows = 0
    for ruleNum in redis.lrange(GAME2RULE%(gameId), 0, -1):
        ruleTile, ruleType, rule, message,depend= redis.hmget(GAME2RULE_DATA%(gameId, ruleNum), ('title', 'type', 'rule', 'message','depend'))
        try:
            message = message.split(',')
        except:
            message = []
        ruleDataList = rule.split(',')
        ruleData = {'type':int(ruleType), 'title':ruleTile, 'list':ruleDataList,'Dependencies':[], 'message':message,'rows':rows}
        if redis.hexists(GAME2RULE_DATA%(gameId, ruleNum), 'row'):
            ruleData['row'] = redis.hget(GAME2RULE_DATA%(gameId, ruleNum), 'row')
        if depend:
            dependsDatas = redis.hget(GAME2RULE_DATA%(gameId, ruleNum), 'depend').split(';')
            for depend in dependsDatas:
                if depend == '0':
                    ruleData['Dependencies'].append({'type':3,'list':[]})
                else:
                    subInfo = depend.split('|')
                    ruleData['Dependencies'].append({'type':int(subInfo[0]),'list':subInfo[1].split(',')})
        rows+=1
        ruleLists.append(ruleData)
    if relationOpts:
        relationOpts = eval(relationOpts)
    else:
        relationOpts = []

    if relationAndOpts:
        relationAndOpts = eval(relationAndOpts)
    else:
        relationAndOpts = []

    gameDatas.append({'name':gameName, 'relationOptsAnd':relationAndOpts,'relationOptsOr':relationOpts,'optionType':optionType, 'gameId':gameId, 'optionsData':ruleLists, 'cardUseDatas':roomCardsDatas})

    # print '[getRoomSetting][info] gameId[%s] gameRule[%s]'%(gameId,gameDatas)

    return {'code':0,'setting':gameDatas}

# @hall_app.get('/testAddRoomCard')
# def testRoomCard(redis,session):
#     ag = '257510'
#     defaultCard = getDefaultRoomCard(redis,ag)
#     print defaultCard

@hall_app.post('/mailRefresh')
@web_util.allow_cross_request
@retry_insert_number()
def do_mailRefresh(redis,session):
    """
    邮件轮询接口
    """
    curTime = datetime.now()
    ip = request.remote_addr
    sid = request.forms.get('sid','').strip()    
    print 'do_mailRefresh'
    #return {'code':0,'mailList':[],'unReadNums':0}
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}

    if not redis.exists(SessionTable):
        return {'code':-3, 'msg':'sid 超时'}

    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code':-5,'msg':'该用户不存在'}

    userId = userTable.split(':')[1]
    userMailList = []
    unReadMailList = []
    userMailTable = FORMAT_USER_MESSAGE_LIST%(userId)
    mailIds = redis.lrange(userMailTable,0,-1)
    for mailId in mailIds:
        mailTable = FORMAT_GAMEHALL_NOTIC_TABLE%(mailId)
        noticeReads = FORMAT_MSG_READ_SET%(mailId)
        readList = redis.smembers(noticeReads)
        mailInfo = redis.hgetall(mailTable)
        if userId in readList:
            mailInfo['read'] = '1'
            userMailList.append(mailInfo)
        else:
            mailInfo['read'] = '0'
            unReadMailList.append(mailInfo)

        # log_debug('[mailRefresh] mailId[%s] mailInfo[%s] readList[%s]'%(mailId,mailInfo,readList))

    #合并消息
    userMailList = unReadMailList + userMailList

    return {'code':0,'mailList':userMailList,'unReadNums':len(unReadMailList)}


@hall_app.get('/invite')
@retry_insert_number()
def getInvitePage(redis,session):
    """
    邀请页面链接
    """
    ip = request.remote_addr
    rid = request.GET.get('rid','').strip()

    HALL2VERS = getHotSettingAll(redis)

    log_debug('[HALL][url:/invite][info] requestIp[%s] rid[%s] versionInfo[%s]'%(ip,rid,HALL2VERS))

    links = {
            'scheme_android'        :       'dsmj://com.dsmj/invite?rid=%s'%(rid),
            'scheme_ios'            :       'com.DSYL://invite?rid=%s'%(rid),
            'download_ios'          :        HALL2VERS['IPAURL'],
            'download_android'      :       'http://a.app.qq.com/o/simple.jsp?pkgname=com.dsmj'
    }

    info = {
        'entry_title'           :           '东胜麻将',
        'scheme_ios'            :           links['scheme_ios'],
        'scheme_android'        :           links['scheme_android'],
        'ios_download'          :           links['download_android'],
        'android_download'      :           links['download_android'],
        'btn_open_res'          :           '/assest/default/image/invite/dakai.png',
        'btn_down_res'          :           '/assest/default/image/invite/dlbtn.png',
        'invite_bg_res'         :           '/assest/default/image/invite/bg1.jpg',
        'ifr_src'               :           '',
        'timeout'               :           1000,
    }

    response.add_header("Expires", 0);
    response.add_header( "Cache-Control", "no-cache" );
    response.add_header( "Cache-Control", "no-store" );
    response.add_header( "Cache-Control", "must-revalidate" );
    #是否限制IP
    return template('invite',info=info)

@hall_app.get('/invite2')
@retry_insert_number()
def getInvitePage(redis,session):
    """
    邀请页面链接
    """
    ip = request.remote_addr
    rid = request.GET.get('rid','').strip()

    HALL2VERS = getHotSettingAll(redis)

    log_debug('[HALL][url:/invite][info] requestIp[%s] rid[%s] versionInfo[%s]'%(ip,rid,HALL2VERS))

    links = {
            'scheme_android'        :       'dsmj://com.dsmj/invite?rid=%s'%(rid),
            'scheme_ios'            :       'com.DSYL://invite?rid=%s'%(rid),
            'download_ios'          :        HALL2VERS['IPAURL'],
            'download_android'      :       'https://a.app.qq.com/o/simple.jsp?pkgname=com.dsmj',
            'web_href'              :       'http://testwxlogin.dongshenggame.cn/lobby'
    }

    info = {
        'entry_title'           :           '东胜麻将',
        'scheme_ios'            :           links['scheme_ios'],
        'scheme_android'        :           links['scheme_android'],
        'ios_download'          :           links['download_android'],
        'android_download'      :           links['download_android'],
        'web_href'              :           links['web_href'],
        'ifr_src'               :           '',
        'timeout'               :           1000,
    }

    response.add_header("Expires", 0);
    response.add_header( "Cache-Control", "no-cache" );
    response.add_header( "Cache-Control", "no-store" );
    response.add_header( "Cache-Control", "must-revalidate" );
    #是否限制IP
    return template('invite2',info=info)

@hall_app.get('/inviteEx')
@retry_insert_number()
def getInviteExPage(redis,session):
    ip = request.remote_addr
    downloadUrl = request.GET.get('downloadUrl','').strip()

    scheme = request.GET.get('scheme','').strip()
    info = {
        'entry_title'           :           '东胜麻将',
        'downloadUrl'           :           downloadUrl,
        'scheme'                :           scheme
    }

    #是否限制IP
    return template('inviteEx',info=info)

"""
安卓下载接口
"""
@hall_app.get('/getApk')
def downloadAPK(redis):
    apkName = 'sxmj.apk'
    downloadApkUrl = '/download/'+apkName

    return redirect(downloadApkUrl)

@hall_app.get('/getWXConfig')
@web_util.allow_cross_request
def do_getWXConfig(redis,session):
    """
    获得微信配置，公众号相关
    需要传入参数：sid, url(页面地址)
    返回值：timestamp，nonceStr，signature, url
    """
    sid = request.GET.get('sid','').strip()
    urlStr = request.GET.get('url','').strip()
    print '[try getWXConfig]sid[%s] url[%s]'%(sid, urlStr)

    SessionTable, account, uid, verfiySid = getInfoBySid(redis,sid)
    if verfiySid and sid != verfiySid:
        return {'code':-4,'msg':'账号已在其他地方登录', 'osid':sid}
    if not redis.exists(SessionTable):
        return {'code':-3,'msg':'sid 超时'}

    jsapi_ticket, errMsg = getJsapiTicket(redis, account)
    if not jsapi_ticket:
        return {'code':-1, 'msg':'获得jsapi_ticket错误:%s'%(errMsg)}
    nonceStr = getOrderNonceStr()
    timeStamp = int(time.time())

    signDict = {
        'noncestr'          :       nonceStr,
        'jsapi_ticket'      :       jsapi_ticket,
        'timestamp'         :       timeStamp,
        'url'               :       urlStr,
    }
    signature = gen_sign4WXConfig(signDict)
    return {'code':0, 'signature':signature, 'noncestr':nonceStr, 'timestamp':timeStamp, 'url':urlStr}

@hall_app.get('/getWXConfig2')
@web_util.allow_cross_request
def do_getWXConfig2(redis,session):
    """
    获得微信配置，公众号相关
    需要传入参数：sid, url(页面地址)
    返回值：timestamp，nonceStr，signature, url
    """
    urlStr = request.GET.get('url','').strip()

    jsapi_ticket, errMsg = getJsapiTicket(redis,account='')
    if not jsapi_ticket:
        return {'code':-1, 'msg':'获得jsapi_ticket错误:%s'%(errMsg)}
    nonceStr = getOrderNonceStr()
    timeStamp = int(time.time())

    signDict = {
        'noncestr'          :       nonceStr,
        'jsapi_ticket'      :       jsapi_ticket,
        'timestamp'         :       timeStamp,
        'url'               :       urlStr,
    }
    signature = gen_sign4WXConfig(signDict)
    return {'code':0, 'signature':signature, 'noncestr':nonceStr, 'timestamp':timeStamp, 'url':urlStr}

@hall_app.post('/bindGroup')
@web_util.allow_cross_request
def do_bindGroup(redis,session):
    """
    将微信unionID和公会ID绑定
    需要传入参数：unionId, groupId（公会ID）, sid
    返回值：code, msg
    """
    #允许跨域
    ip = request.remote_addr
    code = request.forms.get('code','').strip()
    groupId = request.forms.get('groupId','').strip()

    log_debug('[try bindGroup] code[%s] groupId[%s] ip[%s]'%(code,groupId,ip))
    #sid校验
    if not code:
        return {'code':-1, 'msg':'code错误!'}
    if not groupId:
        return {'code':-2,'msg':'groupId错误!'}

    reAccount,rePasswd = onReg(redis,code,'',1,ip)
    if reAccount:
        realAccount = reAccount
        #读取昵称和group_id
        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(realAccount)
        userTable = redis.get(account2user_table)
        id = userTable.split(':')[1]
        #绑定
        reids.hset(userTable,'parentAg',groupId)
    else:
        return {'code':-3,'msg':'游戏授权失败 code[%s]'%(code)}

    return {'code':0}

@hall_app.post('/getHallBroad')
@web_util.allow_cross_request
def get_hall_broad(redis,session):
    """
    获取大厅播放广播
    级别优先级: 全服维护广播>全服循环广播>地区维护广播>地区循环广播
                先播放优先级高的一条
    """
    sid = request.POST.get('sid','').strip()
    log_debug('[try get_hall_broad] sid[%s] '%(sid))

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/refresh/',SessionTable,account,sid,verfiySid)
    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    group_id = redis.hget(user_table,'parentAg')
    topAgId = getTopAgentId(redis,group_id)
    if not group_id:
        return {'code':-5,'msg':'该用户已被移除公会'}

    broad_info = getHallBroadInfo(redis,topAgId,HALL_BRO_CONTAIN_ALL_LIST,'HALL')
    if not broad_info:
        return {'code':0,'broadcasts':[],'requestPerSec':10}

    return {'code':0,'broadcasts':broad_info,'requestPerSec':10}

@hall_app.post('/getwebroomid')
@web_util.allow_cross_request
def do_RoomId(redis,session):
    uid = request.forms.get('uid', '').strip()
    ##########新增###############################
    wait_room = WAIT_JOIN_GAME_ROOMID_PLAYERS%uid
    RoomId = redis.get(wait_room)
    if not RoomId:
        RoomId = ''
    else:
        redis.set(wait_room, '')
    ##########新增###############################
    return  {'code':0,'roomid':RoomId}


@hall_app.post('/getStoreList')
@web_util.allow_cross_request
@retry_insert_number()
def getStoreList(redis, session):
    """
        获取商城列表
    """
    print 'getStoreList'
    sid = request.forms.get('sid','').strip()
    _type = request.forms.get('type','').strip()

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    try:
        print '[on refresh]account[%s] sid[%s]'%(account, sid)
    except Exception as e:
        print 'print error File', e
    if verfiySid and sid != verfiySid:
        return {'code': -4,'msg': '账号已在其他地方登录', 'osid': sid}
    if not redis.exists(SessionTable):
        return {'code': -3, 'msg': 'sid 超时'}

    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code': -5, 'msg': '该用户不存在'}
    groupId = redis.hmget(userTable, 'parentAg')
    if not groupId:
        return {'code': -7, 'msg': '您已被移出公会，请重新加入公会'}

    if _type == '0':
        goodsInfo = get_dia_goods_list(redis, groupId)
    else:
        goodsInfo = getHallGoodsList(redis, _type)

    return {'code': 0, 'data': goodsInfo}

@hall_app.post('/getRanking')
@web_util.allow_cross_request
@retry_insert_number()
def getRanking(redis, session):
    """
        获取商城列表
    """
    print 'getStoreList'
    sid = request.forms.get('sid','').strip()
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    try:
        print '[on refresh]account[%s] sid[%s]'%(account, sid)
    except Exception as e:
        print 'print error File', e
    if verfiySid and sid != verfiySid:
        return {'code': -4,'msg': '账号已在其他地方登录', 'osid': sid}
    if not redis.exists(SessionTable):
        return {'code': -3, 'msg': 'sid 超时'}

    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code': -5, 'msg': '该用户不存在'}
    month_time = time.strftime("%Y-%m", time.localtime())
    lastMonth=getlastMonth()
    MONTHLY_RANKINGFINAL = "finalrank:Mon:%s:hesh"
    finalkey = MONTHLY_RANKINGFINAL % month_time
    thisMonth = redis.lrange(finalkey, 0, -1)
    lastkey = MONTHLY_RANKINGFINAL % lastMonth
    lastMonth = redis.lrange(lastkey, 0, -1)
    listthisMonth=[]
    for each in thisMonth:
        data=each.decode("string_escape")
        data = data.replace('\'', '\"')
        jsondata = json.loads(data)
        listthisMonth.append(jsondata)
    listlastMonth = []
    for each in lastMonth:
        data=each.decode("string_escape")
        data = data.replace('\'', '\"')
        jsondata = json.loads(data)
        listthisMonth.append(jsondata)
    return {'code': 0, 'thismonth': listthisMonth,'lastMonth': listlastMonth}
