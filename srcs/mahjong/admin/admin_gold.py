# coding:utf-8
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    金币场
"""
from bottle import *
from admin import admin_app
from config.config import STATIC_LAYUI_PATH, STATIC_ADMIN_PATH, BACK_PRE, RES_VERSION
from common.utilt import *
from common.log import *
from datetime import datetime
from web_db_define import *
from model.protoclModel import *
from model.goldModel import *
from common import convert_util
from access_module import *

import hashlib
import json


@admin_app.get('/gold/field')
@checkAccess
def getGoldField(redis, session):
    lang = getLang()
    # isList  = request.GET.get('list','').strip()
    # search = request.GET.get('search','').strip()

    fields = ('isList', 'startDate', 'endDate', 'pageSize', 'pageNumber', 'searchId', 'sort_name', 'sort_method')
    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))
    if not pageNumber:
        pageNumber = 1
    else:
        pageNumber = convert_util.to_int(pageNumber)
    if isList:
        return getGoldListInfos(redis, searchId, int(pageSize), int(pageNumber))
    else:
        info = {
            'title': '金币场用户数据总表',
            'listUrl': BACK_PRE + '/gold/field?isList=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
            'searchTxt': '输入玩家账号搜索',
            'sort_bar': True,  # 开启排序
            'member_page': True,  # 开启排序
            'cur_page': pageNumber,
            'cur_size': pageSize,
            'remove_type': '',
        }
        return template('admin_gold_field', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/gold/operate')
@checkAccess
def getGoldOperate(redis, session):
    """
    金币场运营总表
    """
    curTime = datetime.now()
    lang = getLang()
    isList = request.GET.get('list', '').strip()
    selfUid = request.GET.get('id', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    date = request.GET.get('date', '').strip()
    niuniu_type = request.GET.get('niuniu_type', '1').strip()

    if isList:
        report = getGoldOperateInfos(redis, selfUid, startDate, endDate, niuniu_type)
        return json.dumps(report)
    else:
        online_people_sum, online_room_num, user_current_gold_sum = getOnlineOperateInfos(redis)
        info = {
            'title': '金币场运营总表',
            'listUrl': BACK_PRE + '/gold/operate?list=1&niuniu_type=' + niuniu_type,
            'searchTxt': '',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
            'online_people_sum': online_people_sum,
            'online_room_num': online_room_num,
            'user_current_gold_sum': user_current_gold_sum,
            'niuniu_type': niuniu_type,

        }

    return template('admin_gold_operate', PAGE_LIST=PAGE_LIST, info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/gold/ai')
@checkAccess
def getGoldAI(redis, session):
    """
        机器人数据表
    """
    curTime = datetime.now()
    lang = getLang()
    isList = request.GET.get('list', '').strip()
    selfUid = request.GET.get('id', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    date = request.GET.get('date', '').strip()
    # B档 或 D档
    grade = request.GET.get('grade', 'b').strip()

    if isList:
        report = getGoldAIInfos(redis, selfUid, startDate, endDate, grade)
        return json.dumps(report)
    else:
        online_ai_sum, online_ai_room_num, cur_ai_gold_sum = getOnlineAIInfos(redis)
        info = {
            'title': '金币场AI数据表',
            'listUrl': BACK_PRE + '/gold/ai?list=1',
            'searchTxt': '',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
            'online_ai_sum': online_ai_sum,
            'online_ai_room_num': online_ai_room_num,
            'cur_ai_gold_sum': cur_ai_gold_sum,
            'grade': grade,

        }

    return template('admin_gold_ai', PAGE_LIST=PAGE_LIST, info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/gold/buy_record')
def get_buy_record(redis, session):
    """
        购买金币记录
    """
    lang = getLang()
    isList = request.GET.get('list', '').strip()
    account = request.GET.get('account', '').strip()
    if isList:
        if not account:
            res = []
        else:
            res = getBuyGoldRecord(redis, account)
        return {'code': 0, 'data': res}

    info = {
        "title": '购买金币流水',
        "tableUrl": BACK_PRE + "/gold/buy_record?list=%s&account=%s" % (1, account),
        'searchTxt': 'uid',
        'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
        'back_pre': BACK_PRE,
        'backUrl': BACK_PRE + "/gold/filed",
    }
    return template('admin_gold_buy_record', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/gold/journal')
def get_journal(redis, session):
    """
        金币游戏记录
    """
    lang = getLang()
    isList = request.GET.get('list', '').strip()
    account = request.GET.get('account', '').strip()
    if isList:
        if not account:
            res = []
        else:
            res = getJournal(redis, account)
        return {'code': 0, 'data': res}

    info = {
        "title": '金币战绩流水',
        "tableUrl": BACK_PRE + "/gold/journal?list=%s&account=%s" % (1, account),
        'searchTxt': 'uid',
        'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
        'back_pre': BACK_PRE,
        'backUrl': BACK_PRE + "/gold/filed",
    }
    return template('admin_gold_journal', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/gold/buy_record_info')
def get_buy_record_info(redis, session):
    """
        购买金币人数
    """
    lang = getLang()
    isList = request.GET.get('list', '').strip()
    date = request.GET.get('date', '').strip()
    if isList:
        if not date:
            res = []
        else:
            res = getBuyGoldAccounts(redis, date)
        return {'code': 0, 'data': res}

    info = {
        "title": '购买金币玩家',
        "tableUrl": BACK_PRE + "/gold/buy_record_info?list=%s&date=%s" % (1, date),
        'searchTxt': 'uid',
        'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
        'back_pre': BACK_PRE,
        'backUrl': BACK_PRE + "/gold/operate",
    }
    return template('admin_gold_buy_record_info', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/gold/log')
@checkAccess
def getGoldLog(redis, session):
    """
        mysql金币流水表
    """

    lang = getLang()
    isList = request.GET.get('list', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    uid = request.GET.get('uid', '').strip()

    if isList:
        report = get_gold_log(startDate, endDate, uid)
        return json.dumps(report)
    else:

        info = {
            'title': '金币流水表',
            'listUrl': BACK_PRE + '/gold/log?list=1',
            'searchTxt': '',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,

        }

    return template('admin_gold_log', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/gold/amount')
@checkAccess
def getGoldAmount(redis, session):
    """
    mysql - amount 显示'机器人表'各项数据
    :param redis: redis
    :param session: session
    :return: json if isList else template
    """
    lang = getLang()
    fields = ('islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText')

    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))
    if not pageNumber:
        pageNumber = 0
    else:
        pageNumber = convert_util.to_int(pageNumber)

    if islist:
        report = get_gold_amount(startDate, endDate, int(pageSize), int(pageNumber), searchText, redis=redis)
        return json.dumps(report)
    else:
        info = {
            'title': '机器人表',
            'listUrl': BACK_PRE + '/gold/amount?islist=1',
            'sumListUrl': BACK_PRE + '/game/amount/sum/list?list=1',
            'dayListUrl': BACK_PRE + '/game/amount/day/list?list=1',
            'graphListUrl': BACK_PRE + '/game/amount/graph/list?list=1',
            'searchTxt': '',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
            'STARTDATE': startDate,
            'sort_bar': True,
            'member_page': True,
            'cur_page': pageNumber,
            'cur_size': pageSize,
            'remove_type': '',
        }

    return template('admin_gold_amount', info=info, lang=lang, RES_VERSION=RES_VERSION)

@admin_app.get('/game/amount/day/list')
def getGoldAmountDayList(redis, session):
    """
    计算某一段时间内 mysql - amount 统计表中 '投放之前的金额(preBalanc),投放之后的金额(afterBalance),减少/增加的金额(balance)'的总数
    :param redis:
    :param session:
    :return:
    """
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    data = get_gold_amount_daylist(redis, startDate, endDate)
    return json.dumps(data)


@admin_app.get('/game/amount/sum/list')
def getGoldAmountSumList(redis, session):
    """
    mysql - amount 统计表中 '投放之前的金额(preBalanc),投放之后的金额(afterBalance),减少/增加的金额(balance)'的总数
    :param redis:
    :param session:
    :return:
    """
    data = get_gold_amount_sumlist(redis)
    return json.dumps(data)

@admin_app.get('/game/amount/graph/list')
def getGoldAmountGraphList(redis, session):
    """
    统计图表数据
    计算某一段时间内 mysql - amount 统计表中 '投放之前的金额(preBalanc),投放之后的金额(afterBalance),减少/增加的金额(balance)'的总数
    :param redis:
    :param session:
    :return:
    """
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))
    type = request.GET.get('gametype', '').strip()
    gameid = request.GET.get('gameid', '').strip()

    data = get_gold_amount_graphlist(redis, startDate, endDate, type, gameid)
    return json.dumps(data)


@admin_app.get('/gold/roomcost')
@checkAccess
def getGoldRoomCost(redis, session):
    """
    mysql - roomCost 显示'房费表'各项数据
    :param redis: redis
    :param session: session
    :return: json if isList else template
    """

    lang = getLang()
    fields = ('islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText')

    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))

    if not pageNumber:
        pageNumber = 0
    else:
        pageNumber = convert_util.to_int(pageNumber)

    if islist:
        report = get_gold_roomcost(startDate, endDate, int(pageSize), int(pageNumber), searchText, limit=True)
        return json.dumps(report)
    else:

        info = {
            'title': '金币场房费表',
            'listUrl': BACK_PRE + '/gold/roomcost?islist=1',
            'sumListUrl': BACK_PRE + '/game/roomcost/sum/list?list=1',
            'dayListUrl': BACK_PRE + '/game/roomcost/day/list?list=1',
            'dailyListUrl': BACK_PRE + '/game/roomcost/daily/list?list=1',
            'graphListUrl': BACK_PRE + '/game/roomcost/graph/list?list=1',
            'searchTxt': '',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
            'STARTDATE': startDate,
            'sort_bar': True,
            'member_page': True,
            'cur_page': pageNumber,
            'cur_size': pageSize,
            'remove_type': '',
        }

    return template('admin_gold_roomcost', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/game/roomcost/sum/list')
def getGoldRoomcostSumList(redis, session):
    """
    mysql - roomCost 统计表中 '房费(pay_ment)’ 的总数
    :param redis:
    :param session:
    :return:
    """
    data = get_gold_roomcost_sumlist(redis)
    return json.dumps(data)


@admin_app.get('/game/roomcost/day/list')
def getGoldRoomcostDayList(redis, session):
    """
    计算某一段时间内
    mysql - roomCost 统计表中 '房费(pay_ment)’ 的总数
    :param redis:
    :param session:
    :return:
    """
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    data = get_gold_roomcost_daylist(redis, startDate, endDate)
    return json.dumps(data)


@admin_app.get('/game/roomcost/daily/list')
def getGoldRoomcostDailyList(redis, session):
    """
    计算每天内
    mysql - roomCost 统计表中 '房费(pay_ment)' 的总数
    :param redis:
    :param session:
    :return:
    """
    res = []
    sql = """select FROM_UNIXTIME(create_time,'%Y-%m-%d'), 
