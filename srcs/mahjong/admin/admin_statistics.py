# -*- coding:utf-8 -*-
# !/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    数据统计模块
"""
from bottle import *
from admin import admin_app
from config.config import STATIC_LAYUI_PATH, STATIC_ADMIN_PATH, BACK_PRE, RES_VERSION
from common.utilt import *
from common.log import *
from datetime import datetime
from web_db_define import *
from model.orderModel import *
from model.agentModel import *
from model.statisticsModel import *
from model.userModel import *
from common import log_util, convert_util, web_util
from common.mysql_lj_game import MysqlljgameInterface
import json
import copy


@admin_app.get('/statistics/buyReport')
@checkAccess
def getBuyReport(redis, session):
    """
    获取代理的订单报表
    """
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()

    selfAccount, selfUid = session['account'], session['id']

    if not startDate or not endDate:
        # 默认显示一周时间
        startDate, endDate = getDaya4Week()

    if isList:
        reports = getBuyCardReport(redis, selfUid, startDate, endDate)
        return json.dumps(reports)
    else:
        info = {
            'title': '[%s]购钻报表' % (selfAccount),
            'searchStr': '',
            'showLogType': '',
            'startDate': startDate,
            'endDate': endDate,
            'listUrl': BACK_PRE + '/statistics/buyReport?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

        return template('admin_report_buy', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/statistics/saleReport')
@checkAccess
def getSaleReport(redis, session):
    """
    获取代理的订单报表
    """
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()

    selfAccount, selfUid = session['account'], session['id']

    if not startDate or not endDate:
        # 默认显示一周时间
        startDate, endDate = getDaya4Week()

    if isList:
        reports = getSaleCardReport(redis, selfUid, startDate, endDate)
        return json.dumps(reports)
    else:
        info = {
            'title': '[%s]售钻报表' % (selfAccount),
            'searchStr': '',
            'showLogType': '',
            'startDate': startDate,
            'endDate': endDate,
            'listUrl': BACK_PRE + '/statistics/saleReport?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

        return template('admin_report_sale', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/statistics/allAgentSaleReport')
@checkAccess
def getAgentSaleReport(redis, session):
    """
    获取下线代理的售钻订单报表
    """
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    group_id = request.GET.get('group_id', '').strip()

    selfAccount, selfUid = session['account'], session['id']
    adminTable = AGENT_TABLE % (selfUid)
    aType = redis.hget(adminTable, 'type')

    if not startDate or not endDate:
        # 默认显示一周时间
        startDate, endDate = getDaya4Week()

    if isList:
        reports = getAgentSaleCardReport(redis, selfUid, startDate, endDate, group_id)
        return json.dumps(reports)
    else:
        info = {
            'title': '[%s]的下线代理售钻报表' % (selfAccount),
            'searchStr': '',
            'showLogType': '',
            'startDate': startDate,
            'selfUid': aType,
            'endDate': endDate,
            'group_search': True,  # 开启代理查询
            'tableUrl': BACK_PRE + '/order/sale/record?list=1',
            'listUrl': BACK_PRE + '/statistics/allAgentSaleReport?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

        return template('admin_report_agent_sale', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/statistics/allAgentBuyReport')
@checkAccess
def getAgentBuyReport(redis, session):
    """
    获取下线代理的购钻订单报表
    """
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    group_id = request.GET.get('group_id', '').strip()

    selfAccount, selfUid = session['account'], session['id']

    if not startDate or not endDate:
        # 默认显示一周时间
        startDate, endDate = getDaya4Week()

    if isList:
        reports = getAgentBuyCardReport(redis, selfUid, startDate, endDate, group_id)
        return json.dumps(reports)
    else:
        info = {
            'title': '[%s]的下线代理购钻报表' % (selfAccount),
            'searchStr': '',
            'showLogType': '',
            'startDate': startDate,
            'endDate': endDate,
            'group_search': True,  # 开启代理查询
            'listUrl': BACK_PRE + '/statistics/allAgentBuyReport?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

        return template('admin_report_agent_buy', info=info, lang=lang, RES_VERSION=RES_VERSION)


def getTimeList(begin_date, end_date):
    date_list = []
    begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += timedelta(days=1)
    return date_list


def get_downline_rate(redis, date, my_downline_agents, selfUid=''):
    """
    获取下线抽成的列表(循环查询)
    """
    RateReportList = []
    for agent_id in my_downline_agents:
        agentTable = AGENT_TABLE % (agent_id)
        aType, parentId = redis.hmget(agentTable, ('type', 'parent_id'))
        log_util.debug('agent_id[%s] aType[%s] parentId[%s]' % (agent_id, aType, parentId))
        if aType in ['2', '3']:
            agentPerPriceList = redis.smembers(AGENT_ROOMCARD_PER_PRICE % (parentId))
        else:
            agentPerPriceList = redis.smembers(AGENT_ROOMCARD_PER_PRICE % (agent_id))
        log_util.debug('----------------------------------------agentPerPriceList[%s]' % (agentPerPriceList))
        agentRateList = redis.smembers(AGENT_RATE_SET % (agent_id))
        log_util.debug('----------------------------------------agentRateList[%s]' % (agentRateList))
        for price in agentPerPriceList:
            for rate in agentRateList:
                agentRateTable = AGENT_RATE_DATE % (agent_id, rate, price, date)
                if redis.exists(agentRateTable):
                    agentRate = redis.hgetall(agentRateTable)
                    agentRate['date'] = date
                    agentRate['id'] = agent_id
                    if agent_id == selfUid and 'superRateTotal' in agentRate and 'rateTotal' in agentRate:
                        agentRate['superRateTotal'] = ''
                        agentRate['rateTotal'] = ''
                        agentRate['unitPrice'] = ''
                        agentRate['rate'] = ''
                    RateReportList.append(agentRate)

    # log_util.debug('[RateReportList] agentTable[%s] RateReportList[%s]'%(agentTable,RateReportList))
    return RateReportList


def get_downline_rate2(redis, date_list, selfUid, agent_id):
    """
    获取下线抽成的列表(循环查询)
    """
    RateReportList = []
    RateReportDict = {}

    New_agentRate = {'id': agent_id, 'number': 0.0, 'rateTotal': 0.0, 'superRateTotal': 0.0, 'meAndNextTotal': 0.0}

    agentTable = AGENT_TABLE % (agent_id)
    aType, parentId = redis.hmget(agentTable, ('type', 'parent_id'))
    log_util.debug('agent_id[%s] aType[%s] parentId[%s]' % (agent_id, aType, parentId))
    if aType in ['2', '3']:
        agentPerPriceList = redis.smembers(AGENT_ROOMCARD_PER_PRICE % (parentId))
    else:
        agentPerPriceList = redis.smembers(AGENT_ROOMCARD_PER_PRICE % (agent_id))
    log_util.debug('----------------------------------------agentPerPriceList[%s]' % (agentPerPriceList))
    agentRateList = redis.smembers(AGENT_RATE_SET % (agent_id))
    log_util.debug('----------------------------------------agentRateList[%s]' % (agentRateList))

    for price in agentPerPriceList:
        for rate in agentRateList:
            Tmp_agentRate = copy.deepcopy(New_agentRate)

            Tmp_agentRate['rate'] = rate
            Tmp_agentRate['unitPrice'] = price

            for date in date_list:
                agentRateTable = AGENT_RATE_DATE % (agent_id, rate, price, date)
                if redis.exists(agentRateTable):
                    agentRate = redis.hgetall(agentRateTable)
                    for _key in ['number', 'meAndNextTotal', 'rateTotal', 'superRateTotal']:
                        Tmp_agentRate[_key] += float(agentRate.get(_key, 0))

            if Tmp_agentRate.get('number', 0):
                if agent_id == selfUid:
                    Tmp_agentRate['superRateTotal'] = ''
                    Tmp_agentRate['rateTotal'] = ''
                    Tmp_agentRate['unitPrice'] = ''
                    Tmp_agentRate['rate'] = ''

                RateReportList.append(Tmp_agentRate)

            print 'agent_id %s Tmp_agentRate %s price %s rate %s' % (agent_id, Tmp_agentRate, price, rate)

    # log_util.debug('[RateReportList] agentTable[%s] RateReportList[%s]'%(agentTable,RateReportList))
    if RateReportList:
        print 'RateReportList', RateReportList
    return RateReportList


def get_rate_reports(redis, selfUid, startDate, endDate, agent_type):
    """
    获取抽成的列表
    """
    date_list = convert_util.to_week_list(startDate, endDate)
    if agent_type == 0:
        my_downline_agents = redis.smembers(AGENT_CHILD_TABLE % (selfUid))
    elif agent_type > 0:
        my_downline_agents = getAllChildAgentId(redis, selfUid)
    else:
        my_downline_agents = []
    if agent_type == 2:
        my_downline_agents.append(selfUid)
    log_util.debug('my_downline_agents[%s]' % (my_downline_agents))
    RateReportList = []
    for date in date_list:
        downline_reports = get_downline_rate(redis, date, my_downline_agents, selfUid)
        log_util.debug(
            '[get_rate_reports] date[%s] selfId[%s] downline_reports[%s]' % (date, selfUid, downline_reports))
        if not downline_reports:
            continue
        RateReportList.extend(downline_reports)

    log_util.debug('[agentRateTable1111] selfUid[%s] RateReportList[%s]' % (selfUid, RateReportList))
    return {'date': RateReportList}


def get_rate_reports2(redis, selfUid, startDate, endDate, agent_type):
    """
    获取抽成的列表
    """
    date_list = convert_util.to_week_list(startDate, endDate)
    if agent_type == 0:
        my_downline_agents = redis.smembers(AGENT_CHILD_TABLE % (selfUid))
    elif agent_type > 0:
        my_downline_agents = getAllChildAgentId(redis, selfUid)
    else:
        my_downline_agents = []
    if agent_type == 2:
        my_downline_agents.append(selfUid)
    log_util.debug('my_downline_agents[%s]' % (my_downline_agents))
    RateReportList = []

    for _agentid in my_downline_agents:
        downline_reports = get_downline_rate2(redis, date_list, selfUid, _agentid)
        log_util.debug('[get_rate_reports2] _agentid[%s] selfId[%s] date_list[%s]' % (_agentid, selfUid, date_list))
        if not downline_reports:
            continue
        RateReportList.extend(downline_reports)

    print 'RateReportList', RateReportList
    log_util.debug('[agentRateTable1111] selfUid[%s] RateReportList[%s]' % (selfUid, RateReportList))
    return {'date': RateReportList}


@admin_app.get('/statistics/rateReport')
@checkAccess
def get_rate_info(redis, session):
    """
    获取代理的利润分成报表
    """
    lang = getLang()
    isList = request.GET.get('list', '').strip()

    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    selfUid = request.GET.get('id', '').strip()
    date = request.GET.get('date', '').strip()
    unitPrice = request.GET.get('unitPrice', '').strip()

    log_util.debug('[try get_rate_info] selfUid[%s] date[%s]' % (selfUid, date))

    # if selfUid and date and unitPrice:
    #     reports = getNextRateReportInfo(redis,selfUid,date)
    #     return json.dumps(reports)

    if not selfUid:
        selfUid = session['id']

    selfAccount = session['account']
    agent_type = convert_util.to_int(session['type'])
    agentTable = AGENT_TABLE % (selfUid)
    if isList:
        reports = get_rate_reports(redis, selfUid, startDate, endDate, agent_type)
        return json.dumps(reports)
    else:
        info = {
            'title': '[%s]销售利润报表' % (selfAccount),
            'startDate': startDate,
            'endDate': endDate,
            'listUrl': BACK_PRE + '/statistics/rateReport?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
            'aType': session['type'],
        }

        return template('admin_report_rate', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/statistics/rateReport2')
@checkAccess
def get_rate_info2(redis, session):
    """
    获取代理的利润分成报表
    """
    lang = getLang()
    isList = request.GET.get('list', '').strip()

    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    selfUid = request.GET.get('id', '').strip()
    date = request.GET.get('date', '').strip()
    unitPrice = request.GET.get('unitPrice', '').strip()

    log_util.debug('[try get_rate_info] selfUid[%s] date[%s]' % (selfUid, date))

    # if selfUid and date and unitPrice:
    #     reports = getNextRateReportInfo(redis,selfUid,date)
    #     return json.dumps(reports)

    if not selfUid:
        selfUid = session['id']

    selfAccount = session['account']
    agent_type = convert_util.to_int(session['type'])
    agentTable = AGENT_TABLE % (selfUid)
    if isList:
        reports = get_rate_reports2(redis, selfUid, startDate, endDate, agent_type)
        return json.dumps(reports)
    else:
        info = {
            'title': '[%s]销售利润报表2' % (selfAccount),
            'startDate': startDate,
            'endDate': endDate,
            'listUrl': BACK_PRE + '/statistics/rateReport2?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
            'aType': session['type'],
        }

        return template('admin_report_rate2', info=info, lang=lang, RES_VERSION=RES_VERSION)


def getRegCountList(redis, startDate, endDate):
    """
        获取某个时间段注册人数列表
        params:
            [ startDate ] : 开始日期
            [ endDate ]   : 结束日期

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
    while startDate <= endDate:
        if startDate > now_time:
            startDate += deltaTime
            continue
        regInfo = {}
        dateStr = startDate.strftime('%Y-%m-%d')
        regTable = FORMAT_REG_DATE_TABLE % (dateStr)
        regCount = redis.scard(regTable)
        regInfo['reg_date'] = dateStr
        regInfo['reg_count'] = regCount
        regInfo['op'] = []
        regInfo['op'].append({'url': '/admin/statistics/reg/list', 'method': 'GET', 'txt': '查看详情'})
        res.append(regInfo)

        startDate += deltaTime

    res.reverse()
    return res


