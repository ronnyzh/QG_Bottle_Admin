<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/qb/js/jquery-2.1.1.js"></script>
<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/qb/js/bootstrap.min.js"></script>
<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/qb/js/jquery.metisMenu.js"></script>
<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/qb/js/jquery.slimscroll.min.js"></script>
<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/qb/js/inspinia.js"></script>
<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/qb/js/pace.min.js"></script>

<link rel="stylesheet" href="{{ info['STATIC_ADMIN_PATH']}}/qb/css/bootstrap.min.css">
<link rel="stylesheet" href="{{ info['STATIC_ADMIN_PATH']}}/qb/font-awesome/css/font-awesome.css">
<link rel="stylesheet" href="{{ info['STATIC_ADMIN_PATH']}}/qb/css/animate.css">

<div class="cl-mcont">
    <div class="block">
        <div class="header">
            <h3>
                %if info.get('title',None):
                {{ info['title']}}
                %end
            </h3>
        </div>
        <form method="POST" class="form-horizontal" action="" onSubmit="return false;"
              id="createConfig">
            <div class="form-group">
                <label class="col-sm-2 control-label"> 代理账号: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ agentTable.get('account','') }}</span>
                </div>
                <label class="col-sm-2 control-label"> 上级代理: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ agentTable.get('parent_id','') }}</span>
                </div>
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 代理公会ID: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ agentTable.get('id','') }}</span>
                </div>
                <label class="col-sm-2 control-label"> 下级代理: </label>
                <div class="col-sm-5">
                    <textarea class="form-control" rows="4">{{ info.get('agentChildList','') }}</textarea>
                </div>
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 代理名称: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ agentTable.get('name','') }}</span>
                </div>
                <label class="col-sm-2 control-label"> 会员活跃数: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ info.get('members','') }}</span>
                </div>
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 代理类型: </label>
                <div class="col-sm-3">
                            <span class="form-control">{{ info.get('aType','') }}<label
                                    class="label label-success"></label></span>
                </div>
                <label class="col-sm-2 control-label"> 会员总数: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ info.get('allMembers','') }}</span>
                </div>
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 占成: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ agentTable.get('shareRate','') }}</span>
                </div>
                <label class="col-sm-2 control-label"> 当日耗钻数: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ info.get('roomCard','') }}</span>
                </div>
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 注册时间: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ agentTable.get('regDate','') }}</span>
                </div>
                <label class="col-sm-2 control-label"> 剩余钻石: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ agentTable.get('roomcard','') }}</span>
                </div>
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 注册IP: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ agentTable.get('regIp','') }}</span>
                </div>
                %if info['aType'] == '二级代理':
                <label class="col-sm-2 control-label"> 亲友圈总数: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ info.get('clubCount','') }}</span>
                </div>
                %end
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 最后登录IP: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ agentTable.get('lastLoginIp','') }}</span>
                </div>
                %if info['aType'] == '二级代理':
                <label class="col-sm-2 control-label"> 亲友圈列表: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ info.get('clubList','') }}</span>
                </div>
                %end
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 最后登录日期: </label>
                <div class="col-sm-3">
                    <span class="form-control">{{ agentTable.get('lastLoginDate','') }}</span>
                </div>
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 账号状态: </label>
                <div class="col-sm-3">
                    %if agentTable.get('valid'):
                    <span class="form-control "><label class="label label-success">有效</label></span>
                    %else:
                    <span class="form-control"><label class="label label-success">冻结</label></span>
                    %end
                </div>
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 是否试玩: </label>
                <div class="col-sm-3">
                    %if agentTable.get('isTrail') == '1':
                    <span class="form-control"><label class="label label-success">试玩公会</label></span>
                    %else:
                    <span class="form-control"><label class="label label-success">正式公会</label></span>
                    %end
                </div>
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 商城充钻: </label>
                <div class="col-sm-3">
                    %if agentTable.get('recharge') == '1':
                    <span class="form-control"><label class="label label-success">开放</label></span>
                    %else:
                    <span class="form-control"><label class="label label-success">未开放</label></span>
                    %end
                </div>
            </div>
            <div class="form-group">
                <label class="col-sm-2 control-label"> 仅权限者代开房: </label>
                <div class="col-sm-3">
                    %if agentTable.get('open_auth') == '1':
                    <span class="form-control"><label class="label label-warning">是</label></span>
                    %else:
                    <span class="form-control"><label class="label label-warning">否</label></span>
                    %end
                </div>
            </div>
            <div class="hr-line-dashed"></div>
            <div class="form-group">
                <div class="col-sm-4 col-sm-offset-5">
                    <button class="btn btn-primary" type="submit" name="backid" id="backid">返回</button>
                </div>
            </div>
        </form>
    </div>