sum(
if((is_robot=0),pay_ment,0)
),
sum(
if((is_robot=1),pay_ment,0)
),
sum(pay_ment)
from roomCost  GROUP BY from_unixtime(create_time,'%Y-%m-%d') ORDER BY create_time desc"""
    results = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:
            info = {}
            info['datetime'] = i[0]
            info['user_pay_ment'] = float(i[1]) if i[1] else 0
            info['robot_pay_ment'] = float(i[2]) if i[2] else 0
            info['pay_ment'] = float(i[3]) if i[3] else 0
            res.append(info)
    data = {'data': res, 'count': len(res)}
    return json.dumps(data)


@admin_app.get('/game/roomcost/graph/list')
def getGoldRoomcostGraphList(redis, session):
    """
    统计图表数据
    计算某一段时间内 mysql - roomCost 统计表中 '房费(pay_ment)’ 的总数
    :param redis:
    :param session:
    :return:
    """
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))
    gameid = request.GET.get('gameid', '').strip()
    gametype = request.GET.get('gametype', '').strip()

    data = get_gold_roomcost_graphlist(redis, startDate, endDate, gametype, gameid)
    return json.dumps(data)


@admin_app.get('/gold/transorder')
@checkAccess
def getGoldTransOrder(redis, session):
    """
    mysql - trans_order 显示'局数表'各项数据
    :param redis: redis
    :param session: session
    :return: json if isList else template
    """

    lang = getLang()
    fields = ('islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText')

    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))
    if not pageNumber:
        pageNumber = 0
    else:
        pageNumber = convert_util.to_int(pageNumber)

    if islist:
        report = get_gold_transorder(startDate, endDate, int(pageSize), int(pageNumber), searchText, limit=True,
                                     redis=redis)
        return json.dumps(report)
    else:
        info = {
            'title': '金币局数表',
            'listUrl': BACK_PRE + '/gold/transorder?islist=1',
            'serversUrl': BACK_PRE + '/game/transorder/list?list=1',
            'sumListUrl': BACK_PRE + '/game/transorder/sum/list?list=1',
            'dayListUrl': BACK_PRE + '/game/transorder/day/list?list=1',
            'dailyListUrl': BACK_PRE + '/game/transorder/daily/list?list=1',
            'graphListUrl': BACK_PRE + '/game/transorder/graph/list?list=1',
            'searchTxt': '',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
            'STARTDATE': startDate,
            'sort_bar': True,
            'member_page': True,
            'cur_page': pageNumber,
            'cur_size': pageSize,
            'remove_type': '',
        }

    return template('admin_gold_trans_order', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/game/transorder/sum/list')
def getGoldTransSumList(redis, session):
    """
    mysql - trans_order 统计表中'pre_balance,balance,after_balance'中的总数据
    :param redis:
    :param session:
    :return:
    """
    data = get_gold_transorder_sumlist(redis)
    return json.dumps(data)

@admin_app.get('/game/transorder/day/list')
def getGoldTransDayList(redis, session):
    """
    计算某一段时间内
    mysql - trans_order 统计表中'pre_balance,balance,after_balance'中的总数据
    :param redis:
    :param session:
    :return:
    """
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    data = get_gold_transorder_daylist(redis, startDate, endDate)
    return json.dumps(data)


@admin_app.get('/game/transorder/daily/list')
def getGoldTransDailyList(redis, session):
    """
    mysql - trans_order 统计表中'pre_balance,balance,after_balance'中的总数据
    :param redis:
    :param session:
    :return:
    """
    res = []
    sql = """select from_unixtime(create_time,'%Y-%m-%d'),
