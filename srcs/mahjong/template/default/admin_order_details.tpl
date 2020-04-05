
%if info['type'] == 'wechat':
<div class="cl-mcont">
    <div class="block">
    <div class="header">
            <h3>
                %if info.get('title',None):
                {{ info['title']}}
                %end
            </h3>
        </div>
            <div class='col-md-12'>
                <div class="panel panel-info">
                <div class="panel-heading">
                        <span class="panel-title" id="txt1">订单信息 ({{ info.get('orderTable').get('account','') }})</span>
                    </div>
                    <div class="ibox float-e-margins">
                    <div class="ibox-content">
                <form method="POST" class="form-horizontal" action="" onSubmit="return false;"
                      id="createConfig">
                    <div class="form-group">
                        <label class="col-sm-1 control-label"> 订单类型: </label>
                        <div class="col-sm-2">
                            <span class="form-control">商城订单</span>
                        </div>
                        <label class="col-sm-1 control-label"> 订单号: </label>
                        <div class="col-sm-4">
                            <span class="form-control">{{ info.get('orderTable').get('orderNo','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 订单状态:</label>
                        <div class="col-sm-2">
                            <span class="form-control">
                                %if info.get('orderTable').get('type','') == 'successful':
                                交易成功
                                %elif info.get('orderTable').get('type','') == 'pending':
                                交易挂起
                                %else:
                                交易过期
                                %end
                            </span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="col-sm-1 control-label"> 用户:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('orderTable').get('account','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 购买数:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('orderTable').get('roomCards','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 充值公会:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('orderTable').get('groupId','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 一级代理:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('orderTable').get('parentId','') }}</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="col-sm-1 control-label"> 下单时间:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('orderTable').get('startTime','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 支付时间:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('orderTable').get('time','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 成交时间:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('orderTable').get('endTime','') }}</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="col-sm-1 control-label"> 微信支付订单号:</label>
                        <div class="col-sm-4">
                            <span class="form-control">{{ info.get('orderTable').get('orderNum','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 支付签名:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('orderTable').get('sign','') }}</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="col-sm-1 control-label"> 支付ID:</label>
                        <div class="col-sm-4">
                            <span class="form-control">{{ info.get('orderTable').get('prepayID','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 支付字符串:</label>
                        <div class="col-sm-4">
                            <span class="form-control">{{ info.get('orderTable').get('nonceStr','') }}</span>
                        </div>
                    </div>
                </form>
            </div>
                </div>
                </div>
            </div>
    </div>
</div>

<div class="cl-mcont">
    <div class="block">
        <div class='col-md-12'>
            <div class="panel panel-info">
            <div class="panel-heading">
                        <span class="panel-title" id="txt1">商品信息</span>
                    </div>
                <div class="contact-box center-version">
                <div class="ibox-content">
                <form method="POST" class="form-horizontal" action="" onSubmit="return false;"
                      id="createConfig">
                    <div class="form-group">
                        <label class="col-sm-1 control-label"> 商品类型:</label>
                        <div class="col-sm-2">
                            <span class="form-control">
                                %if info.get('goodsTable').get('type','') == '0':
                                钻石
                                %else:
                                金币
                                %end
                            </span>
                        </div>
                        <label class="col-sm-1 control-label"> 商品名:</label>
                        <div class="col-sm-3">
                            <span class="form-control">{{ info.get('goodsTable').get('name','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 商品编号:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('goodsTable').get('id','') }}</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="col-sm-1 control-label"> 商品价格:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('goodsTable').get('price','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 商品数:</label>
                        <div class="col-sm-3">
                            <span class="form-control">{{ info.get('goodsTable').get('cards','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 商品赠送:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('goodsTable').get('present_cards','') }}</span>
                        </div>
                    </div>
                </form>
            </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="cl-mcont">
    <div class="block">
        <div class='col-md-12'>
            <div class="panel panel-info">
            <div class="panel-heading">
                        <span class="panel-title" id="txt1">用户信息</span>
                    </div>
                <div class="contact-box center-version">
                <div class="ibox-content">
                <form method="POST" class="form-horizontal" action="" onSubmit="return false;"
                      id="createConfig">
                    <div class="form-group">
                        <label class="col-sm-1 control-label"> 用户ID:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('userTable').get('memberId','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 用户账号:</label>
                        <div class="col-sm-3">
                            <span class="form-control">{{ info.get('userTable').get('account','') }}</span>
                        </div>
                        <label class="col-sm-1 control-label"> 用户昵称:</label>
                        <div class="col-sm-2">
                            <span class="form-control">{{ info.get('userTable').get('nickname','') }}</span>
                        </div>
                    </div>
                </form>
            </div>
                </div>
            </div>
        </div>
    </div>
</div>

%else:
<div class="cl-mcont">
    <div class="block">
    <div class="header">
            <h3>
                %if info.get('title',None):
                {{ info['title']}}
                %end
            </h3>
        </div>
            <div class='col-md-12'>
                <div class="panel panel-info">
                <div class="panel-heading">
                        <span class="panel-title" id="txt1">订单信息 ({{ info.get('orderTable').get('applyAccount','') }})</span>
                    </div>
                    <div class="ibox float-e-margins">
                    <div class="ibox-content">
                        <form method="POST" class="form-horizontal" action="" onSubmit="return false;"
                              id="createConfig">
                            <div class="form-group">
                                <label class="col-sm-1 control-label"> 订单类型: </label>
                                <div class="col-sm-2">
                                    <span class="form-control">代理订单</span>
                                </div>
                                <label class="col-sm-1 control-label"> 订单号: </label>
                                <div class="col-sm-4">
                                    <span class="form-control">{{ info.get('orderTable',{}).get('orderNo') }}</span>
                                </div>
                                <label class="col-sm-1 control-label"> 订单状态:</label>
                                <div class="col-sm-2">
                            <span class="form-control">
                                %if info.get('orderTable',{}).get('status') == '1':
                                 <label class="label label-success">
                                售钻方已确认
                                     </label>
                                %elif info.get('orderTable',{}).get('status') == '0':
                                 <label class="label label-danger">
                                售钻方未确认
                                     </label>
                                %else:
                                <label class="label label-warning">
                                失败
                                </label>
                                %end
                            </span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-1 control-label"> 订单ID:</label>
                                <div class="col-sm-2">
                                    <span class="form-control">{{ info.get('orderTable',{}).get('id','') }}</span>
                                </div>
                                <label class="col-sm-1 control-label"> 订单备注:</label>
                                <div class="col-sm-2">
                                    <span class="form-control">{{ info.get('orderTable').get('note','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-1 control-label"> 购钻数:</label>
                                <div class="col-sm-2">
                                    <span class="form-control">{{ info.get('orderTable').get('cardNums','') }}</span>
                                </div>
                                <label class="col-sm-1 control-label"> 购钻方:</label>
                                <div class="col-sm-2">
                                    <span class="form-control">{{ info.get('orderTable').get('applyAccount','') }}</span>
                                </div>
                                <label class="col-sm-1 control-label"> 售钻方:</label>
                                <div class="col-sm-2">
                                    <span class="form-control">{{ info.get('orderTable').get('saleAccount','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-1 control-label"> 下单时间:</label>
                                <div class="col-sm-2">
                                    <span class="form-control">{{ info.get('orderTable').get('apply_date','') }}</span>
                                </div>
                                <label class="col-sm-1 control-label"> 成交时间:</label>
                                <div class="col-sm-2">
                                    <span class="form-control">{{ info.get('orderTable').get('finish_date','') }}</span>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
                </div>
            </div>
    </div>
</div>



<div class="cl-mcont">
    <div class="block">
        <div class='col-md-6'>
            <div class="panel panel-info">
            <div class="panel-heading">
                        <span class="panel-title" id="txt1">购钻方 ({{ info.get('orderTable').get('applyAccount','') }})</span>
                    </div>
                <div class="contact-box center-version">

                    %if info.get('applyAgentTable'):
                    <div class="ibox-content">
                        <form method="POST" class="form-horizontal" action="" onSubmit="return false;"
                              id="createConfig">
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 代理账号: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('account','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 代理公会: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('id','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 代理名称: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('name','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 代理类型: </label>
                                <div class="col-sm-3">
                            <span class="form-control">
                                <label class="label label-warning">{{ info.get('applyType','') }}</label>
                            </span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 注册时间: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('regDate','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 注册IP: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('regIp','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 最后登录时间: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('lastLoginDate','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 最后登录IP: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('lastLoginIp','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 账号状态: </label>
                                <div class="col-sm-3">
                            <span class="form-control">
                                %if  info.get('applyAgentTable').get('valid'):
                                <label class="label label-success">有效</label>
                                %else:
                                <label class="label label-success">冻结</label>
                                %end
                            </span>
                                </div>
                                <label class="col-sm-2 control-label"> 是否试玩: </label>
                                <div class="col-sm-3">
                            <span class="form-control">
                                %if info.get('applyAgentTable').get('isTrail') == '1':
                                <label class="label label-success">试玩公会</label>
                                %else:
                                <label class="label label-success">正式公会</label>
                                %end
                            </span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 商城充钻: </label>
                                <div class="col-sm-3">
                            <span class="form-control">
                                %if info.get('applyAgentTable').get('recharge') == '1':
                                <label class="label label-success">开放</label>
                                %else:
                                <label class="label label-success">未开放</label>
                                %end
                            </span>
                                </div>
                                <label class="col-sm-2 control-label"> 仅权限者代开房: </label>
                                <div class="col-sm-3">
                            <span class="form-control">
                                %if info.get('applyAgentTable').get('open_auth') == '1':
                                <label class="label label-success">是</label>
                                %else:
                                <label class="label label-success">否</label>
                                %end
                            </span>
                                </div>
                            </div>
                            <div class="hr-line-dashed"></div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 上级代理: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('parent_id','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 下级代理: </label>
                                <div class="col-sm-3">
                                    <textarea class="form-control" rows="4">{{ info.get('applyAgentTable').get('agentChild','') }}</textarea>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 占成: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('shareRate','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 会员活跃数: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('members','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 会员总数: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('allMembers','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 当日耗钻数: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('todayroomCard','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 剩余钻石: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyAgentTable').get('roomcard','') }}</span>
                                </div>
                            </div>
                        </form>
                    </div>
                    %else:
                    <div class="ibox-content">

                        <form method="POST" class="form-horizontal" action="" onSubmit="return false;"
                              id="createConfig">
                              <div class="contact-box center-version text-center">
                                <img alt="image" class="img-circle" style="width:10%;height:10% "
                                     src="{{ info.get('applyTable').get('headImgUrl','') }}">
                                <h4 class="m-b-xs"><strong>账号: {{ info.get('applyTable').get('account','') }}</strong></h3>
                                <h4 class="m-b-xs"><strong>昵称: {{ info.get('applyTable').get('nickname','') }}</strong></h3>
                                <h4 class="m-b-xs"><strong>所属公会: {{ info.get('applyTable').get('parentAg','') }}</strong></h3>
                                <h4 class="m-b-xs"><strong>充值总额(当前公会): {{ info.get('applyTable').get('parentAg','') }}</strong></h3>
                        </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 金币: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyTable').get('gold','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 钻石: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyTable').get('roomCard','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 登录IP: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyTable').get('last_login_ip','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 登录时间:</label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyTable').get('last_login_date','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 登出IP: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyTable').get('last_logout_ip','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 登出时间:</label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyTable').get('last_logout_date','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 创始亲友圈: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyTable').get('curClubList','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 所属亲友圈:</label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('applyTable').get('playerClubList','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 是否在线: </label>
                                <div class="col-sm-3">
                            <span class="form-control">
                                %if  info.get('applyTable.online'):
                                <label class="label label-warning">是</label>
                                %else:
                                <label class="label label-danger是否">否</label>
                                %end
                            </span>
                                </div>
                            </div>
                        </form>
                    </div>
                    %end
                </div>
            </div>
        </div>
        <div class='col-md-6'>
            <div class="panel panel-info">
            <div class="panel-heading">
                        <span class="panel-title" id="txt1">售钻方 ({{ info.get('orderTable').get('saleAccount','') }})</span>
                    </div>
                <div class="contact-box center-version">
                    <div class="ibox-content">
                        <form method="POST" class="form-horizontal" action="" onSubmit="return false;"
                              id="createConfig">
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 代理账号: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('account','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 代理公会: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('id','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 代理名称: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('name','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 代理类型: </label>
                                <div class="col-sm-3">
                            <span class="form-control">
                                <label class="label label-warning">{{ info.get('saleType','') }}</label>
                            </span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 注册时间: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('regDate','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 注册IP: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('regIp','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 最后登录时间: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('lastLoginDate','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 最后登录IP: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('lastLoginIp','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 账号状态: </label>
                                <div class="col-sm-3">
                            <span class="form-control">
                                %if  info.get('saleAgentTable').get('valid'):
                                <label class="label label-success">有效</label>
                                %else:
                                <label class="label label-success">冻结</label>
                                %end
                            </span>
                                </div>
                                <label class="col-sm-2 control-label"> 是否试玩: </label>
                                <div class="col-sm-3">
                            <span class="form-control">
                                %if info.get('saleAgentTable').get('isTrail') == '1':
                                <label class="label label-success">试玩公会</label>
                                %else:
                                <label class="label label-success">正式公会</label>
                                %end
                            </span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 商城充钻: </label>
                                <div class="col-sm-3">
                            <span class="form-control">
                                %if info.get('saleAgentTable').get('recharge') == '1':
                                <label class="label label-success">开放</label>
                                %else:
                                <label class="label label-success">未开放</label>
                                %end
                            </span>
                                </div>
                                <label class="col-sm-2 control-label"> 仅权限者代开房: </label>
                                <div class="col-sm-3">
                            <span class="form-control">
                                %if info.get('saleAgentTable').get('open_auth') == '1':
                                <label class="label label-success">是</label>
                                %else:
                                <label class="label label-success">否</label>
                                %end
                            </span>
                                </div>
                            </div>
                            % if info.get('aType','') == '0':
                            <div class="hr-line-dashed"></div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 上级代理: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('parent_id','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 下级代理: </label>
                                <div class="col-sm-3">
                                    <textarea class="form-control" rows="4">{{ info.get('saleAgentTable').get('agentChild','') }}</textarea>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 占成: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('shareRate','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 会员活跃数: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('members','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 会员总数: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('allMembers','') }}</span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-2 control-label"> 当日耗钻数: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('todayroomCard','') }}</span>
                                </div>
                                <label class="col-sm-2 control-label"> 剩余钻石: </label>
                                <div class="col-sm-3">
                                    <span class="form-control">{{ info.get('saleAgentTable').get('roomcard','') }}</span>
                                </div>
                            </div>
                            % else:
                            <div class="form-group">
                            </div>
                            % end
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
%end
<script type="text/javascript">
    $('#backid').click(function () {
        window.location.href = "{{info['backUrl']}}";
    });
</script>
<script>
    $(document).ready(function () {

        $('.footable').footable();
        $('.footable2').footable();

    });

</script>
%rebase admin_frame_base