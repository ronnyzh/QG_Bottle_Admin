#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    统计模型
"""
from web_db_define import *
from config.config import *
from common.log import *
from admin import access_module
import agentModel
from model.userModel import *
from datetime import timedelta,datetime
from operator import itemgetter
from common import convert_util
import time
from common.mysql_lj_game import MysqlljgameInterface
#from model.userModel import getAgentAllMemberIds
from itertools import groupby


ACTIVE_OP_LIST = [
        {'url':'/admin/statistics/active/showDay','txt':'查看详细','method':'GET'}
]

def getAllChildAgentId(redis,agentId):
    """
    返回所有下级代理ID
    """
    agentIdList = []
    pipe = redis.pipeline()
    downLines = redis.smembers(AGENT_CHILD_TABLE%(agentId))
    log_debug('[agentModel][Func][getAllChildAgentId] agentId[%s] downlines[%s]'%(agentId,downLines))

    if downLines:
        for downline in downLines:
            agentIdList.append(downline)
            subDownlines = redis.smembers(AGENT_CHILD_TABLE%(downline))
            if subDownlines:
                for subDownline in subDownlines:
                    agentIdList.append(subDownline)

    log_debug('[agentModel][Func][getAllChildAgentId] agentId[%s] allChildIds[%s]'%(agentId,agentIdList))
    return agentIdList

def getDateTotal(redis,agentId,agentIds,endDate,startDate):
    """
    获取某段时间内的总数
    """
    deltaTime = timedelta(1)
    count = 0
    for aid in agentIds:
        nums = redis.get(DAY_ALL_PLAY_COUNT%(endDate,aid))
        if not nums:
            nums = 0
        count+=int(nums)
    #log_debug('[getDateTotal] startDate[%s],endDate[%s] agentIds[%s] count[%s]'%(startDate,endDate,agentIds,count))
    return count

def getCountTotal(redis,agentId,dateStr):
    """
    获取总局数统计数据
    """
    #返回所有下级ID
    parentTable = AGENT_CHILD_TABLE%(agentId)
    agentIds = redis.smembers(parentTable)
    if not agentIds:
        agentIds = [agentId]

    deltaTime = timedelta(1)
    res = []
    totalCount = 0
    for agent_id in agentIds:
        agentDetail = redis.hgetall(AGENT_TABLE%(agent_id))
        count = redis.get(DAY_ALL_PLAY_COUNT%(dateStr,agent_id))
        if not count:
            count = 0
        count = int(count)
        parentTable = AGENT_CHILD_TABLE%(agent_id)
        agent_ids = redis.smembers(parentTable)
        count+=getDateTotal(redis,agent_id,agent_ids,dateStr,dateStr)
        totalCount+=count
        #log_debug('[getAgentActiveReport][FUNC] agentIds[%s] list[%s]'%(agent_id,DAY_AG_LOGIN_COUNT%(agent_id,agentInfo['date'])))

    return int(totalCount)

def get_login_count(redis,selfUid,dateStr,agentIds):
    """
    获取代理当天登录人数统计
    """
    log_debug('--------------------------[%s][%s]'%(selfUid,dateStr))
    login_count = 0
    if int(selfUid) == 1:
        login_count = redis.scard(FORMAT_LOGIN_DATE_TABLE%(dateStr))
    else:
        for _agentId in agentIds:
            count = redis.get(DAY_AG_LOGIN_COUNT%(_agentId,dateStr))
            if not count:
                count = 1
            login_count+=int(count)
    if not login_count:
        login_count = 0
    log_debug('[try get_login_count] agentIds[%s] login_count[%s]'%(agentIds,login_count))
    return int(login_count)

def get_take_count_new(redis,selfUid,dateStr):
    """
    获取代理日消耗砖石统计
    """
    playersData4day = redis.exists('playersData4day:1:%s:count:cache' % dateStr)
    take_count = 0
    agentIdChilds = getAllChildAgentId(redis, selfUid)
    agentIdChilds.append(selfUid)

    if playersData4day:
        playersData4day = eval(redis.get('playersData4day:1:%s:count:cache' % dateStr))
        for each in playersData4day:
            if each.get('parentAg') in agentIdChilds:
                take_count += int(each.get('use_count'))
    else:
        playersData4day = redis.exists('playersData4day:1:%s:cache' % dateStr)
        if playersData4day:
            playersData4day = eval(redis.get('playersData4day:1:%s:cache' % dateStr))
            for each in playersData4day:
                if each.get('parentAg') in agentIdChilds:
                    take_count += int(each.get('use_count'))
        else:
            if selfUid == '1':
                regTable = DAY_ALL_PLAY_ROOM_CARD%(dateStr)
                take_count = redis.get(regTable)
            else:
                take_count = agentModel.getAgentRoomByDay(redis,selfUid,dateStr)
    if not take_count:
        take_count = 0
    log_debug('[try get_take_count] agentIds[%s] take_count[%s]'%(selfUid,take_count))
    return int(take_count)

def get_take_count(redis,selfUid,dateStr):
    """
    获取代理日消耗砖石统计
    """
    if selfUid == '1':
        regTable = DAY_ALL_PLAY_ROOM_CARD%(dateStr)
        take_count = redis.get(regTable)
    else:
        take_count = agentModel.getAgentRoomByDay(redis,selfUid,dateStr)
    if not take_count:
        take_count = 0
    log_debug('[try get_take_count] agentIds[%s] take_count[%s]'%(selfUid,take_count))
    return int(take_count)

def get_active_reports(redis,startDate,endDate,selfUid):
    """
    获取活跃人数数据
    """
    try:
        startDate = datetime.strptime(startDate,'%Y-%m-%d')
        endDate   = datetime.strptime(endDate,'%Y-%m-%d')
    except:
        weekDelTime = timedelta(7)
        weekBefore = datetime.now()-weekDelTime
        startDate = weekBefore
        endDate   = datetime.now()

    deltaTime = timedelta(1)
    if int(selfUid) == 1:
        agentIds = []
    else:
        agentIds = getAllChildAgentId(redis,selfUid)

    res = []
    now_time = datetime.now()
    while endDate >= startDate:
        active_info = {}
        if endDate >= now_time:
            endDate -= deltaTime
            continue
        dateStr = endDate.strftime('%Y-%m-%d')
        login_count = get_login_count(redis,selfUid,dateStr,agentIds)
        take_card  = get_take_count_new(redis,selfUid,dateStr)
        take_count  = getCountTotal(redis,selfUid,dateStr)
        active_info['login_count'] = login_count
        active_info['take_count'] = take_count
        active_info['take_card'] = take_card
        active_info['date'] = dateStr
        active_info['op'] = ACTIVE_OP_LIST

        res.append(active_info)
        endDate -= deltaTime

    return {'data':res, 'count':len(res)}


def get_club_roomcards_reports(redis, startDate, endDate):
    """
    获取亲友圈耗钻统计
    :param redis:
    :param startDate:
    :param endDate:
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
    club_ids = redis.smembers("club:list:set")
    now_time = datetime.now()
    while endDate >= startDate:
        active_info = {}
        if endDate >= now_time:
            endDate -= deltaTime
            continue
        tmp, tmp1 = 0, 0
        dateStr = endDate.strftime('%Y-%m-%d')
        for i in club_ids:
            clubroom_day = redis.get('club:roomCards:day:%s:%s:total' % (i, dateStr))
            if clubroom_day:
                tmp += int(clubroom_day)
            clubroom_all = redis.get("club:roomCards:all:%s:total" % (i))
            if clubroom_all:
                tmp1 += int(clubroom_all)
        active_info['date'] = dateStr
        active_info['clubroom_day'] = tmp
        active_info['clubroom_all'] = tmp1
        active_info['op'] = [{'url': '/admin/statistics/club/showDay', 'txt': '查看当日详细', 'method': 'GET'}]
        res.append(active_info)
        endDate -= deltaTime
    return {'data': res, 'count': len(res)}


