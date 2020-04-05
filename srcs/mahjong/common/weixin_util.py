# -*- coding:utf-8 -*-
# !/bin/python

"""
Author: $Author$
Date: $Date$
Revision: $Revision$

Description:
    微信公众号消息推送
"""

from config.config import *
import requests
from server_common.web_db_define import *
from datetime import datetime
import json

def getWeixinRequest(url, params, key=None):
    """
    获取请求url数据
    """
    try:
        res = requests.get(url=url, params=params).json()
        data = res.get(key) if key else res
    except Exception as err:
        print(u"请求地址失败，可检测网络是否通畅")
        data = None
    return data

def getWeixinRequestData(redis, code):
    """
    获取微信授权用户 access_token 和 openid
    """
    access_token = getWeixinRequest(WX_ACCESS_TOKEN_URL, WX_ACCESS_TOKEN_PARAMS, key="access_token")

    openid_url = WX_USER_OPENID_URL
    openid_params = WX_USER_OPENID_PARAMS
    if code:
        openid_params['code'] = code
    openid = getWeixinRequest(openid_url, openid_params, key="openid")

    if access_token and openid:
        return (access_token, openid)
    else:
        return (None, None)

def getWeixinOrderPush(redis, openid, orderInfo, type="applyAccount"):
    """
    微信公众号推送新订单提醒消息
    """
    access_token = getWeixinRequest(WX_ACCESS_TOKEN_URL, WX_ACCESS_TOKEN_PARAMS, key="access_token")

    member = redis.get("wx:order:%s:member" % orderInfo.get("orderNo"))
    if type == 'applyAccount':
        title = u"""您好！[ {applyAccount} ]
您的申购 ({cardNums}个) 新订单已申请成功
(请注意 , 此笔订单您是购买方 , 当前您的余额为：{balance} , 要购买的数量为：{cardNums})
""".format(**orderInfo)
        url = ""
    else:
        url = "http://lj3.qianguisy.com/admin/wx/order/sale/record?orderNo=%s&saleAccount=%s&applyAccount=%s&member=%s" % (orderInfo.get("orderNo"), orderInfo.get("saleAccount"), orderInfo.get('applyAccount'), member)
        title = u"""您好！[ {saleAccount} ]
您有一笔来以 [ {applyAccount} ] 的申购 ({cardNums}个) 新订单
(请注意 , 此笔订单您是售卖方 , 当前您的余额为：{balance} , 要售出的数量为：{cardNums})
""".format(**orderInfo)

    url_msg = WX_TEMPLATE_URL
    body = {
        "touser": openid,
        "template_id": WX_TEMPLATE_ORDER_PUSH_ID,
        "url": url,
        "topcolor": "#FF0000",

        "data": {
            "first": {
                "value": title,
                "color": "#173177"
            },
            "keyword1": {
                "value": u"申购订单",
                "color": "#053c69"
            },
            "keyword2": {
                "value": "%s" % (orderInfo.get("orderNo")),
                "color": "#053c69"
            },
            "keyword3": {
                "value": u"%s 个" % (orderInfo.get("cardNums")),
                "color": "#053c69"
            },
            "keyword4": {
                "value": "%s" % (orderInfo.get("apply_date")),
                "color": "#053c69"
            },
            "remark": {
                "value": u"\n备注信息：%s" % (orderInfo.get("note", "无")),
                "color": "#d40f24"
            }
        }
    }

    res = requests.post(url=url_msg, params={
        'access_token': access_token
    }, data=json.dumps(body, ensure_ascii=False).encode('utf-8'))