sum(
if((is_robot=0),balance,0)
)
from trans_order  GROUP BY from_unixtime(create_time,'%Y-%m-%d') order by create_time desc"""
    results = MysqlljgameInterface.select(sql, fetchmany=False)

    if results:
        for i in results:
            info = {}
            info['datetime'] = i[0]
            info['pay_ment'] = float(i[1]) if i[1] else 0
            res.append(info)
    data = {'data': res, 'count': len(res)}
    return json.dumps(data)

@admin_app.get('/game/transorder/graph/list')
def getGoldTransGraphList(redis, session):
    """
    统计图表数据
    计算某一段时间内 mysql - trans_order 统计表中'pre_balance,balance,after_balance'中的总数据
    :param redis:
    :param session:
    :return:
    """
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))
    gameid = request.GET.get('gameid', '').strip()
    gametype = request.GET.get('gametype', '').strip()

    data = get_gold_transorder_graphlist(redis, startDate, endDate, gameid, gametype)
    return json.dumps(data)


@admin_app.get('/game/transorder/list')
def getServerList(redis, session):
    """
    获取金币场-局数表中同一局数下的数据
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    trans_id = request.GET.get('id', '').strip()

    if not trans_id:
        return

    data = get_gold_transorder_id(redis, trans_id)
    return json.dumps(data)


