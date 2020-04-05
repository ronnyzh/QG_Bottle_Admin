#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    代理模块
"""
from bottle import *
from admin import admin_app
from config.config import STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,RES_VERSION
from common.utilt import *
from common.log import *
from datetime import datetime
from web_db_define import *
from model.agentModel import *
from model.userModel import *
from club_db_define import *
from access_module import *
from common import convert_util,web_util,json_util
from model.protoclModel import sendProtocol2GameService
import hashlib
import json
import time

GET_FORMS = "%s = request.GET.get('%s','').strip()"
POST_FORMS = "%s = request.forms.get('%s','').strip()"

@admin_app.get('/agent/list')
@checkAccess
def getAgentList(redis,session):
    """
    代理列表
    """
    lang    = getLang()
    #fields = ('isList','id','searchId','start_date','end_date')
    fields = ('isList','id','searchId','start_date','end_date')
    for field in fields:
        exec(GET_FORMS%(field,field))

    if not id:
        id = session['id']

    adminTable = AGENT_TABLE%(id)
    creatAgUrl = BACK_PRE + '/agent/create'
    #搜索条件
    condition = {'start_date':start_date,'end_date':end_date,'searchId':searchId}
    create_auth,aType = redis.hmget(adminTable,('create_auth','type'))

    create_auth = convert_util.to_int(create_auth)

    if redis.sismember(AGENT2ACCESSBAN%(id),creatAgUrl):
        createAg = '0'
    else:
        createAg = '1'

    if isList:
        res = getAgListInfos(redis,session,id,condition,lang)
        return json.dumps(res)
    else:
        info = {
                'title'                  :       '下线代理列表(%s)'%(lang.TYPE_2_ADMINTYPE[str(int(aType)+1)]),
                'showPlus'               :       'true' if aType in ['0','1'] else 'false',
                'createAccess'           :       createAg,
                'atype'                  :       aType,
                'searchTxt'              :       '公会/代理ID/代理账号',
                'createUrl'              :       BACK_PRE+'/agent/create',
                'listUrl'                :       BACK_PRE+'/agent/list?isList=1',
                'create_auth'            :       create_auth,
                'show_date_search'       :       True,
                'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
        }
        return template('admin_agent_list',PAGE_LIST=PAGE_LIST,info=info,lang=lang,RES_VERSION=RES_VERSION)


@admin_app.get('/agent/club')
@admin_app.get('/agent/club/<agent_id>')
def get_agent_club(redis, session, agent_id=None):
    """
    代理ID公会下的所有亲友圈列表
    :param redis: redis
    :param session: session
    :param agent_id: 代理ID
    :return: json.dumps if islist else template
    """
    curTime = datetime.now()
    lang = getLang()

    islist = request.GET.get('islist', '').strip()
    startDate = request.GET.get('startDate', '').strip()
    endDate = request.GET.get('endDate', '').strip()
    uid = request.GET.get('uid', '').strip()
    pageSize = request.GET.get('pageSize', '').strip()
    pageNumber= request.GET.get('pageNumber', '').strip()
    search = request.GET.get('searchText', '').strip()

    if islist:
        agent_id = islist
        data = get_AgClub(redis, agent_id)
        return json.dumps(data)
    else:
        info = {
            'title': '亲友圈列表',
            'listUrl': BACK_PRE + '/agent/club/list?islist=%s' % (agent_id),
            'serversUrl': BACK_PRE + '/agent/club/user/list?list=1',
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
    return template('admin_agent_club', info=info, lang=lang, RES_VERSION=RES_VERSION)

@admin_app.get('/agent/club/user/list')
def get_agent_club_user(redis, session):
    """
    亲友圈下的会员列表
    :param redis: redis
    :param session: session
    :return:
    """
    club_number = request.GET.get('id', '').strip()
    data = get_AgClubUser(redis, club_number)
    return json_dumps(data)

@admin_app.get('/agent/info')
@admin_app.get('/agent/info/<agent_id>')
def get_agent_info(redis,session,agent_id=None):
    """
    代理信息查看
    """
    curTime = datetime.now()
    lang    = getLang()

    if not agent_id:
        abort(404, 'Nont Found')

    adminTable = AGENT_TABLE % (agent_id)
    agentTable = redis.hgetall(adminTable)

    agentChildList = ','.join(redis.smembers('agents:id:%s:child' % (agent_id)))

    #亲友圈
    agentlist = redis.smembers("agent:%s:member:children" % agent_id)
    agentlist = [redis.hget("users:%s" % (i), "account") for i in agentlist]
    _rlis = []
    for i in agentlist:
        club_account = redis.smembers("club:account:%s:set" % (i))
        if club_account:
            for each in club_account:
                _rlis.append(each)

    #订单相关
    #售钻
    saleOrderList = redis.keys("agent:%s:sale:order:*" % (agent_id))
    saleOrderCount, saleOrderAffirmCount, saleORderUnconfirmedCount  = 0, 0, 0
    saleOrderCountList, saleOrderAffirmList, saleOrderUnconfirmedList = [],[],[]
    for each in saleOrderList:
        saleOrderCount += redis.llen(each)
        for i in redis.lrange(each, 0, -1):
            saleOrderAttr = redis.hgetall("orders:id:%s" % (i))
            if saleOrderAttr:
                saleOrderCountList.append(saleOrderAttr)
                if saleOrderAttr.get('status') == '1':
                    saleOrderAffirmCount += 1
                    saleOrderAffirmList.append(saleOrderAttr)
                else:
                    saleORderUnconfirmedCount += 1
                    saleOrderUnconfirmedList.append(saleOrderAttr)
    #购钻
    buyOrderList = redis.keys("agent:%s:buy:order:*" % (agent_id))
    buyOrderCount, buyOrderAffirmCount, buyORderUnconfirmedCount = 0, 0, 0
    buyOrderCountList, buyOrderAffirmList, buyORderUnconfirmedList = [], [], []
    for each in buyOrderList:
        buyOrderCount += redis.llen(each)
        for i in redis.lrange(each, 0, -1):
            buyOrderAttr = redis.hgetall("orders:id:%s" % (i))
            if buyOrderAttr:
                buyOrderCountList.append(buyOrderAttr)
                if buyOrderAttr.get('status') == '1':
                    buyOrderAffirmCount += 1
                    buyOrderAffirmList.append(buyOrderAttr)
                else:
                    buyORderUnconfirmedCount += 1
                    buyORderUnconfirmedList.append(buyOrderAttr)
            else:
                buyOrderCountList.append({'orderNo': i, 'status': '2'})

    info = {
        'title': '代理[%s]详细信息' % (agent_id),
        'backUrl': '/admin/agent/list',
        'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,
        'aType': {'0': '超级管理员', '1': '一级代理', '2': '二级代理'}[agentTable.get('type')],
        'agentTable': agentTable,
        'agentChildList': agentChildList,
        'members': getAgentMembers(redis, agent_id),
        'allMembers': getAgentAllMembers(redis, agent_id),
        'roomCard': getAgentRoomByDay(redis, agent_id, curTime.strftime('%Y-%m-%d')),
        'clubList': ','.join(_rlis),
        'clubCount': len(_rlis),
        'saleOrderCount': saleOrderCount,
        'saleOrderAffirmCount': saleOrderAffirmCount,
        'saleORderUnconfirmedCount': saleORderUnconfirmedCount,
        'saleOrderCountList': saleOrderCountList,
        'saleOrderAffirmList': saleOrderAffirmList,
        'saleOrderUnconfirmedList': saleOrderUnconfirmedList,

        'buyOrderCount': buyOrderCount,
        'buyOrderAffirmCount': buyOrderAffirmCount,
        'buyORderUnconfirmedCount': buyORderUnconfirmedCount,
        'buyOrderCountList': buyOrderCountList,
        'buyOrderAffirmList': buyOrderAffirmList,
        'buyORderUnconfirmedList': buyORderUnconfirmedList,

        'buyOrderUrl': '/admin/'
    }

    return template('admin_agent_info',info=info, lang=lang,
                               session=session, agentTable=agentTable, RES_VERSION=RES_VERSION)

@admin_app.get('/agent/create')
@admin_app.get('/agent/create/<agent_id>')
def get_agent_create(redis,session,agent_id=None):
    """
    创建代理
    """
    curTime = datetime.now()
    if agent_id:
        agentId = agent_id
    else:
        agentId =  request.GET.get('id','').strip()
    lang    = getLang()

    if not agentId:
        agentId = session['id']

    adminTable = AGENT_TABLE%(agentId)
    aType,shareRate = redis.hmget(adminTable,('type','shareRate'))

    createAgentType = int(aType)+ 1
    access = getListAccess(createAgentType,lang)

    info = {
            'title'                  :       '创建代理（上级代理:%s）'%(agentId),
            'parentAg'               :       agentId,
            'aType'                  :       aType,
            'backUrl'                :       BACK_PRE+'/agent/list',
            'submitUrl'              :       BACK_PRE+'/agent/create/{}'.format(agentId),
            'games'                  :       getCreatAgentGames(redis,agentId),
            'defaultGames'           :       redis.smembers(GAME_DEFAULT_BIND),
            'shareRate'              :       shareRate,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
    }

    return template('agent_create',Access=access,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/agent/create')
@admin_app.post('/agent/create/<agent_id>')
def do_create_agent(redis,session,agent_id=None):
    """
    创建代理操作
    """
    curTime = datetime.now()
    now_date = curTime.strftime('%Y-%m-%d')
    selfUid = session['id']
    lang = getLang()

    for fields in AGENT_FIELDS:
        exec(POST_FORMS%(fields,fields))

    parentAg = agent_id
    if not parentAg:
        return {'code':1,'msg':'非法创建代理!'}


    #当前创建的是
    agent_type,is_trail,parent_unitPrice = redis.hmget(AGENT_TABLE%(parentAg),('type','isTrail','unitPrice'))
    is_trail = convert_util.to_int(is_trail)
    #打印一下
    log_util.debug('[try do_create_agent] parentAg[%s] account[%s] passwd[%s] comfirmPasswd[%s]'\
                    %(parentAg,account,passwd,comfirPasswd))

    checkFields = [
        {'field':account,'msg':'代理账号不能为空'},
        {'field':passwd,'msg':'密码不能为空'},
        {'field':comfirPasswd,'msg':'密码不能为空'}
    ]

    for field in checkFields:
        if not field['field']:
            return {'code':1,'msg':field['msg']}

    if unitPrice and shareRate:
        if float(shareRate) > float(unitPrice):
            return {'code':1,'msg':'给下级分成不能大于钻石单价!'}

    if myRate and shareRate:
        if float(shareRate) > float(myRate):
            return {'code':1,'msg':'给下级分成不能大于自己的分成!'}

    agent_table = AGENT_TABLE%(agentId)
    if redis.exists(agent_table):
        return {'code':1,'msg':'代理ID[%s]已存在'%(agentId)}

    parentSetTable  =  AGENT_CHILD_TABLE%(parentAg)
    if int(parentAg) == 1:
        recharge,create_auth,open_auth ='1','0','0'
    else:
        topAgentId = getTopAgentId(redis,parentAg)
        recharge,create_auth = redis.hmget(AGENT_TABLE%(topAgentId),('recharge','create_auth'))
        open_auth = '0'
        create_auth = convert_util.to_int(create_auth)
        if not recharge:
            recharge = '1'

    admimtoIdTalbel = AGENT_ACCOUNT_TO_ID%(account)
    pipe = redis.pipeline()

    if not redis.exists(admimtoIdTalbel):
        if not agentId:
            agentId = getAgentIdNo(redis)
        else:
            pipe.sadd(AGENT_ID_TABLE,agentId)

        agentType = int(agent_type)+1
        agentInfo = {
                'id'                    :           agentId,
                'account'               :           account,
                'passwd'                :           hashlib.sha256(passwd).hexdigest(),
                'name'                  :           '',
                'shareRate'             :           shareRate,
                'valid'                 :            1,
                'roomcard_id'           :           0,
                'parent_id'             :           parentAg,
                'roomcard'              :           0,
                'regIp'                 :           '127.0.0.1',
                'regDate'               :           convert_util.to_dateStr(curTime.now(),"%Y-%m-%d %H:%M:%S"),
                'lastLoginIP'           :           1,
                'lastLoginDate'         :           1,
                'isTrail'               :           is_trail,
                'unitPrice'             :           unitPrice,
                'recharge'              :           recharge,
                'isCreate'              :           '1',
                'create_auth'           :           create_auth,
                'open_auth'             :           open_auth,
                'type'                  :           agentType,
                'defaultRoomCard'       :           defaultRoomCard,
        }

        adminTable  =  AGENT_TABLE%(agentId)
        if unitPrice:
            pipe.sadd(AGENT_ROOMCARD_PER_PRICE%(agentId),unitPrice)

        if shareRate and agent_type in ['0','1','2']:
            if agent_type == '1':
                unitPrice = parent_unitPrice
            elif agent_type == '2':
                unitPrice = get_user_card_money(redis,parentAg)
            pipe.sadd(AGENT_RATE_SET%(agentId),shareRate)
            pipe.sadd(AGENT_ROOMCARD_PER_PRICE%(agentId),unitPrice)

        #创建日期索引
        pipe.sadd(AGENT_CREATE_DATE%(now_date),agentId)
        pipe.hmset(adminTable,agentInfo)
        #创建代理账号映射id
        pipe.set(admimtoIdTalbel,agentId)
        #将该代理添加进父代理集合
        pipe.set(AGENT2PARENT%(agentId),parentAg)
        #创建代理账号的父Id映射
        pipe.sadd(parentSetTable,agentId)
        # 为该代理绑定拥有的游戏
        setAgentGames(request,redis,parentAg,agentId)
        # 为该代理绑定拥有的权限(通过type)
        setAgentAccess(redis,agentType,agentId)
        # 禁止改代理的列表权限
        banAgentAccess(redis,request,agentType,agentId)
        pipe.execute()
    else:
        log_util.debug('[try crateAgent] agent account[%s] is exists!'%(account))
        return {'code':1,'msg':'代理账号(%s)已经存在.'%(account)}

    #创建成功日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['openAgent']%(agentId)}

    writeAgentOpLog(redis,selfUid,logInfo)
    log_util.debug('[try createAgent] SUCCESS agent create success! info[%s]'%(agentInfo))
    return web_util.do_response(0,msg='创建代理[%s]成功'%(account),jumpUrl='/admin/agent/list')

@admin_app.get('/agent/modify')
@admin_app.get('/agent/modify/<agent_id>')
def getAgentModify(redis,session,agent_id=None):
    """
    代理修改
    """
    curTime = datetime.now()
    agentId =  request.GET.get('id','').strip()
    lang    = getLang()
    if not agent_id:
        abort(404,"Not Found")

    adminTable = AGENT_TABLE%(agent_id)
    agent_type,rate,parentId,account,unitPrice,name,defaultRoomCard = \
                                redis.hmget(adminTable,('type','shareRate','parent_id','account','unitPrice','name','defaultRoomCard'))
    parentAdminTable = AGENT_TABLE%(parentId)
    #父代理的属性
    aType,shareRate = redis.hmget(parentAdminTable,('type','shareRate'))
    log_debug('[%s][admin][ag][info] modify ag.parentId[%s]'%(curTime,agent_id))
    #获取自己的游戏
    ownGames = getAgentOwnGames(redis,agent_id)
    #获取权限
    access = getListAccess(agent_type,lang)
    #获取搬掉的权限
    banAccess = getListBanAccess(redis,agent_id)

    info = {
            'title'                  :       '修改代理（上级代理:%s）'%(parentId),
            'agentId'                :       agent_id,
            'aType'                  :       aType,
            'backUrl'                :       BACK_PRE+'/agent/list',
            'submitUrl'              :       BACK_PRE+'/agent/modify',
            'games'                  :       getAgentGames(redis,parentId,agent_id),
            'ownGames'               :       ownGames,
            'shareRate'              :       shareRate,
            'unitPrice'              :       unitPrice,
            'rate'                   :       rate,
            'account'                :       account,
            'name'                   :       name,
            'defaultRoomCard'        :       defaultRoomCard if defaultRoomCard else 0,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
    }

    return template('admin_agent_modify',Access=access,banAccess=banAccess,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/agent/modify')
@checkAccess
def do_agent_modify(redis,session):
    """
    代理修改接口
    :params agentId 修改的代理ID
    :params account
    """
    curTime = datetime.now()
    fields = ('agentId','account','unitPrice','shareRate','myRate','name','defaultRoomCard')
    for field in fields:
        exec("%s = request.forms.get('%s','').strip()"%(field,field))

    if not agentId:
        return {'code':1,'msg':'非法修改代理!'}

    agent_type,parent_id = redis.hmget(AGENT_TABLE%(agentId),('type','parent_id'))
    log_util.debug('[do_agModify] try to modify agentId[%s] account[%s]'\
                    %(agentId,account))


    if unitPrice and shareRate:
        if float(shareRate) > float(unitPrice):
            return {'code':1,'msg':'给下级分成不能大于钻石单价!'}
    if myRate and shareRate:
        if float(shareRate) > float(myRate):
            return {'code':1,'msg':'给下级分成不能大于父代理的分成!'}

    pipe = redis.pipeline()
    adminTable  =  AGENT_TABLE%(agentId)
    agentInfo = {
                'shareRate'             :           shareRate,
                'unitPrice'             :           unitPrice,
                'name'                  :           name,
                'defaultRoomCard'       :           defaultRoomCard,
    }

    if unitPrice:
        log_util.debug('[modify] unitPrice[%s]'%(unitPrice))
        pipe.sadd(AGENT_ROOMCARD_PER_PRICE%(agentId),unitPrice)

    if shareRate and agent_type in ['1','2']:
        unitPrice = get_user_card_money(redis,agentId)
        log_util.debug('[modify] agentId[%s] shareRate[%s]'%(agentId,unitPrice))
        pipe.sadd(AGENT_RATE_SET%(agentId),shareRate)
        if unitPrice:
            pipe.sadd(AGENT_ROOMCARD_PER_PRICE%(agentId),unitPrice)

    elif myRate and agent_type in ['3']:
        unitPrice = get_user_card_money(redis,agentId)
        log_util.debug('[modify] agentId[%s] shareRate[%s]'%(agentId,unitPrice))
        pipe.sadd(AGENT_RATE_SET%(agentId),myRate)
        pipe.sadd(AGENT_ROOMCARD_PER_PRICE%(agentId),unitPrice)

    pipe.hmset(adminTable,agentInfo)
    #为该代理重新绑定拥有的游戏
    modifyAgentGames(request,redis,agentId)
    # 修改代理的禁用列表权限
    banAgentAccessModify(redis,request,agent_type,agentId)
    pipe.execute()

    #创建成功日志
    log_util.debug('[try do_agent_modify] modify success! info[%s]'%(agentInfo))
    return web_util.do_response(0,'修改代理[%s]成功'%(account),jumpUrl='/admin/agent/list')

@admin_app.get('/agent/freeze')
@checkAccess
def do_agFreeze(redis,session):
    """
        代理冻结
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']

    agentId = request.GET.get('id','').strip()

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][freeze][error] agent[%s] is not exists!'%(curTime,agentId))
        return abort(403)

    if redis.hget(adminTable,'valid') == '1':
        agentFreeze(redis,agentId)
        #记录操作日志
        logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['freezeAgent']%(agentId)}
    else:
        redis.hset(adminTable,'valid','1')
        #记录操作日志
        logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['unfreezeAgent']%(agentId)}

    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':'(%s)状态更改成功!'%(agentId),'jumpUrl':'/admin/agent/list'}

