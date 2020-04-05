#-*- coding:utf-8 -*-
#!/usr/bin/python

"""
     金币场模块
"""

from hall import hall_app
from hall_func import getUserByAccount
from common.utilt import *
from bottle import request, response, template, static_file
from model.goldModel import *
from model.protoclModel import sendProtocol2GameService
from common import web_util


@hall_app.post('/party/gold/gameList/bak')
@web_util.allow_cross_request
def getPartyGoldGameListBak(redis, session):
    """
    获取金币场场次列表
    """
    sid = request.POST.get('sid', '').strip()
    if not sid:
        return
    data = get_GoldGameList(redis)
    return {'code': 0, 'msg': '金币场场次列表获取成功', 'data': data}

@hall_app.post('/party/gold/gameList')
@web_util.allow_cross_request
def getPartyGoldGameList(redis, session):
    """
    获取金币场场次列表
    """
    sid = request.POST.get('sid', '').strip()
    if not sid:
        return

    def get_GoldGameList(redis):
        """
        获取金币场场次
        """
        import re
        res = []
        game_online_total = 0
        PARTY_GOLD_GAME_LIST = {}
        online_total_list = []
        gold_game_list = redis.lrange(GAME_GOLD_GAMEID_LIST, 0, -1)
        for each in gold_game_list:
            gold_game_id_list = redis.lrange(GAME_GOLD_GAMEID_TO_LIST.format(each), 0, -1)[::-1] # 获取游戏下场次ID集合
            for i in gold_game_id_list:
                PARTY_GOLD_GAME_LIST.setdefault(each, []).append(redis.hgetall(GAME_GOLD_GAMEID_ID.format(each, i)))

        for gameid in PARTY_GOLD_GAME_LIST.keys():
            list = PARTY_GOLD_GAME_LIST.get(gameid)
            data = copy.deepcopy(list)
            for item in data:
                online = redis.scard(GOLD_ONLINE_PLAYID_ACCOUNT_SET % (gameid, item['id']))
                item['online'] = Bonus_number(Bonus_time, online)
                game_online_total += int(item['online'])
                re_need = re.sub('\，', ',', re.sub('\】', ']', re.sub('\【', '[', item.get('need'))))
                if re.findall(',]$', re_need):
                    re_need = re.sub(',]', ']', re_need)
                item['need'] = eval(re_need)
                online_total_list.append(item['online'])
            redis.set("games:%s:online:total:str" % (gameid), online_total_list)
            online_total_list = []
            res.append({'gameid': gameid, 'config': data})
        return res

    data = get_GoldGameList(redis)
    return {'code': 0, 'msg': '金币场场次列表获取成功', 'data': data}


@hall_app.post('/party/gold/numberList')
@web_util.allow_cross_request
def getPartyGoldNumberList(redis, session):
    sid = request.POST.get('sid', '').strip()
    if not sid:
        return
    res = []
    total_online = 0
    gold_game_list = redis.lrange(GAME_GOLD_GAMEID_LIST, 0, -1)
    for item in gold_game_list:
        online = redis.get("games:%s:online:total:str" % (item))
        total_online += sum(eval(online))
        res.append({item: eval(online)})
    return {'code':0, 'msg':'获取游戏总人数列表成功','data':res, 'total': total_online}


@hall_app.post('/party/gold/gameconfigList')
@web_util.allow_cross_request
def getPartyGoldGame(redis, session):
    """
    获取金币场场次列表
    """
    sid = request.POST.get('sid', '').strip()
    if not sid:
        return

    def get_GoldGameList(redis):
        """
        获取金币场场次
        """
        res = []
        PARTY_GOLD_GAME_LIST = {}
        gold_game_list = redis.lrange('game:gold:gameid:list', 0, -1)[::-1]
        for each in gold_game_list:
            gold_game_id_list = redis.lrange('game:gold:gameid:%s:list' % each, 0, -1)[::-1]
            for i in gold_game_id_list:
                PARTY_GOLD_GAME_LIST.setdefault(each, []).append(redis.hgetall('game:gold:gameid:%s:id:%s' % (each, i)))

        for gameid in PARTY_GOLD_GAME_LIST.keys():
            list = PARTY_GOLD_GAME_LIST.get(gameid)
            data = copy.deepcopy(list)

            res.append({'gameid': gameid, 'config': data})
        return res

    data = get_GoldGameList(redis)
    return {'code': 0, 'msg': '金币场场次列表获取成功', 'data': data}