def getWeixinOrderComfire(redis, openid, orderInfo, type="saleAccount"):
    """
    微信公众号推送订单确认消息
    """
    access_token = getWeixinRequest(WX_ACCESS_TOKEN_URL, WX_ACCESS_TOKEN_PARAMS, key="access_token")

    if type == "saleAccount":
        title = u"""您好！[ {saleAccount} ]
[ {applyAccount} ]发起的申购 ({cardNums}个) 订单已被您确认成功
(请注意 , 此笔订单您是售卖方 , 当前您的余额为：{balance})
""".format(**orderInfo)
        remark = u"""
售卖方：{saleAccount}
购买方：{applyAccount}
购买数：{cardNums}
订单生成日期：{apply_date}
""".format(**orderInfo)
    else:
        title = u"""您好！[ {applyAccount} ]
您的申购 ({cardNums}个) 订单已被 [ {saleAccount} ] 确认成功
(请注意 , 此笔订单您是购买方 , 当前您的余额为：{balance})
""".format(**orderInfo)
        remark = u"""
购买方：{applyAccount}
购卖数：{cardNums}
售卖方：{saleAccount}
订单生成日期：{apply_date}
""".format(**orderInfo)
    url_msg = WX_TEMPLATE_URL
    body = {
        "touser": openid,
        "template_id": WX_TEMPLATE_ORDER_COMFIRM_ID,
        "url": "",
        "topcolor": "#FF0000",

        "data": {
            "first": {
                "value": title,
                "color": "#173177"
            },
            "keyword1": {
                "value": "%s" % (orderInfo.get("finish_date")),
                "color": "#053c69"
            },
            "keyword2": {
                "value": u"%s" % (orderInfo.get("orderNo")),
                "color": "#053c69"
            },
            "remark": {
                "value": remark,
                "color": "#CC3333"
            }
        }
    }

    res = requests.post(url=url_msg, params={
        'access_token': access_token
    }, data=json.dumps(body, ensure_ascii=False).encode('utf-8'))

def getWeixinOrderCancel(redis, openid, orderInfo, type="saleAccount", agent_type=False):
    """
    微信公众号推送订单取消消息
    """
    access_token = getWeixinRequest(WX_ACCESS_TOKEN_URL, WX_ACCESS_TOKEN_PARAMS, key="access_token")

    if type == "saleAccount":
        if agent_type:
            # 购钻方主动取消订单，售钻放收取信息
            title = u"""您好！[ {saleAccount} ]
[ {applyAccount} ]发起的申购 ({cardNums}个) 订单已被本人主动取消成功
(请注意 , 此笔订单您是售卖方 , 当前您的余额为：{balance} , 要售出的数量为：{cardNums})
""".format(**orderInfo)
        else:
            # 售钻方主动取消订单，售钻放收取信息
            title = u"""您好！[ {saleAccount} ]
[ {applyAccount} ]发起的申购 ({cardNums}个) 订单已被您取消成功
(请注意 , 此笔订单您是售卖方 , 当前您的余额为：{balance} , 要售出的数量为：{cardNums})
""".format(**orderInfo)
    else:
        if agent_type:
            # 购钻方主动取消订单，购钻方收取信息
            title = u"""您好！[ {applyAccount} ]
您发起的申购 ({cardNums}个) 订单已被您取消成功
(请注意 , 此笔订单您是购买方 , 当前您的余额为：{balance} , 要购买的数量为：{cardNums})
""".format(**orderInfo)
        else:
            # 售钻方主动取消订单，购钻方收取信息
            title = u"""您好！[ {applyAccount} ]
您发起的申购 ({cardNums}个) 订单已被 [ {saleAccount} ] 主动取消成功
(请注意 , 此笔订单您是购买方 , 当前您的余额为：{balance} , 要购买的数量为：{cardNums})
""".format(**orderInfo)
    url_msg = WX_TEMPLATE_URL
    body = {
        "touser": openid,
        "template_id": WX_TEMPLATE_ORDER_CANCEL_ID,
        "url": "",
        "topcolor": "#FF0000",

        "data": {
            "first": {
                "value": title,
                "color": "#173177"
            },
            "keyword1": {
                "value": u"%s" % (orderInfo.get("orderNo")),
                "color": "#053c69"
            },
            "keyword2": {
                "value": "%s" % (orderInfo.get("apply_date")),
                "color": "#053c69"
            },
            "keyword3": {
                "value": "%s" % (orderInfo.get("applyAccount")),
                "color": "#053c69"
            },
            "keyword4": {
                "value": "%s" % (orderInfo.get("saleAccount")),
                "color": "#053c69"
            },
            "keyword5": {
                "value": "%s 个" % (orderInfo.get("cardNums")),
                "color": "#053c69"
            },
            "remark": {
                "value": "\n订单取消日期：%s\n订单备注：%s" % (orderInfo.get("dateStr"),orderInfo.get("note")),
                "color": "#CC3333"
            }
        }
    }

    res = requests.post(url=url_msg, params={
        'access_token': access_token
    }, data=json.dumps(body, ensure_ascii=False).encode('utf-8'))


