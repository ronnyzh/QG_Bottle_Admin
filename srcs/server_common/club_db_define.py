#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    web数据表及关系对应
"""

CLUB_CREATE_ATTR = "club:create_attribute:hash"
"""創建俱樂部的屬性
max_club_num  : 最大創建的俱樂部數
max_player_num: 創建俱樂部的最大玩家數量 (預留)
allow_create_room : ["account"]
"""
CLUB_LIST = "club:list:set"
""" 列表

亲友圈编号

"""
# 创始人创建的亲友圈列表
CLUB_ACCOUNT_LIST = "club:account:%s:set"
"""　创始人创建的亲友圈列表
%s = 用户account

亲友圈编号
"""

# 亲友圈所属的玩家列表
CLUB_PLAYER_LIST = "club:players:%s:set"
"""亲友圈所属的玩家列表
%s = 亲友圈id

存储
玩家account
"""
# 玩家所属的亲友圈列表
CLUB_PLAYER_TO_CLUB_LIST= "club:players:accounts:%s:set"
"""玩家所属的亲友圈列表
%s =　玩家ACCOUNT

存储：
亲友圈ＩＤ

"""
CLUB_ATTR = "club:attribute:%s:hash"
"""　
%s = 亲友圈编号
亲友圈属性
存储
club_name : 亲友圈名称
club_user : 亲友圈创建人
club_max_players: 亲友圈最大玩家数量（备用）
club_is_vip: 亲友圈是否是ＶＩＰ亲友圈（备用）
club_manager
club_agent
club_use_create_room
"""
# 用戶加入俱樂部审核列表
CLUB_AUDI_LIST = "club:auditing:%s:set"
"""
%s = 俱樂部ＩＤ
存儲:
account:nickname:avatar_url:status
"""
# 亲友圈基础创建属性
CLUB_GLOBAL_ATTRIBUT = "club:global:attribute:hash"
"""



"""
# 玩家进入亲友圈的临时存储
CLUB_PLAYER_INTO = "club:into:%s"
"""
%s = 玩家ACCOUNT


"""

CLUB_PLAYER_NOTES = "club:player:notes:%s:hash"
"""
亲友圈的玩家备注信息


"""

# 自动房间设置
CLUB_EXTENDS_ATTRIBUTE = "club:auto:create:room:%s:%s:hset"
"""
%s = 亲友圈ID

存储:


"""

# 自动房间设置列表
CLUB_EXTENDS_LIST_ATTRIBUTE = "club:auto:create:room:%s:set"
""" 

"""

# 亲友圈包间开房信息
CLUB_ROOM_LIST = "otherCreate:Room:%s:%s:%s:set"
"""
%s:%s:%s (所属公会， 所属亲友圈， 所属包间)

"""

CLUB_GAME_ATTRIBUTE_NUMBER = {
    5: 1,
    9991: 1,
    9992: 1,
    1001: 1,
    1000: 1,
    1003: 1,
    1004: 1,
    1007: 1,
    1005: 1,
    # 1006: 1,
    2000: 1,
    2005: 1,
    3003: 1,
    4001: 1,
    4002: 1,
    9990: 1,
    5003: 1,
    9993: 1,
    5004: 1,
    5006: 1,
    999: 1,
    5002: 1,
    5010: 1,
    5104: 1
}

# 5003,9993,5004,5006

# 是否平局获取大赢家
IS_AVG = True


# 亲友圈统计设计


# CLUB_dissolution
# 解散亲友圈统计数据
CLUB_DISSOLUTION = "club:dissolution:list"
"""存储结构
club_number[亲友圈编号]:account[创始人账户信息]:[datetime]解散日期

"""

CLUB_EXIT_PLAYER_LIST = "club:exit:player:%s:list"
"""亲友圈玩家退出列表 %s  = club_number[亲友圈编号]

存储机构：
玩家ACCOUNT:退出时间:退出标识[0=自己退出 1=管理者踢出]:踢出者账号

"""
CLUB_PLAYER_POINT = "club:date:%s:cid:%s:mid:%s:hesh"
CLUB_PLAYERPOINT_LIMIT = "club:%s:pid:%s:point"
ROOM_BIREFT = "room:%s:brief:hesh"
CLUB_DAILY_ROOM = "club:date:%s:%s:room:set"
CLUB_DAILY_USER_ROOM = "club:date:%s:%s:mid:%s:room:set"
CLUB_DAILY_PLAYERS = "club:date:%s:cid:%s:set"