@hall_app.post('/notJoinGoldRoom')
@web_util.allow_cross_request
def do_NotJoinGoldRoom(redis, session):
    """
        取消加入金币场
    """
    sid = request.forms.get('sid', '').strip()
    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)

    try:
        print '[on notJoinPartyRoom]sid[%s] account[%s]' % (sid, account)
    except Exception as e:
        print 'print error File', e

    if verfiySid and sid != verfiySid:
        return {'code': -4, 'msg': '账号已在其他地方登录', 'osid': sid}
    if not redis.exists(SessionTable):
        return {'code': -3, 'msg': 'sid 超时'}
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code': -5, 'msg': '该用户不存在'}
    return {'code': 0}


@hall_app.post('/joinGoldRoom')
@web_util.allow_cross_request
def do_JoinGoldRoom(redis, session):
    """
        加入金币场
    """
    log_debug('do_joinGoldRoom  *********** ')
    gameid = request.forms.get('gameid', '').strip()
    playid = request.forms.get('id', '').strip()
    sid = request.forms.get('sid', '').strip()
    need = request.forms.get('need', '').strip()  # 参与条件
    cost = request.forms.get('cost', '').strip()  # 报名费
    cost = int(cost)
    base_score = request.forms.get('baseScore', '').strip()  # 底分
    base_score = int(base_score)

    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)

    if verfiySid and sid != verfiySid:
        return {'code': -4, 'msg': '账号已在其他地方登录', 'osid': sid}
    if not redis.exists(SessionTable):
        return {'code': -3, 'msg': 'sid 超时'}
    userTable = getUserByAccount(redis, account)
    if not redis.exists(userTable):
        return {'code': -5, 'msg': '该用户不存在'}

    groupId = redis.hget(userTable, 'parentAg')
    if not groupId:
        return {'code': -7, 'msg': '您已被移出公会，请重新加入公会'}

    gameTable = GAME_TABLE % gameid
    if not redis.exists(gameTable):
        return {'code': -1, 'msg': 'gameId 不存在'}

    serverList = redis.lrange(FORMAT_GAME_SERVICE_SET % gameid, 0, -1)
    if not serverList:
        return {'code': -1, 'msg': '服务器忙碌或维护中'}

    myroom_key = redis.get(GOLD_ROOM_ACCOUNT_KEY % account)
    if myroom_key:
        roomid, myplayid = redis.hmget(myroom_key, 'roomid', 'playid')
        ip, port, _gameid = redis.hmget(ROOM2SERVER % roomid, ('ip', 'port', 'gameid'))
        if ip and port and _gameid:
            if playid != myplayid or _gameid != gameid:
                return {'code': -1, 'msg': '您正在别的场次游戏中'}
            else:
                return {'code': 0, 'msg': '已经在金币场中'}
        else:
            redis.delete(GOLD_ROOM_ACCOUNT_KEY % account)


    coin = redis.hget(FORMAT_USER_TABLE % userTable.split(':')[1], 'gold')
    if not coin:
        coin = 0
    coin = int(coin)
    need = need.split(',')
    min_need = need[0]
    if not min_need:
        min_need = 0
    min_need = int(min_need)
    if len(need) == 1:
        max_need = 9999999999
    else:
        max_need = need[1]
    max_need = int(max_need)
    if coin < min_need:
        return {'code': -2, 'msg': u'您携带的金币数不足以进入本场次游戏，请充值后进入。'}
    # if coin > max_need:
    #     return {'code': -1, 'msg': u'您携带的金币数超出本场次上限，请进入更高一级的场次游戏。'}

    _uuid = get_uuid()
    serverTable = random.choice(serverList)
    sendProtocol2GameService(redis, gameid, "joinGoldRoom|%s|%s|%s" % (account, playid, _uuid), serverTable)
    redis.hmset(GOLD_ACCOUNT_WAIT_JOIN_TABLE % account, {'playid': playid, 'gameid': gameid})
    redis.expire(GOLD_ACCOUNT_WAIT_JOIN_TABLE % account, 5)
    return {'code': 0, 'msg': '加入金币场成功'}