@admin_app.get('/gold/game/day')
@checkAccess
def getGoldGameDay(redis, session):
    """
    统计每日金币场游戏人数在线
    :param redis: redis
    :param session: session
    :return: json if isList else template
    """
    lang = getLang()
    fields = ('islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText')

    for field in fields:
        exec ("%s = request.GET.get('%s', '').strip()" % (field, field))

    if not pageNumber:
        pageNumber = 0
    else:
        pageNumber = convert_util.to_int(pageNumber)

    if islist:
        data = get_gold_game_day(redis, startDate, endDate)
        return json.dumps(data)
    else:
        gamenamelist = sorted(GoldGameDict(redis).keys())
        gameidlist = sorted(GoldGameDict(redis).values())
        info = {
            'title': '每日游戏人数统计表',
            'listUrl': BACK_PRE + '/gold/game/day?islist=1',
            'searchTxt': '',
            'serversUrl': BACK_PRE + '/gold/game/day/list?list=1',
            'sumListUrl': BACK_PRE + '/game/day/sum/list?list=1',
            'dayListUrl': BACK_PRE + '/game/day/day/list?list=1',
            'graphListUrl': BACK_PRE + '/game/day/graph/list?list=1',
            'graphListCountUrl': BACK_PRE + '/game/day/graphcount/list?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
            'STARTDATE': startDate,
            'sort_bar': True,
            'member_page': True,
            'cur_page': pageNumber,
            'cur_size': pageSize,
            'remove_type': '',
            'gamenamelist': gamenamelist,
            'gameidlist': gameidlist,
        }
    return template('admin_gold_game_day', info=info, lang=lang, RES_VERSION=RES_VERSION)