def getCardCountList(redis, agentId, startDate, endDate):
    """
        获取某个时间段注册人数列表
        params:
            [ startDate ] : 开始日期
            [ endDate ]   : 结束日期

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

    while startDate <= endDate:
        regInfo = {}
        dateStr = startDate.strftime('%Y-%m-%d')
        if agentId == '1':
            regTable = DAY_ALL_PLAY_ROOM_CARD % (dateStr)
            regCount = redis.get(regTable)
        else:
            regCount = getAgentRoomByDay(redis, agentId, dateStr)
        if not regCount:
            regCount = 0
        regInfo['reg_date'] = dateStr
        regInfo['reg_count'] = regCount
        res.append(regInfo)

        startDate += deltaTime

    res.reverse()
    return res


@admin_app.get('/statistics/graphs')
@checkAccess
def getGraphs(redis, session):
    """
    图表数据
    """
    lang = getLang()
    curTime = datetime.now()

    info = {
        'title': '图表数据',
        'listUrl': BACK_PRE + '/statistics/graphs?list=1',
        'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
        'show_regMember_url': BACK_PRE + '/statistics/graphs/getRegMember',  # 注册人数统计
        'show_activeMember_url': BACK_PRE + '/statistics/graphs/getActiveMember',  # 活跃人数统计
        'show_wechatOrder_url': BACK_PRE + '/statistics/graphs/getOrderCount?type=wechat',  # 商城订单统计
        'show_agentOrder_url': BACK_PRE + '/statistics/graphs/getOrderCount?type=agent',  # 代理订单统计
        'show_gameRoomcard_url': BACK_PRE + '/statistics/graphs/getGameRoomcard',  # 游戏耗钻统计
        'show_gameRoomcardEach_url': BACK_PRE + '/statistics/graphs/getGameRoomcardEach',  # 各游戏耗钻统计
        'show_saleReport_url': BACK_PRE + '/statistics/graphs/getSaleReport',  # 我的售钻订单统计
        'show_agentSaleReport_url': BACK_PRE + '/statistics/graphs/getAgentSaleReport',  # 下级代理售钻订单统计
        'show_agentBuyReportMain_url': BACK_PRE + '/statistics/graphs/getAgentBuyReport',  # 下级代理购钻统计
        'show_rateReport_url': BACK_PRE + '/statistics/graphs/getRateReport',  # 下级代理购钻统计
    }

    return template('admin_statistics_graphs', info=info, lang=lang, RES_VERSION=RES_VERSION)

@admin_app.get('/statistics/graphs/getRegMember')
def getGraphsRegMember(redis, session):
    """
    注册人数图表
    """
    # 获取生成对象类型
    show_obj = {
        'data': [u'每日注册', u'每日活跃数', u'每日耗卡数'],
        'login_datas': [],
        'take_datas': [],
        'reg_datas': [],
    }
    # 获取当前一周日期并格式化为字符串

    week_date_lists = get_week_date_list()
    for week_date in week_date_lists:
        show_obj['reg_datas'].append(
            convert_util.to_int(redis.scard(FORMAT_REG_DATE_TABLE % (week_date)))
        )
        show_obj['take_datas'].append(
            convert_util.to_int(redis.get(DAY_ALL_PLAY_ROOM_CARD % (week_date)))
        )
        selfUid = '1'  # session['id']
        data = get_active_reports(redis, week_date, week_date, selfUid)
        if data["data"]:
            show_obj['login_datas'].append(convert_util.to_int(data["data"][0]["login_count"]))
        else:
            show_obj['login_datas'].append(
                convert_util.to_int(redis.get(DAY_ALL_LOGIN_COUNT % (week_date)))
            )

    show_obj['series'] = [
        {'name': u'每日注册', 'type': 'line', 'data': show_obj['reg_datas']},
        {'name': u'每日耗卡数', 'type': 'line', 'data': show_obj['take_datas']},
        {'name': u'每日活跃数', 'type': 'line', 'data': show_obj['login_datas']},
    ]

    return web_util.do_response(1, msg="", jumpUrl="",
                                data={'week': week_date_lists, 'series': show_obj['series'], 'legen': show_obj['data']})

@admin_app.get('/statistics/graphs/getActiveMember')
def getGraphsActiveMember(redis, session):
    """
    活跃图表
    """
    # 获取生成对象类型
    show_obj = {
        'data': [u'登录人数', u'当天钻石消耗', u'当天局数统计'],
        'login_count': [],
        'take_card': [],
        'take_count': [],
    }
    # 获取当前一周日期并格式化为字符串

    week_date_lists = get_week_date_list()
    for week_date in week_date_lists:
        selfUid = '1'  # session['id']
        data = get_active_reports(redis, week_date, week_date, selfUid)
        if data["data"]:
            show_obj['login_count'].append(convert_util.to_int(data["data"][0]["login_count"]))
            show_obj['take_card'].append(convert_util.to_int(data["data"][0]["take_card"]))
            show_obj['take_count'].append(convert_util.to_int(data["data"][0]["take_count"]))
        else:
            show_obj['login_count'].append(convert_util.to_int('0'))
            show_obj['take_card'].append(convert_util.to_int('0'))
            show_obj['take_count'].append(convert_util.to_int('0'))

    show_obj['series'] = [
        {'name': u'登录人数', 'type': 'line', 'data': show_obj['login_count']},
        {'name': u'当天钻石消耗', 'type': 'line', 'data': show_obj['take_card']},
        {'name': u'当天局数统计', 'type': 'line', 'data': show_obj['take_count']},
    ]

    return web_util.do_response(1, msg="", jumpUrl="",
                                data={'week': week_date_lists, 'series': show_obj['series'], 'legen': show_obj['data']})


@admin_app.get('/statistics/graphs/getOrderCount')
def getGraphsOrderCount(redis, session):
    """
    订单图表
    """
    type = request.GET.get('type', '').strip()

    # 获取当前一周日期并格式化为字符串
    week_date_lists = get_week_date_list()
    if type == 'wechat':
        # 获取生成对象类型
        show_obj = {
            'data': [u'商城总订单', u'成功订单', u'挂起订单', u'成功订单交易总金额', u'挂起订单交易总金额'],
            'wechat_count': [],
            'succee_count': [],
            'pending_count': [],
            'success_list': [],
            'pending_list': [],
        }
        for week_date in week_date_lists:
            selfUid = '1'  # session['id']
            wechat = redis.llen(DAY_ORDER % week_date)
            succee, pengding, succeeNum, pendingNum = 0, 0, 0, 0
            if wechat:
                for each in redis.lrange(DAY_ORDER % week_date, 0, -1):
                    orderTable = redis.hgetall(ORDER_TABLE % (each))
                    if orderTable.get('type') == 'successful':
                        succee += 1
                        succeeNum += round(float(orderTable.get('money')) * 0.01, 2)
                    elif orderTable.get('type') == 'pending':
                        pengding += 1
                        pendingNum += round(float(orderTable.get('money')) * 0.01, 2)
            else:
                succee, pengding, succeeNum, pendingNum = 0, 0, 0, 0

            try:
                show_obj['wechat_count'].append(convert_util.to_int(wechat))
                show_obj['succee_count'].append(convert_util.to_int(succee))
                show_obj['pending_count'].append(convert_util.to_int(pengding))
                show_obj['success_list'].append(convert_util.to_int(succeeNum))
                show_obj['pending_list'].append(convert_util.to_int(pendingNum))
            except Exception as err:
                show_obj['wechat_count'].append(convert_util.to_int('0'))
                show_obj['succee_count'].append(convert_util.to_int('0'))
                show_obj['pending_count'].append(convert_util.to_int('0'))
                show_obj['success_list'].append(convert_util.to_int('0'))
                show_obj['pending_list'].append(convert_util.to_int('0'))

        show_obj['series'] = [
            {'name': u'商城总订单', 'type': 'line', 'data': show_obj['wechat_count']},
            {'name': u'成功订单', 'type': 'line', 'data': show_obj['succee_count']},
            {'name': u'挂起订单', 'type': 'line', 'data': show_obj['pending_count']},
            {'name': u'成功订单交易总金额', 'type': 'line', 'data': show_obj['success_list']},
            {'name': u'挂起订单交易总金额', 'type': 'line', 'data': show_obj['pending_list']},
        ]
    else:
        show_obj = {
            'data': [u'代理总订单', u'确认订单', u'未确认订单'],
            'agent_count': [],
            'succee_count': [],
            'pending_count': [],
        }
        for week_date in week_date_lists:
            selfUid = '1'  # session['id']
            week_date = week_date.replace('-', '')
            orderList = redis.lrange(ORDER_LIST, 0, -1)
            agentNum, succeeNum, pendingNum = 0, 0, 0
            for each in orderList:
                if week_date in each:
                    agentNum += 1
                    if redis.hget(ORDER_TABLE % each, ('status')) == '1':
                        succeeNum += 1
                    else:
                        pendingNum += 1
            try:
                show_obj['agent_count'].append(convert_util.to_int(agentNum))
                show_obj['succee_count'].append(convert_util.to_int(succeeNum))
                show_obj['pending_count'].append(convert_util.to_int(pendingNum))
            except Exception as err:
                show_obj['agent_count'].append(convert_util.to_int('0'))
                show_obj['succee_count'].append(convert_util.to_int('0'))
                show_obj['pending_count'].append(convert_util.to_int('0'))

        show_obj['series'] = [
            {'name': u'代理总订单', 'type': 'line', 'data': show_obj['agent_count']},
            {'name': u'确认订单', 'type': 'line', 'data': show_obj['succee_count']},
            {'name': u'未确认订单', 'type': 'line', 'data': show_obj['pending_count']},
        ]

    return web_util.do_response(1, msg="", jumpUrl="",
                                data={'week': week_date_lists, 'series': show_obj['series'], 'legen': show_obj['data']})


@admin_app.get('/statistics/graphs/getSaleReport')
def getGraphsSaleReport(redis, session):
    """
    我的售钻报表
    """
    # 获取当前一周日期并格式化为字符串
    week_date_lists = get_week_date_list()
    # 获取生成对象类型
    show_obj = {
        'data': [u'当日售钻数', u'历史售钻数'],
        'cardNums': [],
        'totalNums': [],
    }
    selfUid = session.get('id')

    for week_date in week_date_lists:
        selfUid = '1'  # session['id']
        reportList = []
        saleReportTable = AGENT_SALE_CARD_DATE % (selfUid, week_date)
        reportInfo = redis.hgetall(saleReportTable)
        # 添加入报表
        reportList.append(reportInfo)

        try:
            show_obj['cardNums'].append(convert_util.to_int(reportList[0]['cardNums']))
            show_obj['totalNums'].append(convert_util.to_int(reportList[0]['totalNums']))
        except Exception as err:
            show_obj['cardNums'].append(convert_util.to_int('0'))
            show_obj['totalNums'].append(convert_util.to_int('0'))

    show_obj['series'] = [
        {'name': u'当日售钻数', 'type': 'line', 'data': show_obj['cardNums']},
        {'name': u'历史售钻数', 'type': 'line', 'data': show_obj['totalNums']},
    ]

    return web_util.do_response(1, msg="", jumpUrl="",
                                data={'week': week_date_lists, 'series': show_obj['series'], 'legen': show_obj['data']})


@admin_app.get('/statistics/graphs/getAgentSaleReport')
def getGraphsAgentSaleReport(redis, session):
    """
    下级代理的售钻报表
    """
    # 获取当前一周日期并格式化为字符串
    week_date_lists = get_week_date_list()
    # 获取生成对象类型
    show_obj = {
        'data': [u'当日售钻数', u'总售钻数'],
        'cardNums': [],
        'totalNums': [],
    }
    selfUid = session.get('id')
    subIds = redis.smembers(AGENT_CHILD_TABLE % (selfUid))

    for week_date in week_date_lists:
        cardNum, totalNum = 0, 0
        for sub in subIds:
            if redis.exists(AGENT_SALE_CARD_DATE % (sub, week_date)):
                card = redis.hget(AGENT_SALE_CARD_DATE % (sub, week_date), 'cardNums')
                total = redis.hget(AGENT_SALE_CARD_DATE % (sub, week_date), 'totalNums')
            else:
                card, total = 0, 0
            cardNum += int(card)
            totalNum += int(total)
        show_obj['cardNums'].append(convert_util.to_int(cardNum))
        show_obj['totalNums'].append(convert_util.to_int(totalNum))

    show_obj['series'] = [
        {'name': u'当日售钻数', 'type': 'line', 'data': show_obj['cardNums']},
        {'name': u'总售钻数', 'type': 'line', 'data': show_obj['totalNums']},
    ]

    return web_util.do_response(1, msg="", jumpUrl="",
                                data={'week': week_date_lists, 'series': show_obj['series'], 'legen': show_obj['data']})


@admin_app.get('/statistics/graphs/getAgentBuyReport')
def getGraphsAgentBuyReport(redis, session):
    """
    下级代理的购钻报表
    """
    # 获取当前一周日期并格式化为字符串
    week_date_lists = get_week_date_list()
    # 获取生成对象类型
    show_obj = {
        'data': [u'当日购钻数', u'总购钻数'],
        'cardNums': [],
        'totalNums': [],
    }
    selfUid = session.get('id')
    subIds = redis.smembers(AGENT_CHILD_TABLE % (selfUid))

    for week_date in week_date_lists:
        cardNum, totalNum = 0, 0
        for sub in subIds:
            if redis.exists(AGENT_BUY_CARD_DATE % (sub, week_date)):
                card = redis.hget(AGENT_BUY_CARD_DATE % (sub, week_date), 'cardNums')
                total = redis.hget(AGENT_BUY_CARD_DATE % (sub, week_date), 'totalNums')
            else:
                card, total = 0, 0
            cardNum += int(card)
            totalNum += int(total)
        show_obj['cardNums'].append(convert_util.to_int(cardNum))
        show_obj['totalNums'].append(convert_util.to_int(totalNum))

    show_obj['series'] = [
        {'name': u'当日购钻数', 'type': 'line', 'data': show_obj['cardNums']},
        {'name': u'总购钻数', 'type': 'line', 'data': show_obj['totalNums']},
    ]

    return web_util.do_response(1, msg="", jumpUrl="",
                                data={'week': week_date_lists, 'series': show_obj['series'], 'legen': show_obj['data']})


@admin_app.get('/statistics/graphs/getRateReport')
def getGraphsRateReport(redis, session):
    """
    利润占成报表
    """
    # 获取当前一周日期并格式化为字符串
    week_date_lists = get_week_date_list()
    # 获取生成对象类型
    show_obj = {
        'data': [u'下线代理总占额', u'我的总占额'],
        'rateTotal': [],
        'superRateTotal': [],
    }
    selfUid = session.get('id')
    subIds = redis.smembers(AGENT_CHILD_TABLE % (selfUid))

    for date in week_date_lists:
        RateReportList = []
        rateTotal, superRateTotal = 0, 0
        for agent_id in subIds:
            agentTable = AGENT_TABLE % (agent_id)
            aType, parentId = redis.hmget(agentTable, ('type', 'parent_id'))
            if aType in ['2', '3']:
                agentPerPriceList = redis.smembers(AGENT_ROOMCARD_PER_PRICE % (parentId))
            else:
                agentPerPriceList = redis.smembers(AGENT_ROOMCARD_PER_PRICE % (agent_id))
            agentRateList = redis.smembers(AGENT_RATE_SET % (agent_id))
            for price in agentPerPriceList:
                for rate in agentRateList:
                    agentRateTable = AGENT_RATE_DATE % (agent_id, rate, price, date)
                    if redis.exists(agentRateTable):
                        agentRate = redis.hgetall(agentRateTable)
                        agentRate['date'] = date
                        agentRate['id'] = agent_id
                        if agent_id == selfUid and 'superRateTotal' in agentRate and 'rateTotal' in agentRate:
                            agentRate['superRateTotal'] = 0
                            agentRate['rateTotal'] = 0
                            agentRate['unitPrice'] = 0
                            agentRate['rate'] = 0
                    else:
                        agentRate = {}
                        agentRate['superRateTotal'] = 0
                        agentRate['rateTotal'] = 0
                    rateTotal += int(agentRate['rateTotal'])
                    superRateTotal += int(agentRate['superRateTotal'])
        show_obj['rateTotal'].append(convert_util.to_int(rateTotal))
        show_obj['superRateTotal'].append(convert_util.to_int(superRateTotal))

    show_obj['series'] = [
        {'name': u'下线代理总占额', 'type': 'line', 'data': show_obj['rateTotal']},
        {'name': u'我的总占额', 'type': 'line', 'data': show_obj['superRateTotal']},
    ]

    return web_util.do_response(1, msg="", jumpUrl="",
                                data={'week': week_date_lists, 'series': show_obj['series'], 'legen': show_obj['data']})


@admin_app.get('/statistics/graphs/getGameRoomcard')
def getGraphsGameRoomcard(redis, session):
    """
    游戏耗钻报表
    """
    # 获取当前一周日期并格式化为字符串
    week_date_lists = get_week_date_list()
    # 获取生成对象类型
    show_obj = {
        'data': [u'当日游戏耗钻总数', u'游戏耗钻占比'],
        'roomcards_day': [],
        'roomcards_all': [],
    }

    game_ids = redis.lrange(GAME_LIST, 0, -1)
    allGame_total = 0
    for date in week_date_lists:
        roomcards_day, roomcards_all = 0, 0
        for each in game_ids:
            roomcard_day = redis.get('game:roomCards:%s:%s:total' % (each, date))
            if roomcard_day:
                roomcards_day += int(roomcard_day)
            roomcard_all = redis.get("game:roomCards:%s:total" % (each))
            if roomcard_all:
                roomcards_all += int(roomcard_all)
        allGame_total += roomcards_day

        show_obj['roomcards_day'].append(convert_util.to_int(roomcards_day))

    for each in show_obj['roomcards_day']:
        try:
            baifenbi = "%.2f%%" % (each / float(allGame_total) * 100)
        except Exception as err:
            baifenbi = "%.2f" % 0
        show_obj['roomcards_all'].append(baifenbi)

    show_obj['series'] = [
        {'name': u'当日游戏耗钻总数', 'type': 'line', 'data': show_obj['roomcards_day']},
        {'name': u'游戏耗钻占比', 'type': 'line', 'data': show_obj['roomcards_all']},
    ]

    return web_util.do_response(1, msg="", jumpUrl="",
                                data={'week': week_date_lists, 'series': show_obj['series'], 'legen': show_obj['data']})


@admin_app.get('/statistics/graphs/getGameRoomcardEach')
def getGraphsGameRoomcardEach(redis, session):
    """
    各游戏耗钻报表
    """
    # 获取当前一周日期并格式化为字符串
    week_date_lists = get_week_date_list()
    # 获取生成对象类型

    game_ids = redis.lrange(GAME_LIST, 0, -1)
    game_set = ['%s(%s)' % (each, redis.hget(GAME_TABLE % (each), 'name')) for each in game_ids]

    show_obj = {
        'data': game_set,
    }

    for date in week_date_lists:
        roomcards_day, roomcards_all = 0, 0
        for each in game_ids:
            roomcard_day = redis.get('game:roomCards:%s:%s:total' % (each, date))
            if not roomcard_day:
                roomcard_day = 0

            show_obj.setdefault(each, []).append(convert_util.to_int(roomcard_day))

    for item in game_set:
        show_obj.setdefault('series', []).append(
            {'name': item, 'type': 'line', 'data': show_obj[item.split('(')[0]]}
        )

    return web_util.do_response(1, msg="", jumpUrl="",
                                data={'week': week_date_lists, 'series': show_obj['series'], 'legen': show_obj['data']})

@admin_app.get('/statistics/reg')
@checkAccess
def getRegStatistics(redis, session):
    """
    注册人数统计
    :param redis:
    :param session:
    :return:
    """
    lang = getLang()
    curTime = datetime.now()
    isList = request.GET.get('list', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()

    if isList:
        res = getRegCountList(redis, startDate, endDate)
        return json.dumps(res)
    else:
        info = {
            'title': '注册人数统计',
            'listUrl': BACK_PRE + '/statistics/reg?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
        }

        return template('admin_statistics_reg', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/statistics/takeCard')
@checkAccess
def getCardStatistics(redis, session):
    lang = getLang()
    curTime = datetime.now()
    isList = request.GET.get('list', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()

    if isList:
        res = getCardCountList(redis, session['id'], startDate, endDate)
        return json.dumps(res)
    else:
        info = {
            'title': '日耗钻统计',
            'listUrl': BACK_PRE + '/statistics/takeCard?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
        }

        return template('admin_statistics_card', info=info, lang=lang, RES_VERSION=RES_VERSION)


def getRegListByRegDate(redis, reg_date):
    """
        获取某个时间段注册人数详情
        params:
            [ reg_date ] : 某一天

    """
    print 'reg_date', reg_date
    registMemberList = redis.smembers(FORMAT_REG_DATE_TABLE % (reg_date))
    res = []
    for member in registMemberList:
        memberInfo = {}
        account2user_table = FORMAT_ACCOUNT2USER_TABLE % (member)  # 从账号获得账号信息，和旧系统一样
        table = redis.get(account2user_table)
        nickname, reg_date, regIp, login_out_date, last_login_date, parentAg, headImgUrl = \
            redis.hmget(table, (
                'nickname', 'regDate', 'regIp', 'last_logout_date', 'last_login_date', 'parentAg', 'headImgUrl'))
        memberInfo['nickname'] = nickname
        memberInfo['reg_date'] = reg_date
        memberInfo['regIp'] = regIp
        memberInfo['parentAg'] = regIp
        memberInfo['last_login_date'] = last_login_date if last_login_date else '-'
        memberInfo['login_out_date'] = login_out_date if login_out_date else '-'
        memberInfo['parentAg'] = parentAg if parentAg else '未加入任何公会'
        memberInfo['headImgUrl'] = headImgUrl
        memberInfo['account'] = member

        res.append(memberInfo)
    return res


@admin_app.get('/statistics/reg/list')
def getRegStatisticsList(redis, session):
    lang = getLang()
    curTime = datetime.now()
    isList = request.GET.get('list', '').strip()
    reg_date = request.GET.get('reg_date', '').strip()

    if isList:
        res = getRegListByRegDate(redis, reg_date)
        return json.dumps(res)
    else:
        info = {
            'title': '%s 注册列表' % (reg_date),
            'listUrl': BACK_PRE + '/statistics/reg/list?list=1&reg_date=%s' % (reg_date),
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
        }

        return template('admin_statistics_reg_list', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/statistics/card/list')
def getRegStatisticsList(redis, session):
    lang = getLang()
    curTime = datetime.now()
    isList = request.GET.get('list', '').strip()
    reg_date = request.GET.get('reg_date', '').strip()

    if isList:
        res = getRegListByRegDate(redis, reg_date)
        return json.dumps(res)
    else:
        info = {
            'title': '%s 注册列表' % (reg_date),
            'listUrl': BACK_PRE + '/statistics/reg/list?list=1&reg_date=%s' % (reg_date),
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
        }

        return template('admin_statistics_reg_list', info=info, lang=lang, RES_VERSION=RES_VERSION)


def getloginCountList(redis, agentId, agentIds, startDate, endDate):
    """
        获取某个时间段注册人数列表
        params:
            [ startDate ] : 开始日期
            [ endDate ]   : 结束日期

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

    while startDate <= endDate:
        regInfo = {}
        dateStr = startDate.strftime('%Y-%m-%d')
        if not agentIds and int(agentId) == 1:
            regTable = FORMAT_LOGIN_DATE_TABLE % (dateStr)
            regCount = redis.scard(regTable)
        else:
            if not agentIds:
                agentIds = [agentId]
            regCount = 0
            for _agentId in agentIds:
                count = redis.get(DAY_AG_LOGIN_COUNT % (_agentId, dateStr))
                if not count:
                    count = 0
                regCou += int(count)

        regInfo['reg_date'] = dateStr
        regInfo['reg_count'] = regCount
        regInfo['op'] = []
        regInfo['op'].append({'url': '/admin/statistics/login/list', 'method': 'GET', 'txt': '查看详情'})
        res.append(regInfo)

        startDate += deltaTime

    res.reverse()
    return res