@hall_app.post('/checkJoinGoldRoom')
@web_util.allow_cross_request
def do_CheckJoinGoldRoom(redis, session):
    """
        确认加入金币场结果
    """
    sid = request.forms.get('sid', '').strip()
    print 'do_CheckJoinPartyRoom'
    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
    if verfiySid and sid != verfiySid:
        return {'code': -4, 'msg': '账号已在其他地方登录', 'osid': sid}

    if not redis.exists(SessionTable):
        return {'code': -3, 'msg': 'sid 超时'}

    myroom_key = redis.get(GOLD_ROOM_ACCOUNT_KEY % account)
    if myroom_key:
        roomid = redis.hget(myroom_key, 'roomid')
        ip, port, gameid = redis.hmget(ROOM2SERVER % roomid, ('ip', 'port', 'gameid'))
        return {'code': 0, 'ip': ip, 'port': port, 'gameid': gameid,
                'isParty': PARTY_TYPE_GOLD}

    if not redis.exists(GOLD_ACCOUNT_WAIT_JOIN_TABLE % account):
        return {'code': -1, 'msg': u'匹配超时'}

    playid, gameid = redis.hmget(GOLD_ACCOUNT_WAIT_JOIN_TABLE % account, 'playid', 'gameid')
    roomids = redis.smembers(GOLD_CAN_JOIN_ROOM_SET % (gameid, playid))
    if not roomids:
        return {'code': 0, 'maxPlayers': 5, 'waitPlayers': 1}
    _f = [item.split(':')[4] for item in redis.lrange(GOLD_ROOM_ACCOUNT_LIST % account, 0, 1) if item]
    _roomids = [roomid for roomid in list(roomids) if roomid not in _f]
    if not _roomids:
        return {'code': 0, 'maxPlayers': 5, 'waitPlayers': 1}
    log_debug(u'可以加入的房间 {0}'.format(_roomids))

    choice_roomids = []
    for roomid in _roomids:
        playerCount = redis.hget(ROOM2SERVER % roomid, 'playerCount')
        playerCount = int(playerCount) if playerCount else 0
        if not playerCount:
            continue
        choice_roomids.append(roomid)
    if not choice_roomids:
        roomid = random.choice(_roomids)
    else:
        roomid = random.choice(choice_roomids)
    redis.hmset(SessionTable, {'roomid': roomid, 'action': 0})
    ip, port, gameid = redis.hmget(ROOM2SERVER % roomid, ('ip', 'port', 'gameid'))
    if not ip or not port or not gameid:
        redis.srem(GOLD_CAN_JOIN_ROOM_SET % (gameid, playid), roomid)
    return {'code': 0, 'ip': ip, 'port': port, 'gameid': gameid,
            'isParty': PARTY_TYPE_GOLD}


@hall_app.get('/gold/rank')
@web_util.allow_cross_request
def onGetRank(redis, session):
    """
        获取排行榜数据
    """
    sid = request.GET.get('sid', '').strip()
    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
    if verfiySid and sid != verfiySid:
        return {'code': -4, 'msg': '账号已在其他地方登录', 'osid': sid}
    userTable = getUserByAccount(redis, account)

    if not redis.exists(SessionTable):
        return {'code': -3, 'msg': 'sid 超时'}

    if not redis.exists(userTable):
        return {'code': -5, 'msg': '该用户不存在'}
    picUrl, gender, groupId, isVolntExitGroup, maxScore, baseScore = \
        redis.hmget(userTable, ('headImgUrl', 'sex', 'parentAg', 'isVolntExitGroup', 'maxScore', 'baseScore'))
    if not groupId:
        return {'code': -7, 'msg': '您已被移出公会，请重新加入公会'}
    data = get_gold_rank(redis, groupId, account)
    return {'code': 0, 'data': data}


@hall_app.post('/welfare')
@web_util.allow_cross_request
def getWelfare(redis, session):
    """ 
        福利系统
    """
    sid = request.forms.get('sid', '').strip()

    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
    if verfiySid and sid != verfiySid:
        return {'code': -4, 'msg': '账号已在其他地方登录', 'osid': sid}
    userTable = getUserByAccount(redis, account)

    if not redis.exists(SessionTable):
        return {'code': -3, 'msg': 'sid 超时'}

    if not redis.exists(userTable):
        return {'code': -5, 'msg': '该用户不存在'}
    picUrl, gender, groupId, isVolntExitGroup, maxScore, baseScore = \
        redis.hmget(userTable, ('headImgUrl', 'sex', 'parentAg', 'isVolntExitGroup', 'maxScore', 'baseScore'))
    if not groupId:
        return {'code': -7, 'msg': '您已被移出公会，请重新加入公会'}

    res = get_welfare_info(redis, account)

    return {'code': 0, 'data': res}


@hall_app.post('/welfare/sign')
@web_util.allow_cross_request
def doWelfareSign(redis, session):
    """ 
        签到
    """
    sid = request.forms.get('sid', '').strip()

    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
    if verfiySid and sid != verfiySid:
        return {'code': -4, 'msg': '账号已在其他地方登录', 'osid': sid}
    userTable = getUserByAccount(redis, account)

    if not redis.exists(SessionTable):
        return {'code': -3, 'msg': 'sid 超时'}

    if not redis.exists(userTable):
        return {'code': -5, 'msg': '该用户不存在'}
    picUrl, gender, groupId, isVolntExitGroup, maxScore, baseScore = \
        redis.hmget(userTable, ('headImgUrl', 'sex', 'parentAg', 'isVolntExitGroup', 'maxScore', 'baseScore'))
    if not groupId:
        return {'code': -7, 'msg': '您已被移出公会，请重新加入公会'}

    res = do_PlayerWelfareSign(redis, account)

    if not res:
        return {'code': 1, 'msg': "今日已签到"}
    else:
        return {'code': 0, 'msg': "签到成功,获得 {0} 金币".format(res)}