def get_login_list(redis,agentId,reg_date,isdel_none = False):
    """
    获取某个时间段注册人数详情
    params:
        [ reg_date ] : 某一天
    """

    registMemberList =  redis.smembers(FORMAT_LOGIN_DATE_TABLE%(reg_date))
    if not registMemberList:
        return []
    adminTable = AGENT_TABLE%(agentId)
    agent_type, aId =redis.hmget(adminTable, ('type', 'id'))
    agent_type = convert_util.to_int(agent_type)
    type2getMemberIds = {
            0     :       getSystemMemberIds,
            1     :       getAgentAllMemberIds
    }

    memberIds = None
    if agent_type == 1:
        memberIds = type2getMemberIds[agent_type](redis,agentId)
        if not memberIds:
            return []
    elif agent_type > 1 :
        memberTable = FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(agentId)
        memberIds = redis.smembers(memberTable)
        if not memberIds:
            return []

    res = []
    member_id_keys = []
    for member in registMemberList:
        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(member)
        member_id_keys.append(account2user_table)
    #获取会员ID
    member_id_lists = [user_id.split(":")[1] for user_id in redis.mget(member_id_keys)]
    for member_id in member_id_lists:
        if memberIds and (member_id not in memberIds) or (member_id.strip() == 'robot'):
            continue
        use_count = redis.hget(PLAYER_DAY_DATA%(member_id,reg_date),'roomCard')
        use_count = convert_util.to_int(use_count)
        if isdel_none and not use_count:
            continue
        table = FORMAT_USER_TABLE%(member_id) #从账号获得账号信息，和旧系统一样
        parentAg = \
                redis.hget(table,'parentAg')

        memberInfo = {
                    'id'            :  member_id,
                    'parentAg'      :  parentAg,
                    'use_count'     :  use_count,
        }

        if parentAg:
            parent_id = redis.hget(AGENT_TABLE%parentAg, 'parent_id')
            memberInfo['top_parent_ag'] = parent_id
        res.append(memberInfo)
    return res

def get_login_list2(redis,agentId,reg_date,isdel_none = False):
    """
    获取某个时间段注册人数详情
    params:
        [ reg_date ] : 某一天
    """

    agent_type = redis.hget(AGENT_TABLE % (agentId), 'type')
    print(agentId, reg_date, isdel_none, agent_type)

    memberIds = None
    if int(agent_type) == 1:
        memberIds = redis.smembers(AGENT_CHILD_TABLE % agentId)
    elif int(agent_type) > 1:
        memberIds = [agentId]

    playersDate4dayList = redis.exists('playersData4day:1:%s:cache' % (reg_date))
    if playersDate4dayList:
        playersDate4dayList = eval(redis.get('playersData4day:1:%s:cache' % (reg_date)))
        playersDate4dayList.sort(key=itemgetter('parentAg', 'id'))
        lstg = groupby(playersDate4dayList, itemgetter('parentAg', 'id'))
        data = []
        for key, group in lstg:
            count = 0
            for g in group:
                count += int(g.get('use_count'))
            if count:
                g['use_count'] = count
                g['account'], g['nickname'] = redis.hmget('users:%s' % (g.get('id')), ('account', 'nickname'))
                if memberIds:
                    if g.get('parentAg') in memberIds:
                        data.append(g)
                else:
                    data.append(g)

    else:
        data = []
    return data