@admin_app.get('/statistics/login')
@checkAccess
def getLoginStatistics(redis, session):
    lang = getLang()
    curTime = datetime.now()
    isList = request.GET.get('list', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()

    selfUid = session['id']
    if int(selfUid) == 1:
        agentIds = []
    else:
        agentIds = getAllChildAgentId(redis, selfUid)

    if isList:
        res = getloginCountList(redis, selfUid, agentIds, startDate, endDate)
        return json.dumps(res)
    else:
        info = {
            'title': '日登录人数统计',
            'listUrl': BACK_PRE + '/statistics/login?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

    return template('admin_statistics_login', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/statistics/login/list')
def getRegStatisticsList(redis, session):
    lang = getLang()
    curTime = datetime.now()
    isList = request.GET.get('list', '').strip()
    reg_date = request.GET.get('reg_date', '').strip()
    selfUid = session['id']

    if isList:
        res = getLoginListByRegDate(redis, session['id'], reg_date)
        return json.dumps(res)
    else:
        info = {
            'title': '%s 登录列表' % (reg_date),
            'listUrl': BACK_PRE + '/statistics/login/list?list=1&reg_date=%s' % (reg_date),
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
        }

        return template('admin_statistics_login_list', reg_date=reg_date, info=info, lang=lang, RES_VERSION=RES_VERSION)


# @admin_app.get('/statistics/count')
# def getCountStatics(redis,session):
#     """
#     获取每日的局数统计
#     """
#     lang = getLang()
#     curTime = datetime.now()
#     isList = request.GET.get('list','').strip()
#     startDate = request.GET.get('startDate','').strip()
#     endDate = request.GET.get('endDate','').strip()
#     selfUid = request.GET.get('id','').strip()
#     date    = request.GET.get('date','').strip()

#     if date:
#         endDate = date

#     log_debug('[count] startDate[%s] endDate[%s]'%(startDate,endDate))

#     if not selfUid:
#         selfUid = session['id']

#     agentType = session['type']
#     openList = 'true'
#     if int(agentType) == 2:
#         openList = 'false'
#     if isList:
#         res = getCountTotal(redis,selfUid,startDate,endDate)
#         return json.dumps(res)
#     else:
#         info = {
#                 'title'         :       '局数统计',
#                 'listUrl'                :           BACK_PRE+'/statistics/count?list=1',
#                 'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
#                 'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
#         }

#     return template('admin_statistics_count',openList=openList,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/statistics/active')
def get_active_page(redis, session):
    """
    活跃人数统计
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    start_date = request.GET.get('startDate', '').strip()
    end_date = request.GET.get('endDate', '').strip()
    selfUid = session['id']
    if isList:
        active_reports = get_active_reports(redis, start_date, end_date, selfUid)
        return json.dumps(active_reports)
    else:
        info = {
            'title': '活跃人数统计',
            'listUrl': BACK_PRE + '/statistics/active?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

        return template('admin_statistics_active', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION, lang=lang)


@admin_app.get('/statistics/active/showDay')
def get_active_day(redis, session):
    """
    活跃人数统计
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    date = request.GET.get('day', '').strip()
    selfUid = session['id']
    if isList:
        active_reports = get_login_list2(redis, session['id'], date)
        return json.dumps(active_reports)
    else:
        info = {
            'title': '[%s]统计列表' % (date),
            'listUrl': BACK_PRE + '/statistics/active/showDay?list=1&day=%s' % (date),
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

        return template('admin_statistics_login_list', PAGE_LIST=PAGE_LIST, date=date, info=info,
                        RES_VERSION=RES_VERSION, lang=lang)


@admin_app.get('/statistics/history')
def get_history_active_page(redis, session):
    """
    活跃人数统计
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    start_date = request.GET.get('startDate', '').strip()
    end_date = request.GET.get('endDate', '').strip()
    selfUid = session['id']

    if isList:
        active_reports = statisticsRealTime(redis, start_date, end_date, selfUid)
        return json.dumps(active_reports)
    else:
        info = {
            'title': '活跃人数统计历史',
            'listUrl': BACK_PRE + '/statistics/history?list=1',
            'serversUrl': BACK_PRE + '/statistics/room_cards/history?list=1',
            'serversSubUrl': BACK_PRE + '/statistics/game_record/history?list=1',
            'serversSubsubUrl': BACK_PRE + '/statistics/play_room/history?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

        return template('admin_statistics_history_list', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION,
                        lang=lang)


@admin_app.get('/statistics/room_cards/history')
def getStatisticsHistoryPlayroom(redis, session):
    """
    数据统计-活跃人数统计历史-耗钻详情
    """
    id = request.GET.get('id', '').strip()
    startTime = request.GET.get('startDate', '').strip()
    account = redis.hget(FORMAT_USER_TABLE % (id), 'account')
    startTime = float(time.mktime(time.strptime(startTime, '%Y-%m-%d')))
    endTime = float(startTime + 86400)

    res = []
    try:
        sql = """select id, cards, room_id, agent_id, room_number, user_id, game_id, club_number, create_time, update_time from room_cards where  user_id='%s' and create_time>='%s' and create_time<='%s' order by create_time desc """ \
              % (id, startTime, endTime)
        results = MysqlljgameInterface.select(sql, fetchmany=False)
    except Exception as err:
        results = []

    print(sql)
    if results:
        for each in results:
            info = {}
            info['create_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(each[4].split('-')[1]))) if \
            each[4].split('-')[1] else ''
            info['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(each[8])) if each[8] else ''
            info['id'] = each[5]
            info['account'] = redis.hget(FORMAT_USER_TABLE % (each[5]), "account")
            info['nickname'] = redis.hget(FORMAT_USER_TABLE % (each[5]), "nickname")
            info['room_id'] = each[2]
            info['game_id'] = each[6]
            info['game_name'] = redis.hget(GAME_TABLE % (each[6]), "name")
            info['Ag'] = each[3]
            if each[3]:
                parent_id = redis.hget(AGENT_TABLE % each[3], 'parent_id')
                info['parentAg'] = parent_id
            info['room_number'] = each[4]
            info['club_id'] = each[7]
            info['use_count'] = each[1]
            res.append(info)

    reports = {'data': res, 'count': len(res)}
    return json.dumps(reports)


@admin_app.get('/statistics/game_record/history')
def getStatisticsHistoryGameroom(redis, session):
    """
    数据统计-活跃人数统计历史-耗钻详情
    """

    starttime = request.GET.get('time', '').strip()
    roomId = request.GET.get('roomId', '').strip()
    player = request.GET.get('player', '').strip()
    room_number = request.GET.get('room_number', '').strip()

    try:
        sql = """select game_id, owner, round , total_round, start_time, end_time, room_number,game_type,game_number, create_time, update_time, is_deleted from game_record where game_number='%s'""" \
              % (room_number)
        results = MysqlljgameInterface.select(sql, fetchmany=False)
    except Exception as err:
        results = []

    res = []
    if results:
        for i in results:
            info = {}
            info['game_id'] = i[0]
            info['owner'] = i[1]
            info['round'] = i[2]
            info['total_round'] = i[3]
            info['start_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i[4])) if i[4] else ''
            info['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i[5])) if i[5] else ''
            info['room_number'] = i[6]
            info['game_type'] = i[7]
            info['game_number'] = i[8]
            info['create_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[9])) if i[9] else ''
            info['update_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[10])) if i[10] else ''
            info['is_delete'] = i[11]
            info['owner_account'] = redis.hget("users:%s" % (i[1]), "account")
            info['owner_nickname'] = redis.hget("users:%s" % (i[1]), "nickname")
            res.append(info)

    reports = {'data': res, 'count': len(res)}
    return json.dumps(reports)


@admin_app.get('/statistics/play_room/history')
def getStatisticsHistoryPlayrroom(redis, session):
    """
    数据统计-活跃人数统计历史-耗钻详情
    """
    room_number = request.GET.get('room_number', '').strip()

    try:
        sql = """select user_id, room_id, room_number ,create_time, update_time, is_deleted from player_room where room_number='%s'""" \
              % (room_number)
        results = MysqlljgameInterface.select(sql, fetchmany=False)
    except Exception as err:
        results = []

    print(sql)
    print(results)

    res = []
    if results:
        for i in results:
            info = {}
            info['user_id'] = i[0]
            info['account'] = redis.hget("users:%s" % (i[0]), "account")
            info['nickname'] = redis.hget("users:%s" % (i[0]), "nickname")
            info['room_id'] = i[1]
            info['room_number'] = i[2]
            info['create_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[3])) if i[3] else ''
            info['update_time'] = i[4]
            info['is_delete'] = i[5]
            res.append(info)

    reports = {'data': res, 'count': len(res)}
    return json.dumps(reports)


@admin_app.get('/statistics/new/history')
def get_new_history_active_page(redis, session):
    """
    活跃人数统计历史（新）-- 使用mysql查询
    :param redis: redis
    :param session: session
    :return: template if islist else json
    """
    curTime = datetime.now()
    lang = getLang()

    fields = (
    'islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText', 'userid', 'account', 'nickname',
    'ag', 'parag', 'clubid', 'roomid', 'gameid', 'gamename', 'cards', 'roomkey', 'parentag')

    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))

    if not pageNumber:
        pageNumber = 1
    else:
        pageNumber = convert_util.to_int(pageNumber)

    fields = (
    startDate, endDate, pageNumber, pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey)

    if islist:
        data = get_new_history_active_reports(redis, *fields)
        return json.dumps(data)
    else:
        info = {
            'title': '活跃人数统计历史',
            'listUrl': BACK_PRE + '/statistics/new/history?islist=1',
            'serversUrl': BACK_PRE + '/statistics/new/gamerecord?list=1',
            'serversUrlTwo': BACK_PRE + '/statistics/new/playerroom?list=1',
            'sumListUrl': BACK_PRE + '/statistics/new/sum/history?list=1',
            'sumDayListUrl': BACK_PRE + '/statistics/new/sumday/history?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }
        return template('admin_statistics_new_history_list', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION,
                        lang=lang)


@admin_app.get('/statistics/new/sumday/history')
def get_new_history_active_sumday(redis, session):
    """
    统计活跃人数统计历史耗钻总数（新）- 按搜索条件 - 使用mysql查询
    :param redis: redis
    :param session: session
    :return:
    """
    fields = (
    'islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText', 'userid', 'account', 'nickname',
    'ag', 'parag', 'clubid', 'roomid', 'gameid', 'gamename', 'cards', 'roomkey', 'parentag')
    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))
    fields = (
    startDate, endDate, pageNumber, pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey)

    data = get_new_history_active_sumday_reports(redis, *fields)
    return json.dumps(data)


@admin_app.get('/statistics/new/sum/history')
def get_new_history_active_sum(redis, session):
    """
    统计活跃人数统计历史耗钻总数（新）- 按全部数据 - 使用mysql查询
    :param redis: redis
    :param session: session
    :return:
    """
    res = []
    sql = """select  sum(cards)  from  room_cards"""
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
    data = {'data': res}
    return json.dumps(data)


@admin_app.get('/statistics/new/playerroom')
def get_new_playerroom_active_page(redis, session):
    """
    显示同一房间玩家数据统计详情(玩家房间详情) - mysql查询（按照room_number来分组）
    :param redis: redis
    :param session: session
    :return:
    """
    curTime = datetime.now()
    lang = getLang()
    islist = request.GET.get('list', '').strip()
    roomkey = request.GET.get('roomkey', '').strip()
    if islist:
        res = []
        sql = """select user_id, room_id, room_number ,create_time, update_time, is_deleted from player_room where room_number='%s'""" % (
            roomkey)
        results = MysqlljgameInterface.select(sql, fetchmany=False)
        if results:
            for i in results:
                info = {}
                info['user_id'] = i[0]
                info['account'] = redis.hget("users:%s" % (i[0]), "account")
                info['nickname'] = redis.hget("users:%s" % (i[0]), "nickname")
                info['room_id'] = i[1]
                info['room_number'] = i[2]
                info['create_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[3])) if i[3] else ''
                info['update_time'] = i[4]
                info['is_delete'] = i[5]
                res.append(info)
        return json.dumps(res)
    else:
        info = {
            'title': '同一房间玩家数据统计',
            'listUrl': BACK_PRE + '/statistics/new/playerroom?list=1&roomkey=%s' % (roomkey),
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }
    return template('admin_statistics_new_history_playerroom', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION,
                    lang=lang)


@admin_app.get('/statistics/new/gamerecord')
def get_new_gamerecord_active_page(redis, session):
    """
    显示游戏记录 - mysql查询（按照room_number来查询）
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()
    islist = request.GET.get('list', '').strip()
    roomkey = request.GET.get('roomkey', '').strip()
    if islist:
        res = []
        sql = """select game_id, owner, round , total_round, start_time, end_time, room_number,game_type,game_number, create_time, update_time, is_deleted from game_record where game_number='%s'""" % (
            roomkey)
        results = MysqlljgameInterface.select(sql, fetchmany=False)
        if results:
            for i in results:
                info = {}
                info['game_id'] = i[0]
                info['owner'] = i[1]
                info['round'] = i[2]
                info['total_round'] = i[3]
                info['start_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[4])) if i[4] else ''
                info['end_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[5])) if i[5] else ''
                info['room_number'] = i[6]
                info['game_type'] = i[7]
                info['game_number'] = i[8]
                info['create_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[9])) if i[9] else ''
                info['update_time'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(i[10])) if i[10] else ''
                info['is_delete'] = i[11]
                info['owner_account'] = redis.hget("users:%s" % (i[1]), "account")
                info['owner_nickname'] = redis.hget("users:%s" % (i[1]), "nickname")

                res.append(info)
        return json.dumps(res)
    else:
        info = {
            'title': '游戏记录',
            'listUrl': BACK_PRE + '/statistics/new/gamerecord?list=1&roomkey=%s' % (roomkey),
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }
    return template('admin_statistics_new_history_gamerecord', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION,
                    lang=lang)


@admin_app.get('/statistics/roomcard')
@checkAccess
def get_roomcard_page(redis, session):
    """
    游戏耗钻数统计
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    start_date = request.GET.get('startDate', '').strip()
    end_date = request.GET.get('endDate', '').strip()

    if isList:
        data = get_roomcard_reports(redis, start_date, end_date)
        return json.dumps(data)
    else:
        info = {
            'title': '游戏耗钻数统计',
            'listUrl': BACK_PRE + '/statistics/roomcard?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
        }
    return template('admin_statistics_roomcard', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION, lang=lang)


@admin_app.get('/statistics/roomcard/showDay')
def get_roomcard_day(redis, session):
    """
    游戏耗钻数统计-查看当日详细-（只查询当天一天的数据）
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    date = request.GET.get('day', '').strip()
    gameTotal_Day = 0
    if isList:
        res = []
        game_ids = redis.lrange(GAME_LIST, 0, -1)
        for i in game_ids:
            rcday = redis.get("game:roomCards:%s:%s:total" % (i, date))
            if not rcday:
                rcday = 0
            gameTotal_Day += int(rcday)
            res.append({
                'id': i,
                'gamename': redis.hget(GAME_TABLE % (i), 'name'),
                'roomcards_day': rcday,
            })
        for item in res:
            if gameTotal_Day:
                baifenbi = "%.2f%%" % (float(item.get('roomcards_day')) / float(gameTotal_Day) * 100)
            else:
                baifenbi = "%.2f%%" % (0)
            item.update({'GameBaiFenbi': baifenbi})
        res = {'data': res, 'count': res}
        return json.dumps(res)
    else:
        info = {
            'title': '[%s]统计列表' % (date),
            'listUrl': BACK_PRE + '/statistics/roomcard/showDay?list=1&day=%s' % (date),
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

        return template('admin_statistics_roomcard_list', PAGE_LIST=PAGE_LIST, date=date, info=info,
                        RES_VERSION=RES_VERSION, lang=lang)


@admin_app.get('/statistics/rcday')
def get_roomcard_rcday(redis, session):
    """
    游戏耗钻数统计-（查询某段时间的数据）
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()

    if isList:
        data = get_roomcard_rcday_reports(redis, startDate, endDate)
        return json.dumps(data)
    else:
        info = {
            'title': '游戏耗钻合计列表',
            'listUrl': BACK_PRE + '/statistics/rcday?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

        return template('admin_statistics_rcday', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION,
                        lang=lang)


@admin_app.get('/statistics/club')
@checkAccess
def get_statistics_club_page(redis, session):
    """
    亲友圈耗钻数统计
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    start_date = request.GET.get('startDate', '').strip()
    end_date = request.GET.get('endDate', '').strip()
    selfUid = session['id']
    if isList:
        active_reports = get_club_roomcards_reports(redis, start_date, end_date)
        return json.dumps(active_reports)
    else:
        info = {
            'title': '亲友圈耗钻数统计',
            'listUrl': BACK_PRE + '/statistics/club?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

    return template('admin_statistics_club', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION, lang=lang)


@admin_app.get('/statistics/club/showDay')
def get_club_day(redis, session):
    """
    某段时间内亲友圈耗钻总数统计
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    date = request.GET.get('day', '').strip()
    if isList:
        res = []
        club_ids = redis.smembers(CLUB_LIST)
        for i in club_ids:
            rcday = redis.get("club:roomCards:day:%s:%s:total" % (i, date))
            clubattr = redis.hgetall("club:attribute:%s:hash" % (i))
            if not rcday:
                rcday = 0
            userid = redis.get(FORMAT_ACCOUNT2USER_TABLE % (clubattr.get('club_user', ''))).split(':')[-1]
            nickname = redis.hget(FORMAT_USER_TABLE % userid, "nickname")
            res.append({
                'id': i,
                'roomcards_day': rcday,
                'club_name': clubattr.get('club_name', ''),
                'club_user': clubattr.get('club_user', ''),
                'club_nickname': nickname,
                'club_agent': clubattr.get('club_agent', ''),
                'club_member': redis.scard(CLUB_PLAYER_LIST % i)
            })
        res = {'data': res, 'count': len(res)}
        return json.dumps(res)
    else:
        info = {
            'title': '[%s]统计列表' % (date),
            'listUrl': BACK_PRE + '/statistics/club/showDay?list=1&day=%s' % (date),
            'serversUrl': BACK_PRE + '/agent/club/user/list?list=1&day=%s' % (date),
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

        return template('admin_statistics_club_list', PAGE_LIST=PAGE_LIST, date=date, info=info,
                        RES_VERSION=RES_VERSION, lang=lang)


@admin_app.get('/statistics/clubrcday')
def get_clubrcday(redis, session):
    """
    某段时间内亲友圈耗钻总数统计
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    start_date = request.GET.get('startDate', '').strip()
    end_date = request.GET.get('endDate', '').strip()

    if isList:
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
        game_ids = redis.smembers(CLUB_LIST)
        now_time = datetime.now()

        while endDate >= startDate:
            if endDate >= now_time:
                endDate -= deltaTime
                continue
            dateStr = endDate.strftime('%Y-%m-%d')
            for i in game_ids:
                rcday = redis.get("club:roomCards:day:%s:%s:total" % (i, dateStr))
                if not rcday:
                    rcday = 0
                res.append({
                    'id': i,
                    'clubname': redis.hget(CLUB_ATTR % (i), 'club_name'),
                    'clubuser': redis.hget(CLUB_ATTR % (i), 'club_user'),
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
            club_user = redis.hget(CLUB_ATTR % (v), 'club_user')
            userid = redis.get(FORMAT_ACCOUNT2USER_TABLE % (club_user)).split(':')[-1]
            nickname = redis.hget(FORMAT_USER_TABLE % userid, "nickname")

            createtime = redis.hget(CLUB_ATTR % (v), 'club_createtime')
            createtime = createtime.split(' ')[0] if createtime else ''
            club_agent = redis.hget(CLUB_ATTR % (v), 'club_agent')
            temp1.append(
                {'clubid': v,
                 'roomcards_day': k,
                 'clubuser': club_user,
                 'clubtime': createtime,
                 'userid': userid,
                 'nickname': nickname,
                 'club_agent': club_agent,
                 'club_member': redis.scard(CLUB_PLAYER_LIST % v)
                 })
        data = {'data': temp1, 'count': len(temp1)}
        return json.dumps(data)
    else:
        info = {
            'title': '亲友圈耗钻合计列表',
            'listUrl': BACK_PRE + '/statistics/clubrcday?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

        return template('admin_statistics_clubrcday', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION,
                        lang=lang)


@admin_app.get('/statistics/clubchange')
@checkAccess
def get_clubstatistics(redis, session):
    """
    亲友圈数据统计（新增/删除每一天的数据）
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()

    date = request.GET.get('day', '').strip()
    if isList:
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
        club_dissolution_list = redis.lrange("club:dissolution:list", 0, -1)
        club_list = redis.smembers("club:list:set")
        now_time = datetime.now()
        while endDate >= startDate:
            info = {}
            if endDate >= now_time:
                endDate -= deltaTime
                continue
            dateStr = endDate.strftime('%Y-%m-%d')
            add_count, del_count = 0, 0
            add_club_list, del_club_list = [], []
            for item in club_dissolution_list:
                if dateStr in item:
                    club_id, club_account, date = item.split(':')
                    del_count += 1
                    del_club_list.append(club_id)
                    info['date'] = date
                    info['club_account'] = club_account
                    info['del_club'] = del_count
                    info['del_club_list'] = del_club_list
            for item in club_list:
                club_attr = redis.hgetall("club:attribute:%s:hash" % (item))
                if dateStr in club_attr.get("club_createtime", ""):
                    add_count += 1
                    add_club_list.append(item)
                    info['date'] = dateStr
                    info['add_club'] = add_count
                    info['add_club_list'] = add_club_list
            if info:
                info['op'] = []
                res.append(info)
            endDate -= deltaTime

        res = {'data': res, 'count': len(res)}
        return json.dumps(res)
    else:
        info = {
            'title': '亲友圈数据统计',
            'listUrl': BACK_PRE + '/statistics/clubchange?list=1',
            'serversUrl': BACK_PRE + '/statistics/clubchange/addlist?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }
        return template('admin_statistics_clubchange', PAGE_LIST=PAGE_LIST, date=date, info=info,
                        RES_VERSION=RES_VERSION, lang=lang)


@admin_app.get('/statistics/clubchange/addlist')
def get_clubaddstatistics(redis, session):
    """
    亲友圈数据统计
    :param redis:
    :param session:
    :return:
    """
    date = request.GET.get("date", "").strip()
    club_list = redis.smembers("club:list:set")
    club_dissolution_list = redis.lrange("club:dissolution:list", 0, -1)
    res = []
    for item in club_list:
        club_attr = redis.hgetall("club:attribute:%s:hash" % (item))
        if date in club_attr.get("club_createtime", ""):
            info = {}
            info['date'] = date
            info['type'] = u'新增'
            info['club_id'] = item
            userid = redis.get("users:account:%s" % (club_attr.get('club_user', ''))).split(':')[-1]
            info['club_userid'] = userid
            info['club_nickname'] = redis.hget("users:%s" % userid, "nickname")
            info['club_account'] = club_attr.get('club_user', '')
            info['club_agent'] = club_attr.get('club_agent', '')
            info['club_member'] = redis.scard(CLUB_PLAYER_LIST % item)
            res.append(info)
    for item in club_dissolution_list:
        if date in item:
            info = {}
            club_id, club_account, date = item.split(':')
            info['date'] = date
            info['type'] = u'解散'
            info['club_id'] = club_id
            userid = redis.get("users:account:%s" % (club_account)).split(':')[-1]
            info['club_nickname'] = redis.hget("users:%s" % userid, "nickname")
            info['club_agent'] = redis.hget("users:%s" % userid, "parentAg")
            info['club_userid'] = userid
            info['club_account'] = club_account
            res.append(info)

    data = {"data": res, "count": len(res)}
    return json_dumps(data)


@admin_app.get('/statistics/new/member')
def get_new_history_active_member(redis, session):
    """
    按照会员来显示活跃人数统计历史
    活跃人数统计历史 -- mysql查询 -- 据按照会员来分组显示
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    fields = (
    'islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText', 'userid', 'account', 'nickname',
    'ag', 'parag', 'clubid', 'roomid', 'gameid', 'gamename', 'cards', 'roomkey', 'parentag')

    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))
    if not pageNumber:
        pageNumber = 1
    else:
        pageNumber = convert_util.to_int(pageNumber)
    fields = (
    startDate, endDate, pageNumber, pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey)

    if islist:
        data = get_new_history_active_member_reports(redis, *fields)
        return json.dumps(data)
    else:
        info = {
            'title': '活跃人数统计历史[按会员分组]',
            'listUrl': BACK_PRE + '/statistics/new/member?islist=1',
            'serversUrl': BACK_PRE + '/statistics/new/playerroom?',
            'sumListUrl': BACK_PRE + '/statistics/new/sum/history?list=1',
            'sumDayListUrl': BACK_PRE + '/statistics/new/sumday/history?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }
        return template('admin_statistics_new_history_member', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION,
                        lang=lang)


@admin_app.get('/statistics/new/agentid')
def get_new_history_active_agent(redis, session):
    """
    按照公会ID来显示活跃人数统计历史
    活跃人数统计历史 -- mysql查询 -- 据按照公会来分组显示
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    fields = (
    'islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText', 'userid', 'account', 'nickname',
    'ag', 'parag', 'clubid', 'roomid', 'gameid', 'gamename', 'cards', 'roomkey', 'parentag')

    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))
    if not pageNumber:
        pageNumber = 1
    else:
        pageNumber = convert_util.to_int(pageNumber)
    fields = (
    startDate, endDate, pageNumber, pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey)

    if islist:
        data = get_new_history_active_agent_reports(redis, *fields)
        return json.dumps(data)
    else:
        info = {
            'title': '活跃人数统计历史[按公会分组]',
            'listUrl': BACK_PRE + '/statistics/new/agentid?islist=1',
            'sumListUrl': BACK_PRE + '/statistics/new/sum/history?list=1',
            'sumDayListUrl': BACK_PRE + '/statistics/new/sumday/history?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }
        return template('admin_statistics_new_history_agent_id', PAGE_LIST=PAGE_LIST, info=info,
                        RES_VERSION=RES_VERSION,
                        lang=lang)


@admin_app.get('/statistics/new/clubid')
def get_new_history_active_club(redis, session):
    """
    按照亲友圈来显示活跃人数统计历史
    活跃人数统计历史 -- mysql查询 -- 按照亲友圈来分组显示
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    fields = (
    'islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText', 'userid', 'account', 'nickname',
    'ag', 'parag', 'clubid', 'roomid', 'gameid', 'gamename', 'cards', 'roomkey', 'parentag')

    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))
    if not pageNumber:
        pageNumber = 1
    else:
        pageNumber = convert_util.to_int(pageNumber)
    fields = (
    startDate, endDate, pageNumber, pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey)

    if islist:
        data = get_new_history_active_club_reports(redis, *fields)
        return json.dumps(data)
    else:
        info = {
            'title': '活跃人数统计历史[按亲友圈分组]',
            'listUrl': BACK_PRE + '/statistics/new/clubid?islist=1',
            'sumListUrl': BACK_PRE + '/statistics/new/sum/history?list=1',
            'sumDayListUrl': BACK_PRE + '/statistics/new/sumday/history?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }
        return template('admin_statistics_new_history_clubnumber', PAGE_LIST=PAGE_LIST, info=info,
                        RES_VERSION=RES_VERSION,
                        lang=lang)


@admin_app.get('/statistics/new/roomid')
def get_new_history_active_room(redis, session):
    """
    按照房间来显示活跃人数统计历史
    活跃人数统计历史 -- mysql查询 -- 按照房间来分组显示
    :param redis:
    :param session:
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    fields = (
    'islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText', 'userid', 'account', 'nickname',
    'ag', 'parag', 'clubid', 'roomid', 'gameid', 'gamename', 'cards', 'roomkey', 'parentag')

    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))
    if not pageNumber:
        pageNumber = 1
    else:
        pageNumber = convert_util.to_int(pageNumber)
    fields = (
    startDate, endDate, pageNumber, pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey)

    if islist:
        data = get_new_history_active_room_reports(redis, *fields)
        return json.dumps(data)
    else:
        info = {
            'title': '活跃人数统计历史[按房间分组]',
            'listUrl': BACK_PRE + '/statistics/new/roomid?islist=1',
            'sumListUrl': BACK_PRE + '/statistics/new/sum/history?list=1',
            'sumDayListUrl': BACK_PRE + '/statistics/new/sumday/history?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }
        return template('admin_statistics_new_history_roomid', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION,
                        lang=lang)


@admin_app.get('/statistics/new/gameid')
def get_new_history_active_game(redis, session):
    """
     按照游戏来显示活跃人数统计历史
     活跃人数统计历史 -- mysql查询 -- 按游戏来分组显示
     :param redis:
     :param session:
     :return:
     """
    curTime = datetime.now()
    lang = getLang()

    fields = (
        'islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText', 'userid', 'account',
        'nickname',
        'ag', 'parag', 'clubid', 'roomid', 'gameid', 'gamename', 'cards', 'roomkey', 'parentag')

    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))
    if not pageNumber:
        pageNumber = 1
    else:
        pageNumber = convert_util.to_int(pageNumber)
    fields = (
    startDate, endDate, pageNumber, pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey)

    if islist:
        data = get_new_history_active_game_reports(redis, *fields)
        return json.dumps(data)
    else:
        info = {
            'title': '活跃人数统计历史[按游戏分组]',
            'listUrl': BACK_PRE + '/statistics/new/gameid?islist=1',
            'sumListUrl': BACK_PRE + '/statistics/new/sum/history?list=1',
            'sumDayListUrl': BACK_PRE + '/statistics/new/sumday/history?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }
        return template('admin_statistics_new_history_gameid', PAGE_LIST=PAGE_LIST, info=info, RES_VERSION=RES_VERSION,
                        lang=lang)


@admin_app.get('/statistics/new/roomnumber')
def get_new_history_active_roomnumber(redis, session):
    """
     按照房间标识来显示活跃人数统计历史
     活跃人数统计历史 -- mysql查询 -- 按房间标识来分组显示
     :param redis:
     :param session:
     :return:
     """
    curTime = datetime.now()
    lang = getLang()

    fields = (
        'islist', 'startDate', 'endDate', 'uid', 'pageSize', 'pageNumber', 'searchText', 'userid', 'account',
        'nickname',
        'ag', 'parag', 'clubid', 'roomid', 'gameid', 'gamename', 'cards', 'roomkey', 'parentag')

    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))

    if not pageNumber:
        pageNumber = 1
    else:
        pageNumber = convert_util.to_int(pageNumber)
    fields = (
    startDate, endDate, pageNumber, pageSize, parentag, userid, nickname, ag, clubid, roomid, gameid, cards, roomkey)

    if islist:
        data = get_new_history_active_roomnumber_reports(redis, *fields)
        return json.dumps(data)
    else:
        info = {
            'title': '活跃人数统计历史[按房间标识分组]',
            'listUrl': BACK_PRE + '/statistics/new/roomnumber?islist=1',
            'sumListUrl': BACK_PRE + '/statistics/new/sum/history?list=1',
            'sumDayListUrl': BACK_PRE + '/statistics/new/sumday/history?list=1',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }
        return template('admin_statistics_new_history_roomnumber', PAGE_LIST=PAGE_LIST, info=info,
                        RES_VERSION=RES_VERSION,
                        lang=lang)