def getWeixinMemberRecharge(redis, openid, orderInfo):
    """
    公众号推送会员充值
    """
    access_token = getWeixinRequest(WX_ACCESS_TOKEN_URL, WX_ACCESS_TOKEN_PARAMS, key="access_token")

    title = u"""您好！[ {saleAccount} ]
您向[ {applyAccount} ]的补额( {cardNums}个 )订单已经成功
(请注意 , 此笔订单您是充额方 , 当前您的余额为：{balance} , 该玩家余额为：{playerRoomcard})
""".format(**orderInfo)
    remark = u"\n订单号：%s\n订单完成时间：%s\n" % (orderInfo.get("orderNo"), orderInfo.get("finish_date"))
    url_msg = WX_TEMPLATE_URL
    body = {
        "touser": openid,
        "template_id": WX_TEMPLATE_MEMBER_RECHARGE_ID,
        "topcolor": "#FF0000",

        "data": {
            "first": {
                "value": title,
                "color": "#173177"
            },
            "keyword1": {
                "value": u"%s 个" % (orderInfo.get("cardNums")),
                "color": "#053c69"
            },
            "keyword2": {
                "value": u"会员补额",
                "color": "#053c69"
            },
            "keyword3": {
                "value": u"%s 个" % (orderInfo.get("balance")),
                "color": "#053c69"
            },
            "remark": {
                "value": remark,
                "color": "#d40f24"
            }
        }
    }

    res = requests.post(url=url_msg, params={
        'access_token': access_token
    }, data=json.dumps(body, ensure_ascii=False).encode('utf-8'))


def getWeixinDataPush(redis, openid, dataInfo, agent_type):
    """
    微信公众号推送数据统计
    """
    access_token = getWeixinRequest(WX_ACCESS_TOKEN_URL, WX_ACCESS_TOKEN_PARAMS, key="access_token")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dataInfo['now'] = now
    if agent_type == '0':
        title = u"""您好！[ {account} ]
您的昨日报表 [ {date} ] 已经生成成功
报表发送时间：{now}

时间：{date}
用户数：{member_total}
注册数：{regist_per_day}
活跃数：{login_per_day}
耗钻数：{play_room_per_day}
一级经销购数：{agent_buy_total}
二级经销购数：{agent_sale_report_total}
玩家购数：{player_buy_total}
商城售钻金额：{gold_money_total}
商城售币金额：{card_money_total}
自身利润总占额：{rate_report_total}
下级经销利润总占额：{rate_report_agent_total}
        """.format(**dataInfo)
    elif agent_type == '1':
        title = u"""您好！[ {account} ]
您的昨日报表 [ {date} ] 已经生成成功
报表发送时间：{now}

时间：{date}
用户数：{member_total}
活跃数：{login_per_day}
耗钻数：{play_room_per_day}
自身购数：{self_buy_total}
下级经销购数：{agent_buy_total}
自身利润总占额：{rate_report_total}
下级经销利润总占额：{rate_report_agent_total}
""".format(**dataInfo)
    else:
        title = u"""您好！[ {account} ]
您的昨日报表 [ {date} ] 已经生成成功
报表发送时间：{now}

时间：{date}
用户数：{member_total}
活跃数：{login_per_day}
耗钻数：{play_room_per_day}
自身购数：{self_buy_total}
玩家购数：{player_buy_total}
自身利润总占额：{rate_report_total}
下级经销利润总占额：{rate_report_agent_total}
""".format(**dataInfo)

    url_msg = WX_TEMPLATE_URL
    body = {
        "touser": openid,
        "template_id": WX_TEMPLATE_DATA_PUSH_ID,
        "topcolor": "#FF0000",

        "data": {
            "first": {
                "value": title,
                "color": "#173177"
            },
            "keyword1": {
                "value": u"忽略",
                "color": "#053c69"
            },
            "keyword2": {
                "value": u"忽略",
                "color": "#053c69"
            },
            "remark": {
                "value": u"\n如数据有异常，请及时联系管理员",
                "color": "#d40f24"
            }
        }
    }

    res = requests.post(url=url_msg, params={
        'access_token': access_token
    }, data=json.dumps(body, ensure_ascii=False).encode('utf-8'))