@admin_app.get('/agent/trail')
@checkAccess
def do_agTrail(redis,session):
    """
    设置公会为试玩
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']

    agentId = request.GET.get('id','').strip()

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][trail][error] agent[%s] is not exists!'%(curTime,agentId))
        return {'code':1,'msg':lang.GROUP_NOT_EXISTS_TXT%(agentId)}

    if redis.hget(adminTable,'isTrail') == '0':
        doAgentChange(redis,agentId,'isTrail',1)
        #记录操作日志
        logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['trailAgent']%(agentId)}
    else:
        doAgentChange(redis,agentId,'isTrail',0)
        #记录操作日志
        logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['unTrailAgent']%(agentId)}

    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':lang.GROUP_STATUS_SETTING_SUCCESS%(agentId),'jumpUrl':BACK_PRE+'/agent/list'}

@admin_app.get('/agent/recharge')
@checkAccess
def do_agRecharge(redis,session):
    """
    设置公会是否能给会员充卡接口
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']
    agentId = request.GET.get('id','').strip()

    login_info_dict = {
            '0'             :       'rechargeAg',
            '1'             :       'unRechargeAg'
    }

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][trail][error] agent[%s] is not exists!'%(curTime,agentId))
        return {'code':1,'msg':lang.GROUP_NOT_EXISTS_TXT%(agentId)}

    re_status = redis.hget(adminTable,'recharge')
    if not re_status:
        re_status = '1'

    if re_status == '0':
        doAgentChange(redis,agentId,'recharge',1)
    else:
        doAgentChange(redis,agentId,'recharge',0)

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                    'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE[login_info_dict[re_status]]%(agentId)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':lang.GROUP_RECHARGE_SETTING_SUCCESS%(agentId),'jumpUrl':BACK_PRE+'/agent/list'}