@admin_app.get('/game/day/graph/list')
def getGoldGameGraph(redis, session):
    """
    :param redis:
    :param session:
    :return:
    """
    res = []
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))
    gameid = request.GET.get('gameid', '').strip()
    gametype = request.GET.get('gametype', '').strip()

    if gameid:
        sql = """SELECT fromTime, SUM(userCount) AS userCount,game_id
           FROM (SELECT FROM_UNIXTIME(create_time,'%s') AS fromTime, COUNT(user_id) AS userCount,  game_id
           FROM trans_order WHERE game_id='%s' and is_robot='0' and create_time >='%s' and create_time <='%s' GROUP BY  FROM_UNIXTIME(create_time,'%s'),game_id,user_id) AS a GROUP BY fromTime,game_id ORDER BY fromTime asc
           """ \
              % (gametype, gameid, startDate, endDate, gametype)
    else:
        sql = """SELECT fromTime, SUM(userCount) AS userCount,game_id
    FROM (SELECT FROM_UNIXTIME(create_time,'%s') AS fromTime, COUNT(user_id) AS userCount,  game_id
    FROM trans_order WHERE is_robot='0' and create_time >='%s' and create_time <='%s' GROUP BY  FROM_UNIXTIME(create_time,'%s'),game_id,user_id) AS a GROUP BY fromTime,game_id ORDER BY fromTime asc
    """ \
        % (gametype, startDate, endDate, gametype)
    results = MysqlljgameInterface.select(sql, fetchmany=False)
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
        gameid = 'id' + str(i[2])
        info[gameid] = float(i[1]) if i[1] else 0
        res.append(info)
    x = []
    for a, b in groupby(res, key=lambda i: i['datetime']):
        z = {}
        for y in b:
            z.update(y)
        x.append(z)
    return {'graph_data': x}

@admin_app.get('/game/day/graphcount/list')
def getGoldGameGraph(redis, session):
    """
    :param redis:
    :param session:
    :return:
    """
    res = []
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))
    gameid = request.GET.get('gameid1', '').strip()
    gametype = request.GET.get('gametype1', '').strip()

    if gameid:
        sql = """SELECT fromTime, COUNT(user_id),game_id FROM (SELECT FROM_UNIXTIME(create_time,'%s') AS fromTime, user_id, game_id FROM trans_order WHERE game_id='%s' and is_robot='0' and create_time>='%s' and create_time<='%s' GROUP BY  FROM_UNIXTIME(create_time,'%s'),game_id,user_id) AS a GROUP BY fromTime,game_id ORDER BY fromTime asc
    """ \
        % (gametype, gameid, startDate, endDate, gametype)
    else:
        sql = """SELECT fromTime, COUNT(user_id),game_id
    FROM (SELECT FROM_UNIXTIME(create_time,'%s') AS fromTime, user_id, game_id
    FROM trans_order WHERE is_robot='0' and create_time>='%s' and create_time<='%s' GROUP BY  FROM_UNIXTIME(create_time,'%s'),game_id,user_id) AS a GROUP BY fromTime,game_id ORDER BY fromTime asc
    """ \
        % (gametype, startDate, endDate, gametype)
    results = MysqlljgameInterface.select(sql, fetchmany=False)
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
        gameid = 'id' + str(i[2])
        info[gameid] = float(i[1]) if i[1] else 0
        res.append(info)
    x = []
    for a, b in groupby(res, key=lambda i: i['datetime']):
        z = {}
        for y in b:
            z.update(y)
        x.append(z)
    return {'graph_data': x}

@admin_app.get('/gold/game/day/list')
def getGoldGameDayList(redis, session):
    """
    获取金币场同一局数下的玩家列表
    """
    curTime = datetime.now()
    game_id = request.GET.get('id', '').strip()
    startDate = request.GET.get('startDate', '').strip()

    if not game_id:
        return
    data = get_gold_game_daylist(redis, game_id, startDate)
    return json.dumps(data)

@admin_app.get('/game/day/sum/list')
def getGoldGameSumList(redis, session):
    """
    统计每日金币场游戏人数在线总数据
    :param redis:
    :param session:
    :return:
    """
    data = get_gold_game_sumlist(redis)
    return json.dumps(data)

@admin_app.get('/game/day/day/list')
def getGoldGameSumList(redis, session):
    """
    计算某一段时间内
    统计每日金币场游戏人数在线总数据
    :param redis:
    :param session:
    :return:
    """
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    startDate = '%s %s' % (startDate, '00:00:00')
    startDate = time.mktime(time.strptime(startDate, '%Y-%m-%d %H:%M:%S'))
    endDate = '%s %s' % (endDate, '23:59:59')
    endDate = time.mktime(time.strptime(endDate, '%Y-%m-%d %H:%M:%S'))

    data = get_gold_game_day_list(redis, startDate, endDate)
    return json.dumps(data)

