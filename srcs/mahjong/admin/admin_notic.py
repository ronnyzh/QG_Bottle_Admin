#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    邮件公告模块
"""
from bottle import *
from admin import admin_app
from config.config import STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,PARTY_PLAYER_COUNT
from common.utilt import *
from common.log import *
from datetime import datetime
from model.gameModel import *
from model.agentModel import *
from model.mailModel import *
from model.protoclModel import *
from model.userModel import getAgentAllMemberIds
from common import log_util,convert_util,json_util
import json


@admin_app.get('/notic/list')
@admin_app.get('/notic/list/<action>')
@checkLogin
def get_notic_list(redis,session,action='HALL'):
    lang = getLang()
    action = action.upper()
    fields = ('startDate','endDate','isList')
    for field in fields:
        exec('%s = request.GET.get("%s","").strip()'%(field,field))

    log_util.debug('[get_notic_list] get params startDate[%s] endDate[%s] isList[%s] action[%s]'\
                        %(startDate,endDate,isList,action))
    if isList:
        noticList = getNoticsList(redis,session,lang,session['id'],action)
        return json.dumps(noticList,cls=json_util.CJsonEncoder)
    else:
        info = {
                'title'                 :       lang.GAME_NOTIFY_LIST_TXT,
                'tableUrl'              :       BACK_PRE+'/notic/list/{}?isList=1'.format(action),
                'createUrl'             :       BACK_PRE+'/notice/create/{}'.format(action),
                'STATIC_LAYUI_PATH'     :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'     :       STATIC_ADMIN_PATH,
                'back_pre'              :       BACK_PRE,
                'addTitle'              :       lang.GAME_NOTIFY_CREATE_TXT
        }
        return template('admin_notice_list',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/notice/create')
@admin_app.get('/notice/create/<action>')
def do_createNotice(redis,session,action="HALL"):
    """
        创建新公告
    """
    lang = getLang()
    selfUid = session['id']
    action = action.upper()

    # adminTable = AGENT_TABLE%(selfUid)
    # # adminType  = redis.hget(adminTable,'type')
    info = {
        "title"                 :   lang.GAME_NOTIFY_SEND_TXT,
        "submitUrl"             :   BACK_PRE+"/notice/create",
        'STATIC_LAYUI_PATH'     :   STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'     :   STATIC_ADMIN_PATH,
        'back_pre'              :   BACK_PRE,
        'action'                :   action,
        'backUrl'               :   BACK_PRE+"/notic/list/{}".format(action)
    }

    return template('admin_game_notice_create',selfUid=selfUid,MAIL_SETTING_INFO=MAIL_SETTING_INFO,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/notice/create')
@checkLogin
def do_createNotice(redis,session):

    lang = getLang()
    fields = {
            ('title','公告信息标题',''),
            ('validDate','有效日期',''),
            ('messageType','信息类型',''),
            ('content','信息内容',''),
            ('action','后台系统','')
    }

    for field in fields:
        exec('%s = web_util.get_form("%s","%s","%s")'%(field[0],field[0],field[1],field[2]))

    log_util.debug('[try do_createNotice] title[%s] validDate[%s] messageType[%s] content[%s] action[%s]'\
                            %(title,validDate,messageType,content,action))
    try:
        messageInfo = {
                'title'         :       title,
                'validDate'     :       validDate,
                'messageType'   :       messageType,
                'content'       :       content
        }
        createNotice(redis,session['id'],messageInfo,action)
    except Exception,e:
        log_util.debug('[try do_createNotice] ERROR reason[%s]'%(e))
        return {'code':1,'msg':'添加新公告失败'}

    #记录操作日志
    return {'code':0,'msg':lang.GAME_NOTIFY_SEND_SUCCESS_TXT,'jumpUrl':BACK_PRE+'/notic/list/{}'.format(action)}

@admin_app.get('/notice/del')
def getGameNoticeDel(redis,session):
    """
    删除公告消息
    """
    noticId = request.GET.get('id','').strip()
    if not noticId:
        return {'code':1,'msg':'noticId[%s]不存在'%(noticId)}

    noticListTable = FORMAT_GAMEHALL_NOTIC_LIST_TABLE
    noticTable = FORMAT_GAMEHALL_NOTIC_TABLE%(noticId)
    if not redis.exists(noticTable):
        return {'code':1,'msg':'noticId[%s]的公告已被删除.'}

    info = {
            'title'         :       lang.GAME_NOTIFY_DEL_TXT,
    }

    pipe = redis.pipeline()
    try:
        pipe.lrem(noticListTable,noticId)
        pipe.delete(noticTable)
    except:
        return {'code':1,'msg':lang.GAME_NOTIFY_DEL_ERR_TXT}

    pipe.execute()
    return {'code':0,'msg':lang.GAME_NOTIFY_DEL_SUCCESS_TXT,'jumpUrl':BACK_PRE+'/notic/list'}

@admin_app.get('/notice/modify')
@admin_app.get('/notice/modify/<action>')
def get_notice_modify(redis,session,action="HALL"):
    lang=getLang()
    action = action.upper()
    fields = {
            ('noticeId','公告信息ID','')
    }
    for field in fields:
        exec('%s = web_util.get_query("%s","%s","%s")'%(field[0],field[0],field[1],field[2]))

    noticTable = FORMAT_GAMEHALL_NOTIC_TABLE%(noticeId)
    if not redis.exists(noticTable):
        log_util.debug('[try get_notice_modify] noticeId[%s] is not exists.'%(noticeId))
        return {'code':'1','msg':'公告消息不存在.'}

    noticInfo = redis.hgetall(noticTable)
    info = {
          'title'                 :      lang.GAME_NOTIFY_MODIFY_TXT,
          'noticeId'              :       noticeId,
          'backUrl'               :       BACK_PRE+'/notic/list/{}'.format(action),
          'submitUrl'             :       BACK_PRE+'/notice/modify/{}'.format(action),
          'back_pre'              :       BACK_PRE,
          'STATIC_LAYUI_PATH'     :       STATIC_LAYUI_PATH,
          'STATIC_ADMIN_PATH'     :       STATIC_ADMIN_PATH,
    }

    return template('admin_game_notice_modify',info=info,MSGTYPE2DESC=MSGTYPE2DESC,noticInfo=noticInfo,MAIL_SETTING_INFO=MAIL_SETTING_INFO,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/notice/modify')
@admin_app.post('/notice/modify/<action>')
def do_noticModify(redis,session,action="HALL"):
    lang = getLang()
    action = action.upper()
    fields = {
            ('noticeId','公告信息ID',''),
            ('title','公告信息标题',''),
            ('validDate','有效日期',''),
            ('messageType','信息类型',''),
            ('content','信息内容','')
    }
    for field in fields:
        exec('%s = web_util.get_form("%s","%s","%s")'%(field[0],field[0],field[1],field[2]))

    noticTable = FORMAT_GAMEHALL_NOTIC_TABLE%(noticeId)
    pipe  =  redis.pipeline()
    messageInfo = {
            'title'         :       title,
            'validDate'     :       validDate,
            'messageType'   :       DESC2MSGTYPE[messageType.encode('utf-8')],
            'content'       :       content
    }
    log_util.debug('[try do_noticModify] noticeId[%s] messageInfo[%s] action[%s]'%(noticeId,messageInfo,action))
    pipe.hmset(noticTable,messageInfo)

    pipe.execute()
    return {'code':0,'msg':lang.GAME_NOTIFY_MODIFY_SUC_TXT,'jumpUrl':BACK_PRE+'/notic/list/{}'.format(action)}

@admin_app.get('/notice/push')
@admin_app.get('/notice/push/<action>')
def pushNotices(redis,session,action='hall'):
    """
    将消息放进玩家的信息列表
    """
    type2Msg = {'0':'推送','1':'取消推送'}
    action = action.upper()
    timeStr = convert_util.to_dateStr(datetime.now())
    agentId  = session['id']
    noticId = request.GET.get('id','').strip()

    pipe = redis.pipeline()
    #超级管理员发的公告需要塞到所有玩家的信息盒子
    noticeTable = FORMAT_GAMEHALL_NOTIC_TABLE%(noticId)
    senderId = redis.hget(noticeTable,'groupId')
    if not senderId:
        senderId = 1
    memberIds = getAgentAllMemberIds(redis,senderId)

    if action == 'HALL':
        user_msg_table_list = FORMAT_USER_MESSAGE_LIST
    else:
        user_msg_table_list = FORMAT_USER_MSG_FISH_LIST

    #推送所有公告
    status = convert_util.to_int(redis.hget(noticeTable,'status'))
    log_util.debug('[try pushNotices] agentId[%s] memberIds[%s] status[%s] action[%s]'%(agentId,memberIds,status,action))
    try:
        if status == 0:
            for memberId in memberIds:
                pipe.hset(FORMAT_GAMEHALL_NOTIC_TABLE%(noticId),'time',timeStr)
                pipe.lpush(user_msg_table_list%(memberId),noticId)
            pipe.hset(noticeTable,'status','1')
        else:
            for memberId in memberIds:
                pipe.lrem(user_msg_table_list%(memberId),noticId)
                pipe.srem(FORMAT_MSG_READ_SET%(noticId),memberId)
            pipe.hset(noticeTable,'status','0')
    except Exception,e:
        log_util.debug('[try pushNotices] ERROR agentId[%s] reason[%s]'%(agentId,e))
        return {'code':1,'msg':type2Msg[str(status)]+'失败.'}

    pipe.execute()
    return {'code':0,'msg':type2Msg[str(status)]+'成功.','jumpUrl':BACK_PRE+'/notic/list/{}'.format(action)}

@admin_app.get('/notice/read')
def getNoticeReadPage(redis,session):
    """
    读取信息
    """
    curTime = datetime.now()
    lang    = getLang()
    msgType = request.GET.get('type','').strip()
    msgId   = request.GET.get('id','').strip()
    agentId = request.GET.get('agentId','').strip()
    memberId = request.GET.get('memberId','').strip()
    action   = request.GET.get('action','').strip()

    #log
    #log_util.debug('[try getNoticeReadPage] msgId[%s] msgType[%s] agentId[%s] action[%s]'%(curTime,msgId,msgType,agentId,action))

    noticeItem = FORMAT_GAMEHALL_NOTIC_TABLE%(msgId)
    if not redis.exists(noticeItem):
        return template('notice_not_exists')

    noticeReads = FORMAT_MSG_READ_SET%(msgId)
    readList = redis.smembers(noticeReads)

    #设置消息为已读
    if memberId not in readList:
        redis.sadd(noticeReads,memberId)

    title,content = redis.hmget(noticeItem,('title','content'))

    if msgType == MAIL_TYPE:
        #setReward2User(msgId,userId)
        deleteMsg(redis,msgId,memberId)

    # log_util.debug('[try getNoticeReadPage] RETURN msgId[%s] title[%s] content[%s] action[%s]'%(curTime,msgId,title,content,action))
    return template('notice_content_page',content=content,title=title)