@admin_app.get('/agent/auto_check')
@checkAccess
def do_Auto(redis,session):
    """
    设置公会是否能给会员充卡接口
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']
    agentId = request.GET.get('id','').strip()

    login_info_dict = {
            '0'             :       'autocheck',
            '1'             :       'unAutocheck'
    }

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][trail][error] agent[%s] is not exists!'%(curTime,agentId))
        return {'code':1,'msg':lang.GROUP_NOT_EXISTS_TXT%(agentId)}

    auto_check = redis.hget(adminTable,'auto_check')
    if not auto_check:
        auto_check = '1'

    if auto_check == '0':
        doAgentChange(redis,agentId,'auto_check',1)
    else:
        doAgentChange(redis,agentId,'auto_check',0)

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                    'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE[login_info_dict[auto_check]]%(agentId)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':lang.GROUP_CHECK_SETTING_SUCCESS,'jumpUrl':BACK_PRE+'/agent/list'}

@admin_app.get('/agent/create_auth')
@checkAccess
def do_createAuth(redis,session):
    """
    是否允许公会创建三级公会
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']
    agentId = request.GET.get('id','').strip()

    login_info_dict = {
            '0'             :       'createAuth',
            '1'             :       'unCreateAuth'
    }

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][trail][error] agent[%s] is not exists!'%(curTime,agentId))
        return {'code':1,'msg':lang.GROUP_NOT_EXISTS_TXT%(agentId)}

    create_auth = redis.hget(adminTable,'create_auth')
    if not create_auth:
        create_auth = '0'

    if create_auth == '0':
        doAgentChange(redis,agentId,'create_auth',1)
    else:
        doAgentChange(redis,agentId,'create_auth',0)

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                    'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE[login_info_dict[create_auth]]%(agentId)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':lang.GROUP_CHECK_SETTING_SUCCESS,'jumpUrl':BACK_PRE+'/agent/list'}