def get_active_reports_history(redis,selfUid,startDate,endDate):
    """
    获取活跃人数数据
    """
    try:
        startDate = datetime.strptime(startDate,'%Y-%m-%d')
        endDate   = datetime.strptime(endDate,'%Y-%m-%d')
    except:
        weekDelTime = timedelta(7)
        weekBefore = datetime.now()-weekDelTime
        startDate = weekBefore
        endDate   = datetime.now()

    deltaTime = timedelta(1)
    # if int(selfUid) == 1:
    #     agentIds = []
    # else:
    #     agentIds = getAllChildAgentId(redis,selfUid)

    res = []
    now_time = datetime.now()
    while endDate >= startDate:
        if endDate >= now_time:
            endDate -= deltaTime
            continue
        dateStr = endDate.strftime('%Y-%m-%d')
        active_infos = get_login_list(redis,selfUid,dateStr,True)
        for info in active_infos:
            info['date'] = dateStr
        # print '[get_active_reports_history] active_info:',active_info
        if active_infos:
            res.extend(active_infos)
        endDate -= deltaTime
    return {'data':res,'count':len(res)}

def statisticsRealTime(redis, start_date, end_date, agentId):
    """
    数据统计-活跃人数总耗钻-MODEL
    """
    adminTable = AGENT_TABLE % (agentId)
    agent_type, aId = redis.hmget(adminTable, ('type', 'id'))
    agent_type = convert_util.to_int(agent_type)

    memberIds = None
    if agent_type == 1:
        memberIds = redis.smembers(AGENT_CHILD_TABLE % aId)
    elif agent_type > 1:
        memberIds = [aId]

    try:
        startDate = datetime.strptime(start_date, '%Y-%m-%d')
        endDate = datetime.strptime(end_date, '%Y-%m-%d')
    except:
        weekDelTime = timedelta(7)
        weekBefore = datetime.now() - weekDelTime
        startDate = weekBefore
        endDate = datetime.now()

    deltaTime = timedelta(1)

    res = []
    now_time = datetime.now()
    while endDate >= startDate:
        if endDate >= now_time:
            endDate -= deltaTime
            continue
        dateStr = endDate.strftime('%Y-%m-%d')
        data = []
        playersCountList = redis.exists('playersData4day:1:%s:count:cache' % (dateStr))
        if playersCountList:
            datas = eval(redis.get('playersData4day:1:%s:count:cache' % (dateStr)))
            if memberIds:
                for g in datas:
                    if g.get('parentAg') in memberIds:
                        data.append(g)
            else:
                for g in datas:
                    data.append(g)
            datas = data
        else:
            playersDate4dayList = redis.exists('playersData4day:1:%s:cache' % (dateStr))
            if playersDate4dayList:
                playersDate4dayList = eval(redis.get('playersData4day:1:%s:cache' % (dateStr)))
                playersDate4dayList.sort(key=itemgetter('parentAg', 'id'))
                lstg = groupby(playersDate4dayList, itemgetter('parentAg', 'id'))
                for key, group in lstg:
                    count = 0
                    for g in group:
                        count += int(g.get('use_count'))
                    if count:
                        g['use_count'] = count
                        g['account'], g['nickname'] = redis.hmget('users:%s' % (g.get('id')), ('account', 'nickname'))
                        if memberIds:
                            if g.get('parentAg') in memberIds:
                                data.append(g)
                        else:
                            data.append(g)
            else:
                data = []
            datas = data
        res.extend(datas)
        endDate -= deltaTime
    active_reports = {'count': len(res), 'data': res}
    return active_reports

