# -*- coding:utf-8 -*-
# !/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    代理模型
"""
from web_db_define import *
from admin import access_module
from datetime import datetime, timedelta
from config.config import *
from common.log import *
from common.utilt import get_week_date_obj
import random
import time
from datetime import datetime
from operator import itemgetter
from common import convert_util, log_util
from club_db_define import *
from userModel import *

# 菜单权限
TYPE2ACCESS = {
    '0': access_module.ACCESS_SADMIN_MODULES,
    '1': access_module.ACCESS_COMPANY_MODULES,
    '2': access_module.ACCESS_AG_ONE_CLASS_MODULES,
    '3': access_module.ACCESS_AG_TWO_CLASS_MODULES

}
# 列表权限
TYPE2ACCESSLIST = {
    '0': access_module.ACCESS_SADMIN_LIST,
    '1': access_module.ACCESS_COMPANY_LIST,
    '2': access_module.ACCESS_AG_ONE_CLASS_LIST,
    '3': access_module.ACCESS_AG_TWO_CLASS_LIST

}
# 代开描述
OPENAUTH_2_TXT = {
    0: '所有玩家代开',
    1: '仅权限玩家代开'
}

# 房卡套餐
ROOMCARD2TYPE = {
    'agent': [
        {'txt': '220个钻石', 'roomCard': '220'},
        {'txt': '550个钻石', 'roomCard': '550'},
        {'txt': '1100个钻石', 'roomCard': '1100'},
        {'txt': '2200个钻石', 'roomCard': '2200'},
        {'txt': '5500个钻石', 'roomCard': '5500'},
        {'txt': '11000个钻石', 'roomCard': '11000'}
    ],

    'member.cards': [
        {'type': '6', 'txt': '2000送200', 'roomCard': '2200'},
        {'type': '5', 'txt': '800送80', 'roomCard': '880'},
        {'type': '4', 'txt': '400送40', 'roomCard': '440'},
        {'type': '3', 'txt': '200送20', 'roomCard': '220'},
        {'type': '2', 'txt': '120送12', 'roomCard': '132'},
        {'type': '1', 'txt': '80送8', 'roomCard': '88'},
        {'type': '0', 'txt': '40送4', 'roomCard': '44'},
    ],

    'member.coin': [

        {'type': '0', 'txt': '1000金币', 'roomCard': '1000'},
        {'type': '1', 'txt': '5000金币', 'roomCard': '5000'},
        {'type': '2', 'txt': '10000金币', 'roomCard': '10000'},
        {'type': '3', 'txt': '50000金币', 'roomCard': '5000'},

    ]
}

"""
代理模型的数据类型
添加一个模型field
注意:
    模板的提交名称属性必须与此处新增的一致，否则服务器将解析不到提交数据