@hall_app.post('/welfare/patch_sign')
@web_util.allow_cross_request
def doWelfarePatchSign(redis, session):
    """ 
        补签
    """
    sid = request.forms.get('sid', '').strip()
    date = request.forms.get('date', '').strip()

    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
    if verfiySid and sid != verfiySid:
        return {'code': -4, 'msg': '账号已在其他地方登录', 'osid': sid}
    userTable = getUserByAccount(redis, account)

    if not redis.exists(SessionTable):
        return {'code': -3, 'msg': 'sid 超时'}

    if not redis.exists(userTable):
        return {'code': -5, 'msg': '该用户不存在'}
    picUrl, gender, groupId, isVolntExitGroup, maxScore, baseScore = \
        redis.hmget(userTable, ('headImgUrl', 'sex', 'parentAg', 'isVolntExitGroup', 'maxScore', 'baseScore'))
    if not groupId:
        return {'code': -7, 'msg': '您已被移出公会，请重新加入公会'}

    if not date:
        return {'code': 1, 'msg': "补签失败"}

    return doPatchSign(redis, account, date)




@hall_app.post('/welfare/coin/GMSet')
@web_util.allow_cross_request
def checkWelfareIsGM(redis, session):
    """
        设置该玩家金币 
    """
    sid = request.forms.get('sid', '').strip()
    coinNum = request.forms.get('coinNum', '').strip()
    isNumber = all(c in "0123456789.+-" for c in coinNum)
    if not coinNum or not isNumber:
        return {'code': 1, 'msg': '输入值错误'}
    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
    if player_set_gold(redis, account, coinNum):
        return {'code': 0, 'msg': '设置金币成功'}
    return {'code': -1, 'msg': '设置金币失败'}


@hall_app.post('/welfare/insurance')
@web_util.allow_cross_request
def doWelfareInsurancen(redis, session):
    """ 
        低保
    """
    sid = request.forms.get('sid', '').strip()
    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
    res = doWelfareById(redis, uid, account, '2')
    return res


@hall_app.post('/welfare/get_welfare')
@web_util.allow_cross_request
def do_get_welfare(redis, session):
    """ 
        获取福利
    """
    sid = request.forms.get('sid', '').strip()
    id = request.forms.get('id', '').strip()
    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
    if verfiySid and sid != verfiySid:
        return {'code': -4, 'msg': '账号已在其他地方登录', 'osid': sid}
    userTable = getUserByAccount(redis, account)

    if not redis.exists(SessionTable):
        return {'code': -3, 'msg': 'sid 超时'}

    if not redis.exists(userTable):
        return {'code': -5, 'msg': '该用户不存在'}
    picUrl, gender, groupId, isVolntExitGroup, maxScore, baseScore = \
        redis.hmget(userTable, ('headImgUrl', 'sex', 'parentAg', 'isVolntExitGroup', 'maxScore', 'baseScore'))
    if not groupId:
        return {'code': -7, 'msg': '您已被移出公会，请重新加入公会'}

    return doWelfareById(redis, uid, account, id)


@hall_app.post('/welfare/get_daily_reward')
@web_util.allow_cross_request
def do_get_daily_reward(redis, session):
    """
        领取50金币。 当身上少于50金币的情况下可以领取，每日只能4次, 每日6点重置
    """
    sid = request.forms.get('sid', '').strip()

    SessionTable, account, uid, verfiySid = getInfoBySid(redis, sid)
    if verfiySid and sid != verfiySid:
        return {'code': -4, 'msg': '账号已在其他地方登录', 'osid': sid}
    userTable = getUserByAccount(redis, account)

    if not redis.exists(SessionTable):
        return {'code': -3, 'msg': 'sid 超时'}

    if not redis.exists(userTable):
        return {'code': -5, 'msg': '该用户不存在'}
    picUrl, gender, groupId, isVolntExitGroup, maxScore, baseScore = \
        redis.hmget(userTable, ('headImgUrl', 'sex', 'parentAg', 'isVolntExitGroup', 'maxScore', 'baseScore'))
    if not groupId:
        return {'code': -7, 'msg': '您已被移出公会，请重新加入公会'}


    return get_daily_reward(redis, uid)