def get_roomcard_reports(redis, startDate, endDate):
    """
    获取游戏耗钻数统计
    :param redis:
    :param startDate:
    :param endDate:
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
    game_ids = redis.lrange(GAME_LIST, 0, -1)
    now_time = datetime.now()
    allGame_total = 0
    while endDate >= startDate:
        active_info = {}
        if endDate >= now_time:
            endDate -= deltaTime
            continue
        roomcards_day, roomcards_all = 0, 0
        dateStr = endDate.strftime('%Y-%m-%d')
        for i in game_ids:
            roomcard_day = redis.get('game:roomCards:%s:%s:total' % (i, dateStr))
            if roomcard_day:
                roomcards_day += int(roomcard_day)
            roomcard_all = redis.get("game:roomCards:%s:total" % (i))
            if roomcard_all:
                # print(i,roomcards_all)
                roomcards_all += int(roomcard_all)
        active_info['date'] = dateStr
        active_info['roomcards_day'] = roomcards_day
        active_info['roomcards_all'] = roomcards_all
        active_info['op'] = [{'url': '/admin/statistics/roomcard/showDay', 'txt': '查看当日详细', 'method': 'GET'}]
        res.append(active_info)
        allGame_total += roomcards_day
        endDate -= deltaTime
    if res:
        for item in res:
            if allGame_total:
                baifenbi = "%.2f%%" % (float(item.get('roomcards_day')) / float(allGame_total) * 100)
                all_baifenbi = "%.2f%%" % (float(item.get('roomcards_day')) / float(roomcards_all) * 100)
            else:
                baifenbi = "%.2f%%" % 0
                all_baifenbi = "%.2f%%" % 0
            item.update({'GameBaiFenbi':baifenbi})
            item.update({'all_baifenbi': all_baifenbi})
    return {'data': res, 'count': len(res)}


def get_new_history_active_reports(redis, startDate, endDate,pageNumber,pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey):
    """
    获取活跃人数统计历史（新）
    :param redis:
    :param parentag:
    :return:
    """
    if parentag:
        if redis.exists(AGENT_CHILD_TABLE % (parentag)):
            pag = redis.scard(AGENT_CHILD_TABLE % (parentag))
            if pag > 1:
                parentag = tuple(map(int, redis.smembers(AGENT_CHILD_TABLE % (parentag))))
            else:
                parentag = '(%s)' % list(redis.smembers(AGENT_CHILD_TABLE % (parentag)))[0]
        else:
            parentag = '(%s)' % '-1'

    searchDict = {"user_id": userid, "nickname": nickname, "ag": ag, "clubid": clubid, "roomid": roomid,
                  "gameid": gameid, "cards": cards, "roomkey": roomkey, "parentag": parentag}
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    if pageNumber:
        pageNumber = (pageNumber - 1) * int(pageSize)

    res = []
    if any(searchDict.values()):
        sqlStr = "user_id={user_id} and agent_id={ag} and club_number={clubid} and  room_id={roomid} and game_id={gameid} and cards={cards} and  agent_id in {parentag} and  room_number=\'{roomkey}\' ".format(
            **searchDict)
        searchText = 'and'.join(
            [i for i in sqlStr.split('and') if ('= ') not in i and "=''" not in i and ("in  ") not in i])
        sql = """select cards, room_id, agent_id, room_number,user_id,game_id,club_number,create_time, update_time, is_deleted,id from room_cards where  %s and create_time>='%s' and create_time<='%s' order by create_time desc limit %s,%s""" \
              % (searchText, startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(1) from room_cards where %s and create_time >= '%s' and create_time <='%s'""" \
              % (searchText, startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)
    else:
        sql = """select cards, room_id, agent_id, room_number,user_id,game_id,club_number,create_time, update_time, is_deleted,id from room_cards where create_time>='%s' and create_time<='%s' order by create_time desc limit %s,%s""" \
              % (startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(1) from room_cards where  create_time >= '%s' and create_time <='%s'""" \
              % (startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:
            info = {}
            pageNumber += 1
            info['number'] = pageNumber
            info['create_time'] = time.strftime('%Y-%m-%d', time.localtime(i[7])) if i[7] else ''
            info['id'] = i[4]
            info['account'] = redis.hget(FORMAT_USER_TABLE % (i[4]), "account")
            info['nickname'] = redis.hget(FORMAT_USER_TABLE % (i[4]), "nickname")
            info['room_id'] = i[1]
            info['game_id'] = i[5]
            info['game_name'] = redis.hget(GAME_TABLE % (i[5]), "name")
            info['Ag'] = i[2]
            if i[2]:
                parent_id = redis.hget(AGENT_TABLE % i[2], 'parent_id')
                info['parentAg'] = parent_id
            info['club_id'] = i[6]
            info['use_count'] = i[0]
            info['room_number'] = i[3] if i[3] else ''
            info['op'] = [
                {'url': '/admin/statistics/new/playerroom', 'txt': '玩家房间详情', 'method': 'GET'},
                {'url': '/admin/statistics/new/gamerecord', 'txt': '游戏记录', 'method': 'GET'},
            ]
            res.append(info)
    return {"count": count, "data": res}


def get_new_history_active_sumday_reports(redis, startDate, endDate,pageNumber,pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey):
    """
    统计历史耗钻搜索总数
    :param redis:
    :return:
    """
    if parentag:
        if redis.exists(AGENT_CHILD_TABLE % (parentag)):
            pag = redis.scard(AGENT_CHILD_TABLE % (parentag))
            if pag > 1:
                parentag = tuple(map(int, redis.smembers(AGENT_CHILD_TABLE % (parentag))))
            else:
                parentag = '(%s)' % list(redis.smembers(AGENT_CHILD_TABLE % (parentag)))[0]
        else:
            parentag = '(%s)' % '-1'

    searchDict = {"user_id": userid, "nickname": nickname, "ag": ag, "clubid": clubid, "roomid": roomid,
                  "gameid": gameid, "cards": cards, "roomkey": roomkey, "parentag": parentag}
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    res = []
    if any(searchDict.values()):
        sqlStr = "user_id={user_id} and agent_id={ag} and club_number={clubid} and  room_id={roomid} and game_id={gameid} and cards={cards} and  agent_id in {parentag} and  room_number=\'{roomkey}\' ".format(
            **searchDict)
        searchText = 'and'.join([i for i in sqlStr.split('and') if ('= ') not in i and "=''" not in i and ("in  ") not in i])

        sql = """select sum(cards) from room_cards where  %s and create_time>='%s' and create_time<='%s'""" \
              % (searchText, startDate, endDate)

        results = MysqlljgameInterface.select(sql, fetchmany=False)
    else:
        sql = """select sum(cards) from room_cards where  create_time>='%s' and create_time<='%s'""" \
              % (startDate, endDate)

        results = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:
            info = {}
            if i[0]:
                info['use_count'] = float(i[0])
                res.append(info)
            else:
                info['use_count'] = 0
                res.append(info)
    return {'data': res}


def get_roomcard_rcday_reports(redis, startDate, endDate):
    """
    获取游戏耗钻数统计-（查询某段时间的数据）
    :param redis:
    :param startDate:
    :param endDate:
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
    game_ids = redis.lrange(GAME_LIST, 0, -1)
    now_time = datetime.now()

    gameTotal_Day, AllGameBaiFenbi = 0, 0
    while endDate >= startDate:
        if endDate >= now_time:
            endDate -= deltaTime
            continue
        dateStr = endDate.strftime('%Y-%m-%d')
        for i in game_ids:
            rcday = redis.get("game:roomCards:%s:%s:total" % (i, dateStr))
            if not rcday:
                rcday = 0
            roomcard_all = redis.get("game:roomCards:%s:total" % (i))
            if roomcard_all:
                AllGameBaiFenbi += int(roomcard_all)
            gameTotal_Day += int(rcday)
            res.append({
                'id': i,
                'gamename': redis.hget('games:id:%s' % (i), 'name'),
                'roomcards_day': rcday,
                'time': dateStr,
            })
        endDate -= deltaTime
    ids = map(lambda x: x.get("id"), res)
    var = map(lambda x: x.get("roomcards_day"), res)
    zips = zip(ids, var)
    temp = dict()
    temp1 = list()
    for items in zips:
        if items[0] not in temp:
            temp[items[0]] = int(items[1])
        else:
            temp[items[0]] += int(items[1])

    for v, k in temp.items():
        temp1.append(
            {
                'gameid': v,
                'roomcards_day': k,
                'gamename': redis.hget('games:id:%s' % (v), 'name'),
                'GameBaiFenbi': "%.2f%%" % (float(k) / float(gameTotal_Day) * 100) if gameTotal_Day else "%.2f%%" %(0),
                'AllGameBaiFenbi': "%.2f%%" % (float(k) / float(AllGameBaiFenbi) * 100) if AllGameBaiFenbi else "%.2f%%" % (0)
             })
    return {'data': temp1, 'count': len(temp1)}


def get_new_history_active_member_reports(redis, startDate, endDate,pageNumber,pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey):
    """
    获取活跃人数统计历史(会员） -- mysql查询 -- 据按照会员来分组显示
    :param redis:
    :return:
    """
    if parentag:
        if redis.exists(AGENT_CHILD_TABLE % (parentag)):
            pag = redis.scard(AGENT_CHILD_TABLE % (parentag))
            if pag > 1:
                parentag = tuple(map(int, redis.smembers(AGENT_CHILD_TABLE % (parentag))))
            else:
                parentag = '(%s)' % list(redis.smembers(AGENT_CHILD_TABLE % (parentag)))[0]
        else:
            parentag = '(%s)' % '-1'

    searchDict = {"user_id": userid, "nickname": nickname, "ag": ag, "clubid": clubid, "roomid": roomid,
                  "gameid": gameid, "cards": cards, "roomkey": roomkey, "parentag": parentag}
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    if pageNumber:
        pageNumber = (pageNumber - 1) * int(pageSize)

    res = []

    if any(searchDict.values()):
        sqlStr = "user_id={user_id} and agent_id={ag} and club_number={clubid} and  room_id={roomid} and game_id={gameid} and cards={cards} and  agent_id in {parentag} and  room_number=\'{roomkey}\' ".format(
            **searchDict)
        searchText = 'and'.join(
            [i for i in sqlStr.split('and') if ('= ') not in i and "=''" not in i and ("in  ") not in i])
        sql = """select create_time, user_id, agent_id,group_concat(club_number),group_concat(room_id), group_concat(game_id),sum(cards), count(room_number),group_concat(room_number) from room_cards where  %s and create_time>='%s' and create_time<='%s' group by user_id order by create_time desc limit %s,%s""" \
              % (searchText, startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(*) as count from (SELECT count(*) FROM room_cards where %s and  create_time >= '%s' and create_time <='%s' GROUP BY user_id ) a""" \
              % (searchText, startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)
    else:
        sql = """select create_time, user_id, group_concat(agent_id),group_concat(club_number),group_concat(room_id), group_concat(game_id),sum(cards), count(distinct room_number),group_concat(room_number) from room_cards where create_time>='%s' and create_time<='%s' group by user_id order by create_time desc limit %s,%s""" \
              % (startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)
        print(sql)

        sql = """select count(*) as count from (SELECT count(*) FROM room_cards where  create_time >= '%s' and create_time <='%s' GROUP BY user_id ) a""" \
              % (startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:

            info = {}
            pageNumber += 1
            info['number'] = pageNumber
            info['create_time'] = time.strftime('%Y-%m-%d', time.localtime(i[0])) if i[0] else ''
            info['id'] = i[1]
            info['Ag'] = join_history_data(i[2], 3)
            info['club_id'] = join_history_data(i[3], 3)
            info['room_id'] = join_history_data(i[4], 3)
            info['game_id'] = join_history_data([ redis.hget(GAME_TABLE % each, "name") for each in list(set(i[5].split(','))) if redis.hget(GAME_TABLE % each, "name") ],3)
            info['use_count'] = float(i[6])
            info['room_set'] = join_history_data(i[8], 3)
            info['account'] = redis.hget(FORMAT_USER_TABLE % (i[1]), "account")
            info['nickname'] = redis.hget(FORMAT_USER_TABLE % (i[1]), "nickname")
            if i[2]:
                parent_id = [ str(redis.hget(AGENT_TABLE % (each), "parent_id")) for  each in list(set(i[2].split(','))) if redis.hget(AGENT_TABLE % (each), "parent_id")]
                info['parentAg'] = join_history_data(parent_id, 3)
            info['op'] = [

            ]
            res.append(info)
    return {"count": count, "data": res}


def get_new_history_active_agent_reports(redis, startDate, endDate,pageNumber,pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey):
    """
    获取活跃人数统计历史(公会） -- mysql查询 -- 按照公会来分组显示
    :param redis:
    :return:
    """
    if parentag:
        if redis.exists(AGENT_CHILD_TABLE % (parentag)):
            pag = redis.scard(AGENT_CHILD_TABLE % (parentag))
            if pag > 1:
                parentag = tuple(map(int, redis.smembers(AGENT_CHILD_TABLE % (parentag))))
            else:
                parentag = '(%s)' % list(redis.smembers(AGENT_CHILD_TABLE % (parentag)))[0]
        else:
            parentag = '(%s)' % '-1'

    searchDict = {"user_id": userid, "nickname": nickname, "ag": ag, "clubid": clubid, "roomid": roomid,
                  "gameid": gameid, "cards": cards, "roomkey": roomkey, "parentag": parentag}
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    if pageNumber:
        pageNumber = (pageNumber - 1) * int(pageSize)

    res = []

    if any(searchDict.values()):
        sqlStr = "user_id={user_id} and agent_id={ag} and club_number={clubid} and  room_id={roomid} and game_id={gameid} and cards={cards} and  agent_id in {parentag} and  room_number=\'{roomkey}\' ".format(
            **searchDict)
        searchText = 'and'.join(
            [i for i in sqlStr.split('and') if ('= ') not in i and "=''" not in i and ("in  ") not in i])
        sql = """select create_time, agent_id, group_concat(user_id), group_concat(club_number), group_concat(room_id) ,group_concat(game_id), sum(cards), group_concat(room_number) from room_cards where  %s and create_time>='%s' and create_time<='%s' group by agent_id order by create_time desc limit %s,%s""" \
              % (searchText, startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(*) as count from (SELECT count(*) FROM room_cards where %s and  create_time >= '%s' and create_time <='%s' GROUP BY agent_id ) a""" \
              % (searchText, startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)
    else:
        sql = """select create_time, agent_id, group_concat(user_id), group_concat(club_number), group_concat(room_id) ,group_concat(game_id), sum(cards), group_concat(room_number) from room_cards   where create_time>='%s' and create_time<='%s' group by agent_id order by create_time desc limit %s,%s""" \
              % (startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(*) as count from (SELECT count(*) FROM room_cards where  create_time >= '%s' and create_time <='%s' GROUP BY agent_id ) a""" \
              % (startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:
            info = {}
            pageNumber += 1
            info['number'] = pageNumber
            info['create_time'] = time.strftime('%Y-%m-%d', time.localtime(i[0])) if i[0] else ''
            info['Ag'] = i[1]
            info['user_id'] = join_history_data(i[2], 3)
            info['club_id'] = join_history_data(i[3], 3)
            info['room_id'] = join_history_data(i[4], 3)
            info['game_id'] = join_history_data([ redis.hget(GAME_TABLE % each, "name") for each in list(set(i[5].split(','))) if redis.hget(GAME_TABLE % each, "name") ],3)
            info['use_count'] = float(i[6])
            info['roomkey'] = join_history_data(i[7], 3)
            if i[2]:
                parent_id = redis.hget(AGENT_TABLE % i[1], 'parent_id')
                info['parentAg'] = parent_id
            info['op'] = [

            ]
            res.append(info)
    return {"count": count, "data": res}


def get_new_history_active_club_reports(redis, startDate, endDate,pageNumber,pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey):
    """
    获取活跃人数统计历史(亲友圈） -- mysql查询 -- 按照亲友圈来分组显示
    :param redis:
    :return:
    """
    if parentag:
        if redis.exists("agents:id:%s:child" % (parentag)):
            pag = redis.scard("agents:id:%s:child" % (parentag))
            if pag > 1:
                parentag = tuple(map(int, redis.smembers("agents:id:%s:child" % (parentag))))
            else:
                parentag = '(%s)' % list(redis.smembers("agents:id:%s:child" % (parentag)))[0]
        else:
            parentag = '(%s)' % '-1'

    searchDict = {"user_id": userid, "nickname": nickname, "ag": ag, "clubid": clubid, "roomid": roomid,
                  "gameid": gameid, "cards": cards, "roomkey": roomkey, "parentag": parentag}
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    if pageNumber:
        pageNumber = (pageNumber - 1) * int(pageSize)

    res = []

    if any(searchDict.values()):
        sqlStr = "user_id={user_id} and agent_id={ag} and club_number={clubid} and  room_id={roomid} and game_id={gameid} and cards={cards} and  agent_id in {parentag} and  room_number=\'{roomkey}\' ".format(
            **searchDict)
        searchText = 'and'.join(
            [i for i in sqlStr.split('and') if ('= ') not in i and "=''" not in i and ("in  ") not in i])
        sql = """select create_time, club_number, group_concat(distinct user_id), group_concat(distinct agent_id) ,group_concat(room_id),group_concat(game_id), sum(cards) ,group_concat(room_number) from room_cards where  %s and create_time>='%s' and create_time<='%s' group by club_number order by create_time desc limit %s,%s""" \
              % (searchText, startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(*) as count from (SELECT count(*) FROM room_cards where %s and  create_time >= '%s' and create_time <='%s' GROUP BY club_number ) a""" \
              % (searchText, startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)
    else:
        sql = """select create_time, club_number, group_concat(distinct user_id), group_concat(distinct agent_id) ,group_concat(room_id),group_concat(game_id), sum(cards) ,group_concat(room_number) from room_cards where create_time>='%s' and create_time<='%s' group by club_number order by create_time desc limit %s,%s""" \
              % (startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(*) as count from (SELECT count(*) FROM room_cards where  create_time >= '%s' and create_time <='%s' GROUP BY club_number ) a""" \
              % (startDate, endDate)

        count = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:
            info = {}
            pageNumber += 1
            info['number'] = pageNumber
            info['create_time'] = time.strftime('%Y-%m-%d', time.localtime(i[0])) if i[0] else ''
            info['club_id'] = i[1]
            info['id'] = join_history_data(i[2], 3)
            info['Ag'] = join_history_data(i[3], 3)
            info['room_id'] = join_history_data(i[4], 3)
            info['game_id'] = join_history_data([ redis.hget(GAME_TABLE % each, "name") for each in list(set(i[5].split(','))) if redis.hget(GAME_TABLE % each, "name") ],3)
            info['use_count'] = float(i[6])
            info['roomkey'] = join_history_data(i[7], 3)
            if i[3]:
                parent_id = [str(redis.hget(AGENT_TABLE % (each), "parent_id")) for each in list(set(i[3].split(','))) if redis.hget(AGENT_TABLE % (each), "parent_id")]
                info['parentAg'] = join_history_data(parent_id, 3)
            info['op'] = [

            ]
            res.append(info)
    return {"count": count, "data": res}

def get_new_history_active_room_reports(redis, startDate, endDate,pageNumber,pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey):
    """
    获取活跃人数统计历史(房间） -- mysql查询 -- 按照房间来分组显示
    :param redis:
    :return:
    """
    if parentag:
        if redis.exists("agents:id:%s:child" % (parentag)):
            pag = redis.scard("agents:id:%s:child" % (parentag))
            if pag > 1:
                parentag = tuple(map(int, redis.smembers("agents:id:%s:child" % (parentag))))
            else:
                parentag = '(%s)' % list(redis.smembers("agents:id:%s:child" % (parentag)))[0]
        else:
            parentag = '(%s)' % '-1'

    searchDict = {"user_id": userid, "nickname": nickname, "ag": ag, "clubid": clubid, "roomid": roomid,
                  "gameid": gameid, "cards": cards, "roomkey": roomkey, "parentag": parentag}
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    if pageNumber:
        pageNumber = (pageNumber - 1) * int(pageSize)

    res = []

    if any(searchDict.values()):
        sqlStr = "user_id={user_id} and agent_id={ag} and club_number={clubid} and  room_id={roomid} and game_id={gameid} and cards={cards} and  agent_id in {parentag} and  room_number=\'{roomkey}\' ".format(
            **searchDict)
        searchText = 'and'.join(
            [i for i in sqlStr.split('and') if ('= ') not in i and "=''" not in i and ("in  ") not in i])
        sql = """select create_time, room_id, group_concat(user_id), group_concat(agent_id) , group_concat(club_number), group_concat(game_id), sum(cards) ,group_concat(room_number) from room_cards where  %s and create_time>='%s' and create_time<='%s' group by room_id order by create_time desc limit %s,%s""" \
              % (searchText, startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)
        print(sql)

        sql = """select count(*) as count from (SELECT count(*) FROM room_cards where %s and  create_time >= '%s' and create_time <='%s' GROUP BY room_id ) a""" \
              % (searchText, startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)
    else:
        sql = """select create_time, room_id, group_concat(user_id), group_concat(agent_id), group_concat(club_number), group_concat(game_id), sum(cards) ,group_concat(room_number) from room_cards  where create_time>='%s' and create_time<='%s' group by room_id order by create_time desc limit %s,%s""" \
              % (startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(*) as count from (SELECT count(*) FROM room_cards where  create_time >= '%s' and create_time <='%s' GROUP BY room_id ) a""" \
              % (startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:
            info = {}
            pageNumber += 1
            info['number'] = pageNumber
            info['create_time'] = time.strftime('%Y-%m-%d', time.localtime(i[0])) if i[0] else ''
            info['room_id'] = i[1]
            info['id'] = join_history_data(i[2], 3)
            info['Ag'] = join_history_data(i[3], 3)
            info['club_id'] = join_history_data(i[4], 3)
            info['game_id'] = join_history_data([ redis.hget(GAME_TABLE % each, "name") for each in list(set(i[5].split(','))) if redis.hget(GAME_TABLE % each, "name") ],3)
            info['use_count'] = float(i[6])
            info['roomkey'] = join_history_data(i[7], 3)
            if i[3]:
                parent_id = [str(redis.hget(AGENT_TABLE % (each), "parent_id")) for each in list(set(i[3].split(','))) if redis.hget(AGENT_TABLE % (each), "parent_id")]
                info['parentAg'] = join_history_data(parent_id, 3)
            info['op'] = [

            ]
            res.append(info)
    return {"count": count, "data": res}


def get_new_history_active_game_reports(redis, startDate, endDate,pageNumber,pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey):
    """
    获取活跃人数统计历史(游戏） -- mysql查询 -- 按照游戏来分组显示
    :param redis:
    :return:
    """
    if parentag:
        if redis.exists("agents:id:%s:child" % (parentag)):
            pag = redis.scard("agents:id:%s:child" % (parentag))
            if pag > 1:
                parentag = tuple(map(int, redis.smembers("agents:id:%s:child" % (parentag))))
            else:
                parentag = '(%s)' % list(redis.smembers("agents:id:%s:child" % (parentag)))[0]
        else:
            parentag = '(%s)' % '-1'

    searchDict = {"user_id": userid, "nickname": nickname, "ag": ag, "clubid": clubid, "roomid": roomid,
                  "gameid": gameid, "cards": cards, "roomkey": roomkey, 'parentag': parentag}
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    if pageNumber:
        pageNumber = (pageNumber - 1) * int(pageSize)

    res = []

    if any(searchDict.values()):
        sqlStr = "user_id={user_id} and agent_id={ag} and club_number={clubid} and  room_id={roomid} and game_id={gameid} and cards={cards} and  agent_id in {parentag} and  room_number=\'{roomkey}\' ".format(
            **searchDict)
        searchText = 'and'.join(
            [i for i in sqlStr.split('and') if ('= ') not in i and "=''" not in i and ("in  ") not in i])
        sql = """select create_time, game_id, group_concat(user_id), group_concat(agent_id), group_concat(club_number), sum(cards) ,group_concat(room_number), group_concat(room_id) from room_cards where  %s and create_time>='%s' and create_time<='%s' group by game_id order by create_time desc limit %s,%s""" \
              % (searchText, startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(*) as count from (SELECT count(*) FROM room_cards where %s and  create_time >= '%s' and create_time <='%s' GROUP BY game_id ) a""" \
              % (searchText, startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)
    else:
        sql = """select create_time, game_id, group_concat(user_id), group_concat(agent_id), group_concat(club_number), sum(cards) ,group_concat(room_number), group_concat(room_id) from room_cards  where create_time>='%s' and create_time<='%s' group by game_id order by create_time desc limit %s,%s""" \
              % (startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(*) as count from (SELECT count(*) FROM room_cards where  create_time >= '%s' and create_time <='%s' GROUP BY game_id ) a""" \
              % (startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:
            info = {}
            pageNumber += 1
            info['number'] = pageNumber
            info['create_time'] = time.strftime('%Y-%m-%d', time.localtime(i[0])) if i[0] else ''
            info['game_id'] = i[1]
            info['game_name'] = redis.hget('games:id:%s' % (i[1]), "name")
            info['id'] = join_history_data(i[2], 3)
            info['Ag'] = join_history_data(i[3], 3)
            info['club_id'] = join_history_data(i[4], 3)
            info['use_count'] = float(i[5])
            info['roomkey'] = join_history_data(i[6], 3)
            info['room_id'] = join_history_data(i[7], 3)
            if i[3]:
                parent_id = [str(redis.hget(AGENT_TABLE % (each), "parent_id")) for each in list(set(i[3].split(',')))
                             if redis.hget(AGENT_TABLE % (each), "parent_id")]
                info['parentAg'] = join_history_data(parent_id, 3)
            info['op'] = [

            ]
            res.append(info)
    return {"count": count, "data": res}

def get_new_history_active_roomnumber_reports(redis, startDate, endDate,pageNumber,pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey):
    """
    获取活跃人数统计历史(房间标识） -- mysql查询 -- 按照房间标识来分组显示
    :param redis:
    :return:
    """
    if parentag:
        if redis.exists("agents:id:%s:child" % (parentag)):
            pag = redis.scard("agents:id:%s:child" % (parentag))
            if pag > 1:
                parentag = tuple(map(int, redis.smembers("agents:id:%s:child" % (parentag))))
            else:
                parentag = '(%s)' % list(redis.smembers("agents:id:%s:child" % (parentag)))[0]
        else:
            parentag = '(%s)' % '-1'

    searchDict = {"user_id": userid, "nickname": nickname, "ag": ag, "clubid": clubid, "roomid": roomid,
                  "gameid": gameid, "cards": cards, "roomkey": roomkey, 'parentag': parentag}
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    if pageNumber:
        pageNumber = (pageNumber - 1) * int(pageSize)

    res = []

    if any(searchDict.values()):
        sqlStr = "user_id={user_id} and agent_id={ag} and club_number={clubid} and  room_id={roomid} and game_id={gameid} and cards={cards} and  agent_id in {parentag} and  room_number=\'{roomkey}\' ".format(
            **searchDict)
        searchText = 'and'.join(
            [i for i in sqlStr.split('and') if ('= ') not in i and "=''" not in i and ("in  ") not in i])
        sql = """select create_time, room_number, group_concat(user_id), group_concat(agent_id), group_concat(club_number), group_concat(room_id), group_concat(game_id) ,sum(cards) from room_cards where  %s and create_time>='%s' and create_time<='%s' group by room_number order by create_time desc limit %s,%s""" \
              % (searchText, startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(1) from room_cards where %s and create_time >= '%s' and create_time <='%s' group by room_number""" \
              % (searchText, startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)
    else:
        sql = """select create_time, room_number, group_concat(user_id), group_concat(agent_id), group_concat(club_number), group_concat(room_id), group_concat(game_id) ,sum(cards) from room_cards  where create_time>='%s' and create_time<='%s'  group by room_number order by create_time desc limit %s,%s""" \
              % (startDate, endDate, pageNumber, pageSize)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        sql = """select count(*) as count from (SELECT count(*) FROM room_cards  where  create_time >= '%s' and create_time <='%s'  GROUP BY room_number ) a""" \
              % (startDate, endDate)
        count = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:
            info = {}
            pageNumber += 1
            info['number'] = pageNumber
            info['create_time'] = time.strftime('%Y-%m-%d', time.localtime(i[0])) if i[0] else ''
            info['room_number'] = i[1]
            info['id'] = join_history_data(i[2], 3)
            info['Ag'] = join_history_data(i[3], 3)
            info['club_id'] = join_history_data(i[4], 3)
            info['room_id'] = join_history_data(i[5], 3)
            info['game_id'] = join_history_data([ redis.hget(GAME_TABLE % each, "name") for each in list(set(i[6].split(','))) if redis.hget(GAME_TABLE % each, "name") ],3)
            info['use_count'] = float(i[7])
            if i[3]:
                parent_id = [str(redis.hget(AGENT_TABLE % (each), "parent_id")) for each in list(set(i[3].split(',')))
                             if redis.hget(AGENT_TABLE % (each), "parent_id")]
                info['parentAg'] = join_history_data(parent_id, 3)
            info['op'] = [

            ]
            res.append(info)
    return {"count": count, "data": res}

def join_history_data(res, slice):
    try:
        res = set(res.split(','))
    except:
        pass
    if len(res) > 5:
        return '%s<br>......' % '<br>'.join(list(res)[:slice])
    else:
        return '%s' % '<br>'.join(list(res)[:slice])