@admin_app.get('/gold/field/ranking')
@checkAccess
def getGoldFieldRanking(redis, session):
    """
    mysql - 排行
    :param redis: redis
    :param session: session
    :return: json if isList else template
    """

    lang = getLang()
    fields = ('islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText')

    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))
    if not pageNumber:
        pageNumber = 0
    else:
        pageNumber = convert_util.to_int(pageNumber)

    import datetime
    if islist:
        res = []
        sql = """select  FROM_UNIXTIME(create_time,'%%Y-%%m-%%d'),user_id, balance ,after_balance from (
	select * from `trans_order` where FROM_UNIXTIME(create_time,'%%Y-%%m-%%d')='%s' and is_robot=0 order by `create_time` desc
) `temp`  group by user_id order by `after_balance` desc""" \
        % (endDate)
        results = MysqlljgameInterface.select(sql, fetchmany=False)

        if results:
            sum = 1
            for i in results:
                info = {}
                info['number'] = sum
                sum += 1
                info['create_time'] = i[0]
                info['user_id'] = i[1]
                info['account'], = redis.hmget("users:%s" % (i[1]), "account")
                info['balance'] = float(i[2])
                info['after_balance'] = float(i[3])
                info['op'] = [
                    {"url": "/admin/gold/transorder", "txt": "跳转流水"},
                ]
                res.append(info)

        report = {'data': res, 'count':len(res)}
        return json.dumps(report)
    else:
        info = {
            'title': '当前金币排行',
            'listUrl': BACK_PRE + '/gold/field/ranking?islist=1',
            'serversUrl': BACK_PRE + '/game/field/ranking/list?list=1',
            'searchTxt': '',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
            'STARTDATE': startDate,
            'sort_bar': True,
            'member_page': True,
            'cur_page': pageNumber,
            'cur_size': pageSize,
            'remove_type': '',
        }

    return template('admin_gold_field_ranking', info=info, lang=lang, RES_VERSION=RES_VERSION)

@admin_app.get('/game/field/ranking/list')
def getGameFieldRankingList(redis, session):
    curTime = datetime.now()
    user_id = request.GET.get('id', '').strip()
    endDate = request.GET.get('endDate', '').strip()

    if not user_id:
        return

    res = []
    sql = """select user_id, trans_id, game_id,pre_balance, balance, after_balance, banker, room_id, playid, chair, status, create_time  from trans_order where user_id='%s' and FROM_UNIXTIME(create_time,'%%Y-%%m-%%d')='%s' order by create_time desc
""" \
    % (user_id, endDate)
    results = MysqlljgameInterface.select(sql, fetchmany=False)
    if results:
        num = 1
        for i in results:
            info = {}
            info['number'] = num
            num += 1
            info['user_id'] = i[0]
            info['trans_id'] = i[1]
            info['game_id'] = i[2]
            info['pre_balance'] = i[3]
            info['balance'] = i[4]
            info['after_balance'] = i[5]
            info['banker'] = '庄家' if i[6] else '闲家'
            info['room_id'] = i[7]
            info['playid'] = PLAYTYPE(i[8])
            info['chair'] = i[9]
            info['status'] = '正常' if i[10] else '异常'
            info['create_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[11])) if i[11] else ''
            gameid = redis.lindex("game:gold:gameid:%s:list" % (i[2]), 0)
            info['gameName'] = redis.hmget("game:gold:gameid:%s:id:%s" % (i[2], gameid), "gameName")
            res.append(info)
    data = {'data': res, 'count': len(res)}
    return json.dumps(data)


@admin_app.get('/gold/robot')
def getGoldRobot(redis, session):
    lang = getLang()
    id = request.GET.get('id', '').strip()
    level = request.GET.get('level', '').strip()
    isbot_data = redis.hgetall("users:robot:level:%s:%s" % (level, id))
    print(isbot_data)
    print(len(isbot_data))
    info = {
        'title': '金币局数表',
        'listUrl': BACK_PRE + '/gold/transorder?list=1',
        'searchTxt': '',
        'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,

    }
    return template('admin_gold_robot', info=info, lang=lang, RES_VERSION=RES_VERSION, isbot_data=isbot_data)