</div>

<div class="row">
    <div class="col-lg-12">
        <div class="ibox float-e-margins">
            <div class="ibox-title">
                <h5><strong>代理订单信息</strong></h5>
            </div>
            <div class="ibox-content">
                <div style='clear:both'></div>
                <div class="tabs-container">
                    <ul class="nav nav-tabs">
                        <li class="active"><a data-toggle="tab" href="#tab-1"> 售钻总订单 ({{ info.get('saleOrderCount','0')}})</a>
                        </li>
                        <li class=""><a data-toggle="tab" href="#tab-2"> 售钻已确认订单 ({{ info.get('saleOrderAffirmCount','0')}})</a>
                        </li>
                        <li class=""><a data-toggle="tab" href="#tab-3"> 售钻未确认订单({{ info.get('saleORderUnconfirmedCount','0') }})</a>
                        </li>
                        <li class=""><a data-toggle="tab" href="#tab-4"> 购钻总订单 ({{ info.get('buyOrderCount','0') }})</a></li>
                        <li class=""><a data-toggle="tab" href="#tab-5"> 购钻已确认订单 ({{ info.get('buyOrderAffirmCount','0')}})</a>
                        </li>
                        <li class=""><a data-toggle="tab" href="#tab-6">
                            购钻未确认订单({{ info.get('buyORderUnconfirmedCount','0')}})</a></li>
                    </ul>
                    <div class="tab-content">
                        <div id="tab-1" class="tab-pane active">
                            <div class="fixed-table-container panel-body" style="padding-bottom: 0px;">
                                <div class="fixed-table-body ibox-content">
                                    <table style="font-size: 14px;font-weight:bolder ;" class="footable table table-striped table-bordered table-hover dataTables-example
                    " data-page-size="10">
                                        <thead>
                                        <tr>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单号</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻数</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">售钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单类型</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">申请购钻日期(购钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">确认订单日期(售钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">备注</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单状态</div>
                                                <div class="fht-cell"></div>
                                            </th>

                                        </tr>
                                        </thead>
                                        <tbody>
                                        %for item in info['saleOrderCountList']:
                                        <tr>
                                            <td style="text-align: center; vertical-align: middle; "
                                                class="text-muted">{{ item.get('orderNo','') }}
                                            </td>
                                            <td style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('cardNums','') }}
                                            </td>
                                            <td class="text-success"
                                                style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('applyAccount','') }}
                                            </td>
                                            <td class="text-danger"
                                                style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('saleAccount','') }}
                                            </td>
                                            %if item.get('type') == '0':
                                            <td style="text-align: center; vertical-align: middle; ">代理充卡</td>
                                            %else:
                                            <td style="text-align: center; vertical-align: middle; ">会员充卡</td>
                                            %end
                                            <td style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('apply_date','') }}</td>
                                            %if item['finish_date']:
                                            <td style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('finish_date','') }}
                                            </td>
                                            %else:
                                            <td style="text-align: center; vertical-align: middle; ">
                                                ----------------------------—
                                            </td>
                                            %end
                                            <td style="text-align: center; vertical-align: middle; ">{{ item.get('note','') }}
                                            </td>
                                            %if item.get('status') == '0':
                                            <td style="text-align: center; vertical-align: middle; color:blue;">
                                                售钻方未确认
                                            </td>
                                            %elif item.get('status') == '1':
                                            <td style="text-align: center; vertical-align: middle; color:green;">
                                                售钻方已确认
                                            </td>
                                            %else:
                                            <td style="text-align: center; vertical-align: middle; color:red;">订单已取消
                                            </td>
                                            %end
                                        </tr>
                                        %end
                                        </tbody>
                                        <tfoot>
                                        <tr>
                                            <td colspan="10">
                                                <ul class="pagination pull-right"></ul>
                                            </td>
                                        </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            </div>
                        </div>
                        <div id="tab-2" class="tab-pane">
                            <div class="fixed-table-container panel-body" style="padding-bottom: 0px;">
                                <div class="fixed-table-body ibox-content">
                                    <table style="font-size: 14px;font-weight:bolder ;" class="footable table table-striped table-bordered table-hover dataTables-example
                    " data-page-size="10">
                                        <thead>
                                        <tr>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单号</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻数</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">售钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单类型</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">申请购钻日期(购钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">确认订单日期(售钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">备注</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单状态</div>
                                                <div class="fht-cell"></div>
                                            </th>

                                        </tr>
                                        </thead>
                                        <tbody>
                                        %for item in info['saleOrderAffirmList']:
                                        <tr>
                                            <td style="text-align: center; vertical-align: middle; "
                                                class="text-muted">{{ item.get('orderNo','') }}
                                            </td>
                                            <td style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('cardNums','') }}
                                            </td>
                                            <td class="text-success"
                                                style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('applyAccount','') }}
                                            </td>
                                            <td class="text-danger"
                                                style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('saleAccount','') }}
                                            </td>
                                            %if item.get('type') == '0':
                                            <td style="text-align: center; vertical-align: middle; ">代理充卡</td>
                                            %else:
                                            <td style="text-align: center; vertical-align: middle; ">会员充卡</td>
                                            %end
                                            <td style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('apply_date','') }}</td>
                                            %if item['finish_date']:
                                            <td style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('finish_date','') }}
                                            </td>
                                            %else:
                                            <td style="text-align: center; vertical-align: middle; ">
                                                ----------------------------—
                                            </td>
                                            %end
                                            <td style="text-align: center; vertical-align: middle; ">{{ item.get('note','') }}
                                            </td>
                                            %if item.get('status') == '0':
                                            <td style="text-align: center; vertical-align: middle; color:blue;">
                                                售钻方未确认
                                            </td>
                                            %elif item.get('status') == '1':
                                            <td style="text-align: center; vertical-align: middle; color:green;">
                                                售钻方已确认
                                            </td>
                                            %else:
                                            <td style="text-align: center; vertical-align: middle; color:red;">订单已取消
                                            </td>
                                            %end
                                        </tr>
                                        %end
                                        </tbody>
                                        <tfoot>
                                        <tr>
                                            <td colspan="10">
                                                <ul class="pagination pull-right"></ul>
                                            </td>
                                        </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            </div>
                        </div>
                        <div id="tab-3" class="tab-pane">
                            <div class="fixed-table-container panel-body" style="padding-bottom: 0px;">
                                <div class="fixed-table-body ibox-content">
                                    <table style="font-size: 14px;font-weight:bolder ;" class="footable table table-striped table-bordered table-hover dataTables-example
                    " data-page-size="10">
                                        <thead>
                                        <tr>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单号</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻数</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">售钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单类型</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">申请购钻日期(购钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">确认订单日期(售钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">备注</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单状态</div>
                                                <div class="fht-cell"></div>
                                            </th>

                                        </tr>
                                        </thead>
                                        <tbody>
                                        %for item in info['saleOrderUnconfirmedList']:
                                        <tr>
                                            <td style="text-align: center; vertical-align: middle; "
                                                class="text-muted">{{ item.get('orderNo','') }}
                                            </td>
                                            <td style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('cardNums','') }}
                                            </td>
                                            <td class="text-success"
                                                style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('applyAccount','') }}
                                            </td>
                                            <td class="text-danger"
                                                style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('saleAccount','') }}
                                            </td>
                                            %if item.get('type') == '0':
                                            <td style="text-align: center; vertical-align: middle; ">代理充卡</td>
                                            %else:
                                            <td style="text-align: center; vertical-align: middle; ">会员充卡</td>
                                            %end
                                            <td style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('apply_date','') }}</td>
                                            %if item['finish_date']:
                                            <td style="text-align: center; vertical-align: middle; ">
                                                {{ item.get('finish_date','') }}
                                            </td>
                                            %else:
                                            <td style="text-align: center; vertical-align: middle; ">
                                                ----------------------------—
                                            </td>
                                            %end
                                            <td style="text-align: center; vertical-align: middle; ">{{ item.get('note','') }}
                                            </td>
                                            %if item.get('status') == '0':
                                            <td style="text-align: center; vertical-align: middle; color:blue;">
                                                售钻方未确认
                                            </td>
                                            %elif item.get('status') == '1':
                                            <td style="text-align: center; vertical-align: middle; color:green;">
                                                售钻方已确认
                                            </td>
                                            %else:
                                            <td style="text-align: center; vertical-align: middle; color:red;">订单已取消
                                            </td>
                                            %end
                                        </tr>
                                        %end
                                        </tbody>
                                        <tfoot>
                                        <tr>
                                            <td colspan="10">
                                                <ul class="pagination pull-right"></ul>
                                            </td>
                                        </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div id="tab-4" class="tab-pane">
                            <div class="fixed-table-container panel-body" style="padding-bottom: 0px;">
                                <div class="fixed-table-body ibox-content">
                                    <table style="font-size: 14px;font-weight:bolder ;" class="footable table table-striped table-bordered table-hover dataTables-example
                    " data-page-size="10">
                                        <thead>
                                        <tr>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单号</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻数</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">售钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单类型</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">申请购钻日期(购钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">确认订单日期(售钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">备注</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单状态</div>
                                                <div class="fht-cell"></div>
                                            </th>

                                        </tr>
                                        </thead>
                                        <tbody>
                                        %if info.get('buyOrderCountList'):
                                        %for item in info['buyOrderCountList']:
                                            <tr>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-muted">{{ item.get('orderNo','') }}
                                                </td>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-muted">{{ item.get('cardNums','') }}</td>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-success">{{ item.get('applyAccount','') }}
                                                </td>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-danger">{{ item.get('saleAccount','') }}
                                                </td>
                                                %if item.get('type') == '0':
                                                    <td style="text-align: center; vertical-align: middle; ">代理充卡</td>
                                                %else:
                                                    <td style="text-align: center; vertical-align: middle; ">会员充卡</td>
                                                %end
                                                <td style="text-align: center; vertical-align: middle; ">{{item.get('apply_date','') }}
                                                </td>
                                                %if item.get('finish_date'):
                                                    <td style="text-align: center; vertical-align: middle; ">{{item.get('finish_date','') }}
                                                    </td>
                                                %else:
                                                    <td style="text-align: center; vertical-align: middle; ">
                                                        ----------------------------—
                                                    </td>
                                                %end
                                                <td style="text-align: center; vertical-align: middle; ">{{ item.get('note','')}}
                                                </td>
                                                %if item.get('status') == '0':
                                                    <td style="text-align: center; vertical-align: middle; color:blue;">售钻方未确认</td>
                                                %elif item.get('status') == '1':
                                                    <td style="text-align: center; vertical-align: middle; color:green;">售钻方已确认</td>
                                                %else:
                                                    <td style="text-align: center; vertical-align: middle; color:red;">订单已取消</td>
                                                %end
                                            </tr>
                                        %end
                                        %end
                                        </tbody>
                                        <tfoot>
                                        <tr>
                                            <td colspan="10">
                                                <ul class="pagination pull-right"></ul>
                                            </td>
                                        </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div id="tab-5" class="tab-pane">
                            <div class="fixed-table-container panel-body" style="padding-bottom: 0px;">
                                <div class="fixed-table-body ibox-content">
                                    <table style="font-size: 14px;font-weight:bolder ;" class="footable table table-striped table-bordered table-hover dataTables-example
                    " data-page-size="10">
                                        <thead>
                                        <tr>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单号</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻数</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">售钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单类型</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">申请购钻日期(购钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">确认订单日期(售钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">备注</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单状态</div>
                                                <div class="fht-cell"></div>
                                            </th>

                                        </tr>
                                        </thead>
                                        <tbody>
                                        %if info.get('buyOrderAffirmList'):
                                        %for item in info['buyOrderAffirmList']:
                                            <tr>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-muted">{{ item.get('orderNo','') }}
                                                </td>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-muted">{{ item.get('cardNums','') }}</td>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-success">{{ item.get('applyAccount','') }}
                                                </td>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-danger">{{ item.get('saleAccount','') }}
                                                </td>
                                                %if item.get('type') == '0':
                                                    <td style="text-align: center; vertical-align: middle; ">代理充卡</td>
                                                %else:
                                                    <td style="text-align: center; vertical-align: middle; ">会员充卡</td>
                                                %end
                                                <td style="text-align: center; vertical-align: middle; ">{{item.get('apply_date','') }}
                                                </td>
                                                %if item.get('finish_date'):
                                                    <td style="text-align: center; vertical-align: middle; ">{{item.get('finish_date','') }}
                                                    </td>
                                                %else:
                                                    <td style="text-align: center; vertical-align: middle; ">
                                                        ----------------------------—
                                                    </td>
                                                %end
                                                <td style="text-align: center; vertical-align: middle; ">{{ item.get('note','')}}
                                                </td>
                                                %if item.get('status') == '0':
                                                    <td style="text-align: center; vertical-align: middle; color:blue;">售钻方未确认</td>
                                                %elif item.get('status') == '1':
                                                    <td style="text-align: center; vertical-align: middle; color:green;">售钻方已确认</td>
                                                %else:
                                                    <td style="text-align: center; vertical-align: middle; color:red;">订单已取消</td>
                                                %end
                                            </tr>
                                        %end
                                        %end
                                        </tbody>
                                        <tfoot>
                                        <tr>
                                            <td colspan="10">
                                                <ul class="pagination pull-right"></ul>
                                            </td>
                                        </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div id="tab-6" class="tab-pane">
                            <div class="fixed-table-container panel-body" style="padding-bottom: 0px;">
                                <div class="fixed-table-body ibox-content">
                                    <table style="font-size: 14px;font-weight:bolder ;" class="footable table table-striped table-bordered table-hover dataTables-example
                    " data-page-size="10">
                                        <thead>
                                        <tr>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单号</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻数</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">购钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">售钻方</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单类型</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">申请购钻日期(购钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">确认订单日期(售钻方)</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">备注</div>
                                                <div class="fht-cell"></div>
                                            </th>
                                            <th style="text-align: center; vertical-align: middle; "
                                                data-field="num">
                                                <div class="th-inner sortable both">订单状态</div>
                                                <div class="fht-cell"></div>
                                            </th>

                                        </tr>
                                        </thead>
                                        <tbody>
                                        %if info.get('buyORderUnconfirmedList'):
                                        %for item in info['buyORderUnconfirmedList']:
                                            <tr>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-muted">{{ item.get('orderNo','') }}
                                                </td>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-muted">{{ item.get('cardNums','') }}</td>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-success">{{ item.get('applyAccount','') }}
                                                </td>
                                                <td style="text-align: center; vertical-align: middle; "
                                                    class="text-danger">{{ item.get('saleAccount','') }}
                                                </td>
                                                %if item.get('type') == '0':
                                                    <td style="text-align: center; vertical-align: middle; ">代理充卡</td>
                                                %else:
                                                    <td style="text-align: center; vertical-align: middle; ">会员充卡</td>
                                                %end
                                                <td style="text-align: center; vertical-align: middle; ">{{item.get('apply_date','') }}
                                                </td>
                                                %if item.get('finish_date'):
                                                    <td style="text-align: center; vertical-align: middle; ">{{item.get('finish_date','') }}
                                                    </td>
                                                %else:
                                                    <td style="text-align: center; vertical-align: middle; ">
                                                        ----------------------------—
                                                    </td>
                                                %end
                                                <td style="text-align: center; vertical-align: middle; ">{{ item.get('note','')}}
                                                </td>
                                                %if item.get('status') == '0':
                                                    <td style="text-align: center; vertical-align: middle; color:blue;">售钻方未确认</td>
                                                %elif item.get('status') == '1':
                                                    <td style="text-align: center; vertical-align: middle; color:green;">售钻方已确认</td>
                                                %else:
                                                    <td style="text-align: center; vertical-align: middle; color:red;">订单已取消</td>
                                                %end
                                            </tr>
                                        %end
                                        %end
                                        </tbody>
                                        <tfoot>
                                        <tr>
                                            <td colspan="10">
                                                <ul class="pagination pull-right"></ul>
                                            </td>
                                        </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/qb/js/footable.all.min.js"></script>
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