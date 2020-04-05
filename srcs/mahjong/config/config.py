#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    后台配置文件
"""
#[resorce version]
RES_VERSION = 4.0

#[role]
SYSTEM_ADMIN = 0
systemId = 1

PROVINCE_AGENT  = 1
#配置文件
CONF_FILE = 'conf_release.json'
#[consts config]
API_ROOT           =           'http://192.168.0.99:9797'
BACK_PRE           =           '/admin'
TEMPLATE_NAME      =           'default'
TEMPLATE_PATH      =           'mahjong/template/%s'%(TEMPLATE_NAME)

#[path config]
DOWNLOAD_PATH             =            'mahjong/static/download/'
STATIC_PATH               =            'mahjong/static/'
STATIC_ADMIN_PATH         =            '/assest/default'
STATIC_LAYUI_PATH         =            '/assest/common/layui'

'''
======================================================== 后台上传/下载参数配置
'''
#允许上传的文件格式
FILES_ALLOW_EXTS = ['.jpg','.png','.gif']
#奖品文件上传路劲
FILES_REWARD_UPLOAD_PATH = 'mahjong/static/assest/default/image/reward'
#[game Pack Address]
GAME_DOWNLOAD_URL = 'http://119.23.203.197:9798/download/games/%s'
'''
======================================================== 后台下载参数配置 结束
'''


HALL_PICK_ROUTES = {
    'CN'        :   ("45.127.184.2",),
    #'CN'        :   ("192.168.0.99","192.168.0.168"),
    'DEFAULT'   :   ("45.127.184.2",),
    'TW'        :   ("45.127.184.2",),
    'HK'        :   ("45.127.184.2",),
    'MY'        :   ("45.127.184.2",),
    'SG'        :   ("45.127.184.2",),
    'ID'        :   ("45.127.184.2",),
    'PH'        :   ("45.127.184.2",),
    'JP'        :   ("45.127.184.2",),
    'KR'        :   ("45.127.184.2",),
    'US'        :   ("45.127.184.2",),
    'RU'        :   ("45.127.184.2",),
}

#[基本分配置]
PLAYER_BASE_SCORE  =  [
    {'name':'score1','score':1},
    {'name':'score2','score':2},
    {'name':'score3','score':3},
    {'name':'score4','score':4},
    {'name':'score5','score':5},
    {'name':'score6','score':6},
    {'name':'score7','score':7},
    {'name':'score8','score':8},
    {'name':'score9','score':9},
    {'name':'score10','score':10},
    {'name':'score11','score':11},
    {'name':'score12','score':12},
    {'name':'score13','score':13},
    {'name':'score14','score':14},
    {'name':'score15','score':15},
    {'name':'score16','score':16},
    {'name':'score17','score':17},
    {'name':'score18','score':18},
    {'name':'score19','score':19},
    {'name':'score2','score':20}
]
DEFAULT_BASE_SCORE = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
#[party roomPlayerSetting]
PARTY_PLAYER_COUNT = 4
#大厅VERSION
HALL2VERS = {
        "resVersion"            :   '1',
        "minVersion"            :   '1.0.1',
        "iosMinVersion"         :   '1.0.1',
        "downloadURL"           :   API_ROOT+"/download/hall/hall.apk",
        "IPAURL"                :   "",
        "apkSize"               :   22307533, #字节
        "apkMD5"                :   "67BD3A586E608AF76075F458AFB8056F",
        "hotUpdateURL"          :   API_ROOT+"/download/hall/hall.zip",
        "hotUpdateScriptsURL"   :   API_ROOT+"/download/hall/script.zip",
        "updateAndroid"         :   1,
        "updateYYB"             :   1,
        "updateAppStore1"       :   False,
        "updateAppStore2"       :   True,
        'packName'              :   'hall.zip'
}
###########################################################################
# 广播常量配置
###########################################################################
BROAD_TYPE_2_TITLE = {
        '0'         :       '【系统广播】',
        '1'         :       '【系统广播】',
        '2'         :       '【地区广播】',
        '3'         :       '【地区广播】'
}

###########################################################################
# 商城常量配置
###########################################################################
REWARD_ONLINE  = 1
REWARD_OFFLINE = 0
'''
======================================================== 前端控制参数配置
'''
#前端分页配置
PAGE_LIST = [15,50,100]
FONT_CONFIG = {
        'PAGE_LIST'         :       [15,50,100], #前端可选分页
        'STR_2_SORT'        :       {'asc':False,'desc':True}, #排序
}
'''
======================================================== 前端控制参数配置s 结束
'''
##################################################################################
### 邮件服务参数 ###
# 邮件服务器
SMTP = 'smtp.qq.com'
# 邮件服务器端口
SMTP_PORT = 465
# email发送账号
EMAIL_USER = '514303208@qq.com'
# email发送密码
EMAIL_PWD = 'cwkahrftixtfbied'
# 系统异常邮件通知地址，多个地址用逗号分隔
EMAIL_LIST = '514303208@qq.com'
# 异常邮件通知标题
# ——由于我们有开发环境、测试环境、预生产环境、生产环境等多个不同的环境，
# ——所以在发送异常通知时如果区分的话，可能就弄不清是那个环境出了问题，
# ——我们可以通过设置邮件标题为：开发、测试、预生产、生产等标签来方便区分是那个环境发送的异常通知
EMAIL_ERR_TITLE = '系统异常通知-ds_admin-系统'

##################################################################################
###  微信access_token  ###
WX_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?'
WX_ACCESS_TOKEN_PARAMS = {
    "grant_type": 'client_credential',
    'appid': 'wx2c83827f2cf8a040',
    'secret': '8ad08b6a6ac71e7c49ab1ccb8376e17e',
}

###  微信用户openid  ###
WX_USER_OPENID_URL = "https://api.weixin.qq.com/sns/oauth2/access_token?"
WX_USER_OPENID_PARAMS = {
    "grant_type": "authorization_code",
    "appid": "wx2c83827f2cf8a040",
    "secret": "8ad08b6a6ac71e7c49ab1ccb8376e17e",
}

### 微信公众号模板请求Url ###
WX_TEMPLATE_URL = 'https://api.weixin.qq.com/cgi-bin/message/template/send?'

### 微信公众号的模板ID ###
WX_TEMPLATE_ORDER_PUSH_ID = "Ac63JeL57VxhlXRWN5hPxOcwubQPC8_dIpkJFlhnQIc"  # 订单生成
WX_TEMPLATE_ORDER_COMFIRM_ID = "tVouygef9VrCCQIbtzzdC0h6h5bvQNVgsd3bHFVt0y4"  # 订单确认
WX_TEMPLATE_ORDER_CANCEL_ID = "wbf6E8MuzXaQAq2Ec4Wn0bZqHe2ptKkN-YQt1vDiKl0"  # 订单取消
WX_TEMPLATE_MEMBER_RECHARGE_ID = "J9QNsOGUaVHHVjDvGMQc_hVe7p1Nd6dOefmcvuJbGgs"  # 会员充钻
WX_TEMPLATE_DATA_PUSH_ID = "izbuHa76uoA--uYq2J-m6u8VXdtxRfw5Vc1d-MjwSHs"  # 数据推送