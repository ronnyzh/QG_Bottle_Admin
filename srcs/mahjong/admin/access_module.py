#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Author: $Author$
Date: $Date$
Revision: $Revision$

Description:
    权限名及路径表配置
"""

from config.config import BACK_PRE
from common.utilt import getLang

class AccessObj(object):
    def __init__(self, tree, method, field, check=False):
        self.tree = tree
        self.method = method
        if method in ('GET', 'POST'):
            self.url = BACK_PRE +'/'+'/'.join(tree)
            self.accessTag = '%s:'%(method) + self.url
        else:
            self.url = BACK_PRE +'/'+str(tree)
            self.accessTag = ''
        self.field = field
        self.check = check

    def getTxt(self, lang):
        return getattr(lang, self.field)

MENU_MODULES = (
    AccessObj(("menu"), None, 'MENU_PRIMARY_TXT',True), \

    AccessObj(("sys"), None, 'MENU_SYS_TXT'), \
    AccessObj(("setting", "system"), 'GET', 'MENU_GAME_PAY_LIST_TXT'), \
    AccessObj(("setting", "hotUpDateSetting"), 'GET', 'MENU_HOT_UPDATE_LIST_TXT'), \

    AccessObj(("game"), None, 'MENU_GAME_TXT'), \
    AccessObj(("game", "module/list"), 'GET', 'MENU_GAME_MODULE_LIST_TXT'), \
    AccessObj(("game", "list"), 'GET', 'MENU_GAME_LIST_TXT'), \
    AccessObj(("game", "broadList?broad_belone=HALL"), 'GET', 'MENU_GAME_BROAD_LIST_TXT'), \
    AccessObj(("game", "openIP"), 'GET', 'OPEN_THE_IP'), \
    AccessObj(("game", "gold"), 'GET', 'MENU_GAME_CONFIGURATION'), \

    AccessObj(("notic"), None, 'MENU_NOTIC_TXT'), \
    AccessObj(("notic", "temp/list"), 'GET', 'MENU_NOTIC_TEMP_TXT'), \
    AccessObj(("notic", "list"), 'GET', 'MENU_NOTIC_LIST_TXT'), \
    AccessObj(("notic", "mail/list"), 'GET', 'MENU_NOTIC_MAIL_LIST_TXT'), \

    AccessObj(("goods"), None, 'MENU_GOODS_TXT'), \
    AccessObj(("goods", "list"), 'GET', 'MENU_GOODS_LIST_TXT'), \

    AccessObj(("agent"), None, 'MENU_AGENT_TXT'), \
    AccessObj(("agent", "list"), 'GET', 'MENU_AGENT_LIST_TXT'), \
    AccessObj(("agent", "clublist"), 'GET', 'MENU_AGENT_CLUBLIST_TXT'), \
    AccessObj(("agent", "active"), 'GET', 'MENU_AGENT_ACTIVE_TXT'), \
    AccessObj(("agent", "room/list"), 'GET', 'MENU_AGENT_ROOM_LIST_TXT'), \
    AccessObj(("agent", "child/room/list"), 'GET', 'MENU_AGENT_CHILD_ROOM_LIST_TXT'), \
    AccessObj(("agent", "binding"), 'GET', 'MENU_AGENT_BINDING_TXT'), \

    AccessObj(("member"), None, 'MENU_MEMBER_TXT'), \
    AccessObj(("agent", "member/curOnline"), 'GET', 'MENU_AGENT_MEMBER_CURONLINE_TXT'), \
    AccessObj(("member", "dayUseCard"), 'GET', 'MENU_AGENT_MEMBER_DAYUSE_TXT'), \
    AccessObj(("member", "search/hall"), 'GET', 'MENU_MEMBER_SEARCH_TXT'), \
    AccessObj(("member", "list"), 'GET', 'MENU_MEMBER_LIST_TXT'), \
    AccessObj(("member", "joinList"), 'GET', 'MENU_MEMBER_JOINLIST_TXT'), \
    AccessObj(("member", "gm/list"), 'GET', 'MENU_MEMBER_GM_SET_TXT'), \

    AccessObj(("order"), None, 'MENU_ORDER_TXT'), \
    AccessObj(("order", "all"), 'GET', 'MENU_ORDER_ALL'), \
    AccessObj(("order", "buy"), 'GET', 'MENU_ORDER_BUY_TXT'), \
    AccessObj(("order", "wechat/record"), 'GET', 'MENU_ORDER_WECHAT_TXT'), \
    AccessObj(("order", "wechat/sale/record"), 'GET', 'MENU_ORDER_WECHAT_SALE_CURRENCY_TXT'), \
    AccessObj(("order", "buy/record"), 'GET', 'MENU_ORDER_BUY_RECORD_TXT'), \
    AccessObj(("order", "sale/record"), 'GET', 'MENU_ORDER_SALE_RECORD_TXT'), \

    #数据统计
    AccessObj(("accounts"), None, 'MENU_ACCOUNTS_TXT',True), \
    AccessObj(("statistics", "graphs"), 'GET', 'MENU_STATISTICS_GRAPHS_TXT'), \
    AccessObj(("statistics", "reg"), 'GET', 'MENU_STATISTICS_REG_TXT'), \
    #AccessObj(("statistics", "login"), 'GET', 'MENU_STATISTICS_LOGIN_TXT'), \
    AccessObj(("statistics", "active"), 'GET', 'MENU_STATISTICS_ACTIVE_TXT'), \
    # AccessObj(("statistics", "takeCard"), 'GET', 'MENU_STATISTICS_CARD_TXT'), \
    # AccessObj(("statistics", "count"), 'GET', 'MENU_STATISTICS_COUNT_TXT'), \
    AccessObj(("statistics", "history"), 'GET', 'MENU_STATISTICS_ACTIVE_HISTORY_TXT'), \
    # AccessObj(("statistics", "new/history"), 'GET', 'MENU_STATISTICS_ACTIVE_HISTORY2_TXT'), \
    AccessObj(("statistics", "clubchange"), 'GET', 'MENU_STATISTICS_CLUB_CHANGE_TXT'), \
    AccessObj(("statistics", "roomcard"), 'GET', 'MENU_STATISTICS_ROOMCARD_TXT'), \
    AccessObj(("statistics", "club"), 'GET', 'MENU_STATISTICS_CLUB_TXT'), \
    #订单
    AccessObj(("accounts"), None, 'MENU_REPORT_TXT',True), \
    AccessObj(("statistics","saleReport"), 'GET', 'MENU_STATISTICS_SALEREPORT_TXT'), \
    AccessObj(("statistics", "buyReport"), 'GET', 'MENU_STATISTICS_BUYREPORT_TXT'), \
    AccessObj(("statistics", "allAgentSaleReport"), 'GET', 'MENU_STATISTICS_AGENT_SALEREPORT_TXT'), \
    AccessObj(("statistics", "allAgentBuyReport"), 'GET', 'MENU_STATISTICS_AGENT_BUYREPORT_TXT'), \
    AccessObj(("statistics", "rateReport"), 'GET', 'MENU_STATISTICS_RATEREPORT_TXT'), \
    AccessObj(("statistics", "rateReport2"), 'GET', 'MENU_STATISTICS_RATEREPORT2_TXT'), \
    #个人设置
    AccessObj(("person"), None, 'MENU_PERSON_TXT',True), \
    AccessObj(("self","modifyPasswd"), 'GET', 'MENU_SELF_MODIFYPASSWD_TXT'), \
    AccessObj(("self", "syslog"), 'GET', 'MENU_SELF_SYSLOG_TXT'), \
    AccessObj(("self", "loginLog"), 'GET', 'MENU_SELF_LOGINLOG_TXT'), \

    # 竞技场&金币场模块
    AccessObj(("party"), None, 'MENU_PARTY_MODEL_TXT', True), \
    AccessObj(("party"), None, 'MENU_PARTY_ONE'), \
    AccessObj(("party", "setting"), 'GET', 'PARTY_COMPETITION_SETTING'), \
    AccessObj(("party", "competition/journal"), 'GET', 'PARTY_COMPETITION_JOURNAL'), \
    AccessObj(("party", "competition/operate"), 'GET', 'PARTY_COMPETITION_OPERATE'), \
    AccessObj(("gold"), None, 'MENU_PARTY_TWO'), \
    AccessObj(("gold", "field"), 'GET', 'GOLD_USER_DATA'), \
    AccessObj(("gold", "operate"), 'GET', 'GOLD_OPERATE'), \
    AccessObj(("gold", "ai"), 'GET', 'GOLD_AI_DATA'), \
    AccessObj(("gold", "log"), 'GET', 'GOLD_LOG_DATA'), \
    AccessObj(("gold", "amount"), 'GET', 'GOLD_AMOUNT'), \
    AccessObj(("gold", "roomcost"), 'GET', 'GOLD_ROOMCOST'), \
    AccessObj(("gold", "transorder"), 'GET', 'GOLD_TRANS_ORDER'), \
    AccessObj(("gold", "game/day"), 'GET', 'GOLD_GAME_DAY_DATA'), \
    AccessObj(("gold", "field/ranking"), 'GET', "GOLD_FIELD_RANKING"), \
    AccessObj(("party"), None, 'MENU_PARTY_THREE'), \

    # 背包模块
    AccessObj(("bag"), None, 'BAG_MODEL_TXT', True), \
    # AccessObj(("bag","create/item"), 'GET', 'BAG_CREATE_ITEM'), \
    # AccessObj(("bag","list"), 'GET', 'BAG_LIST'), \
    AccessObj(("bag","send/mail"), 'GET', 'BAG_SEND_MAIL'), \
    # AccessObj(("bag","vcoin/day"), 'GET', 'BAG_VCOIN_DAY'), \

)

'''
捕鱼后台菜单
'''
FISH_MENU_MODULES = (
    AccessObj(("menu"), None, 'MENU_PRIMARY_TXT',True), \

    AccessObj(("sys"), None, 'MENU_SYS_TXT'), \
    AccessObj(("setting", "fish/system"), 'GET', 'MENU_FISH_SETTING_TXT'), \
    AccessObj(("setting", "hotUpDateSetting?sys=fish"), 'GET', 'MENU_HOT_UPDATE_LIST_TXT'), \
    #捕鱼房间管理
    AccessObj(("game"), None, 'MENU_GAME_TXT'), \
    AccessObj(("fish", "room/list"), 'GET', 'MENU_FISH_ROOM_LIST_TXT'), \
    #捕鱼信息公告管理
    AccessObj(("notic"), None, 'MENU_NOTIC_TXT'), \
    AccessObj(("game", "broadList?broad_belone=FISH"), 'GET', 'MENU_GAME_BROAD_LIST_TXT'), \
    AccessObj(("notic", "list/fish"), 'GET', 'MENU_NOTIC_LIST_TXT'), \
    #捕鱼商品管理
    AccessObj(("goods"), None, 'MENU_GOODS_TXT'), \
    AccessObj(("goods", "list?sys=fish"), 'GET', 'MENU_GOODS_LIST_TXT'), \
    AccessObj(("goods", "fish/reward/list"), 'GET', 'MENU_GOODS_REWARD_LIST_TXT'), \
    AccessObj(("goods", "reward/exchange/list"), 'GET', 'MENU_GOODS_EXCHANGE_LIST_TXT'), \
    #捕鱼会员管理
    AccessObj(("member"), None, 'MENU_MEMBER_TXT'), \
    AccessObj(("member", "search/fish"), 'GET', 'MENU_MEMBER_SEARCH_COIN_TXT'), \
    AccessObj(("fish", "member/list"), 'GET', 'MENU_MEMBER_LIST_TXT'), \
    AccessObj(("fish", "online/list"), 'GET', 'MENU_FISH_ONLINE_LIST_TXT'), \
    AccessObj(("order", "wechat/record/FISH"), 'GET', 'MENU_FISH_RECHARGE_LIST_TXT'), \


    AccessObj(("member"), None, 'MENU_FISH_DATA_TXT',True), \
    AccessObj(("fish", "bet/list"), 'GET', 'MENU_FISH_BET_LIST_TXT'), \
    AccessObj(("fish", "data/query"), 'GET', 'MENU_HOT_DATA_QUERY_TXT'), \
    #AccessObj(("fish", "data/modify"), 'GET', 'MENU_FISH_DATA_MODIFY_TXT'), \

)

# 系统管理员权限
ACCESS_SADMIN_MODULES = (
    AccessObj(("menu"), None, 'MENU_PRIMARY_TXT',True), \

    AccessObj(("sys"), None, 'MENU_SYS_TXT'), \
    AccessObj(("setting", "system"), 'GET', 'MENU_GAME_PAY_LIST_TXT'), \
    AccessObj(("setting", "hotUpDateSetting"), 'GET', 'MENU_HOT_UPDATE_LIST_TXT'), \

    #捕鱼数据
    AccessObj(("fish", "data/reward/modify"), 'GET', 'MENU_FISH_DATA_MODIFY_TXT'), \
    AccessObj(("fish", "bet/list"), 'GET', 'MENU_FISH_BET_LIST_TXT'), \
    AccessObj(("fish", "data/modify"), 'GET', 'MENU_FISH_DATA_MODIFY_TXT'), \
    AccessObj(("fish", "online/list"), 'GET', 'MENU_FISH_ONLINE_LIST_TXT'), \
    AccessObj(("fish", "recharge/list"), 'GET', 'MENU_FISH_RECHARGE_LIST_TXT'), \
    AccessObj(("fish", "room/list"), 'GET', 'MENU_FISH_ROOM_LIST_TXT'), \
    AccessObj(("goods", "fish/reward/list"), 'GET', 'MENU_GOODS_REWARD_LIST_TXT'), \
    AccessObj(("goods", "reward/exchange/list"), 'GET', 'MENU_GOODS_EXCHANGE_LIST_TXT'), \
    AccessObj(("goods", "list?sys=fish"), 'GET', 'MENU_GOODS_LIST_TXT'), \
    AccessObj(("fish", "data/query"), 'GET', 'MENU_HOT_DATA_QUERY_TXT'), \
    AccessObj(("setting", "fish/system"), 'GET', 'MENU_GAME_PAY_LIST_TXT'), \
    AccessObj(("fish", "member/list"), 'GET', 'MENU_MEMBER_LIST_TXT'), \
    AccessObj(("game", "broadList?broad_belone=HALL"), 'GET', 'MENU_GAME_BROAD_LIST_TXT'), \
    AccessObj(("game", "broadList?broad_belone=FISH"), 'GET', 'MENU_GAME_BROAD_LIST_TXT'), \
    AccessObj(("notic", "list/fish"), 'GET', 'MENU_NOTIC_LIST_TXT'), \
    AccessObj(("order", "wechat/record/FISH"), 'GET', 'MENU_FISH_RECHARGE_LIST_TXT'), \
    AccessObj(("setting", "hotUpDateSetting?sys=fish"), 'GET', 'MENU_HOT_UPDATE_LIST_TXT'), \
    AccessObj(("member", "search/fish"), 'GET', 'MENU_MEMBER_SEARCH_COIN_TXT'), \


    AccessObj(("game"), None, 'MENU_GAME_TXT'), \
    AccessObj(("game", "list"), 'GET', 'MENU_GAME_LIST_TXT'), \
    AccessObj(("game", "notice"), 'GET', 'MENU_GAME_NOTICE_TXT'), \
    #AccessObj(("game", "broadcast"), 'GET', 'MENU_GAME_BROADCAST_TXT'), \
    AccessObj(("game", "broadList"), 'GET', 'MENU_GAME_BROAD_LIST_TXT'), \
    AccessObj(("game", "openIP"), 'GET', 'OPEN_THE_IP'), \
    AccessObj(("game", "openIP"), 'POST', 'OPEN_THE_IP'), \
    AccessObj(("game", "gold"), 'GET', 'MENU_GAME_CONFIGURATION'), \

    AccessObj(("notic"), None, 'MENU_NOTIC_TXT'), \
    #AccessObj(("notic", "temp/list"), 'GET', 'MENU_NOTIC_TEMP_TXT'), \
    AccessObj(("notic", "list"), 'GET', 'MENU_NOTIC_LIST_TXT'), \
    #AccessObj(("notic", "mail/list"), 'GET', 'MENU_NOTIC_MAIL_LIST_TXT'), \

    AccessObj(("agent"), None, 'MENU_AGENT_TXT'), \
    AccessObj(("agent", "list"), 'GET', '代理列表'), \
    AccessObj(("agent", "clublist"), 'GET', 'MENU_AGENT_CLUBLIST_TXT'), \
    AccessObj(("agent", "active"), 'GET', 'MENU_AGENT_ACTIVE_TXT'), \
    AccessObj(("agent", "room/list"), 'GET', 'MENU_AGENT_ROOM_LIST_TXT'), \
    #AccessObj(("agent", "child/room/list"), 'GET', 'MENU_AGENT_CHILD_ROOM_LIST_TXT'), \
    AccessObj(("agent", "room/kick"), 'GET', 'LIST_ROOM_DISSOLVE_TXT'), \

    AccessObj(("goods"), None, 'MENU_GOODS_TXT'), \
    AccessObj(("goods", "list"), 'GET', 'MENU_GOODS_LIST_TXT'), \

    AccessObj(("member"), None, 'MENU_MEMBER_TXT'), \
    AccessObj(("agent", "member/curOnline"), 'GET', 'MENU_AGENT_MEMBER_CURONLINE_TXT'), \
    AccessObj(("member", "dayUseCard"), 'GET', 'MENU_AGENT_MEMBER_DAYUSE_TXT'), \
    AccessObj(("member", "list"), 'GET', 'MENU_MEMBER_LIST_TXT'), \
    AccessObj(("member", "gm/list"), 'GET', 'MENU_MEMBER_GM_SET_TXT'), \
    #AccessObj(("member", "joinList"), 'GET', 'MENU_MEMBER_JOINLIST_TXT'), \

    AccessObj(("order"), None, 'MENU_ORDER_TXT'), \
    #AccessObj(("order", "buy"), 'GET', 'MENU_ORDER_BUY_TXT'), \
    #AccessObj(("order", "buy/record"), 'GET', 'MENU_ORDER_BUY_RECORD_TXT'), \
    AccessObj(("order", "all"), 'GET', 'MENU_ORDER_ALL'), \
    AccessObj(("order", "wechat/record"), 'GET', 'MENU_ORDER_WECHAT_TXT'), \
    AccessObj(("order", "wechat/sale/record"), 'GET', 'MENU_ORDER_WECHAT_SALE_CURRENCY_TXT'), \
    AccessObj(("order", "sale/record"), 'GET', 'MENU_ORDER_SALE_RECORD_TXT'), \

    AccessObj(("accounts"), None, 'MENU_ACCOUNTS_TXT',True), \
    AccessObj(("statistics","saleReport"), 'GET', 'MENU_STATISTICS_SALEREPORT_TXT'), \
    #AccessObj(("statistics", "buyReport"), 'GET', 'MENU_STATISTICS_BUYREPORT_TXT'), \
    AccessObj(("statistics", "allAgentSaleReport"), 'GET', 'MENU_STATISTICS_AGENT_SALEREPORT_TXT'), \
    AccessObj(("statistics", "allAgentBuyReport"), 'GET', 'MENU_STATISTICS_AGENT_BUYREPORT_TXT'), \
    AccessObj(("statistics", "rateReport"), 'GET', 'MENU_STATISTICS_RATEREPORT_TXT'), \
    AccessObj(("statistics", "rateReport2"), 'GET', 'MENU_STATISTICS_RATEREPORT2_TXT'), \
 \
    AccessObj(("statistics", "graphs"), 'GET', 'MENU_STATISTICS_GRAPHS_TXT'), \
    AccessObj(("statistics", "reg"), 'GET', 'MENU_STATISTICS_REG_TXT'), \
    #AccessObj(("statistics", "login"), 'GET', 'MENU_STATISTICS_LOGIN_TXT'), \
    AccessObj(("statistics", "active"), 'GET', 'MENU_STATISTICS_ACTIVE_TXT'), \
    #AccessObj(("statistics", "takeCard"), 'GET', 'MENU_STATISTICS_CARD_TXT'), \
    #AccessObj(("statistics", "count"), 'GET', 'MENU_STATISTICS_COUNT_TXT'), \
    AccessObj(("statistics", "history"), 'GET', 'MENU_STATISTICS_ACTIVE_HISTORY_TXT'), \
    # AccessObj(("statistics", "new/history"), 'GET', 'MENU_STATISTICS_ACTIVE_HISTORY2_TXT'), \
    AccessObj(("statistics", "clubchange"), 'GET', 'MENU_STATISTICS_CLUB_CHANGE_TXT'), \
    AccessObj(("statistics", "roomcard"), 'GET', 'MENU_STATISTICS_ROOMCARD_TXT'), \
    AccessObj(("statistics", "club"), 'GET', 'MENU_STATISTICS_CLUB_TXT'), \

    AccessObj(("person"), None, 'MENU_PERSON_TXT',True), \
    AccessObj(("self","modifyPasswd"),'GET', 'MENU_SELF_MODIFYPASSWD_TXT'), \
    AccessObj(("self", "syslog"), 'GET', 'MENU_SELF_SYSLOG_TXT'), \
    AccessObj(("self", "loginLog"), 'GET', 'MENU_SELF_LOGINLOG_TXT'), \

    # 竞技场&金币场模块
    AccessObj(("party"), None, 'MENU_PARTY_MODEL_TXT', True), \
    AccessObj(("party"), None, 'MENU_PARTY_ONE'), \
    AccessObj(("party", "setting"), 'GET', 'PARTY_COMPETITION_SETTING'), \
    AccessObj(("party", "competition/journal"), 'GET', 'PARTY_COMPETITION_JOURNAL'), \
    AccessObj(("party", "competition/operate"), 'GET', 'PARTY_COMPETITION_OPERATE'), \
    AccessObj(("gold"), None, 'MENU_PARTY_TWO'), \
    AccessObj(("gold", "field"), 'GET', 'GOLD_USER_DATA'), \
    AccessObj(("gold", "operate"), 'GET', 'GOLD_OPERATE'), \
    AccessObj(("gold", "ai"), 'GET', 'GOLD_AI_DATA'), \
    AccessObj(("gold", "log"), 'GET', 'GOLD_LOG_DATA'), \
    AccessObj(("gold", "amount"), 'GET', 'GOLD_AMOUNT'), \
    AccessObj(("gold", "roomcost"), 'GET', 'GOLD_ROOMCOST'), \
    AccessObj(("gold", "transorder"), 'GET', 'GOLD_TRANS_ORDER'), \
    AccessObj(("gold", "game/day"), 'GET', 'GOLD_GAME_DAY_DATA'), \
    AccessObj(("gold", "field/ranking"), 'GET', "GOLD_FIELD_RANKING"), \
    AccessObj(("gold", "field/ranking"), 'GET', ''), \
    AccessObj(("party"), None, 'MENU_PARTY_THREE'), \


    # 背包模块
    AccessObj(("bag"), None, 'BAG_MODEL_TXT', True), \
    # AccessObj(("bag","create/item"), 'GET', 'BAG_CREATE_ITEM'), \
    # AccessObj(("bag","list"), 'GET', 'BAG_LIST'), \
    # AccessObj(("bag","item/modify"), 'GET', 'BAG_LIST'), \
    # AccessObj(("bag","item/modify"), 'POST', 'BAG_LIST'), \
    AccessObj(("bag","send/mail"), 'POST', 'BAG_LIST'), \
    # AccessObj(("bag","vcoin/day"), 'GET', 'BAG_VCOIN_DAY'), \
    # AccessObj(("bag","vcoin/sum"), 'GET', 'BAG_VCOIN_SUM'), \

)

# 总公司权限
ACCESS_COMPANY_MODULES = (
    AccessObj(("menu"), None, 'MENU_PRIMARY_TXT',True), \

    AccessObj(("game"), None, 'MENU_GAME_TXT'), \
    # AccessObj(("game", "list"), 'GET', 'MENU_GAME_LIST_TXT'), \
    # AccessObj(("game", "notice"), 'GET', 'MENU_GAME_NOTICE_TXT'), \
    #AccessObj(("game", "broadcast"), 'GET', 'MENU_GAME_BROADCAST_TXT'), \
    AccessObj(("game", "broadList"), 'GET', 'MENU_GAME_BROAD_LIST_TXT'), \
    AccessObj(("game", "broadList?broad_belone=HALL"), 'GET', 'MENU_GAME_BROAD_LIST_TXT'), \

    AccessObj(("agent"), None, 'MENU_AGENT_TXT'), \
    AccessObj(("agent", "list"), 'GET', 'MENU_AGENT_LIST_TXT'), \
    AccessObj(("agent", "clublist"), 'GET', 'MENU_AGENT_CLUBLIST_TXT'), \
    AccessObj(("agent", "active"), 'GET', 'MENU_AGENT_ACTIVE_TXT'), \
    #AccessObj(("agent", "room/list"), 'GET', 'MENU_AGENT_ROOM_LIST_TXT'), \
    AccessObj(("agent", "child/room/list"), 'GET', 'MENU_AGENT_CHILD_ROOM_LIST_TXT'), \
    AccessObj(("agent", "room/kick"), 'GET', 'LIST_ROOM_DISSOLVE_TXT'), \
    AccessObj(("agent", "binding"), 'GET', 'MENU_AGENT_BINDING_TXT'), \

    AccessObj(("notic"), None, 'MENU_NOTIC_TXT'), \
    #AccessObj(("notic", "temp/list"), 'GET', 'MENU_NOTIC_TEMP_TXT'), \
    AccessObj(("notic", "list"), 'GET', 'MENU_NOTIC_LIST_TXT'), \
    #AccessObj(("notic", "mail/list"), 'GET', 'MENU_NOTIC_MAIL_LIST_TXT'), \

    AccessObj(("member"), None, 'MENU_MEMBER_TXT'), \
    AccessObj(("agent", "member/curOnline"), 'GET', 'MENU_AGENT_MEMBER_CURONLINE_TXT'), \
    AccessObj(("member", "list"), 'GET', 'MENU_MEMBER_LIST_TXT'), \
    AccessObj(("member", "search/hall"), 'GET', 'MENU_MEMBER_SEARCH_TXT'), \

    AccessObj(("order"), None, 'MENU_ORDER_TXT'), \
    AccessObj(("order", "buy"), 'GET', 'MENU_ORDER_BUY_TXT'), \
    AccessObj(("order", "buy/record"), 'GET', 'MENU_ORDER_BUY_RECORD_TXT'), \
    AccessObj(("order", "sale/record"), 'GET', 'MENU_ORDER_SALE_RECORD_TXT'), \

    AccessObj(("accounts"), None, 'MENU_ACCOUNTS_TXT',True), \
    AccessObj(("statistics","saleReport"), 'GET', 'MENU_STATISTICS_SALEREPORT_TXT'), \
    AccessObj(("statistics", "buyReport"), 'GET', 'MENU_STATISTICS_BUYREPORT_TXT'), \
    AccessObj(("statistics", "allAgentSaleReport"), 'GET', 'MENU_STATISTICS_AGENT_SALEREPORT_TXT'), \
    AccessObj(("statistics", "allAgentBuyReport"), 'GET', 'MENU_STATISTICS_AGENT_BUYREPORT_TXT'), \
    AccessObj(("statistics", "rateReport"), 'GET', 'MENU_STATISTICS_RATEREPORT_TXT'), \
    AccessObj(("statistics", "rateReport2"), 'GET', 'MENU_STATISTICS_RATEREPORT2_TXT'), \
    AccessObj(("statistics", "login"), 'GET', 'MENU_STATISTICS_LOGIN_TXT'), \
    AccessObj(("statistics", "active"), 'GET', 'MENU_STATISTICS_ACTIVE_TXT'), \
    AccessObj(("statistics", "history"), 'GET', 'MENU_STATISTICS_ACTIVE_HISTORY_TXT'), \
    # AccessObj(("statistics", "new/history"), 'GET', 'MENU_STATISTICS_ACTIVE_HISTORY2_TXT'), \
    #AccessObj(("statistics", "takeCard"), 'GET', 'MENU_STATISTICS_CARD_TXT'), \
    #AccessObj(("statistics", "count"), 'GET', 'MENU_STATISTICS_COUNT_TXT'), \

    AccessObj(("person"), None, 'MENU_PERSON_TXT',True), \
    AccessObj(("self","modifyPasswd"),'GET', 'MENU_SELF_MODIFYPASSWD_TXT'), \
    AccessObj(("self", "syslog"), 'GET', 'MENU_SELF_SYSLOG_TXT'), \
    AccessObj(("self", "loginLog"), 'GET', 'MENU_SELF_LOGINLOG_TXT'), \

    # 背包模块
    AccessObj(("bag"), None, 'BAG_MODEL_TXT', True), \
    # AccessObj(("bag", "item/modify"), 'GET', 'BAG_LIST'), \
    # AccessObj(("bag", "item/changeI"), 'GET', 'BAG_LIST'), \
    # AccessObj(("bag", "item/isgoods"), 'GET', 'BAG_LIST'), \
    AccessObj(("bag", "send/mail"), 'GET', 'BAG_SEND_MAIL'), \
    AccessObj(("bag", "send/mail"), 'POST', 'BAG_SEND_MAIL'), \
    # AccessObj(("bag", "vcoin/sum"), 'GET', 'BAG_VCOIN_SUM'), \

    )


# 一级代理权限
ACCESS_AG_ONE_CLASS_MODULES = (
    AccessObj(("menu"), None, 'MENU_PRIMARY_TXT',True), \

    #AccessObj(("game"), None, 'MENU_GAME_TXT'), \
    #AccessObj(("game", "broadcast"), 'GET', 'MENU_GAME_BROADCAST_TXT'), \

    AccessObj(("agent"), None, 'MENU_AGENT_TXT'), \
    AccessObj(("agent", "list"), 'GET', 'MENU_AGENT_LIST_TXT'), \
    AccessObj(("agent", "clublist"), 'GET', 'MENU_AGENT_CLUBLIST_TXT'), \
    AccessObj(("agent", "active"), 'GET', 'MENU_AGENT_ACTIVE_TXT'), \
    #AccessObj(("agent", "room/list"), 'GET', 'MENU_AGENT_ROOM_LIST_TXT'), \
    AccessObj(("agent", "child/room/list"), 'GET', 'MENU_AGENT_CHILD_ROOM_LIST_TXT'), \
    AccessObj(("agent", "room/kick"), 'GET', 'LIST_ROOM_DISSOLVE_TXT'), \
    AccessObj(("agent", "binding"), 'GET', 'MENU_AGENT_BINDING_TXT'), \

    AccessObj(("member"), None, 'MENU_MEMBER_TXT'), \
    AccessObj(("member", "search/hall"), 'GET', 'MENU_MEMBER_SEARCH_TXT'), \
    AccessObj(("agent", "member/curOnline"), 'GET', 'MENU_AGENT_MEMBER_CURONLINE_TXT'), \
    AccessObj(("member", "list"), 'GET', 'MENU_MEMBER_LIST_TXT'), \
    AccessObj(("member", "joinList"), 'GET', 'MENU_MEMBER_JOINLIST_TXT'), \

    AccessObj(("order"), None, 'MENU_ORDER_TXT'), \
    AccessObj(("order", "buy"), 'GET', 'MENU_ORDER_BUY_TXT'), \
    AccessObj(("order", "buy/record"), 'GET', 'MENU_ORDER_BUY_RECORD_TXT'), \
    AccessObj(("order", "sale/record"), 'GET', 'MENU_ORDER_SALE_RECORD_TXT'), \

    AccessObj(("accounts"), None, 'MENU_ACCOUNTS_TXT',True), \
    AccessObj(("statistics","saleReport"), 'GET', 'MENU_STATISTICS_SALEREPORT_TXT'), \
    AccessObj(("statistics", "buyReport"), 'GET', 'MENU_STATISTICS_BUYREPORT_TXT'), \
    AccessObj(("statistics", "allAgentSaleReport"), 'GET', 'MENU_STATISTICS_AGENT_SALEREPORT_TXT'), \
    AccessObj(("statistics", "allAgentBuyReport"), 'GET', 'MENU_STATISTICS_AGENT_BUYREPORT_TXT'), \
    AccessObj(("statistics", "rateReport"), 'GET', 'MENU_STATISTICS_RATEREPORT_TXT'), \
    #AccessObj(("statistics", "takeCard"), 'GET', 'MENU_STATISTICS_CARD_TXT'), \
    AccessObj(("statistics", "login"), 'GET', 'MENU_STATISTICS_LOGIN_TXT'), \
    AccessObj(("statistics", "active"), 'GET', 'MENU_STATISTICS_ACTIVE_TXT'), \
    AccessObj(("statistics", "history"), 'GET', 'MENU_STATISTICS_ACTIVE_HISTORY_TXT'), \
    #AccessObj(("statistics", "count"), 'GET', 'MENU_STATISTICS_COUNT_TXT'), \

    AccessObj(("person"), None, 'MENU_PERSON_TXT',True), \
    AccessObj(("self","modifyPasswd"),'GET', 'MENU_SELF_MODIFYPASSWD_TXT'), \
    AccessObj(("self", "syslog"), 'GET', 'MENU_SELF_SYSLOG_TXT'), \
    AccessObj(("self", "loginLog"), 'GET', 'MENU_SELF_LOGINLOG_TXT'), \
)


# 二级代理权限
ACCESS_AG_TWO_CLASS_MODULES = (
    AccessObj(("menu"), None, 'MENU_PRIMARY_TXT',True), \

    #AccessObj(("game"), None, 'MENU_GAME_TXT'), \
    #AccessObj(("game", "broadcast"), 'GET', 'MENU_GAME_BROADCAST_TXT'), \

    AccessObj(("agent"), None, 'MENU_AGENT_TXT'), \
    AccessObj(("agent", "clublist"), 'GET', 'MENU_AGENT_CLUBLIST_TXT'), \
    #AccessObj(("agent", "room/list"), 'GET', 'MENU_AGENT_ROOM_LIST_TXT'), \
    AccessObj(("agent", "child/room/list"), 'GET', 'MENU_AGENT_CHILD_ROOM_LIST_TXT'), \
    AccessObj(("agent", "room/kick"), 'GET', 'LIST_ROOM_DISSOLVE_TXT'), \
    AccessObj(("agent", "binding"), 'GET', 'MENU_AGENT_BINDING_TXT'),\

    AccessObj(("member"), None, 'MENU_MEMBER_TXT'), \
        AccessObj(("member", "search/hall"), 'GET', 'MENU_MEMBER_SEARCH_TXT'), \
    AccessObj(("agent", "member/curOnline"), 'GET', 'MENU_AGENT_MEMBER_CURONLINE_TXT'), \
    AccessObj(("member", "list"), 'GET', 'MENU_MEMBER_LIST_TXT'), \
    AccessObj(("member", "joinList"), 'GET', 'MENU_MEMBER_JOINLIST_TXT'), \

    AccessObj(("order"), None, 'MENU_ORDER_TXT'), \
    AccessObj(("order", "buy"), 'GET', 'MENU_ORDER_BUY_TXT'), \
    AccessObj(("order", "buy/record"), 'GET', 'MENU_ORDER_BUY_RECORD_TXT'), \

    AccessObj(("accounts"), None, 'MENU_ACCOUNTS_TXT',True), \
    AccessObj(("statistics", "buyReport"), 'GET', 'MENU_STATISTICS_BUYREPORT_TXT'), \
    AccessObj(("statistics", "takeCard"), 'GET', 'MENU_STATISTICS_CARD_TXT'), \
    AccessObj(("statistics", "login"), 'GET', 'MENU_STATISTICS_LOGIN_TXT'), \
    AccessObj(("statistics", "count"), 'GET', 'MENU_STATISTICS_COUNT_TXT'), \
    AccessObj(("statistics", "rateReport"), 'GET', 'MENU_STATISTICS_RATEREPORT_TXT'), \
    AccessObj(("statistics", "active"), 'GET', 'MENU_STATISTICS_ACTIVE_TXT'), \
    AccessObj(("statistics", "history"), 'GET', 'MENU_STATISTICS_ACTIVE_HISTORY_TXT'), \

    AccessObj(("person"), None, 'MENU_PERSON_TXT',True), \
    AccessObj(("self","modifyPasswd"),'GET', 'MENU_SELF_MODIFYPASSWD_TXT'), \
    AccessObj(("self", "syslog"), 'GET', 'MENU_SELF_SYSLOG_TXT'), \
    AccessObj(("self", "loginLog"), 'GET', 'MENU_SELF_LOGINLOG_TXT'), \
)

# 系统管理员权限
ACCESS_SADMIN_LIST = (

    AccessObj(("fish", "list"), 'GET', 'FISH_ROOM_LIST_TXT'), \
    AccessObj(("fish", "room/create"), 'GET', 'FISH_ROOM_CREATE_TXT'), \

    AccessObj(("agent", "list"), 'GET', 'MENU_AGENT_LIST_TXT'), \
    AccessObj(("agent", "clublist"), 'GET', 'MENU_AGENT_CLUBLIST_TXT'), \
    AccessObj(("agent", "create"), 'GET', 'LIST_AGENT_CREATE_TXT'), \
    AccessObj(("agent", "modify"), 'GET', 'LIST_AGENT_MODIFY_TXT'), \
    AccessObj(("agent", "info"), 'GET', 'LIST_AGENT_INFO_TXT'), \
    AccessObj(("agent", "club"), 'GET', 'LIST_AGENT_CLUB_TXT'), \
    AccessObj(("agent", "modifyPasswd"), 'GET', 'LIST_AGENT_MODIFY_PASSWD_TXT'), \
    AccessObj(("agent", "freeze"), 'GET', 'LIST_AGENT_FREEZE_TXT'), \
    AccessObj(("agent", "trail"), 'GET', 'LIST_AGENT_TRAIL_TXT'), \
    AccessObj(("agent", "recharge"), 'GET', 'LIST_AGENT_RECHARGE_TXT'), \
    AccessObj(("agent", "auto_check"), 'GET', 'LIST_AGENT_CHECK_TXT'), \
    AccessObj(("agent", "create_auth"), 'GET', 'LIST_AGENT_AUTH_TXT'), \
    AccessObj(("agent", "open_auth"), 'GET', 'LIST_AGENT_OPEN_AUTH_TXT'), \

    AccessObj(("member", "list"), 'GET', 'MENU_MEMBER_LIST_TXT'), \
    AccessObj(("member", "kick"), 'GET', 'LIST_MEMBER_KICK_TXT'), \
    AccessObj(("member", "removeCard"), 'GET', 'LIST_MEMBER_REMOVECARD_TXT'), \
    AccessObj(("member", "modify"), 'GET', 'LIST_MEMBER_MODIFY_TXT'), \
    AccessObj(("member", "freeze"), 'GET', 'LIST_MEMBER_FREEZE_TXT'), \
    AccessObj(("member", "addCard"), 'GET', 'LIST_MEMBER_CHARGE_TXT'), \
    #AccessObj(("member", "open_auth"), 'POST', 'LIST_MEMBER_OPEN_TXT'), \

    AccessObj(("notice", "list"), 'GET', 'MENU_GAME_NOTICE_LIST_TXT'), \
    AccessObj(("notice", "modify"), 'GET', 'LIST_GAME_NOTICE_MODIFY'), \
    AccessObj(("notice", "del"), 'GET', 'LIST_GAME_NOTICE_DEL'),\
    AccessObj(("notice", "push"), 'GET', 'LIST_GAME_NOTICE_PUSH'), \
)
# 总公司权限
ACCESS_COMPANY_LIST = (
    AccessObj(("agent", "list"), 'GET', 'MENU_AGENT_LIST_TXT'), \
    AccessObj(("agent", "create"), 'GET', 'LIST_AGENT_CREATE_TXT'), \
    AccessObj(("agent", "modify"), 'GET', 'LIST_AGENT_MODIFY_TXT'), \
    AccessObj(("agent", "info"), 'GET', 'LIST_AGENT_INFO_TXT'), \
    AccessObj(("agent", "club"), 'GET', 'LIST_AGENT_CLUB_TXT'), \
    AccessObj(("agent", "modifyPasswd"), 'GET', 'LIST_AGENT_MODIFY_PASSWD_TXT'), \
    AccessObj(("agent", "freeze"), 'GET', 'LIST_AGENT_FREEZE_TXT'), \
    AccessObj(("agent", "open_auth"), 'GET', 'LIST_AGENT_OPEN_AUTH_TXT'), \

    AccessObj(("member", "list"), 'GET', 'MENU_MEMBER_LIST_TXT'), \
    AccessObj(("member", "kick"), 'GET', 'LIST_MEMBER_KICK_TXT'), \
    AccessObj(("member", "removeCard"), 'GET', 'LIST_MEMBER_REMOVECARD_TXT'), \
    AccessObj(("member", "modify"), 'GET', 'LIST_MEMBER_MODIFY_TXT'), \
    AccessObj(("member", "freeze"), 'GET', 'LIST_MEMBER_FREEZE_TXT'), \
    #AccessObj(("member", "open_auth"), 'POST', 'LIST_MEMBER_OPEN_TXT'), \

    AccessObj(("notice", "list"), 'GET', 'MENU_GAME_NOTICE_LIST_TXT'), \
    AccessObj(("notice", "modify"), 'GET', 'LIST_GAME_NOTICE_MODIFY'), \
    AccessObj(("notice", "del"), 'GET', 'LIST_GAME_NOTICE_DEL'),\
    AccessObj(("notice", "push"), 'GET', 'LIST_GAME_NOTICE_PUSH'), \
    )

# 一级代理权限
ACCESS_AG_ONE_CLASS_LIST = (
    AccessObj(("agent", "list"), 'GET', 'MENU_AGENT_LIST_TXT'), \
    AccessObj(("agent", "create"), 'GET', 'LIST_AGENT_CREATE_TXT'), \
    AccessObj(("agent", "modify"), 'GET', 'LIST_AGENT_MODIFY_TXT'), \
    AccessObj(("agent", "info"), 'GET', 'LIST_AGENT_INFO_TXT'), \
    AccessObj(("agent", "club"), 'GET', 'LIST_AGENT_CLUB_TXT'), \
    AccessObj(("agent", "modifyPasswd"), 'GET', 'LIST_AGENT_MODIFY_PASSWD_TXT'), \
    #AccessObj(("agent", "freeze"), 'GET', 'LIST_AGENT_FREEZE_TXT'), \

    AccessObj(("member", "list"), 'GET', 'MENU_MEMBER_LIST_TXT'), \
    AccessObj(("member", "kick"), 'GET', 'LIST_MEMBER_KICK_TXT'), \
    #AccessObj(("member", "removeCard"), 'GET', 'LIST_MEMBER_REMOVECARD_TXT'), \
    AccessObj(("member", "modify"), 'GET', 'LIST_MEMBER_MODIFY_TXT'), \
    AccessObj(("member", "open_auth"), 'POST', 'LIST_MEMBER_OPEN_TXT'), \
   # AccessObj(("member", "freeze"), 'GET', 'LIST_MEMBER_FREEZE_TXT'), \

    #AccessObj(("agent", "room/list"), 'GET', 'MENU_AGENT_ROOM_LIST_TXT'), \
    AccessObj(("agent", "child/room/list"), 'GET', 'MENU_AGENT_CHILD_ROOM_LIST_TXT'), \
    AccessObj(("agent", "room/kick"), 'GET', 'LIST_ROOM_DISSOLVE_TXT'), \
)

# 二级代理权限
ACCESS_AG_TWO_CLASS_LIST = (
    AccessObj(("agent", "list"), 'GET', 'MENU_AGENT_LIST_TXT'), \
    AccessObj(("agent", "create"), 'GET', 'LIST_AGENT_CREATE_TXT'), \
    AccessObj(("agent", "modify"), 'GET', 'LIST_AGENT_MODIFY_TXT'), \
    AccessObj(("agent", "info"), 'GET', 'LIST_AGENT_INFO_TXT'), \
    AccessObj(("agent", "club"), 'GET', 'LIST_AGENT_CLUB_TXT'), \
    AccessObj(("agent", "modifyPasswd"), 'GET', 'LIST_AGENT_MODIFY_PASSWD_TXT'), \
    AccessObj(("agent", "freeze"), 'GET', 'LIST_AGENT_FREEZE_TXT'), \

    AccessObj(("member", "list"), 'GET', 'MENU_MEMBER_LIST_TXT'), \
    AccessObj(("member", "kick"), 'GET', 'LIST_MEMBER_KICK_TXT'), \
    #AccessObj(("member", "removeCard"), 'GET', 'LIST_MEMBER_REMOVECARD_TXT'), \
    AccessObj(("member", "modify"), 'GET', 'LIST_MEMBER_MODIFY_TXT'), \
    AccessObj(("member", "open_auth"), 'POST', 'LIST_MEMBER_OPEN_TXT'), \
    #AccessObj(("member", "freeze"), 'GET', 'LIST_MEMBER_FREEZE_TXT'), \

    #AccessObj(("agent", "room/list"), 'GET', 'MENU_AGENT_ROOM_LIST_TXT'), \
    AccessObj(("agent", "child/room/list"), 'GET', 'MENU_AGENT_CHILD_ROOM_LIST_TXT'), \
    AccessObj(("agent", "room/kick"), 'GET', 'LIST_ROOM_DISSOLVE_TXT'), \

)

ACCESS_AGENT_LIST = (
    AccessObj(("agent", "club"), 'GET', 'LIST_AGENT_CLUB_TXT'), \
    AccessObj(("agent", "create"), 'GET', 'LIST_AGENT_CREATE_TXT'), \
    AccessObj(("agent", "modify"), 'GET', 'LIST_AGENT_MODIFY_TXT'), \
    AccessObj(("agent", "info"), 'GET', 'LIST_AGENT_INFO_TXT'), \
    AccessObj(("agent", "freeze"), 'GET', 'LIST_AGENT_FREEZE_TXT'), \
    AccessObj(("agent", "trail"), 'GET', 'LIST_AGENT_TRAIL_TXT'), \
    AccessObj(("agent", "recharge"), 'GET', 'LIST_AGENT_RECHARGE_TXT'), \
    AccessObj(("agent", "auto_check"), 'GET', 'LIST_AGENT_CHECK_TXT'), \
    AccessObj(("agent", "create_auth"), 'GET', 'LIST_AGENT_AUTH_TXT'), \
    AccessObj(("agent", "open_auth"), 'GET', 'LIST_AGENT_OPEN_AUTH_TXT'), \
    AccessObj(("agent", "modifyPasswd"), 'GET', 'LIST_AGENT_MODIFY_PASSWD_TXT'), \
    )

ACCESS_MEMBER_LIST = (
    AccessObj(("member", "kick"), 'GET', 'LIST_MEMBER_KICK_TXT'), \
    AccessObj(("member", "removeCard"), 'GET', 'LIST_MEMBER_REMOVECARD_TXT'), \
    AccessObj(("member", "modify"), 'GET', 'LIST_MEMBER_MODIFY_TXT'), \
    AccessObj(("member", "freeze"), 'GET', 'LIST_MEMBER_FREEZE_TXT'), \
    AccessObj(("member", "addCard"), 'GET', 'LIST_MEMBER_CHARGE_TXT'), \
    AccessObj(("member", "open_auth"), 'POST', 'LIST_MEMBER_OPEN_TXT'), \
)

ACCESS_GAME_NOTICE_LIST = (
    AccessObj(("notice", "modify"), 'GET', 'LIST_GAME_NOTICE_MODIFY'), \
    #AccessObj(("notice", "del"), 'GET', 'LIST_GAME_NOTICE_DEL'),\
    AccessObj(("notice", "push"), 'GET', 'LIST_GAME_NOTICE_PUSH'), \

)

ACCESS_AGENT_ROOM_LIST = (
        AccessObj(("agent", "room/kick"), 'GET', 'LIST_ROOM_DISSOLVE_TXT'), \
)

ACCESS_AGENT_CHILD_ROOM_LIST = (
        AccessObj(("agent", "child/room/kick"), 'GET', 'LIST_ROOM_DISSOLVE_TXT'), \
)