"""
AGENT_FIELDS = (
    'parentAg',
    'account',
    'passwd',
    'shareRate',
    'unitPrice',
    'comfirPasswd',
    'myRate',
    'defaultRoomCard',
    'recharge',
    'agentId'
)

"""
代理列表需要展示的参数
"""
AGENT_LIST_DIS = (
    'type',  # 类型
    'valid',  # 状态
    'regDate',  # 注册日期
    'account',  # 账户
    'roomcard',  # 钻石数
    'id',  # 公会iD
    'isTrail',  # 试玩标志
    'isCreate',  # 是否有创建权限
    'recharge',  # 代理线上充值
    'auto_check',  # 是否自动审核
    'create_auth',  # 是否允许创建3级公会
    'open_auth',  # 仅权限者带开房
)

# 仅超管和一级代理需要显示的操作
ONLY_SUPERNTOP_SHOW = [
    '/admin/agent/create_auth'
]
# 只有2三级需要显示
ONLY_2_3_SHOW = [
    '/admin/agent/open_auth'
]


def getAgentIdNo(redis):
    """
    生成会员Id号(6位且不重复)
    """
    agentId = ''
    for i in range(6):
        # a = random.randint(0,9)
        a = random.randrange(9)
        agentId += str(a)
    if not redis.sadd(AGENT_ID_TABLE, agentId):
        getAgentIdNo(redis, session)
    return agentId


def getTopAgentId(redis, agentId):
    """
    获取总公司ID
    """
    agType = redis.hget(AGENT_TABLE % (agentId), 'type')
    if agType in ['0', '1']:
        return agentId

    while 1:
        agentId = redis.hget(AGENT_TABLE % (agentId), 'parent_id')
        agType = redis.hget(AGENT_TABLE % (agentId), 'type')
        try:
            if int(agType) == 1:
                return agentId
        except:
            log_util.info('[try getTopAgentId] agentId[%s] agentType[%s]' % (agentId, agType))
            return agentId


def getAgentOwnGames(redis, agentId):
    """
        获取代理自己被勾选(拥有)的所有游戏
    """
    try:
        gameList = redis.lrange(AGENT_OWN_GAME % (agentId), 0, -1)
    except:
        gameList = redis.smembers(AGENT_OWN_GAME % (agentId))
    exterGame = redis.smembers(GAME_DEFAULT_BIND)
    if not exterGame:
        exterGame = []
    gameList, exterGame = list(gameList), list(exterGame)
    gameList.extend(exterGame)
    return set(gameList)


def getCreatAgentGames(redis, agentId):
    """
        创建代理时获取代理下的所有游戏
    """
    exterGames = redis.smembers(GAME_DEFAULT_BIND)
    if agentId == '1':
        gameList = redis.lrange(GAME_LIST, 0, -1)
    else:
        try:
            gameList = redis.smembers(AGENT_OWN_GAME % (agentId))
            gameList = list(gameList)
            gameList.extend(list(exterGames))
        except:
            gameList = redis.lrange(AGENT_OWN_GAME % (agentId), 0, -1)
            gameList.extend(exterGames)
    # 增加游戏
    gameList = list(set(gameList))
    gamesInfo = []
    for game in gameList:
        gameInfo = {}
        name = redis.hget(GAME_TABLE % (game), 'name')
        gameInfo['name'] = name
        gameInfo['id'] = game
        gamesInfo.append(gameInfo)
    return gamesInfo


def getAgentGames(redis, parentId, agentId):
    """
        获取代理下的所有游戏
    """
    exterGames = redis.smembers(GAME_DEFAULT_BIND)
    if parentId == '1':
        parentGameList = redis.lrange(GAME_LIST, 0, -1)

    else:
        try:
            parentGameList = redis.smembers(AGENT_OWN_GAME % (parentId))
            parentGameList = list(parentGameList)
            parentGameList.extend(list(exterGames))
        except:
            parentGameList = redis.lrange(AGENT_OWN_GAME % (parentId), 0, -1)
    try:
        agentGameList = redis.smembers(AGENT_OWN_GAME % (agentId))
        agentGameList = list(agentGameList)
        agentGameList.extend(list(exterGames))
    except:
        agentGameList = redis.lrange(AGENT_OWN_GAME % (agentId), 0, -1)

    gameList = list(set(parentGameList).union(set(agentGameList)))
    gamesInfo = []
    for game in gameList:
        gameInfo = {}
        name = redis.hget(GAME_TABLE % (game), 'name')
        gameInfo['name'] = name
        gameInfo['id'] = game
        gamesInfo.append(gameInfo)
    return gamesInfo


def modifyAgentGames(request, redis, agentId):
    """
        通代理Id 给修改代理的游戏
    """
    agentOwnGamesTabel = AGENT_OWN_GAME % (agentId)
    agentTable = AGENT_TABLE % (agentId)
    aType, parentId = redis.hmget(agentTable, ('type', 'parent_id'))
    if aType == '1':
        parentGameList = redis.lrange(GAME_LIST, 0, -1)
    else:
        try:
            parentGameList = redis.smembers(AGENT_OWN_GAME % (parentId))
        except:
            parentGameList = redis.lrange(AGENT_OWN_GAME % (parentId), 0, -1)
    try:
        agentGameList = redis.smembers(AGENT_OWN_GAME % (agentId))
    except:
        agentGameList = redis.lrange(AGENT_OWN_GAME % (agentId), 0, -1)

    gameList = list(set(parentGameList).union(set(agentGameList)))

    for game in gameList:
        if request.forms.get('game%s' % (game)):
            try:
                redis.sadd(agentOwnGamesTabel, game)
            except:
                redis.delete(agentOwnGamesTabel)
                redis.sadd(agentOwnGamesTabel, game)
        else:
            redis.srem(agentOwnGamesTabel, game)


def setAgentGames(request, redis, parentId, agentId):
    """
    通过父代理Id 给代理存储代理的游戏
    """
    agentOwnGamesTabel = AGENT_OWN_GAME % (agentId)
    if parentId == '1':
        gameList = redis.lrange(GAME_LIST, 0, -1)
    else:
        try:
            gameList = redis.smembers(AGENT_OWN_GAME % (parentId))
        except:
            gameList = redis.lrange(AGENT_OWN_GAME % (parentId), 0, -1)

    default_ids = redis.smembers(GAME_DEFAULT_BIND)
    pipe = redis.pipeline()
    for game in gameList:
        if request.forms.get('game%s' % (game)):
            pipe.sadd(agentOwnGamesTabel, game)

    for game in default_ids:
        # 加入默认游戏
        pipe.sadd(agentOwnGamesTabel, game)

    pipe.execute()


def getListBanAccess(redis, agentId):
    """
        获得代理被禁用的权限列表
    """
    banTabel = AGENT2ACCESSBAN % (agentId)
    banList = redis.smembers(banTabel)
    return banList


def banAgentAccess(redis, request, agentType, agentId):
    """
        禁用代理的权限
    """
    agentType = str(agentType)
    banTabel = AGENT2ACCESSBAN % (agentId)
    accesslists = getAgentNewListAccessUrl(agentType)
    for accesslist in accesslists:
        if not request.forms.get('url%s' % (accesslist)):
            redis.sadd(banTabel, accesslist)


def banAgentAccessModify(redis, request, agentType, agentId):
    """
        修改禁用代理的权限
    """
    agentType = str(agentType)
    banTabel = AGENT2ACCESSBAN % (agentId)
    accesslists = getAgentNewListAccessUrl(agentType)
    for accesslist in accesslists:
        if not request.forms.get('url%s' % (accesslist)):
            redis.sadd(banTabel, accesslist)
        else:
            redis.srem(banTabel, accesslist)


def setAgentAccess(redis, agentType, agentId):
    """
        通过代理Id 和代理类型给代理存储权限
    """
    agentType = str(agentType)
    accessTable = AGENT2ACCESS % (agentId)

    for accessObj in TYPE2ACCESS[agentType]:
        redis.sadd(accessTable, accessObj.url)

    for access in TYPE2ACCESSLIST[agentType]:
        if access.url not in [menu.url for menu in TYPE2ACCESS[agentType]] and access.url not in [menu.url for menu in
                                                                                                  access_module.MENU_MODULES]:
            redis.sadd(accessTable, access.url)


def getNewAccess(redis, agentId):
    """
        代理登录后台生成最新的权限
    """
    agentTable = AGENT_TABLE % (agentId)
    aType = redis.hget(agentTable, ('type'))
    # print redis.sadd('str',)
    accessTable = AGENT2ACCESS % (agentId)
    # 获得菜单权限
    Access = TYPE2ACCESS[aType]
    # 获得列表权限
    ListAccess = TYPE2ACCESSLIST[aType]
    lists = []
    for listac in ListAccess:
        if listac.url not in [menu.url for menu in TYPE2ACCESS[aType]] and listac.url not in [menu.url for menu in
                                                                                              access_module.MENU_MODULES]:
            lists.append(listac)
    lists = tuple(lists)
    Access = Access + lists

    s1 = redis.smembers(accessTable)
    accessUrlsList = []
    for access in Access:
        redis.sadd(accessTable, access.url)
        accessUrlsList.append(access.url)
    #
    s2 = redis.smembers(accessTable)
    deleteUrls = []
    for s in s2:
        if s not in accessUrlsList:
            deleteUrls.append(s)
    if deleteUrls:
        redis.srem(accessTable, *deleteUrls)
    # 被勾选掉的权限
    accessBan = redis.smembers(AGENT2ACCESSBAN % (agentId))
    if accessBan:
        redis.srem(accessTable, *accessBan)


def getAgentNewListAccessUrl(aType):
    aType = str(aType)
    menuAccess = access_module.MENU_MODULES
    menulist = [acc.url for acc in menuAccess]
    newList = []
    sd = 1
    for access in TYPE2ACCESSLIST[aType]:
        if access.url in menulist:
            if access.url in [menu.url for menu in TYPE2ACCESS[aType]]:
                sd = 1
            else:
                sd = 0
        elif sd == 1:
            newList.append(access.url)
    return newList


def getAgentNewListAccess(aType):
    aType = str(aType)
    menuAccess = access_module.MENU_MODULES
    menulist = [acc.url for acc in menuAccess]
    newList = []
    sd = 1
    for access in TYPE2ACCESSLIST[aType]:
        if access.url in menulist:
            if access.url in [menu.url for menu in TYPE2ACCESS[aType]]:
                newList.append(access)
                sd = 1
            else:
                sd = 0
        elif sd == 1:
            newList.append(access)
    return newList


def getListAccess(aType, lang):
    """
        创建代理它拥有的列表权限
    """
    lists = []
    sublists = []
    aType = str(aType)
    for access in getAgentNewListAccess(aType):
        if access.url in [menu.url for menu in TYPE2ACCESS[aType]]:
            sub = {}
            sublists = []
            sub['belong'] = access.getTxt(lang)
            sub['sub'] = sublists
            lists.append(sub)
        else:
            sublists.append(access)
    return lists


def getAgentId(redis, account):
    agentIdTable = AGENT_ACCOUNT_TO_ID % (account)
    return redis.get(agentIdTable)


def get_agent_list_infos(redis, sub_agent_ids, agent_own_accesses, lang, agent_userid=None):
    sub_ag_lists = []
    curTime = datetime.now()
    for subId in sub_agent_ids:
        agentTable = AGENT_TABLE % (subId)
        agentAccountTable = redis.get('agents:account:%s:to:id' % (subId))
        if agentAccountTable:
            agentTable = AGENT_TABLE % (agentAccountTable)
        if agentTable:
            aType, valid, reg_date, account, roomCard, aId, isTrail, isCreate, recharge, auto_check, create_auth, open_auth = redis.hmget(
                agentTable, AGENT_LIST_DIS)

        if not account or aType == '4':
            continue

        agentlist = redis.smembers("agent:%s:member:children" % subId)
        agentlist = [redis.hget("users:%s" % (i), "account") for i in agentlist]
        day_total = 0
        del_total = 0
        _rlis = []
        for i in agentlist:
            club_account = redis.smembers("club:account:%s:set" % (i))
            if club_account:
                for each in club_account:
                    _rlis.append(each)

        nowtime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        for i in _rlis:
            club_createtime = redis.hget("club:attribute:%s:hash" % (i), "club_createtime")
            if club_createtime:
                if nowtime in club_createtime:
                    day_total += 1

        agInfo = {
            'valid': valid,
            'parentId': aId,
            'regDate': reg_date,
            'members': getAgentMembers(redis, subId),
            'allMembers': getAgentAllMembers(redis, subId),
            'agentType': lang.TYPE_2_ADMINTYPE[aType],
            'parentAg': account,
            'recharge': recharge if recharge else '0',
            'roomCard': getAgentRoomByDay(redis, subId, curTime.strftime('%Y-%m-%d')),
            'club_total': len(_rlis),
            'club_daytotal': day_total,
            'leaf_roomcard': convert_util.to_int(roomCard),
            'isTrail': isTrail if isTrail else '0',
            'auto_check': auto_check if auto_check else '1',
            'create_auth': create_auth if create_auth else '0',  # 默认不开启
            'open_auth': open_auth if open_auth else '0',  # 默认不开启
        }

        # 获取操作权限
        agInfo['op'] = []
        for access in access_module.ACCESS_AGENT_LIST:
            if access.url in agent_own_accesses:
                if (aType != '1' and (aType in ['3'] or create_auth != '1') and access.url == '/admin/agent/create'):
                    # 最多只能创建三级代理
                    continue

                if (aType in ['2', '3']) and access.url in ONLY_SUPERNTOP_SHOW:  # 只有管理员显示开启和关闭
                    continue

                if (aType in ['1']) and access.url in ONLY_2_3_SHOW:  # 只有二三级显示
                    continue

                if access.url[-5:] == 'trail':
                    agInfo['op'].append({'url': access.url, 'txt': '设置试玩' \
                        if agInfo['isTrail'] == '0' else '解除试玩', 'method': access.method})
                elif access.url[-8:] == 'recharge':
                    agInfo['op'].append({'url': access.url, 'txt': '开放商城' \
                        if agInfo['recharge'] == '0' else '关闭商城', 'method': access.method})
                elif access.url[-10:] == 'auto_check':
                    agInfo['op'].append({'url': access.url, 'txt': '开启自动审核' \
                        if agInfo['auto_check'] == '0' else '关闭自动审核', 'method': access.method})
                elif access.url[-11:] == 'create_auth':
                    agInfo['op'].append({'url': access.url, 'txt': '开启市级(2)' \
                        if agInfo['create_auth'] == '0' else '关闭市级(2)', 'method': access.method})
                elif access.url[-9:] == 'open_auth':
                    agInfo['op'].append({'url': access.url, 'txt': '所有玩家代开房)' \
                        if agInfo['open_auth'] == '1' else '仅权限玩家代开房', 'method': access.method})
                elif access.url[-6:] == 'freeze':
                    agInfo['op'].append({'url': access.url, 'txt': '冻结' \
                        if agInfo['valid'] == '1' else '解冻', 'method': access.method})
                else:
                    agInfo['op'].append({'url': access.url, 'method': access.method, 'txt': access.getTxt(lang)})

        sub_ag_lists.append(agInfo)
    return sub_ag_lists


def getAgListInfos(redis, session, agentId, condition, lang):
    """
    获取代理列表
    """
    parentTable = AGENT_CHILD_TABLE % (agentId)
    subIds = redis.smembers(parentTable)
    is_super_admin = int(agentId) in [systemId]

    sub_agent_ids = []
    is_search_time, is_search_id = False, False
    if condition['start_date'] and not condition['searchId']:
        is_search_time = True
        date_lists = get_week_date_obj(condition['start_date'], condition['end_date'])
        for date in date_lists:
            sub_agent_ids.extend(list(redis.smembers(AGENT_CREATE_DATE % (date))))

    if condition['searchId']:  # 搜索ID
        is_search_id = True
        sub_agent_ids = [condition['searchId']]

    sub_ag_lists = []
    sub_agent_own_ids = []
    if sub_agent_ids:
        for sub_agent_id in sub_agent_ids:
            if sub_agent_id in subIds:
                sub_agent_own_ids.append(sub_agent_id)
        if not sub_agent_own_ids:
            for item in subIds:
                if sub_agent_ids[0] == redis.hget("agents:id:%s" % (item), "account"):
                    sub_agent_own_ids.append(sub_agent_id)

        if is_search_id and is_super_admin:  # 管理员不需要检查ID是否存在
            sub_agent_own_ids = [condition['searchId']]
    else:
        if is_search_time:
            sub_agent_own_ids = []
        else:
            sub_agent_own_ids = subIds

    agent_own_accesses = eval(session['access'])
    sub_ag_lists = get_agent_list_infos(redis, sub_agent_own_ids, agent_own_accesses, lang)

    return {'count': len(sub_ag_lists), 'data': sub_ag_lists}


def agentOpLog(redis, account, atype, ip):
    """
    写登录日志
    @params:
        redis     redis实例
        account   操作代理ID
        toAccount      操作日期
        atype      状态,1成功 2密码错误
    """
    curTime = datetime.now()
    dateStr = curTime.strftime("%Y-%m-%d")
    timeStr = curTime.strftime("%Y-%m-%d %H:%M:%S")

    adminLogDatesetTable = FORMAT_AGENT_OP_LOG_DATESET_TABLE % (dateStr)
    # 创建新的操作日志
    id = redis.incr(FORMAT_AGENT_OP_LOG_COUNT_TABLE)
    adminLogTable = FORMAT_AGENT_OP_LOG_TABLE % (id)
    pipe = redis.pipeline()
    pipe.hmset(adminLogTable, {
        'account': account,
        'type': atype,
        'datetime': timeStr,
        'ip': ip
    })
    pipe.expire(adminLogTable, LOG_TABLE_TTL)
    pipe.lpush(adminLogDatesetTable, id)
    pipe.execute()


def writeAgentOpLog(redis, agentId, logInfo):
    """
    写操作日志
    @params:
        redis     redis实例
        agentId   操作代理ID
        date      操作日期
        desc      操作记录描述
    """
    curTime = datetime.now()

    dateStr = curTime.strftime('%Y-%m-%d')

    logId = redis.incr(AGENT_OP_COUNT)
    logTable = AGENT_OP_LOG_TABLE % (logId)
    agentLogTable = AGENT_OP_LOG_DATESET_TABLE % (agentId, dateStr)
    pipe = redis.pipeline()
    pipe.hmset(logTable, logInfo)
    pipe.lpush(agentLogTable, logId)
    pipe.execute()


def getAgentOpLog(redis, agentId, startDate, endDate):
    """
    获取代理操作日志
    @params:
        redis    链接实例
        agentId  代理ID
        startDate   开始日期
        endDate     结束日期
    """
    deltaTime = timedelta(1)

    startDate = datetime.strptime(startDate, '%Y-%m-%d')
    endDate = datetime.strptime(endDate, '%Y-%m-%d')

    opList = []
    while endDate >= startDate:

        agentLogTable = AGENT_OP_LOG_DATESET_TABLE % (agentId, endDate.strftime('%Y-%m-%d'))
        if not redis.exists(agentLogTable):
            endDate -= deltaTime
            continue

        logIds = redis.lrange(agentLogTable, 0, -1)
        for logId in logIds:
            logInfo = redis.hgetall(AGENT_OP_LOG_TABLE % (logId))

            opList.append(logInfo)

        endDate = endDate - deltaTime

    return opList


def agentFreeze(redis, agentId):
    """
    冻结代理所有下属代理
    @params:
        redis    链接实例
        agentId  代理ID
    """
    pipe = redis.pipeline()
    adminTable = AGENT_TABLE % (agentId)
    pipe.hset(adminTable, 'valid', '0')
    childList = redis.smembers(AGENT_CHILD_TABLE % (agentId))
    if childList:
        for child in childList:
            pipe.hset(AGENT_TABLE % (child), 'valid', '0')
            childSonList = redis.smembers(AGENT_CHILD_TABLE % (child))
            if childSonList:
                for childson in childSonList:
                    pipe.hset(AGENT_TABLE % (childson), 'valid', '0')

    pipe.execute()


def doAgentChange(redis, agentId, field, change):
    """
    设置代理所有下属代理
    @params:
        redis    链接实例
        agentId  代理ID
    """

    pipe = redis.pipeline()
    adminTable = AGENT_TABLE % (agentId)
    pipe.hset(adminTable, field, change)
    childList = redis.smembers(AGENT_CHILD_TABLE % (agentId))

    if childList:
        for child in childList:
            pipe.hset(AGENT_TABLE % (child), field, change)
            childSonList = redis.smembers(AGENT_CHILD_TABLE % (child))
            if childSonList:
                for childson in childSonList:
                    pipe.hset(AGENT_TABLE % (childson), field, '0')

    pipe.execute()


def getAllChildAgentId(redis, agentId):
    """
    返回所有下级代理ID
    """
    agentIdList = []
    pipe = redis.pipeline()
    downLines = redis.smembers(AGENT_CHILD_TABLE % (agentId))

    if downLines:
        for downline in downLines:
            agentIdList.append(downline)
            subDownlines = redis.smembers(AGENT_CHILD_TABLE % (downline))
            if subDownlines:
                for subDownline in subDownlines:
                    agentIdList.append(subDownline)

    log_util.debug('[try getAllChildAgentId] agentId[%s] allChildIds[%s]' % (agentId, agentIdList))
    return agentIdList


def getAgRoomListInfos(redis, session, agentId, lang):
    """
        获取代理直属玩家房间列表
    """

    subAgLists = []

    # 获取亲友圈房间列表
    for club_number in redis.smembers("club:list:set"):
        club_user = redis.hget("club:attribute:%s:hash" % club_number, "club_user")
        userTable = redis.get(FORMAT_ACCOUNT2USER_TABLE % club_user)
        parentAg = redis.hget(userTable, "parentAg")
        roomTable = AG2SERVER % ("%s-%s" % (parentAg, club_number))
        subIds = redis.smembers(roomTable)
        if not subIds:
            continue
        for subId in subIds:
            roomInfo = {}
            roomTable = ROOM2SERVER % (subId)
            ag, game_id, room_type, game_name, dealer, player_count, club_number_room = \
                redis.hmget(roomTable, ('ag', 'gameid', 'type', 'gameName', 'dealer', 'playerCount', "club_number"))
            if club_number != club_number_room:
                continue
            roomInfo['id'] = subId
            roomInfo['ag'] = ag
            roomInfo['game_id'] = game_id
            roomInfo['room_type'] = room_type
            roomInfo['game_name'] = game_name
            roomInfo['player_count'] = player_count
            roomInfo['dealer'] = dealer
            roomInfo["club_number"] = club_number
            # roomInfo['gameid'] = redis.hget(GAME_TABLE%(roomInfo['gameid']),'name')
            # 获取操作权限
            roomInfo['op'] = []
            # sessiob['access']
            for access in access_module.ACCESS_AGENT_ROOM_LIST:
                if access.url in eval(session['access']):
                    roomInfo['op'].append({'url': access.url, 'method': access.method, 'txt': access.getTxt(lang)})
            subAgLists.append(roomInfo)

    # 获取代开房间列表
    agentId2Childs = getAllChildAgentId(redis, agentId)
    agentId2Childs.extend(["%s-" % i for i in agentId2Childs])
    for aId in agentId2Childs:
        roomTable = AG2SERVER % (aId)
        subIds = redis.smembers(roomTable)
        if not subIds:
            continue
        for subId in subIds:
            roomInfo = {}
            roomTable = ROOM2SERVER % (subId)
            ag, game_id, room_type, game_name, dealer, player_count = \
                redis.hmget(roomTable, ('ag', 'gameid', 'type', 'gameName', 'dealer', 'playerCount'))
            roomInfo['id'] = subId
            roomInfo['ag'] = ag
            roomInfo['game_id'] = game_id
            roomInfo['room_type'] = room_type
            roomInfo['game_name'] = game_name
            roomInfo['player_count'] = player_count
            roomInfo['dealer'] = dealer
            # roomInfo['gameid'] = redis.hget(GAME_TABLE%(roomInfo['gameid']),'name')

            # 获取操作权限
            roomInfo['op'] = []
            # sessiob['access']
            for access in access_module.ACCESS_AGENT_ROOM_LIST:
                if access.url in eval(session['access']):
                    roomInfo['op'].append({'url': access.url, 'method': access.method, 'txt': access.getTxt(lang)})
            subAgLists.append(roomInfo)

    return {
        'data': subAgLists,
        'count': len(subAgLists)
    }


def getAgChildRoomListInfos(redis, session, agentId, lang):
    """
    获取一二级代理直属玩家房间列表
    """
    subAgLists = []
    # 获取亲友圈房间列表
    agentId2Childs = getAllChildAgentId(redis, agentId)
    agentId2Childs.append(agentId)
    for club_number in redis.smembers("club:list:set"):
        for parentAg in agentId2Childs:
            roomTable = AG2SERVER % ("%s-%s" % (parentAg, club_number))
            subIds = redis.smembers(roomTable)
            if not subIds:
                continue
            for subId in subIds:
                roomInfo = {}
                roomTable = ROOM2SERVER % (subId)
                ag, game_id, room_type, game_name, dealer, player_count, club_number_room = \
                    redis.hmget(roomTable, ('ag', 'gameid', 'type', 'gameName', 'dealer', 'playerCount', "club_number"))
                if club_number != club_number_room:
                    continue

                roomInfo['id'] = subId
                roomInfo['club_id'] = club_number
                roomInfo['ag'] = ag
                roomInfo['game_id'] = game_id
                roomInfo['room_type'] = room_type
                roomInfo['game_name'] = game_name
                roomInfo['player_count'] = player_count
                roomInfo['dealer'] = dealer
                roomInfo["club_number"] = club_number
                # roomInfo['gameid'] = redis.hget(GAME_TABLE%(roomInfo['gameid']),'name')
                # 获取操作权限
                roomInfo['op'] = []
                # sessiob['access']
                for access in access_module.ACCESS_AGENT_CHILD_ROOM_LIST:
                    roomInfo['op'].append({'url': access.url, 'method': access.method, 'txt': access.getTxt(lang)})
                subAgLists.append(roomInfo)

    # 获取代开房间列表
    agentId2Childs = getAllChildAgentId(redis, agentId)
    agentId2Childs.extend(["%s-" % i for i in agentId2Childs])
    for aId in agentId2Childs:
        roomTable = AG2SERVER % (aId)
        subIds = redis.smembers(roomTable)
        if not subIds:
            continue
        for subId in subIds:
            roomInfo = {}
            roomTable = ROOM2SERVER % (subId)
            ag, game_id, room_type, game_name, dealer, player_count = \
                redis.hmget(roomTable, ('ag', 'gameid', 'type', 'gameName', 'dealer', 'playerCount'))
            roomInfo['id'] = subId
            roomInfo['ag'] = ag
            roomInfo['club_id'] = club_number
            roomInfo['game_id'] = game_id
            roomInfo['room_type'] = room_type
            roomInfo['game_name'] = game_name
            roomInfo['player_count'] = player_count
            roomInfo['dealer'] = dealer
            # roomInfo['gameid'] = redis.hget(GAME_TABLE%(roomInfo['gameid']),'name')

            # 获取操作权限
            roomInfo['op'] = []
            # sessiob['access']
            for access in access_module.ACCESS_AGENT_CHILD_ROOM_LIST:
                roomInfo['op'].append({'url': access.url, 'method': access.method, 'txt': access.getTxt(lang)})
            subAgLists.append(roomInfo)

    return {
        'data': subAgLists,
        'count': len(subAgLists)
    }


def getAgentMembers(redis, agentId):
    """
    获取该公会下的活跃会员总数
    """
    agentIdChilds = getAllChildAgentId(redis, agentId)
    curTime = datetime.now()

    downLineCount = redis.get(DAY_AG_LOGIN_COUNT % (agentId, curTime.strftime('%Y-%m-%d')))
    if not downLineCount:
        downLineCount = 0

    for subId in agentIdChilds:
        count = redis.get(DAY_AG_LOGIN_COUNT % (subId, curTime.strftime('%Y-%m-%d')))
        if not count:
            count = 0
        downLineCount = int(downLineCount) + int(count)
        log_debug('[try getAgentAllMembers] agentId[%s] downLineCount[%s]' % (subId, downLineCount))

    return downLineCount

    curTime = datetime.now()
    count = redis.get(DAY_AG_LOGIN_COUNT % (agentId, curTime.strftime('%Y-%m-%d')))
    if not count:
        return 0

    return int(count)


def getAgentAllMembers(redis, agentId):
    """
    获取该公会下的活跃会员总数
    """
    agentIdChilds = getAllChildAgentId(redis, agentId)
    curTime = datetime.now()

    downLineCount = redis.scard(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE % (agentId))
    for subId in agentIdChilds:
        downLineCount += int(redis.scard(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE % (subId)))
    # downLineCount+=redis.scard(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(agentId))

    return downLineCount


def getAgentMemberTotal(redis, agentId):
    """
    获取所有会员总数
    """
    agentIdChilds = getAllChildAgentId(redis, agentId)
    total = redis.scard(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE % (agentId))
    if not total:
        total = 0
    for subId in agentIdChilds:
        subTotal = redis.scard(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE % (subId))
        if not subTotal:
            subTotal = 0
        total += int(subTotal)

    return total


def getAgentMemberLogin(redis, agentId, dateStr):
    """
    获取所有会员总数
    """
    agentIdChilds = getAllChildAgentId(redis, agentId)
    total = redis.get(DAY_AG_LOGIN_COUNT % (agentId, dateStr))
    if not total:
        total = 0

    total = int(total)
    for subId in agentIdChilds:
        subTotal = redis.get(DAY_AG_LOGIN_COUNT % (subId, dateStr))
        if not subTotal:
            subTotal = 0
        total += int(subTotal)

    return total


def getAgentRoomByDay(redis, agentId, dateStr):
    """
    获取所有会员总数
    """
    agentIdChilds = getAllChildAgentId(redis, agentId)
    total = redis.get(DAY_AG_PLAY_ROOM_CARD % (agentId, dateStr))
    if not total:
        total = 0
    total = int(total)
    for subId in agentIdChilds:
        subTotal = redis.get(DAY_AG_PLAY_ROOM_CARD % (subId, dateStr))
        if not subTotal:
            subTotal = 0
        total += int(subTotal)

    return total


def getDateAgTotal(redis, agentId, agentIds, endDate, startDate):
    """
    获取某段时间内的总数
    """
    endDate = datetime.strptime(endDate, '%Y-%m-%d')
    deltaTime = timedelta(1)
    count = 0
    while endDate >= startDate:
        date = endDate.strftime('%Y-%m-%d')
        for aid in agentIds:
            nums = redis.get(DAY_AG_LOGIN_COUNT % (aid, date))
            if not nums:
                nums = 0
            count += int(nums)
        endDate -= deltaTime
    # log_debug('[getDateTotal] startDate[%s],endDate[%s] agentIds[%s] count[%s]'%(startDate,endDate,agentIds,count))
    return count


def get_agent_by_date(redis, agentId, agent_ids, date):
    count = 0
    for agent_id in agent_ids:
        nums = redis.get(DAY_AG_LOGIN_COUNT % (agent_id, date))
        count += convert_util.to_int(nums)

    return count


def get_agent_active(redis, agentId, startDate, endDate):
    """
    获取直属下级代理活跃数
    """
    self_child_table = AGENT_CHILD_TABLE % (agentId)
    self_child_ids = redis.smembers(self_child_table)

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
    now_date = datetime.now()
    while endDate >= startDate:
        if endDate > now_date:
            endDate -= deltaTime
            continue
        for child_id in self_child_ids:
            agentInfo = {}
            agentInfo['id'] = child_id
            agentInfo['date'] = endDate.strftime('%Y-%m-%d')
            count = convert_util.to_int(redis.get(DAY_AG_LOGIN_COUNT % (child_id, agentInfo['date'])))

            parentTable = AGENT_CHILD_TABLE % (child_id)
            agent_ids = redis.smembers(parentTable)
            count = get_agent_by_date(redis, child_id, agent_ids, agentInfo['date'])
            agentInfo['active'] = count
            agentInfo['roomcard'] = getAgentRoomByDay(redis, child_id, agentInfo['date']),
            agentInfo['members'] = getAgentAllMembers(redis, child_id),
            res.append(agentInfo)
        endDate -= deltaTime
    res = sorted(res, key=itemgetter('date', 'active', 'id'), reverse=True)
    return {'data': res, 'count': len(res)}


def get_AgClub(redis, agent_id):
    """
    获取代理对应下的亲友圈列表
    :param redis:
    :param agent_id:
    :return:
    """
    agentlist = redis.smembers(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE % agent_id)
    agentlist = [redis.hget(FORMAT_USER_TABLE % (i), "account") for i in agentlist]

    club_list = []
    _rlis = []
    for i in agentlist:
        c = redis.smembers(CLUB_ACCOUNT_LIST % (i))
        if c:
            for each in c:
                _rlis.append({each: i})

    nowtime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    for each in _rlis:
        for item, account in each.items():
            club = redis.hgetall(CLUB_ATTR % item)
            club['club_id'] = item
            if eval(club['club_manager']):
                club_accounts = [redis.get(FORMAT_ACCOUNT2USER_TABLE % (i)) for i in list(eval(club['club_manager']))]
                club['club_manager'] = [redis.hmget(FORMAT_USER_TABLE % (i.split(':')[1]), "nickname") for i in
                                        club_accounts]
            else:
                club['club_manager'] = ''
            userTable = redis.get(FORMAT_ACCOUNT2USER_TABLE % (account))
            if userTable:
                club['user_id'] = userTable.split(':')[-1]
            avatar_url = redis.hget(userTable, "headImgUrl")
            club['imgurl'] = avatar_url
            club_person_number = len(redis.smembers(CLUB_PLAYER_LIST % item)) + 1
            club['count'] = club_person_number
            club['roomcards_day'] = redis.get("club:roomCards:day:%s:%s:total" % (item, nowtime))
            club['roomcards_all'] = redis.get("club:roomCards:all:%s:total" % (item))
            club['op'] = [
                {'url': '/admin/agent/clublist/addUser', 'txt': '添加玩家', 'method': 'POST'},
                {'url': '/admin/agent/clublist/delUser', 'txt': '移除玩家', 'method': 'POST'},
                {'url': '/admin/agent/clublist/audit', 'txt': '审批', 'method': 'GET'},
                {'url': '/admin/agent/clublist/transferUser', 'txt': '转移亲友圈', 'method': 'POST'},
                {'url': '/admin/agent/clublist/showDay', 'txt': '玩家出入记录', 'method': 'GET'},
                {'url': '/admin/agent/clublist/userbanList', 'txt': '同桌管理列表', 'method': 'GET'},

                # {'url': '/admin/agent/clublist/delClub', 'txt': '删除亲友圈', 'method': 'POST'},
            ]
            club_list.append(club)
    return {'data': club_list, 'count': len(club_list)}


def get_AgClubUser(redis, club_number):
    """
    获取亲友圈对应下的会员列表
    :param redis:
    :param id:
    :return:
    """
    players = []
    accounts = redis.smembers(CLUB_PLAYER_LIST % club_number)
    accounts = list(accounts)
    managerAccount = redis.hget(CLUB_ATTR % club_number, "club_user")

    members = redis.smembers(ONLINE_ACCOUNTS_TABLE)  # 获取在线正在玩的玩家
    num = 1
    nowDay = datetime.now().strftime('%Y-%m-%d')
    for item in accounts:
        userTable = redis.get(FORMAT_ACCOUNT2USER_TABLE % item)  # 获取users:id
        player = {}
        player['club_id'] = club_number
        player['number'] = num
        num += 1
        nickname, headImgUrl, account, last_logout_date, parentAg = redis.hmget(userTable, 'nickname', 'headImgUrl',
                                                                                'account',
                                                                                "last_logout_date", "parentAg")
        player["account"] = account
        player["nickname"] = nickname
        player["avatar_url"] = headImgUrl
        player["online"] = 0
        player["user_id"] = int(userTable.split(":")[-1])
        account_type = redis.get(FORMAT_ACCOUNT2USER_TABLE % (account))
        if 'robot' in account_type:
            player["account_type"] = '机器人'
        else:
            player["account_type"] = '用户'

        notes = redis.hget(CLUB_PLAYER_NOTES % club_number, account)
        if not notes:
            notes = ''
        player["notes"] = notes

        if account in members:
            player["online"] = 1
        if not last_logout_date.strip():
            player["time"] = u"未登录过"
        else:
            _time = int(time.mktime(time.strptime(last_logout_date, '%Y-%m-%d %H:%M:%S')))
            curtime = int(time.time())
            seco = (curtime - _time)
            mon = seco / 60
            hour = mon / 60
            day = hour / 24
            if day >= 1:
                player["time"] = u"%s天前" % day
            elif hour >= 1:
                player["time"] = u"%s小时前" % hour
            elif mon >= 1:
                player["time"] = u"%s分钟前" % mon
            else:
                player["time"] = u"%s秒前" % seco

        isManager = 0
        data = eval(redis.hget(CLUB_ATTR % club_number, 'club_manager'))
        if account in data:
            isManager = 1
        player.update(
            {
                "isManager": isManager
            }
        )

        player["creator"] = 0
        if item == managerAccount:
            player["isManager"] = 1
            player["creator"] = 1
        player["guest"] = 0

        cardDate = redis.lrange(PLAYER_DAY_USE_CARD % (int(userTable.split(":")[-1]), nowDay), 0,
                                -1)
        if cardDate:
            roomcard_day = 0
            for item in cardDate:
                roomcard_day += int(item.split(';')[0])
            player['roomcard_day'] = roomcard_day
        else:
            player['roomcard_day'] = ''
        player['roomcard_total'] = redis.get(USER4AGENT_CARD % (parentAg, int(userTable.split(":")[-1])))
        player['op'] = [
            {'url': '/admin/agent/clublist/delManager' if player['isManager'] else '/admin/agent/clublist/addManager',
             'txt': '解除管理' if player['isManager'] else '提升管理', 'method': 'POST'},
            {'url': '/admin/agent/clublist/dcuManager', 'txt': '踢出', 'method': 'POST'},
            # {'url': '', 'txt': '同桌管理', 'method': 'GET'},
            # {'url': '', 'txt': '战绩回放', 'method': 'GET'},
            # {'url': '', 'txt': '大赢家', 'method': 'GET'},
        ]
        players.append(player)

    return {'data': players, 'count': len(players)}


def get_AgClubList(redis, agent_id):
    """
    获取亲友圈数据列表
    :param redis:
    :return: {'data': [{}], 'count': int}
    """
    res = []
    nowtime = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    adminTable = AGENT_TABLE % (agent_id)
    agent_type = redis.hget(adminTable, 'type')
    agent_type = convert_util.to_int(agent_type)
    child_member_ids = None
    club_list, res = [], []

    if agent_type == 0:
        club_list = redis.smembers(CLUB_LIST)
    elif agent_type == 1:
        child_member_ids = getAgentAllMemberIds(redis, agent_id)
        if not child_member_ids:
            return {'count': 0, 'data': []}
    else:
        child_member_ids = redis.smembers(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE % (agent_id))
        if not child_member_ids:
            return {'count': 0, 'data': []}

    if child_member_ids:
        for each in child_member_ids:
            account = redis.hget(FORMAT_USER_TABLE % (each), 'account')
            club_list.extend(list(redis.smembers(CLUB_ACCOUNT_LIST % account)))

    for item in set(club_list):
        club = redis.hgetall(CLUB_ATTR % item)
        club['club_id'] = item
        userTable = redis.get(FORMAT_ACCOUNT2USER_TABLE % (club['club_user']))
        avatar_url = redis.hget(userTable, "headImgUrl")
        club['imgurl'] = avatar_url
        if eval(club['club_manager']):
            club_accounts = [redis.get(FORMAT_ACCOUNT2USER_TABLE % (i)) for i in list(eval(club['club_manager']))]
            club['club_manager'] = [redis.hmget(FORMAT_USER_TABLE % (i.split(':')[1]), "nickname") for i in
                                    club_accounts]
        else:
            club['club_manager'] = ''
        club['user_id'] = userTable.split(':')[-1]
        club['nickname'] = redis.hget(FORMAT_USER_TABLE % (userTable.split(':')[-1]), "nickname")
        club_person_number = len(redis.smembers(CLUB_PLAYER_LIST % item)) + 1
        club['count'] = club_person_number
        club['roomcards_day'] = redis.get("club:roomCards:day:%s:%s:total" % (item, nowtime))
        club['roomcards_all'] = redis.get("club:roomCards:all:%s:total" % (item))
        club['op'] = [
            {'url': '/admin/agent/clublist/addUser', 'txt': '添加玩家', 'method': 'POST'},
            {'url': '/admin/agent/clublist/delUser', 'txt': '移除玩家', 'method': 'POST'},
            {'url': '/admin/agent/clublist/audit', 'txt': '审批', 'method': 'GET'},
            {'url': '/admin/agent/clublist/transferUser', 'txt': '转移亲友圈', 'method': 'POST'},
            {'url': '/admin/agent/clublist/showDay', 'txt': '玩家出入记录', 'method': 'GET'},
            {'url': '/admin/agent/clublist/userbanList', 'txt': '同桌管理列表', 'method': 'GET'},
            # {'url': '/admin/agent/clublist/delClub', 'txt': '删除亲友圈', 'method': 'POST'},
        ]
        res.append(club)

    return {'data': res, 'count': len(res)}


def get_AgClubListShowDay(redis, club_id):
    """
    获取亲友圈对应下的玩家退出记录列表
    :param redis:
    :param club_id:
    :return:
    """
    res = []
    club_history = redis.lrange(CLUB_EXIT_PLAYER_LIST % (club_id), 0, -1)
    club_history = sorted(club_history, key=lambda i: i.split(':')[1], reverse=True)
    for i in club_history:
        club_name, time, key, account = i.split(':')
        userTable = redis.get(FORMAT_ACCOUNT2USER_TABLE % club_name)
        club_nickname = redis.hget(FORMAT_USER_TABLE % userTable.split(':')[-1], 'nickname'),

        agentTable = redis.get(FORMAT_ACCOUNT2USER_TABLE % (account))
        agent_nickname = redis.hget(FORMAT_USER_TABLE % agentTable.split(':')[-1], 'nickname'),
        res.append({
            'id': club_id,
            'club_name': ' / '.join([club_name, club_nickname[0]]),
            'club_agent': redis.hget(CLUB_ATTR % (club_id), "club_name"),
            'time': time,
            'key': '管理者踢出' if int(key) else '自己退出',
            'account': ' / '.join([account, agent_nickname[0]]),
        })
    return {'data': res, 'count': len(res)}


def get_AgClubListUserBanList(redis, club_id):
    """
    获取亲友圈对应下的同桌管理列表（禁止同台）
    :param redis:
    :param club_id:
    :return:
    """
    res = []
    userbanlist = redis.hgetall("club:userbanList:%s:hset" % (club_id))
    for v, k in userbanlist.items():
        info = {}
        userTable = redis.hgetall(FORMAT_USER_TABLE % v)
        info['id'] = v
        info['nickname'] = userTable['nickname']
        info['username'] = userTable['account']
        info['clubid'] = club_id
        info['op'] = [
            {'url': '/admin/agent/clublist/userbanList/addUser', 'txt': '添加禁止玩家', 'method': 'POST'},
            {'url': '/admin/agent/clublist/userbanList/delUser', 'txt': '删除禁止玩家', 'method': 'POST'},
            {'url': '/admin/agent/clublist/userbanList/remUser', 'txt': '移除同桌记录', 'method': 'POST'},
        ]
        res.append(info)
    return {'data': res, 'count': len(res)}


def get_AgClubListUserBan(redis, user_id, club_id):
    """
    获取亲友圈对应下的玩家ID对应下的同桌列表
    :param redis:
    :param club_id:
    :return:
    """
    res = []
    userbanlist = redis.hgetall("club:userbanList:%s:hset" % (club_id))
    for i in userbanlist:
        if user_id in i:
            for item in list(eval(userbanlist[i])):
                info = {}
                userTable = redis.hgetall(FORMAT_USER_TABLE % item)
                info['usertype'] = '用户'
                info['id'] = item
                if not userTable:
                    robotTable = redis.keys("users:robot:level:*:%s" % item)[0]
                    userTable = redis.hgetall(robotTable)
                    info['usertype'] = '机器人'
                info['nickname'] = userTable.get('nickname')
                info['username'] = userTable.get('account')
                info['clubid'] = club_id
                info['userid'] = user_id
                info['op'] = [
                    {'url': '/admin/agent/clublist_userban/list/delUser', 'txt': '删除', 'method': 'POST'},
                ]
                res.append(info)
    return {'data': res, 'count': len(res)}


def get_AgClubDissolution(redis, startDate, endDate, ):
    """
    获取已解散亲友圈的列表
    :param redis:
    :return:
    """
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
    now_time = datetime.now()
    clubDissolution = redis.lrange(CLUB_DISSOLUTION, 0, -1)
    clubDissolution = sorted(clubDissolution, key=lambda i: i.split(':')[-1], reverse=True)
    while endDate >= startDate:
        if endDate > now_time:  # 不查没有数据的时间
            endDate -= deltaTime
            continue
        for item in clubDissolution:
            club_number, account, dissolutiondate = item.split(':')
            nowDay = endDate.strftime('%Y-%m-%d')
            if dissolutiondate == nowDay:
                info = {}
                info['club_number'] = club_number
                info['account'] = account
                info['dissolutiondate'] = dissolutiondate
                res.append(info)
        endDate -= deltaTime
    return {'data': res, 'count': len(res)}