@admin_app.get('/agent/open_auth')
@checkAccess
def do_openAuth(redis,session):
    """
    是否允许有权限的玩家代开房
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']
    agentId = request.GET.get('id','').strip()

    login_info_dict = {
            '0'             :       'openAuth',
            '1'             :       'unOpenAuth'
    }

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][trail][error] agent[%s] is not exists!'%(curTime,agentId))
        return {'code':1,'msg':lang.GROUP_NOT_EXISTS_TXT%(agentId)}

    open_auth = redis.hget(adminTable,'open_auth')
    if not open_auth:
        open_auth = '0'

    if open_auth == '0':
        redis.hset(adminTable,'open_auth',1)
        #doAgentChange(redis,agentId,'open_auth',1)
    else:
        redis.hset(adminTable,'open_auth',0)

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                    'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE[login_info_dict[open_auth]]%(agentId)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':lang.GROUP_CHECK_SETTING_SUCCESS,'jumpUrl':BACK_PRE+'/agent/list'}

@admin_app.get('/agent/member/curOnline')
@checkAccess
def getCurOnline(redis,session):
    """
    获取在线用户接口
    """
    lang    =  getLang()
    curTime =  datetime.now()
    isList  =  request.GET.get('list','').strip()

    if isList:
        onlineInfos = get_member_online_list(redis,lang,session['id'])
        return json.dumps(onlineInfos)
    else:
        info = {
                'title'                  :           '会员实时在线',
                'listUrl'                :           BACK_PRE+'/agent/member/curOnline?list=1',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_member_online',info=info,lang=lang,RES_VERSION=RES_VERSION)


@admin_app.get('/agent/checkBuyCard')
def getAgentCardRefresh(redis,session):
    """
    轮询检查下级代理向自己是否购买钻石
    """
    curTime = datetime.now()
    selfUid = session['id']

    number = request.GET.get('number','').strip()
    buyOrderTable = AGENT_SALEPENDING_ORDER_LIST%(selfUid,curTime.strftime('%Y-%m-%d'))
    if not redis.exists(buyOrderTable):
        return {'code':2,'orderNo':0}

    orderNo = redis.llen(buyOrderTable)

    if int(number) > orderNo:
        return {'code':2,'orderNo':orderNo}
    elif int(number) < orderNo:
        return {'code':0,'msg':'您有%s笔未处理的订单'%(orderNo),'orderNo':orderNo,'jumpUrl':BACK_PRE+'/order/sale/record'}
    else :
        return {'code':3}

@admin_app.get('/agent/cardRefresh')
def getAgentCardRefresh(redis,session):
    """
    代理钻石刷新
    """
    curTime = datetime.now()
    selfAccount,selfUid = session['account'],session['id']
    if selfUid == '1':
        #超级管理员直接返回
        return {'roomCard':'无限制'}

    adminTable = AGENT_TABLE%(selfUid)
    roomCards,agent_type = redis.hmget(adminTable,('roomcard','type'))
    if not agent_type:
        return {'roomCard':'会话信息超时'}

    return {'roomCard':roomCards}

@admin_app.get('/agent/comfirmJoin')
def getComfirmJoin(redis,session):
    """
    确认加入
    """
    curTime = datetime.now()

    selfAccount,selfUid = session['account'],session['id']

    memberIds = redis.lrange(JOIN_GROUP_LIST%(selfUid),0,-1)
    pipe = redis.pipeline()
    for memberId in memberIds:
        if int(memberId) <= 0:
            continue
        status = redis.get(JOIN_GROUP_RESULT%(memberId)).split(':')[1]
        if int(status) == 0:
            status = 1
            pipe.set(JOIN_GROUP_RESULT%(memberId),"%s:%s"%(selfUid,status))
            pipe.sadd(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(selfUid), memberId)
            pipe.hset(FORMAT_USER_TABLE%(memberId),'parentAg',selfUid)
            pipe.lrem(JOIN_GROUP_LIST%(selfUid),memberId)
            pipe.execute()
            return {'code':0,'msg':'会员[%s]审核成功.'%(memberId)}

    return {'code':1}

@admin_app.get('/agent/room/list')
@checkAccess
def getAgentRoomList(redis,session):
    """
    代理直属玩家房间列表
    """
    curTime = datetime.now()
    lang    = getLang()
    isList  = request.GET.get('list','').strip()
    agentId = session['id']

    if isList:
        res = getAgRoomListInfos(redis,session,agentId,lang)
        log_debug('res[%s]'%(res))
        return json.dumps(res)
    else:
        info = {
                'title'                  :       '玩家房间列表',
                'listUrl'                :       BACK_PRE+'/agent/room/list?list=1',
                'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
        }
        return template('admin_agent_room_list',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/agent/child/room/list')
@checkAccess
def getAgentChildRoomList(redis,session):
    """
    一二级代理直属玩家房间列表
    :param redis:  redis
    :param session:  session
    :return:
    """
    curTime = datetime.now()
    lang    = getLang()
    isList  = request.GET.get('list','').strip()
    agentId = session['id']

    if isList:
        res = getAgChildRoomListInfos(redis,session,agentId,lang)
        return json.dumps(res)
    else:
        info = {
                'title'                  :       '玩家房间列表',
                'listUrl'                :       BACK_PRE+'/agent/child/room/list?list=1',
                'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
        }
        return template('admin_agent_child_room_list',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/agent/room/kick')
@checkAccess
def getAgentRoomList(redis,session):
    """
    代理直属玩家房间列表 - 强制解散房间
    """
    curTime = datetime.now()
    lang    = getLang()
    roomId  = request.GET.get('id','').strip()
    print 'roomId',roomId
    roomTable = ROOM2SERVER%(roomId)
    try:
        gameId = redis.hget(roomTable,'gameid')
    except:
        return {'code':1,'msg':'房间已解散'}

    sendProtocol2GameService(redis, gameId,HEAD_SERVICE_PROTOCOL_DISSOLVE_ROOM%(roomId))

    return {'code':0,'msg':lang.GAME_DISSOLVE_ROOM_SUCCESS,'jumpUrl':BACK_PRE+'/agent/room/list'}

@admin_app.get('/agent/child/room/kick')
def getAgentChildRoomList(redis,session):
    """
    一二代理下线玩家房间列表 - 强制解散房间
    :param redis:  redis
    :param session:  session
    :return:
    """
    curTime = datetime.now()
    lang    = getLang()
    roomId  = request.GET.get('id','').strip()
    print 'roomId',roomId
    roomTable = ROOM2SERVER%(roomId)
    try:
        gameId = redis.hget(roomTable,'gameid')
    except:
        return {'code':1, 'msg':'房间已解散'}

    sendProtocol2GameService(redis, gameId,HEAD_SERVICE_PROTOCOL_DISSOLVE_ROOM%(roomId))

    return {'code':0,'msg':lang.GAME_DISSOLVE_ROOM_SUCCESS,'jumpUrl':BACK_PRE+'/agent/child/room/list'}

@admin_app.get('/agent/active')
@checkAccess
def getAgentActive(redis,session):
    """
    下线代理活跃数统计
    """
    curTime  = datetime.now()
    lang     = getLang()

    fields = ('isList','id','startDate','endDate','date')
    for field in fields:
        exec("%s = request.GET.get('%s','').strip()"%(field,field))

    if date:
        endDate = date

    if not id:
        id = session['id']

    if isList:
        """  获取接口数据 """
        report = get_agent_active(redis,id,startDate,endDate)
        return json.dumps(report)
    else:
        """ 返回模板信息 """
        info = {
                    'title'                  :       '下线代理活跃',
                    'listUrl'                :       BACK_PRE+'/agent/active?isList=1',
                    'searchTxt'              :       '请输入公会号',
                    'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
        }

    return template('admin_agent_active',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/agent/binding')
@checkAccess
def getAgentBinding(redis,session):
    """
    代理绑定账号
    """
    curTime  = datetime.now()
    lang     = getLang()

    strTime  = curTime.strftime('%Y-%m-%d %H:%M:%S')

    fields = ('memberId','unbind')
    for field in fields:
        exec("%s = request.GET.get('%s','').strip()"%(field,field))

    selfAccount, selfUid = session['account'], session['id']
    # adminTable = AGENT_TABLE % (selfUid)
    # binding = redis.hget(adminTable, 'binding')

    message = ''
    agent_table = AGENT_BINDING_TABLE % (selfUid)
    binding_cont = redis.llen(agent_table)

    #解绑
    if memberId and unbind:
        msg = '失败'
        binding_list = redis.lrange(agent_table,0,-1)
        if binding_list:
            for i in binding_list:
                bind_uid = i.split('|')[0]
                bind_time = i.split('|')[1]
                if bind_uid == memberId:
                    bind_timestamp = time.mktime(time.strptime(bind_time,'%Y-%m-%d %H:%M:%S'))
                    now_timestamp = time.time()
                    if int(now_timestamp - bind_timestamp) >= (3600*24*7):
                        redis.lrem(agent_table,i,0)
                        msg = '成功'

                    else:
                        msg = '未到解绑时间(7天)'

        return msg

    """ 返回模板信息 """
    info = {
        'title': lang.MENU_AGENT_BINDING_TXT,
        'memberId': memberId,
        'searchUrl': BACK_PRE + '/agent/binding',
        'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH,

    }

    if memberId and binding_cont < 1:
        value = '%s|%s' % (memberId, strTime)
        redis.rpush(agent_table, value)

    elif binding_cont == 1:
        message = '达到最大绑定数'

    elif binding_cont == 0:
        message = '未绑定账号'

    binding_list = redis.lrange(agent_table, 0, -1)
    binding_info = []
    if binding_list:
        for i in binding_list:
            _info = {}
            _info['memberId'] = i.split('|')[0]
            _info['bindingTime'] = i.split('|')[1]
            nickname, headImgUrl = redis.hmget(FORMAT_USER_TABLE % (_info['memberId']), ('nickname', 'headImgUrl'))
            _info['nickname'] = nickname
            _info['headImgUrl'] = headImgUrl
            binding_info.append(_info)

    return template('admin_agent_binding', info=info, lang=lang, message=message, binding_info=binding_info, RES_VERSION=RES_VERSION)


@admin_app.get('/agent/modifyPasswd/<agent_id>')
def getSelfModifyPasswd(redis,session, agent_id):
    """
    修改代理下线的密码
    :param redis: redis
    :param session: session
    :param agent_id: 代理ID
    :return:
    """
    lang = getLang()
    info  =  {

        "title"                  :   '修改代理密码',
        "submitUrl"              :   BACK_PRE+"/agent/modifyPasswd/%s" % (agent_id),
        'STATIC_LAYUI_PATH'      :   STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'      :   STATIC_ADMIN_PATH
    }

    return template('admin_agent_modifyPasswd',lang=lang,info=info,RES_VERSION=RES_VERSION)

@admin_app.post('/agent/modifyPasswd/<agent_id>')
def do_ModifyPasswd(redis,session,agent_id):
    """
    修改代理下线的密码逻辑
    :param redis: redis
    :param session: session
    :param agent_id: 代理ID
    :return:
    """
    curTime = datetime.now()
    selfAccount,selfUid = session['account'],session['id']
    comfirmPasswd = request.forms.get('comfirmPasswd','').strip()
    comfirmPasswd1 = request.forms.get('comfirmPasswd1','').strip()

    checkNullFields = [
            {'field':comfirmPasswd,'msg':'请输入新的登录密码'},
            {'field':comfirmPasswd1,'msg':'请再次输入新的登录密码'}
    ]
    #
    for check in checkNullFields:
        if not check['field']:
            return {'code':1, 'msg':check['msg']}
    #
    agentTable = AGENT_TABLE%(agent_id)
    passwd = redis.hget(agentTable,'passwd')

    pipe = redis.pipeline()
    try:
        pipe.hset(agentTable,'passwd',hashlib.sha256(comfirmPasswd).hexdigest())
    except Exception,e:
        return {'code':1,'msg':'修改密码错误'}

    pipe.execute()
    return {'code':0,'msg':'密码修改成功,请牢记.','jumpUrl':BACK_PRE+'/agent/modifyPasswd/%s' % (agent_id)}


@admin_app.get('/agent/clublist')
@checkAccess
def getAgentClubList(redis,session):
    """
    亲友圈列表
    :param redis: redis
    :param session: session
    :return: template if islist else json
    """
    curTime = datetime.now()
    lang = getLang()

    fields = ('isList', 'id', 'startDate', 'endDate', 'date')
    for field in fields:
        exec ("%s = request.GET.get('%s','').strip()" % (field, field))

    agent_id = session.get('id')

    if isList:
        data = get_AgClubList(redis, agent_id)
        return json.dumps(data)
    else:
        info = {
            'title': '亲友圈列表',
            'listUrl': BACK_PRE + '/agent/clublist?isList=1',
            'serversUrl': BACK_PRE + '/agent/club/user/list?list=1',
            'searchTxt': '请输入公会号',
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }
    return template('admin_agent_clublist', info=info, lang=lang, RES_VERSION=RES_VERSION)


@admin_app.get('/agent/clublist/showDay')
def getAgentClubListShowDay(redis, session):
    """
    亲友圈对应下的玩家退出记录列表
    :param redis: redis
    :param session: session
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list','').strip()
    club_id = request.GET.get('club','').strip()
    if isList:
        data = get_AgClubListShowDay(redis, club_id)
        return json.dumps(data)
    else:
        info = {
                'title'                  :          '亲友圈 [%s] 玩家退出列表'%(club_id),
                'listUrl'                :           BACK_PRE+'/agent/clublist/showDay?list=1&club=%s'%(club_id),
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_agent_club_history',PAGE_LIST=PAGE_LIST,date=club_id,info=info,RES_VERSION=RES_VERSION,lang=lang)

@admin_app.get('/agent/clublist/userbanList')
def get_clublist_userbanList(redis, session):
    """
    亲友圈的同桌管理列表（禁止同台）
    :param redis: redis
    :param session: session
    :return:
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list','').strip()
    club_id = request.GET.get('club','').strip()
    if isList:
        data = get_AgClubListUserBanList(redis, club_id)
        return json.dumps(data)
    else:
        info = {
                'title'                  :          '亲友圈：[%s] 同桌管理列表'%(club_id),
                'listUrl'                :           BACK_PRE+'/agent/clublist/userbanList?list=1&club=%s'%(club_id),
                'serversUrl'             :           BACK_PRE+'/agent/clublist_userban/list?list=1&club=%s'%(club_id),
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }
        return template('admin_agent_club_userbanList',PAGE_LIST=PAGE_LIST,date=club_id,info=info,RES_VERSION=RES_VERSION,lang=lang)

@admin_app.get("/agent/clublist_userban/list")
def get_clublist_userban(redis, session):
    """
    亲友圈 玩家 下的同桌管理列表
    :param redis: redis
    :param session: session
    :return:
    """
    user_id = request.GET.get('id','').strip()
    club_id = request.GET.get('club', '').strip()
    data = get_AgClubListUserBan(redis, user_id , club_id)
    return json.dumps(data)

@admin_app.get("/agent/club/dissolution")
def get_club_dissolution(redis, session):
    """
    已解散亲友圈的列表
    :param redis: redis
    :param session: session
    :return:
    """
    curTime  = datetime.now()
    lang     = getLang()

    fields = ('isList','id','startDate','endDate','date')
    for field in fields:
        exec("%s = request.GET.get('%s','').strip()"%(field,field))

    if isList:
        data = get_AgClubDissolution(redis, startDate, endDate)
        return json.dumps(data)
    else:
        info = {
                    'title'                  :       '已解散亲友圈列表',
                    'listUrl'                :       BACK_PRE+'/agent/club/dissolution?isList=1',
                    'searchTxt'              :       '请输入公会号',
                    'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
        }

    return template('admin_agent_club_dissolution',info=info,lang=lang,RES_VERSION=RES_VERSION)


@admin_app.get('/agent/club_user/showDay')
def get_agent_club_user(redis, session):
    """
    亲友圈下的会员列表
    :param redis:
    :param session:
    :return:
    """
    club_number = request.GET.get('id', '').strip()
    date = request.GET.get('day', '').strip()
    players = []
    accounts = redis.smembers(CLUB_PLAYER_LIST % club_number)
    roomcard_accounts = set([ redis.hget("users:%s" % (i.split(':')[-4]), "account") for i in redis.keys("playerUseCardData:player:*:day:%s:list" % (date))])
    accounts = accounts & roomcard_accounts
    accounts = list(accounts)
    managerAccount = redis.hget(CLUB_ATTR % club_number, "club_user")

    members = redis.smembers(ONLINE_ACCOUNTS_TABLE)  # 获取在线正在玩的玩家
    num = 1
    nowDay = datetime.now().strftime('%Y-%m-%d')
    if not accounts:
        return
    for item in accounts:
        userTable = redis.get(FORMAT_ACCOUNT2USER_TABLE % item)  # 获取users:id
        player = {}
        player['number'] = num
        num += 1
        nickname, headImgUrl, account, last_logout_date, parentAg = redis.hmget(userTable, 'nickname', 'headImgUrl','account',"last_logout_date", "parentAg")
        player["account"] = account
        player["nickname"] = nickname
        player["avatar_url"] = headImgUrl
        player["online"] = 0
        player["user_id"] = int(userTable.split(":")[-1])
        account_type = redis.get("users:account:%s" % (account)).split(':')
        if 'robot' in account_type:
            player["account_type"] = '机器人'
        else:
            player["account_type"] = '用户'

        # 查找备注信息
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

        cardDate = redis.lrange("playerUseCardData:player:%s:day:%s:list" % (int(userTable.split(":")[-1]), nowDay),
                                0, -1)
        if cardDate:
            roomcard_day = 0
            for item in cardDate:
                roomcard_day += int(item.split(';')[0])
            player['roomcard_day'] = roomcard_day
        else:
            player['roomcard_day'] = ''
        player['roomcard_total'] = redis.get("agent:%s:user:%s:card" % (parentAg, int(userTable.split(":")[-1])))
        players.append(player)

    data = {'data': players, 'count': len(players)}
    return json_dumps(data)

@admin_app.post('/agent/clublist/addUser/<club_id>/<clubplay>')
def get_agent_clublist_addUser(redis, session, club_id, clubplay):
    """
    添加玩家到亲友圈
    :param redis:  redis
    :param session: session
    :param club_id:  亲友圈ID
    :param clubplay: 玩家ID/ACCOUNT
    :return:
    """
    if not club_id and not clubplay:
        return {'code': 1, 'msg': '不正确的亲友圈号码/玩家ID。'}
    club_play_list = redis.smembers(CLUB_PLAYER_LIST % (club_id))
    clubplay =  [ i for i in clubplay.split(',') if i ]
    not_account_list = []
    account_list = []
    for i in clubplay:
        if redis.exists(FORMAT_USER_TABLE % (i)):
            account_list.append(redis.hget(FORMAT_USER_TABLE % (i), "account"))
        elif redis.exists(FORMAT_ACCOUNT2USER_TABLE % (i)):
            account_list.append(i)
        else:
            not_account_list.append(i)
    if not account_list:
        return {'code': 1, 'msg': '该玩家不存在。'}
    if club_play_list & set(account_list) == set(account_list):
        return {'code': 1, 'msg': '该玩家已加入该亲友圈，无需重复添加。'}
    try:
        for club_account in account_list:
            redis.sadd(CLUB_PLAYER_TO_CLUB_LIST % club_account, club_id)
            redis.sadd(CLUB_PLAYER_LIST % club_id, club_account)
        return {'code': 1, 'msg': '添加玩家[ %s ]成功。<br><br> 添加玩家[ %s ]失败。' % (account_list,not_account_list)}
    except Exception as err:
        return {'code': 1, 'msg': '添加玩家失败。'}


@admin_app.post('/agent/clublist/delUser/<club_id>/<clubplay>')
def get_agent_clublist_delUser(redis, session, club_id, clubplay):
    """
    删除玩家到亲友圈
    :param redis:  redis
    :param session: session
    :param club_id:  亲友圈ID
    :param clubplay:  玩家ID/ACCOUNT
    :return:
    """
    if not club_id and not clubplay:
        return {'code': 1, 'msg': '不正确的亲友圈号码/玩家ID。'}
    club_play_list = redis.smembers(CLUB_PLAYER_LIST % (club_id))
    clubplay = [i for i in clubplay.split(',') if i]
    not_account_list = []
    account_list = []
    for i in clubplay:
        if redis.exists(FORMAT_USER_TABLE % (i)):
            account_list.append(redis.hget(FORMAT_USER_TABLE % (i), "account"))
        elif redis.exists(FORMAT_ACCOUNT2USER_TABLE % (i)):
            account_list.append(i)
        else:
            not_account_list.append(i)

    if not account_list:
        return {'code': 1, 'msg': '该玩家不存在。'}
    if not (club_play_list & set(account_list)):
        return {'code': 1, 'msg': '该玩家不是本亲友圈的人，无需删除。'}

    try:
        for club_account in account_list:
            redis.srem(CLUB_PLAYER_LIST % club_id, club_account)
            redis.srem(CLUB_PLAYER_TO_CLUB_LIST % club_account, club_id)
        return {'code': 1, 'msg': '该玩家已被移除该亲友圈。'}
    except Exception as err:
        return {'code': 1, 'msg': '移除失败。'}



@admin_app.get('/agent/clublist/audit/<club_id>')
def get_agent_clublist_audit(redis, session, club_id):
    """
    亲友圈审批申请
    :param redis: redis
    :param session: session
    :param club_id: 亲友圈ID
    :return:
    """
    curTime = datetime.now()
    lang = getLang()
    isList = request.GET.get('list', '').strip()
    start_date = request.GET.get('startDate', '').strip()
    end_date = request.GET.get('endDate', '').strip()
    selfUid = session['id']
    if isList:
        club_number = club_id
        if redis.exists(CLUB_ATTR % club_number):
            data = []
            result = redis.smembers(CLUB_AUDI_LIST % club_number)
            for item in result:
                try:
                    account, nickname, avatar_url, status = item.split("|---|")
                except Exception as err:
                    log_info(err)
                    print("item:%s, err:%s" % (item, err))
                    continue
                if not account or account.strip() == 'None':
                    log_info("[error][club_audit]%s,  %s" % (CLUB_AUDI_LIST % club_number, item))
                    redis.srem(CLUB_AUDI_LIST % club_number, item)
                    continue

                user_path = redis.get(FORMAT_ACCOUNT2USER_TABLE % account)
                user_id = user_path.split(":")[-1]
                reg_date = redis.hget(user_path, "reg_date")
                status_keys = {0: "申请中", 1: '成功', -1: '拒绝'}
                orders = {
                    0: 2,
                    1: 1,
                    -1: 0
                }

                data.append(
                    {
                        "account": account,
                        "nickname": nickname,
                        "avatar_url": avatar_url,
                        "code": status,
                        "status": status_keys[int(status)],
                        "club_number": club_number,
                        "user_id": user_id,
                        "reg_date": reg_date,
                        "order": orders[int(status)],
                        "op":  [{'url': '/admin/agent/clublist/apply/list/%s/%s/%s' % (club_number,account,'1'), 'txt': '同意', 'method': 'POST'},
                                {'url': '/admin/agent/clublist/apply/list/%s/%s/%s' % (club_number,account,'-1'), 'txt': '拒绝', 'method': 'POST'}
                         ]
                                if orders[int(status)] == 2 else ''
                    }
                )
            data = sorted(data, key=lambda x: -x["order"])
        return json.dumps({'data': data})
    else:
        info = {
            'title': '亲友圈 [%s] 申请审批列表' % (club_id),
            'listUrl': BACK_PRE + '/agent/clublist/audit/%s?list=1' % (club_id),
            'STATIC_LAYUI_PATH': STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH': STATIC_ADMIN_PATH
        }

    return template('admin_agent_clublist_audit', info=info, lang=lang, RES_VERSION=RES_VERSION)

@admin_app.get('/agent/clublist/apply/list/<club_id>/<account>/<status>')
def get_agent_clublist_apply(redis, session, club_id, account, status):
    """
    亲友圈申请审批
    :param redis: redis
    :param session: session
    :param club_id:  申请的亲友圈ID
    :param account:  申请人的账号
    :param status:   申请人的状态 {'1': '同意', '-1':'拒接'}
    :return: redirect('/admin/agent/clublist/audit'）
    """
    apply_user_account = account
    club_number = club_id
    status = status
    if int(status) == 1:
        apply_list = redis.smembers(CLUB_AUDI_LIST % club_number)
        for item in apply_list:
            account, nickname, avatar_url, state = item.split("|---|")
            if account == apply_user_account and int(state) == 0:
                redis.srem(CLUB_AUDI_LIST % club_number, item)
                redis.sadd(CLUB_AUDI_LIST % club_number,"%s|---|%s|---|%s|---|%s" % (account, nickname, avatar_url, status))

                redis.sadd(CLUB_PLAYER_TO_CLUB_LIST % account, club_number)
                redis.sadd(CLUB_PLAYER_LIST % club_number, account)
    else:
        apply_list = redis.smembers(CLUB_AUDI_LIST % club_number)
        for item in apply_list:
            account, nickname, avatar_url, state = item.split("|---|")
            if account == apply_user_account and int(state) == 0:
                redis.srem(CLUB_AUDI_LIST % club_number, item)
                redis.sadd(CLUB_AUDI_LIST % club_number, "%s|---|%s|---|%s|---|%s" % (account, nickname, avatar_url, status))

    return redirect('/admin/agent/clublist/audit/%s' % (club_id))

@admin_app.post('/agent/clublist/delClub/<club_id>')
def get_agent_clublist_delClub(redis, session ,club_id):
    """
    删除亲友圈
    :param redis: redis
    :param session: session
    :param club_id: 亲友圈ID
    :return:
    """
    try:
        pipe = redis.pipeline()
        club_number = club_id
        club_attr = redis.hgetall(CLUB_ATTR % club_number)
        account = club_attr.get('club_user')
        club_user = club_attr.get('club_user')

        # 删除亲友圈的属性
        pipe.delete(CLUB_ATTR % club_number)
        # 从总举了表中移除
        pipe.srem(CLUB_LIST, club_number)
        # 从创始人中的亲友圈列表中移除
        pipe.srem(CLUB_ACCOUNT_LIST % account, club_number)

        # 检查亲友圈的玩家，并将这些玩家从这个亲友圈中踢出
        for player in redis.smembers(CLUB_PLAYER_LIST % club_number):
            pipe.srem(CLUB_PLAYER_TO_CLUB_LIST % player, club_number)
        # 删除亲友圈存储的玩家信息

        pipe.delete(CLUB_PLAYER_LIST % club_number)
        # 删除自动开房信息
        userTable = redis.get(FORMAT_ACCOUNT2USER_TABLE %  club_user)
        parentAg = redis.hget(userTable, "parentAg")
        agClubNumber = "%s-%s" % (club_number, parentAg)

        for i in range(1, 6):
            pipe.delete(CLUB_EXTENDS_LIST_ATTRIBUTE % agClubNumber)
            pipe.delete(CLUB_EXTENDS_ATTRIBUTE % (agClubNumber, i))

        pipe.lpush(CLUB_DISSOLUTION, "%s:%s:%s" % (club_number, account, time.strftime("%Y-%m-%d", time.localtime())))
        pipe.execute()
        return {'code': 1, "msg": '删除成功。'}
    except Exception as err:
        return {'code': 1, "msg": '删除失败。'}


@admin_app.post('/agent/clublist/addManager/<club_id>/<clubplay>')
def get_agent_clublist_addManager(redis, session, club_id, clubplay):
    """
    添加玩家到亲友圈管理者
    :param redis:  redis
    :param session:  session
    :param club_id:  亲友圈ID
    :param clubplay:  玩家ID
    :return:
    """
    club_manager = redis.hget(CLUB_ATTR % (club_id), "club_manager")
    if clubplay in eval(club_manager):
        return {'code': 1, 'msg': '该玩家已是亲友圈的管理者。'}
    club_manager = eval(club_manager)
    club_manager.add(clubplay)
    try:
        redis.hmset(CLUB_ATTR % (club_id),{"club_manager": club_manager})
        return {'code': 1, 'msg': '添加玩家成功。'}
    except Exception as err:
        return {'code': 1, 'msg': '添加失败。'}


@admin_app.post('/agent/clublist/delManager/<club_id>/<clubplay>')
def get_agent_clublist_delManager(redis, session, club_id, clubplay):
    """
    移除玩家到亲友圈管理者
    :param redis:  redis
    :param session:  session
    :param club_id:  亲友圈ID
    :param clubplay:  玩家ID
    :return:
    """
    club_manager = redis.hget(CLUB_ATTR % (club_id), "club_manager")
    if clubplay not in eval(club_manager):
        return {'code': 1, 'msg': '该玩家不是亲友圈的管理者。'}
    club_manager = eval(club_manager)
    club_manager = club_manager - set([clubplay,])
    try:
        redis.hmset(CLUB_ATTR % (club_id),{"club_manager": club_manager})
        return {'code': 1, 'msg': '移除玩家成功。'}
    except Exception as err:
        return {'code': 1, 'msg': '移除失败。'}


@admin_app.post('/agent/clublist/dcuManager/<club_id>/<clubplay>')
def get_agent_clublist_dcuManager(redis, session, club_id, clubplay):
    """
    把玩家踢出亲友圈
    :param redis:  redis
    :param session:  session
    :param club_id:  亲友圈ID
    :param clubplay:  玩家ID
    :return:
    """
    club_users = redis.smembers(CLUB_PLAYER_LIST % (club_id))
    if clubplay not in club_users:
        return {'code':1 , 'msg': '该玩家不在亲友圈。'}
    try:
        redis.srem(CLUB_PLAYER_LIST % (club_id), clubplay)
        redis.srem(CLUB_PLAYER_TO_CLUB_LIST % (clubplay), club_id)
        return {'code': 1, 'msg': '踢出成功。'}
    except Exception as err:
        return {'code':1 ,'msg': '踢出失败。'}


@admin_app.post('/agent/clublist/createClub/<clubplay>')
def get_agent_clublist_createClub(redis, session, clubplay):
    """
    创建亲友圈
    :param redis: redis
    :param session: session
    :param playid: 创建人ID
    :return:
    """
    try:
        club_list = [int(i) for i in redis.smembers(CLUB_LIST)]
        if not club_list:
            next_id = 2000
        else:
            next_id = max(club_list) + 1

        next_id = str(next_id)
        if '4' in next_id:
            next_id = next_id.replace('4', str(4 + 1))
        next_id = int(next_id)
        account = redis.hget(FORMAT_USER_TABLE % clubplay, "account")
        club_name = account
        ag = redis.hget(FORMAT_USER_TABLE % clubplay, "parentAg" )
        if not ag:
            return {"code": 1, 'msg': "你没有任何公会，不能创建亲友圈"}
        club_content = club_name
        if len(redis.smembers(CLUB_ACCOUNT_LIST % account)) >= 10:
            return {"code": 1, "msg": "你已经超出了创建亲友圈的上限"}

        redis.sadd(CLUB_LIST, next_id)
        redis.hmset(
            CLUB_ATTR % next_id, {
                "club_name": club_name,
                "club_user": account,
                "club_max_players": 9999,
                "club_is_vip": 0,
                "club_content": club_content,
                "club_use_create_room": 1,  # 是否允许成员自己创建房间！默认允许,
                "club_manager": 'set()',
                "club_agent": ag,  # 第一次设置的时候加入的公会
                "club_createtime": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            }
        )
        redis.sadd(CLUB_ACCOUNT_LIST % account, next_id)
        return {"code": 1, "msg": "恭喜，创建亲友圈成功，您的亲友圈ID为%s" % next_id, "club_number": next_id}
    except Exception as err:
        return {"code": 1, "msg": "创建失败"}

@admin_app.post('/agent/clublist/userbanList/addUser/<clubid>/<userid>/<playid>')
def get_agent_clublist_userban_adduser(redis, session, clubid, userid, playid):
    """
    添加玩家到同桌禁止列表
    :param redis:  redis
    :param session:  session
    :param clubid:  亲友圈ID
    :param userid:  用户ID
    :param playid:  要禁止的同桌用户ID
    :return:
    """
    try:
        playid = playid.split(',')
        playid = [ i for i in playid if i]
        user_list = []
        none_user = []
        for i in playid:
            if i == str(userid):
                continue
            if not redis.exists('users:%s' % (i)):
                none_user.append(i)
            else:
                user_list.append(i)
        if not user_list:
            return {'code': 1, 'msg': '不存在的玩家。'}
        else:
            userban = redis.hget("club:userbanList:%s:hset" % (clubid), userid)
            user_list = [i for i in user_list if
                         redis.hget(FORMAT_USER_TABLE % (i), "account") in redis.smembers("club:players:%s:set" % (clubid))]
            if user_list:
                redis.hmset("club:userbanList:%s:hset" % (clubid) , {userid: set(user_list) | (eval(userban))})
                return {'code':1 , 'msg': '添加玩家 %s 成功。' % user_list}
            else:
                return {'code': 1, 'msg': '添加失败，该玩家不属于该亲友圈。'}
    except Exception as err:
        return {'code':1 , 'msg': '添加失败。'}


@admin_app.post('/agent/clublist/userbanList/delUser/<clubid>/<userid>/<playid>')
def get_agent_clublist_userban_deluser(redis, session, clubid, userid, playid):
    """
    删除玩家到同桌禁止列表
    :param redis: redis
    :param session: session
    :param clubid: 亲友圈ID
    :param userid: 用户ID
    :param playid: 要删除的同桌用户ID
    :return:
    """
    try:
        playid = playid.split(',')
        playid = [i for i in playid if i]
        user_list = []
        none_user = []
        for i in playid:
            if not redis.exists(FORMAT_USER_TABLE % (i)):
                none_user.append(i)
            else:
                user_list.append(i)
        if not user_list:
            return {'code': 1, 'msg': '不存在的玩家。'}
        else:
            userban = redis.hget("club:userbanList:%s:hset" % (clubid), userid)
            userban = eval(userban) - set(user_list)
            redis.hmset("club:userbanList:%s:hset" % (clubid), {'%s' % (userid): '%s' % (userban)})
            return {'code': 1, 'msg': '删除玩家%s成功。' % user_list}
    except Exception as err:
        return {'code':1 , 'msg': '删除失败。'}


@admin_app.post('/agent/clublist/userbanList/remUser/<clubid>/<userid>')
def get_agent_clublist_userban_remuser(redis, session, clubid, userid):
    """
    删除该玩家的同桌禁止列表记录
    :param redis: redis
    :param session: session
    :param clubid: 亲友圈ID
    :param userid: 用户ID
    :return:
    """
    try:
        club_userban = redis.hgetall("club:userbanList:%s:hset" % (clubid))
        if not club_userban:
            return {'code': 1, 'msg': '该亲友圈不存在。'}
        redis.hdel("club:userbanList:%s:hset" % (clubid), userid)
        return {'code': 1, 'msg': '删除成功。'}
    except Exception as err:
        return {'code': 1, 'msg': '删除失败。'}


@admin_app.post('/agent/clublist_userban/list/delUser/<clubid>/<userid>/<key>')
def get_clublist_userban_delUser(redis, session, clubid, userid, key):
    """
    移除玩家到同桌禁止列表
    :param redis: redis
    :param session: session
    :param clubid: 亲友圈ID
    :param userid: 要移除的玩家ID
    :return:
    """
    try:
        club_userban = redis.hgetall("club:userbanList:%s:hset" % (clubid))
        if not club_userban:
            return {'code': 1, 'msg': '该亲友圈不存在。'}
        club_user = eval(club_userban[key]) - set([userid])
        redis.hmset("club:userbanList:%s:hset" % (clubid) , {key:club_user})
        return {'code': 1, 'msg': '删除成功'}
    except Exception as err:
        return {'code': 1, 'msg':'删除失败'}

@admin_app.post('/agent/clublist_userban/list/createUserBan/<clubid>/<userid>/<userbanid>')
def get_clublist_userban_createUserBan(redis, session, clubid, userid, userbanid):
    """
    创建新的同桌禁止用户列表
    :param redis: redis
    :param session: session
    :param clubid: 亲友圈ID
    :param userid: 用户给ID
    :param userbanid: 禁止同桌的用户ID
    :return:
    """
    try:
        if not userid:
            return {'code': 1, 'msg': '用户ID不能为空。'}
        userbanid = [ i for i in userbanid.split(',') if i]
        user_list = []
        none_user = []
        if not redis.exists(FORMAT_USER_TABLE % userid):
            return {'code': 1, 'msg': '该用户不存在。'}
        if redis.hget(FORMAT_USER_TABLE % userid, "account") not in redis.smembers("club:players:%s:set" % (clubid)):
            return {'code': 1, 'msg': '该用户不是该亲友圈的玩家。'}
        for i in userbanid:
            if not redis.exists('users:%s' % (i)):
                none_user.append(i)
            else:
                user_list.append(i)
        userbanlist = redis.hgetall("club:userbanList:%s:hset" % (clubid))
        if userbanlist.get(userid):
            return {'code': 1, 'msg': '已存在该玩家的同桌列表。'}
        else:
            user_list = [ i for i in user_list if redis.hget(FORMAT_USER_TABLE % (i),"account") in redis.smembers(CLUB_PLAYER_LIST % (clubid)) ]
            redis.hmset("club:userbanList:%s:hset" % (clubid), {userid: set(user_list) - set([userid])})
            return {'code': 1, 'msg': '新增成功。'}
    except Exception as err:
        return {'code': 1, 'msg': '添加失败。'}


@admin_app.post('/agent/clublist/transferUser/<club_id>/<play_id>')
def get_agent_clublist_transferUser(redis, session, club_id, play_id):
    """
    转移亲友圈
    :param redis: redis
    :param session: session
    :param club_id: 亲友圈ID
    :param play_id: 要转移人ID
    :return: {'code': 1} 弹出结果框
    """
    user = redis.exists("users:%s" % play_id)

    if user:
        club_table = "club:attribute:%s:hash" % club_id #获取亲友圈属性
        userAccount = redis.hget("users:%s" % play_id, "account") # 被迁移人的用户账号

        playerTable = "club:players:accounts:%s:set" % userAccount  # 被迁移人玩家所属的亲友圈列表
        clubPlayerTable = "club:players:%s:set" % club_id # 亲友圈所属的玩家列表

        sourceAccount = redis.hget(club_table, "club_user") # 亲友圈原创建人
        creatorSourceClub = "club:account:%s:set" % sourceAccount  #创建人的亲友圈列表

        sourceAccount = redis.hget(club_table, "club_user")
        if sourceAccount == userAccount:
            return {"code": 1, "msg": "你不能转让给自己"}

        if userAccount not in redis.smembers(clubPlayerTable):
            return {"code": 1, "msg": "该玩家不是亲友圈的人，请先邀请加入"}

        pipe = redis.pipeline()
        pipe.srem(creatorSourceClub, club_id) #删除创建人的亲友圈

        targetClub = "club:account:%s:set" % userAccount #获取要迁移的玩家的创建亲友圈列表
        sourceUidTable = redis.get("users:account:%s" % userAccount) #获取被迁移人的 user:id

        club_name = redis.hget(sourceUidTable, "nickname") #获取被迁移人的昵称
        pipe.sadd(targetClub, club_id) #在玩家的创建亲友圈中添加进去
        pipe.srem(playerTable, club_id) #将要迁移的玩家所属亲友圈中移去
        pipe.srem(clubPlayerTable, userAccount) #玩家列表中移去
        pipe.hset(club_table, "club_user", userAccount)
        pipe.hset(club_table, "club_name", club_name)
        pipe.execute()

        def add_club(redis, account, club_number):
            """
            添加玩家到亲友圈
            """
            if redis.exists(CLUB_ATTR % club_number):
                try:
                    redis.sadd(CLUB_PLAYER_TO_CLUB_LIST % account, club_number)
                    redis.sadd(CLUB_PLAYER_LIST % club_number, account)
                    return True
                except Exception as err:
                    return False
            return False
        add_club(redis, sourceAccount, club_id)
        from datetime import datetime
        transfer = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M')
        redis.lpush("club:transfer:list", "%s:%s:%s:%s" % (userAccount,transfer,club_id,sourceAccount))
        return {"code": 1, 'msg': '转移成功'}
    else:
        return {'code': 1, 'msg': '找不到该账号的信息。'}

