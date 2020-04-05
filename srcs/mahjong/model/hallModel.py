# -*- coding:utf-8 -*-
# !/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    大厅Model
"""

from web_db_define import *
from datetime import datetime, timedelta
from wechat.wechatData import *
from admin import access_module
from config.config import *
from datetime import datetime
import mahjong_pb2
import poker_pb2
import replay4proto_pb2
from mahjong.model.agentModel import getTopAgentId
from common import log_util
import json
import time
import requests


# import socket


# def sendRemoveIpaddr(address):
#     host='183.60.133.234'
#     port = 9797
#     socket.setdefaulttimeout(50)
#     sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#     try:
#             sock.connect((host,port))
#             address = address
#             sock.sendall(address)
#             print address
#             sock.close()
#             print 'done'
#     except:
#             print 'error'


def onReg(redis, account, passwd, type, ip):  # 传入参数：账号，密码，类型；返回参数：成功返回账号和密码，失败返回None, None

    curTime = datetime.now()

    # print
    log_util.debug('[try onReg] account[%s] passwd[%s] type[%s]' % (account, passwd, type))

    if type == 1:  # 微信code登录
        tokenMessage = checkWeixinCode(account)
        if tokenMessage:
            password = account
            accessToken = tokenMessage["access_token"]
            refreshToken = tokenMessage["refresh_token"]
            openID = tokenMessage["openid"]
            userData = getWeixinData(openID, accessToken)
            unionid = userData['unionid']
            if redis.exists(WEIXIN2ACCOUNT % (unionid)):
                realAccount = redis.get(WEIXIN2ACCOUNT % (unionid))
                account2user_table = FORMAT_ACCOUNT2USER_TABLE % (realAccount)
                table = redis.get(account2user_table)
                redis.hmset(table, {'accessToken': accessToken, 'refreshToken': refreshToken,
                                    'password': md5.new(password).hexdigest()})
            else:
                setOpenid2account(openID, accessToken, refreshToken, ip, redis, account)
            redis.srem(FORMAT_LOGIN_POOL_SET, account)
            return unionid, password
        redis.srem(FORMAT_LOGIN_POOL_SET, account)
    elif type == 2:
        if redis.exists(WEIXIN2ACCOUNT % (account)):
            realAccount = redis.get(WEIXIN2ACCOUNT % (account))
            account2user_table = FORMAT_ACCOUNT2USER_TABLE % (realAccount)
            table = redis.get(account2user_table)
            truePassword, openID, accessToken = redis.hmget(table, ('password', 'openid', 'accessToken'))
            log_util.debug(
                'type 2:passwd[%s] md5[%s] truePassword[%s]' % (md5.new(passwd).hexdigest(), passwd, truePassword))
            if truePassword == md5.new(passwd).hexdigest():
                userData = getWeixinData(openID, accessToken)
                log_util.debug('onReg for type 2, userData:%s' % (userData))
                if userData:
                    redis.hmset(table,
                                {
                                    'nickname': userData['nickname'],
                                    'sex': userData['sex'],
                                    'headImgUrl': userData['headimgurl']
                                }
                                )
                redis.srem(FORMAT_LOGIN_POOL_SET, account)
                return account, passwd
        redis.srem(FORMAT_LOGIN_POOL_SET, account)
    elif type == 3:  # 微信WEBcode登录
        tokenMessage = checkWeixinCodeWEB(account)
        if tokenMessage:
            password = account
            accessToken = tokenMessage["access_token"]
            refreshToken = tokenMessage["refresh_token"]
            openID = tokenMessage["openid"]
            userData = getWeixinData(openID, accessToken)
            unionid = userData['unionid']
            if redis.exists(WEIXIN2ACCOUNT % (unionid)):
                realAccount = redis.get(WEIXIN2ACCOUNT % (unionid))
                account2user_table = FORMAT_ACCOUNT2USER_TABLE % (realAccount)
                table = redis.get(account2user_table)
                redis.hmset(table, {'accessToken': accessToken, 'refreshToken': refreshToken,
                                    'password': md5.new(password).hexdigest()})
            else:
                setOpenid2account(openID, accessToken, refreshToken, ip, redis, account)
            redis.srem(FORMAT_LOGIN_POOL_SET, account)
            return unionid, password
        redis.srem(FORMAT_LOGIN_POOL_SET, account)
    elif type == 4:  # 微信WEBcode登录
        tokenMessage = checkWeixinCodeWEB(account)
        if tokenMessage:
            password = account
            accessToken = tokenMessage["access_token"]
            refreshToken = tokenMessage["refresh_token"]
            openID = tokenMessage["openid"]
            userData = getWeixinData(openID, accessToken)
            unionid = userData['unionid']
            if redis.exists(WEIXIN2ACCOUNT % (unionid)):
                realAccount = redis.get(WEIXIN2ACCOUNT % (unionid))
                account2user_table = FORMAT_ACCOUNT2USER_TABLE % (realAccount)
                table = redis.get(account2user_table)
                redis.hmset(table, {'accessToken': accessToken, 'refreshToken': refreshToken,
                                    'password': md5.new(password).hexdigest()})
            else:
                setOpenid2account(openID, accessToken, refreshToken, ip, redis, account)
            redis.srem(FORMAT_LOGIN_POOL_SET, account)
            return unionid, password
        redis.srem(FORMAT_LOGIN_POOL_SET, account)
    elif type == 0:
        account2user_table = FORMAT_ACCOUNT2USER_TABLE % (account)
        if redis.exists(account2user_table):
            table = redis.get(account2user_table)
            truePassword = redis.hget(table, 'password')
            if truePassword == md5.new(passwd).hexdigest():
                return account, passwd
    redis.srem(FORMAT_LOGIN_POOL_SET, account)
    return None, None


def onRegFish(redis, account, passwd, type, ip):  # 传入参数：账号，密码，类型；返回参数：成功返回账号和密码，失败返回None, None

    curTime = datetime.now()

    # print
    log_util.debug('[try onReg] account[%s] passwd[%s] type[%s]' % (account, passwd, type))

    if type == 1:  # 微信code登录
        tokenMessage = checkWeixinCode4fish(account)
        if tokenMessage:
            password = account
            accessToken = tokenMessage["access_token"]
            refreshToken = tokenMessage["refresh_token"]
            openID = tokenMessage["openid"]
            userData = getWeixinData(openID, accessToken)
            unionid = userData['unionid']
            if redis.exists(WEIXIN2ACCOUNT4FISH % (unionid)):  # or redis.exists(WEIXIN2ACCOUNT%(unionid)):
                realAccount = redis.get(WEIXIN2ACCOUNT4FISH % (unionid))
                if not realAccount:
                    realAccount = redis.get(WEIXIN2ACCOUNT % (unionid))
                account2user_table = FORMAT_ACCOUNT2USER_TABLE % (realAccount)
                table = redis.get(account2user_table)
                redis.hmset(table, {'accessToken': accessToken, 'refreshToken': refreshToken,
                                    'password': md5.new(password).hexdigest()})
            else:
                setOpenid2account4fish(openID, accessToken, refreshToken, ip, redis, account)
            redis.srem(FORMAT_LOGIN_POOL_SET, account)
            return unionid, password
        redis.srem(FORMAT_LOGIN_POOL_SET, account)
    elif type == 2:
        if redis.exists(WEIXIN2ACCOUNT4FISH % (account)):  # or redis.exists(WEIXIN2ACCOUNT%(account)):
            realAccount = redis.get(WEIXIN2ACCOUNT4FISH % (account))
            if not realAccount:
                realAccount = redis.get(WEIXIN2ACCOUNT % (account))
            account2user_table = FORMAT_ACCOUNT2USER_TABLE % (realAccount)
            table = redis.get(account2user_table)
            truePassword, openID, accessToken = redis.hmget(table, ('password', 'openid', 'accessToken'))
            log_util.debug(
                'type 2:passwd[%s] md5[%s] truePassword[%s]' % (md5.new(passwd).hexdigest(), passwd, truePassword))
            if truePassword == md5.new(passwd).hexdigest():
                userData = getWeixinData(openID, accessToken)
                log_util.debug('onReg for type 2, userData:%s' % (userData))
                if userData:
                    redis.hmset(table,
                                {
                                    'nickname': userData['nickname'],
                                    'sex': userData['sex'],
                                    'headImgUrl': userData['headimgurl']
                                }
                                )
                redis.srem(FORMAT_LOGIN_POOL_SET, account)
                return account, passwd
        redis.srem(FORMAT_LOGIN_POOL_SET, account)
    elif type == 3:  # 微信WEBcode登录
        tokenMessage = checkWeixinCodeWEB(account)
        if tokenMessage:
            password = account
            accessToken = tokenMessage["access_token"]
            refreshToken = tokenMessage["refresh_token"]
            openID = tokenMessage["openid"]
            userData = getWeixinData(openID, accessToken)
            unionid = userData['unionid']
            if redis.exists(WEIXIN2ACCOUNT4FISH % (unionid)):  # or redis.exists(WEIXIN2ACCOUNT%(unionid)):
                realAccount = redis.get(WEIXIN2ACCOUNT4FISH % (unionid))
                if not realAccount:
                    realAccount = redis.get(WEIXIN2ACCOUNT % (unionid))
                account2user_table = FORMAT_ACCOUNT2USER_TABLE % (realAccount)
                table = redis.get(account2user_table)
                redis.hmset(table, {'accessToken': accessToken, 'refreshToken': refreshToken,
                                    'password': md5.new(password).hexdigest()})
            else:
                setOpenid2account4fish(openID, accessToken, refreshToken, ip, redis, account)
            redis.srem(FORMAT_LOGIN_POOL_SET, account)
            return unionid, password
        redis.srem(FORMAT_LOGIN_POOL_SET, account)
    elif type == 4:  # 微信WEBcode登录
        tokenMessage = checkWeixinCodeWEB(account)
        if tokenMessage:
            password = account
            accessToken = tokenMessage["access_token"]
            refreshToken = tokenMessage["refresh_token"]
            openID = tokenMessage["openid"]
            userData = getWeixinData(openID, accessToken)
            unionid = userData['unionid']
            if redis.exists(WEIXIN2ACCOUNT4FISH % (unionid)):  # or redis.exists(WEIXIN2ACCOUNT%(unionid)):
                realAccount = redis.get(WEIXIN2ACCOUNT4FISH % (unionid))
                if not realAccount:
                    realAccount = redis.get(WEIXIN2ACCOUNT % (unionid))
                account2user_table = FORMAT_ACCOUNT2USER_TABLE % (realAccount)
                table = redis.get(account2user_table)
                redis.hmset(table, {'accessToken': accessToken, 'refreshToken': refreshToken,
                                    'password': md5.new(password).hexdigest()})
            else:
                setOpenid2account4fish(openID, accessToken, refreshToken, ip, redis, account)
            redis.srem(FORMAT_LOGIN_POOL_SET, account)
            return unionid, password
        redis.srem(FORMAT_LOGIN_POOL_SET, account)
    elif type == 0:
        account2user_table = FORMAT_ACCOUNT2USER_TABLE % (account)
        if redis.exists(account2user_table):
            table = redis.get(account2user_table)
            truePassword = redis.hget(table, 'password')
            if truePassword == md5.new(passwd).hexdigest():
                return account, passwd
    redis.srem(FORMAT_LOGIN_POOL_SET, account)
    return None, None


def saveHotUpDateSetting(redis, settingInfo, sys="HALL"):
    """
    保存热更新配置
    """
    if sys == 'HALL':
        hot_table = HOTUPDATE_TABLE
    else:
        hot_table = FISH_HOTUPDATE_TABLE

    return redis.hmset(hot_table, settingInfo)


def getHotSettingField(redis, field):
    """
    获取单个配置信息
    """
    return redis.hget(HOTUPDATE_TABLE, field)


def getHotSettingAll(redis):
    return redis.hgetall(HOTUPDATE_TABLE)


def get_fish_hall_setting(redis):
    return redis.hgetall(FISH_HOTUPDATE_TABLE)


def getUserByAccount(redis, account):
    """
    通过account获取玩家数据
    """
    account2user_table = FORMAT_ACCOUNT2USER_TABLE % (account)
    userTable = redis.get(account2user_table)
    return userTable


def do_sessionExpire(redis, session, SessionTable, SESSION_TTL):
    """
    刷新session
    """
    # refresh session
    redis.expire(session['session_key'], 60 * 60)
    redis.expire(SessionTable, 60 * 10)
    session.expire()


def check_session_verfiy(redis, api_name, SessionTable, account, sid, verfiySid):
    '''
    验证session是否合法
    return code,msg
    '''
    log_util.debug('[on refresh] account[%s] sid[%s]' % (account, sid))

    if verfiySid and sid != verfiySid:
        # session['member_account'],session['member_id'] = '',''
        return -4, '账号已在其他地方登录', False

    if not redis.exists(SessionTable):
        return -3, 'sid 超时', False

    user_table = getUserByAccount(redis, account)
    if not redis.exists(user_table):
        return -5, '该用户不存在', False

    return 0, True, user_table


def packPrivaTeData4Game(chair, data, resp, proto):
    privateResp = proto()
    privateResp.ParseFromString(resp.privateData)
    for data in privateResp.data.gameInfo.roomInfo.playerList:
        if int(data.side) == int(chair):
            print 'replay side get,side:%s nickname:%s' % (data.side, data.nickname)
            privateResp.data.gameInfo.selfInfo.side = data.side
            privateResp.data.gameInfo.selfInfo.nickname = data.nickname
            privateResp.data.gameInfo.selfInfo.coin = data.coin
            privateResp.data.gameInfo.selfInfo.ip = data.ip
            privateResp.data.gameInfo.selfInfo.sex = data.sex
            privateResp.data.gameInfo.selfInfo.headImgUrl = data.headImgUrl
            privateResp.data.gameInfo.selfInfo.roomCards = 0
    resp.privateData = privateResp.SerializeToString()
    replayStr = resp.SerializeToString()
    return replayStr


def packPrivaTeData(chair, data):
    resp = replay4proto_pb2.ReplayData()
    resp.ParseFromString(data)
    refreshDataNameProtos = [mahjong_pb2.S_C_RefreshData, poker_pb2.S_C_RefreshData]
    for proto in refreshDataNameProtos:
        try:
            replayStr = packPrivaTeData4Game(chair, data, resp, proto)
            break
        except Exception as e:
            print 'packPrivaTeData error', e
    return replayStr


def getRuleText(rule, gameId, redis):
    ruleList = eval(rule)
    ruleText = '底分: %s\n' % (max(int(ruleList[-1]), 1))
    gameTable = GAME_TABLE % (gameId)

    for data in redis.lrange(USE_ROOM_CARDS_RULE % (gameId), 0, -1):
        datas = data.split(':')
        name, cards = datas[0], datas[1]
        try:
            playCount = int(datas[2])
        except:
            playCount = name
        if int(cards) == ruleList[-2]:
            ruleText += '局数: %s\n' % (playCount)

    num = 0
    for ruleNum in redis.lrange(GAME2RULE % (gameId), 0, -1):
        ruleTile, ruleType, rule = redis.hmget(GAME2RULE_DATA % (gameId, ruleNum), ('title', 'type', 'rule'))
        ruleDataList = rule.split(',')
        if int(ruleType) == 1:
            # print '[on getRuleText]get ruleList[%s] num[%s]'%(ruleList, num)
            try:
                ruleText += '%s: %s\n' % (ruleTile, ruleDataList[int(ruleList[num])])
            except:
                ruleText += '%s: %s\n' % (ruleTile, ruleDataList[int(ruleList[num][0])])
        else:
            text = '%s: ' % (ruleTile)
            textList = []
            for ruleData in ruleList[num]:
                textList.append(ruleDataList[ruleData])
            textData = ','.join(textList)
            text += textData
            ruleText = ruleText + text + '\n'
        num += 1
    ruleText = ruleText.decode('utf-8')
    return ruleText


def tryExitGroup(redis, userTable, account, id, groupId):
    pipe = redis.pipeline()
    key = redis.get(ACCOUNT2WAIT_JOIN_PARTY_TABLE % account)
    # for key in redis.keys(WAIT_JOIN_PARTY_ROOM_PLAYERS%('*', '*', '*')): #在等待匹配娱乐模式的话则离开列表
    if key:
        waitJoinList = redis.lrange(key, 0, -1)
        if account in waitJoinList:
            pipe.lrem(key, account)
    pipe.srem(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE % (groupId), id)  # 上线代理需要获得
    pipe.hmset(userTable, {'parentAg': '', 'isVolntExitGroup': 1, 'lastGroup': groupId})
    # 记录到省级公会的房卡
    topAgId = getTopAgentId(redis, groupId)
    roomcard = redis.get(USER4AGENT_CARD % (groupId, id))
    if not roomcard:
        roomcard = 0
    print '[try exitGroup] topAgId[%s] roomCards[%s]' % (topAgId, roomcard)
    pipe.set(USER4AGENT_CARD % (topAgId, id), int(roomcard))
    pipe.execute()


def getGroupIds(redis, groupId):
    """
    获取所有上级代理ID
    """
    Ids = []
    if redis.exists(AGENT_TABLE % (groupId)):
        parentId = redis.get(AGENT2PARENT % (groupId))
        if parentId:
            if int(parentId) == 1:
                return ['1']
            Ids.extend(getGroupIds(redis, parentId))
        else:
            Ids.append(parentId)

    return Ids


def getBroadcasts(redis, groupId, isNew=''):
    """
    获取广播列表
    """
    bIds = redis.lrange(HALL_BROADCAST_LIST, 0, -1)
    broadInfos = []
    groupIds = getGroupIds(redis, groupId)
    groupIds.append(groupId)
    log_util.debug('[groupIds][%s] bids[%s]' % (groupIds, bIds))
    for bid in bIds:
        if redis.exists(FORMAT_BROADCAST_TABLE % (bid)):
            bInfos = redis.hgetall(FORMAT_BROADCAST_TABLE % (bid))
            if bInfos['ag'] in groupIds:
                broadInfos.append(bInfos)
        else:
            redis.lrem(FORMAT_BROADCAST_LIST_TABLE, '1', bid)

    broadcasts = {'broadcasts': broadInfos}

    if isNew:
        broadcasts['isNew'] = isNew

    return broadcasts


def getHallBroadInfo(redis, group_id, broad_table, broad_belone):
    """
    获取大厅广播列表
    """
    play_set = redis.smembers(HALL_BRO_PLAY_SET)
    broads = redis.lrange(broad_table % (1), 0, -1)
    broad_list = []
    for broad in broads:
        if broad in play_set:
            broadDetail = {}
            broadInfo = redis.hgetall(HALL_BRO_TABLE % (broad))
            broadDetail['content'] = broadInfo['content']
            broadDetail['repeatInterval'] = int(broadInfo['per_sec'])
            broad_list.append(broadDetail)

    broads = redis.lrange(broad_table % (0), 0, -1)
    for broad in broads:
        if broad in play_set:
            broadDetail = {}
            broadInfo = redis.hgetall(HALL_BRO_TABLE % (broad))
            broadDetail['content'] = broadInfo['content']
            broadDetail['repeatInterval'] = int(broadInfo['per_sec'])
            broad_list.append(broadDetail)
            return broad_list

    if broad_belone == 'HALL':
        broads = redis.lrange(HALL_BRO_CONTAIN_AG_LIST % (2, group_id), 0, -1)
        for broad in broads:
            if broad in play_set:
                broadDetail = {}
                broadInfo = redis.hgetall(HALL_BRO_TABLE % (broad))
                broadDetail['content'] = broadInfo['content']
                broadDetail['repeatInterval'] = int(broadInfo['per_sec'])
                broad_list.append(broadDetail)
                return broad_list

        broads = redis.lrange(HALL_BRO_CONTAIN_AG_LIST % (3, group_id), 0, -1)
        for broad in broads:
            if broad in play_set:
                broadDetail = {}
                broadInfo = redis.hgetall(HALL_BRO_TABLE % (broad))
                broadDetail['content'] = broadInfo['content']
                broadDetail['repeatInterval'] = int(broadInfo['per_sec'])
                broad_list.append(broadDetail)
                return broad_list

    return broad_list


def extendSession(redis, session, SessionTable):
    """
    延长session有效时间
    """
    redis.expire(session['session_key'], 60 * 60)
    redis.expire(SessionTable, 60 * 40)


def postChatRoomScoreData(redis, session, groupId, playGame, initiator, uid):
    """
    获取亲友圈房间战绩详情
    :param playGame: game:%s:startTime:%s:playGame:hash
    :return: {'game': gameName, 'roomId': roomId, 'count': count, 'gameTime': gameTime,  'userList': userList}
    """
    if not redis.exists(playGame):
        return {"code": 1, "msg": "该战绩不存在"}

    curTime = datetime.now().strftime('%Y-%m-%d')
    _, roomId, _, startTime, _, _ = playGame.split(':')
    gameRoom_key = 'game:%s:startTime:%s:game2room:list' % (roomId, startTime)
    gameid, players, descs, scores, roomSettings, ownner = redis.hmget(playGame, ('gameid',
                                                                                  'player', 'descs', 'score',
                                                                                  'roomSettings', 'ownner'))
    gameName = redis.hget('games:id:%s' % gameid, 'name')
    if redis.exists(gameRoom_key):
        count = str(redis.llen(gameRoom_key))
        endTime = redis.hget(redis.lindex(gameRoom_key, 0), 'endTime')
    else:
        count = '0'
        endTime = startTime
    startTime = time.strftime('%m/%d %H:%M', time.localtime(float(startTime) / 1000))
    endTime = time.strftime('%H:%M', time.localtime(float(endTime) / 1000))
    gameTime = '%s-%s' % (startTime, endTime)
    nicknames = []
    headImgUrls = []
    accounts = []
    ids = []
    players = players.split(':')
    scores = scores.split(':')
    for player in players:
        account = player.split(',')[1]
        account2user_table = "users:account:%s" % (account)
        table = redis.get(account2user_table)
        id = table.split(':')[-1]
        nickname, headImgUrl = redis.hmget(table, ('nickname', 'headImgUrl'))
        headImgUrls.append(headImgUrl)
        nicknames.append(nickname)
        accounts.append(account)
        ids.append(id)
    userList = []
    for index in xrange(len(nicknames)):
        userList.append(
            {'name': nicknames[index], 'score': int(scores[index]), 'ID': ids[index], 'headImg': headImgUrls[index]})
    if userList:
        h5_post, app_post = redis.hmget('club:to:chatroom:hash', ('h5', 'app'))
        res_msg, app_msg = '分享成功', '分享成功'
        postTime = int(time.time())

        if h5_post:
            params = {'groupID': groupId, 'game': gameName, 'roomID': roomId, 'count': count, 'gameTime': gameTime,
                      'userList': userList}
            data = json.dumps(params)
            url = 'http://183.131.206.155:39706/qunliao/'
            url = 'http://110.42.66.117:39705/qunliao/'
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            h5_chatrooom_Key = 'user:%s:%s:%s:share:h5:hash' % (uid, roomId, postTime)
            h5_share_key = 'club:share:h5:%s:%s:set' % (groupId, curTime)
            try:
                res = requests.post(url=url, data=data, headers=headers, timeout=10)
                res_code = res.status_code
                code = res_code
                if res_code == 200:
                    redis.sadd(h5_share_key, h5_chatrooom_Key)
                    redis.hmset(h5_chatrooom_Key, {'code': code, 'msg': res_msg, 'uid': uid})
                    redis.hmset(h5_chatrooom_Key, params)
                    redis.expire(h5_share_key, 8 * 86400)
                    redis.expire(h5_chatrooom_Key, 8 * 86400)
                else:
                    res_msg = '分享失败1'
            except Exception as err:
                res_msg = '分享失败2'

        if False and app_post:
            params = {'qid': groupId, 'game': gameName, 'roomID': roomId, 'count': count, 'gameTime': gameTime,
                      'userList': userList}
            app_data = json.dumps(params)
            app_url = 'http://app.wjiew.cn/bg99rb01/record/'
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            app_chatrooom_Key = 'user:%s:%s:%s:share:app:hash' % (uid, roomId, postTime)
            app_share_key = 'club:share:app:%s:%s:set' % (groupId, curTime)
            try:
                app_res = requests.post(url=app_url, data=app_data, headers=headers, timeout=10)
                app_code = app_res.status_code
                code = app_code
                app_text = eval(app_res.text)
                if app_code != 200:
                    app_msg = '分享失败3'
                    app_text = {}
                if app_text.has_key('key'):
                    redis.sadd(app_share_key, app_chatrooom_Key)
                    redis.hmset(app_chatrooom_Key, params)
                    redis.hmset(app_chatrooom_Key, {'code': code, 'msg': app_msg, 'uid': uid})
                    redis.expire(app_share_key, 8 * 86400)
                    redis.expire(app_chatrooom_Key, 8 * 86400)
            except Exception as err:

                app_msg = '分享失败4'

        redis.hmset("club:replay:to:chatroom:%s:hash" % roomId, {initiator: postTime})

        if res_msg == '分享成功':
            return {'code': 0, 'msg': '分享成功'}
        else:
            print 'postChatRoomScoreData error %s %s'%(res_msg,app_msg)
            return {'code': 1, 'msg': '分享失败5'}
    else:
        return {"code": 1, "msg": "战绩不存在"}


def joinRoom_to_chatroom(redis, session, club_number, roomId, account, uid):
    """
    获取房间邀请详情
    """

    clubTochatroom_key = "club:replay:to:chatroom:%s:hash" % roomId
    old_postTime = redis.hget(clubTochatroom_key, account)
    new_postTime = time.time()
    if old_postTime != '0' and (new_postTime - float(old_postTime)) < 10:
        return {'code': 1, 'msg': '您的邀请过快'}

    curTime = datetime.now().strftime('%Y-%m-%d')

    room2server_key = 'room2server:%s:hesh' % roomId
    game, personInNumber, personLackNumber, text = redis.hmget(room2server_key,
                                                               ('gameName', 'playerCount', 'maxPlayer', 'ruleText'))
    params = {}
    params['game'] = game
    params['roomID'] = roomId
    params['personInNumber'] = int(personInNumber)
    params['personLackNumber'] = int(personLackNumber) - params['personInNumber']
    if params['personLackNumber'] == 0:  # 游戏人数已满，不再POST数据至H5聊天室
        return
    params['text'] = text
    params['logoText'] = u'钱柜手游'
    params['groupID'] = club_number
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    h5_post, app_post = redis.hmget('club:to:chatroom:hash', ('h5', 'app'))
    res_msg, app_msg = '邀请成功', '邀请成功'
    postTime = int(time.time())
    if h5_post:
        data = json.dumps(params)
        url = 'http://183.131.206.155:39706/share/'
        url = 'http://110.42.66.117:39705/share/'
        h5_chatrooom_Key = 'user:%s:%s:%s:invite:h5:hash' % (uid, roomId, postTime)
        h5_invite_key = 'club:invite:h5:%s:%s:set' % (club_number, curTime)
        try:
            res = requests.post(url=url, data=data, headers=headers, timeout=10)
            res_code = res.status_code
            code = res_code
            if res_code == 200:
                redis.sadd(h5_invite_key, h5_chatrooom_Key)
                redis.hmset(h5_chatrooom_Key, {'code': code, 'msg': res_msg, 'uid': uid})
                redis.hmset(h5_chatrooom_Key, params)
                redis.expire(h5_invite_key, 8 * 86400)
                redis.expire(h5_chatrooom_Key, 8 * 86400)
            else:
                res_msg = '邀请失败'
        except Exception as err:
            res_msg = '邀请失败'

    if False and app_post:
        params['uri'] = 'http://game5h.qianguisy.com/entry1.html?rid=rid:%s' % roomId
        params['qid'] = club_number
        app_data = json.dumps(params)
        app_url = 'http://app.wjiew.cn/bg99rb01/share/'
        app_chatrooom_Key = 'user:%s:%s:%s:invite:app:hash' % (uid, roomId, postTime)
        app_invite_key = 'club:invite:app:%s:%s:set' % (club_number, curTime)
        try:
            app_res = requests.post(url=app_url, data=app_data, headers=headers, timeout=10)
            app_code = app_res.status_code
            code = app_code
            app_text = eval(app_res.text)
            if app_code != 200:
                app_msg = '邀请失败'
                app_text = {}
            if app_text.has_key('key'):
                redis.sadd(app_invite_key, app_chatrooom_Key)
                redis.hmset(app_chatrooom_Key, {'code': code, 'msg': app_msg, 'uid': uid})
                redis.hmset(app_chatrooom_Key, params)
                redis.expire(app_invite_key, 8 * 86400)
                redis.expire(app_chatrooom_Key, 8 * 86400)
        except Exception as err:
            app_msg = '邀请失败'

    redis.hmset(clubTochatroom_key, {account: postTime})

    if res_msg == '邀请成功':
        return {'code': 0, 'msg': '邀请成功'}
    else:
        return {'code': 1, 'msg': '邀请失败'}


def postChatRoomScoreData2(redis, session, groupId, playGame, initiator, uid):
    """
    获取亲友圈房间战绩详情
    :param playGame: game:%s:startTime:%s:playGame:hash
    :return: {'game': gameName, 'roomId': roomId, 'count': count, 'gameTime': gameTime,  'userList': userList}
    """
    if not redis.exists(playGame):
        return {"code": 1, "msg": "该战绩不存在"}

    curTime = datetime.now().strftime('%Y-%m-%d')
    _, roomId, _, startTime, _, _ = playGame.split(':')
    gameRoom_key = 'game:%s:startTime:%s:game2room:list' % (roomId, startTime)
    gameid, players, descs, scores, roomSettings, ownner = redis.hmget(playGame, ('gameid',
                                                                                  'player', 'descs', 'score',
                                                                                  'roomSettings', 'ownner'))
    gameName = redis.hget('games:id:%s' % gameid, 'name')
    if redis.exists(gameRoom_key):
        count = str(redis.llen(gameRoom_key))
        endTime = redis.hget(redis.lindex(gameRoom_key, 0), 'endTime')
    else:
        count = '0'
        endTime = startTime
    startTime = time.strftime('%m/%d %H:%M', time.localtime(float(startTime) / 1000))
    endTime = time.strftime('%H:%M', time.localtime(float(endTime) / 1000))
    gameTime = '%s-%s' % (startTime, endTime)
    nicknames = []
    headImgUrls = []
    accounts = []
    ids = []
    players = players.split(':')
    scores = scores.split(':')
    for player in players:
        account = player.split(',')[1]
        account2user_table = "users:account:%s" % (account)
        table = redis.get(account2user_table)
        id = table.split(':')[-1]
        nickname, headImgUrl = redis.hmget(table, ('nickname', 'headImgUrl'))
        headImgUrls.append(headImgUrl)
        nicknames.append(nickname)
        accounts.append(account)
        ids.append(id)
    userList = []
    for index in xrange(len(nicknames)):
        userList.append(
            {'name': nicknames[index], 'score': int(scores[index]), 'ID': ids[index], 'headImg': headImgUrls[index]})
    if userList:
        res_msg, app_msg = '分享成功', '分享成功'
        postTime = int(time.time())

        if True:
            params = {'groupID': groupId, 'game': gameName, 'roomID': roomId, 'count': count, 'gameTime': gameTime,
                      'userList': userList}
            data = json.dumps(params)
            url = 'http://183.131.206.155:39706/qunliao/'
            url = 'http://110.42.66.117:39706/qunliao/'
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            h5_chatrooom_Key = 'user:%s:%s:%s:share:h5:hash' % (uid, roomId, postTime)
            h5_share_key = 'club:share:h5:%s:%s:set' % (groupId, curTime)
            try:
                # print 'data %s' % data
                res = requests.post(url=url, data=data, headers=headers, timeout=10)
                res_code = res.status_code
                code = res_code
                # print res.text
                if res_code == 200:

                    redis.sadd(h5_share_key, h5_chatrooom_Key)
                    redis.hmset(h5_chatrooom_Key, {'code': code, 'msg': res_msg, 'uid': uid})
                    redis.hmset(h5_chatrooom_Key, params)
                    redis.expire(h5_share_key, 8 * 86400)
                    redis.expire(h5_chatrooom_Key, 8 * 86400)

                else:
                    res_msg = '分享失败6'
            except Exception as err:
                res_msg = '分享失败7'

        if False:
            print 'apppost'
            params = {'qid': groupId, 'game': gameName, 'roomID': roomId, 'count': count, 'gameTime': gameTime,
                      'userList': userList}
            app_data = json.dumps(params)
            print 'apppost'
            app_url = 'http://app.wjiew.cn/bg99rb01/record/'
            # app_url = 'http://183.131.206.155:39706/qunliao/'
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            app_chatrooom_Key = 'user:%s:%s:%s:share:app:hash' % (uid, roomId, postTime)
            app_share_key = 'club:share:app:%s:%s:set' % (groupId, curTime)
            if True:
                app_res = requests.post(url=app_url, data=app_data, headers=headers, timeout=10)
                app_code = app_res.status_code
                code = app_code
                app_text = eval(app_res.text)
                if app_code != 200:
                    app_msg = '分享失败8'
                    app_text = {}
                if app_text.has_key('key'):
                    redis.sadd(app_share_key, app_chatrooom_Key)
                    redis.hmset(app_chatrooom_Key, params)
                    redis.hmset(app_chatrooom_Key, {'code': code, 'msg': app_msg, 'uid': uid})
                    redis.expire(app_share_key, 8 * 86400)
                    redis.expire(app_chatrooom_Key, 8 * 86400)
            # except Exception as err:
            #     app_msg = '分享失败'

        redis.hmset("club:replay:to:chatroom:%s:hash" % roomId, {initiator: postTime})

        if res_msg == '分享成功' and app_msg == '分享成功':
            return {'code': 0, 'msg': '分享成功'}
        else:
            return {'code': 1, 'msg': '分享失败9'}
    else:
        return {"code": 1, "msg": "战绩不存在"}


def getClubRoomBrief(redis, club_number, room_id):
    try:
        datas = []
        ROOM_BIREFT = "room:%s:brief:hesh"
        roomkey = '%s:%s' % (club_number, room_id)
        key = ROOM_BIREFT % roomkey
        data = redis.hgetall(key)
        if data:
            playinfo = {}
            sorceinfo = {}
            for key, value in data.items():
                if len(key) == 1:
                    sorceinfo[key] = value
                elif len(key) == 2:
                    playinfo[key[1:]] = value
            for side, value in playinfo.items():
                nickname, avatar_url = getNameURLbyAccount(redis, value)
                onedata = {'chair': side, 'account': value, 'point': sorceinfo[side], 'nickname': nickname,
                           'headImgUrl': avatar_url}
                datas.append(onedata)
            return datas, data['time'], data.get('gameid', '0')
        else:
            return None, None, None
    except:
        return None, None, None


def checkWinRoom(account, oneRoomdata=[]):
    highestpoint = 0
    for eachdata in oneRoomdata:
        mypoint = int(eachdata.get('point', '0'))
        if mypoint > highestpoint:
            highestpoint = mypoint
    highestlist = []
    for eachdata in oneRoomdata:
        mypoint = int(eachdata.get('point', '0'))
        if mypoint == highestpoint:
            highestlist.append(eachdata.get('account', ''))
    if account in highestlist:
        return True
    return False


def getNameURLbyAccount(redis, account):
    FORMAT_ACCOUNT2USER_TABLE = "users:account:%s"
    account2user_table = FORMAT_ACCOUNT2USER_TABLE % (account)
    userTable = redis.get(account2user_table)
    avatar_url, nickName = redis.hmget(userTable, "headImgUrl", "nickname")
    return nickName, avatar_url

def getPlayerClubScore(redis, account, date_time, club_number):
    CLUB_PLAYERPOINT_LIMIT = "club:%s:pid:%s:point"
    key1 = CLUB_PLAYERPOINT_LIMIT % (club_number, account)
    try:
        point_limit = redis.get(key1)
        CLUB_PLAYER_POINT = "club:date:%s:cid:%s:mid:%s:hesh"
        key2 = CLUB_PLAYER_POINT % (date_time, club_number, account)
        play_point = redis.hget(key2, 'pp')
        play_point = int(play_point) if play_point else None
        point_limit = int(point_limit) if point_limit else None
        return point_limit, play_point
    except:
        return None, None
