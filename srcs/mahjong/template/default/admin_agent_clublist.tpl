<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/bootstrap-select.min.js"></script>
<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<link rel="stylesheet" type="text/css" href="{{info['STATIC_ADMIN_PATH']}}/css/bootstrap-select.min.css"/>
<link rel="stylesheet" type="text/css" href="{{info['STATIC_ADMIN_PATH']}}/layui/css/layui.css"/>
<script src="/assest/default/layui/layui.js" charset="utf-8"></script>
<div class="block">
    %include admin_frame_header
    <div class="content">
        <div class="table-toolbar" style="float:left;width:100%;position:relative;top:3.2em">
            <div class='col-sm-12' style='margin-left:1em;'>
                <div style='float:left;margin-left:1em;' class="input-group date datetime col-md-1 col-xs-1"
                     data-min-view="2" data-date-format="yyyy-mm-dd">
                    <input class="form-control" size="12" type="text" style='width:140px;height:28px;'
                           id='pick-date-start' name="startdate" value="{{lang.INPUT_LABEL_START_DATE_TXT}}" readonly>
                    <span class="input-group-addon btn btn-primary pickdate-btn"><span
                            class="glyphicon pickdate-btn pickdate glyphicon-th"></span>
                </div>

                <div style='float:left;margin-left:1em;' class="input-group date datetime col-md-1 col-xs-1"
                     data-min-view="2" data-date-format="yyyy-mm-dd">
                    <input class="form-control" style='width:140px;height:28px;' id='pick-date-end' name="enddate"
                           size="12" type="text" value="{{lang.INPUT_LABEL_END_DATE_TXT}}" readonly>
                    <span class="input-group-addon btn btn-primary pickdate-btn"><span
                            class="pickdate glyphicon pickdate-btn glyphicon-th"></span></span>
                </div>
                <div style='float:left;margin-left:1em;'>
                    <button id="btn_query" class='btn btn-primary btn-sm btn-xs'><i class='fa fa-search'></i>{{lang.INPUT_LABEL_QUERY}}
                    </button>
                    <button id="btn_lastMonth" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_PREV_MONTH}}</button>
                    <button id="btn_thisMonth" class='btn btn-sm btn-xs '>{{lang.INPUT_LABEL_CURR_MONTH}}</button>
                    <button id="btn_lastWeek" class='btn btn-sm btn-xs '>{{lang.INPUT_LABEL_PREV_WEEK}}</button>
                    <button id="btn_thisWeek" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_CURR_WEEK}}</button>
                    <button id="btn_yesterday" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_PREV_DAY}}</button>
                    <button id="btn_today" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_CURR_DAY}}</button>
                    <div class='clearfix'></div>
                </div>
            </div>
            <div>
                <span>&nbsp;</span>
            </div>
            <div>
                <button id="btn_add" type="button" class="btn btn-sm btn-primary">
                      <span class="">
                          <a href="club/dissolution" style='color:#FFF;text-decoration:none;'>已解散亲友圈列表&nbsp;&nbsp;</a>
                      </span>
                </button>
            </div>
            <!--
            <div>
                <button id="btn_add" onclick="createClub()" type="button" class="btn btn-sm btn-primary">
                  <span class="glyphicon glyphicon-plus">
                     创建亲友圈&nbsp;&nbsp;
                  </span>
              </button>
            </div>
            -->
        </div>
        <table id="dataTable" class="table table-bordered table-hover"></table>
    </div>
</div>

<!-- 初始化搜索栏的日期 -->
<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/layui/layui.js" charset="utf-8"></script>
<script type="text/javascript">
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 6);
    $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
    $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));

    function createClub() {
        layer.open({
            id: 1,
            type: 1,
            title: '请输入要创建的亲友圈信息',
            skin: 'layui-layer-rim',
            area: ['450px', 'auto'],
            content: ' <div class="row" style="width: 420px;  margin-left:7px; margin-top:10px;">'
            + '<div class="col-sm-12">'
            + '<div class="input-group">'
            + '<span class="input-group-addon">创建人ID:</span>'
            + '<input id="clubplayid" style="width:280px;" type="input" class="form-control" placeholder="请输入创建人ID">'
            + '</div>'
            + '</div>'
            + '<div class="col-sm-12" style="margin-top: 10px">'
            + '<div class="input-group">'
            + '</div>'
            + '</div>'
            + '</div>'
            ,
            btn: ['确认', '取消'],
            yes: function (index) {
                var playaccont = $('#clubplayid').val();
                var urls = '/admin/agent/clublist/createClub/' + playaccont;
                var method = 'post';
                var jsonStr = '{@id@:@2202@}';
                normalAjaxStrData(urls, method, jsonStr);
                layer.close(index);
            },
        });
    };

    function showClubAudit(url, method, jsonStr, text, utype) {
        var pageii = layer.open({
            type: 1
            ,
            content: String.format("<iframe src='\{0}\' width='100%' height='800px'></iframe>", url)
            //,anim: 'up'
            ,
            success: function (elem) {
                $(".layui-m-layercont").css({"text-align": "left", "padding-top": "20px", "overflow": "auto"});
                $('.layui-m-layerchild').append('<div class="closePage">x</div>');
            }
            ,
            style: 'position:fixed; left:10%; top:10%; width:80%; border: none; -webkit-animation-duration: .5s; animation-duration: .5s;'
        });

    }

    function AddRemovePlayer(url, method, jsonStr, text, utype) {
        if (utype == 'addUser')
            input_txt = "请输入要添加的玩家ID/账号"
        else
            input_txt = "请输入要删除的玩家ID/账号"
        var clubid = text.toString();
        layer.open({
            id: 1,
            type: 1,
            title: '当前亲友圈ID为：' + text,
            skin: 'layui-layer-rim',
            area: ['450px', 'auto'],
            content: ' <div class="row" style="width: 420px;  margin-left:7px; margin-top:10px;">'
            + '<div class="col-sm-12">'
            + '<div class="input-group">'
            + '<span class="input-group-addon">请输入:</span>'
            + '<input id="clubplayid" type="input"  style="width:280px;" class="form-control" placeholder="请输入该玩家的ID/账号，多用户以逗号隔开。"'
            + '</div>'
            + '</div>'
            + '<div class="col-sm-12" style="margin-top: 10px">'
            + '<div class="input-group">'
            + '</div>'
            + '</div>'
            + '</div>'
            ,
            btn: ['确认', '取消'],
            yes: function (index) {
                var playaccont = $('#clubplayid').val();
                var urls = url + '/' + playaccont;
                normalAjaxStrData(urls, method, jsonStr);
                layer.close(index);
                var child_table = String.format("#child_table{0}", text);
                $(child_table).bootstrapTable('refresh',{'url': String.format('/admin/agent/club/user/list?list=1&id={0}',clubid)});
            },
        });
    };

    function transFerUser(url, method, jsonStr, text, utype) {
        layer.open({
            id: 1,
            type: 1,
            title: '当前亲友圈ID为：' + text,
            skin: 'layui-layer-rim',
            area: ['450px', 'auto'],
            content: ' <div class="row" style="width: 420px;  margin-left:7px; margin-top:10px;">'
            + '<div class="col-sm-12">'
            + '<div class="input-group">'
            + '<span class="input-group-addon">请输入:</span>'
            + '<input id="clubplayid" type="input"  style="width:280px;" class="form-control" placeholder="请输入要转移该玩家的ID。"'
            + '</div>'
            + '</div>'
            + '<div class="col-sm-12" style="margin-top: 10px">'
            + '<div class="input-group">'
            + '</div>'
            + '</div>'
            + '</div>'
            ,
            btn: ['确认', '取消'],
            yes: function (index) {
                var playaccont = $('#clubplayid').val();
                var urls = url + '/' + playaccont;
                normalAjaxStrData(urls, method, jsonStr);
                layer.close(index);
            },
        });
    };


    function ChangeClubManager(url, method, jsonStr, text, utype) {
        if (utype == 'addManager')
            txt = '将该玩家提升会管理者。'
        if (utype == 'delManager')
            txt = '将该玩家移除会管理者。'
        if (utype == 'dcuManager')
            txt = '将该玩家踢出亲友圈。'
        if (utype == 'delClub')
            txt = "删除该前有钱。"
        var comfirmTxt = '是否确定此操作<br>' + txt;
        var clubid = text.toString();
        layer.open({
            title: [
                '后台提醒你',
                'background-color:#204077; color:#fff;'
            ]
            , anim: 'up'
            , content: comfirmTxt
            , btn: ['确认', '取消']
            , fixed: true
            , style: 'width:550px;position:fixed;top:25%;left:50%;margin-left:-250px;'
            , yes: function (index) {
                normalAjaxStrData(url, method, jsonStr);
                layer.close(index);
                var child_table = String.format("#child_table{0}", text);
                $(child_table).bootstrapTable('refresh',{'url': String.format('/admin/agent/club/user/list?list=1&id={0}',clubid)});
            }
        });
    }

    function showClubRecord(url, method, userId) {
        var pageii = layer.open({
            type: 1
            ,
            content: String.format("<iframe src='\{1}\' width='100%' height='800px'></iframe>", userId, url)
            ,
            anim: 'up'
            ,
            success: function (elem) {
                $(".layui-m-layercont").css({"text-align": "left", "padding-top": "20px", "overflow": "auto"});
                $('.layui-m-layerchild').append('<div class="closePage">x</div>');
            }
            ,
            style: 'position:fixed; left:10%; top:10%; width:80%; border: none; -webkit-animation-duration: .5s; animation-duration: .5s;'
        });

    }
</script>

<script type="text/javascript">

    function initTable() {
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        $('#dataTable').bootstrapTable({
            url: '{{info["listUrl"]}}',
            method: 'get',
            contentType: "application/json",
            datatype: "json",
            //striped: true,
            minimumCountColumns: 2,
            search: true,
            toolbar: '#toolbar',
            detailView: true,//父子表
            exportTypes: ['excel', 'csv', 'pdf', 'json'],
            showRefresh: true,
            showExport: true,
            showFooter: true,
            showToggle: true,
            cardView: false,
            pagination: true,
            pageSize: 10,
            pageList: [10, 25, 50, 100],
            queryParamsType: '',
            //sidePagination:"server",
            clickToSelect: true,
            //responseHandler:responseFun,
            queryParams: getSearchP,
            columns: [
                {
                    field: 'club_createtime',
                    title: '日期',
                    align: 'center',
                    valign: 'middle'
                }, {
                    field: 'club_id',
                    title: '亲友圈ID',
                    align: 'center',
                    valign: 'middle',
                }, {
                    field: 'club_name',
                    title: '亲友圈名称',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'user_id',
                    title: '创建者ID',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'club_user',
                    title: '创建者账号',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'nickname',
                    title: '创建者昵称',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'imgurl',
                    title: '创建者头像',
                    align: 'center',
                    formatter: function (value, row, index) {
                        return '<img style="width: 40px;height: 40px;" src="' + value + '" class="img-rounded">';
                    }
                }, {
                    field: 'club_agent',
                    title: '代理工会',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'club_content',
                    title: '亲友圈信息',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'roomcards_day',
                    title: '当日耗钻总数',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'roomcards_all',
                    title: '耗钻总数',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'club_is_vip',
                    title: '是否VIP',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    formatter: function (value, row, index) {
                        if (value == 1) {
                            return "<strong><span style='font-weight:bold'>&radic;</span></strong>"
                        }
                        else {
                            return ''
                        }
                    }
                }, {
                    field: 'club_use_create_room',
                    title: '是否允许成员自己创建房间',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    formatter: function (value, row, index) {
                        if (value == 1) {
                            return "<strong><span style='font-weight:bold'>&radic;</span></strong>"
                        }
                        else {
                            return ''
                        }
                    }
                }, {
                    field: 'club_manager',
                    title: '管理者',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'count',
                    title: '亲友圈人数',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'op',
                    title: '操作',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    formatter: getOp
                }],
            onExpandRow: function (index, row, $detail) {
                console.log(index, row, $detail);
                InitSubTable(index, row, $detail);
            }
        });

        function getSearchP(p) {
            startDate = $("#pick-date-start").val();
            endDate = $("#pick-date-end").val();
            var searchId = $("#searchId").val();

            sendParameter = p;
            sendParameter['searchId'] = searchId;
            sendParameter['startDate'] = startDate;
            sendParameter['endDate'] = endDate;

            return sendParameter;
        }

        function responseFun(res) {
            count = res.total;
            //实时刷
            //$('.count').text(String.format("会员总人数:{0}",count));
            pageNumber = parseInt(res.pageNumber);
            return {
                "rows": res.data,
                "total": res.count
            };
        }

        function getOp(value, row, index) {
            var showDataUrls = [
                '/admin/agent/clublist/showDayd11'
            ];
            eval('rowobj=' + JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({id: rowobj['club_id']});
                var cStr = str.replace(/\"/g, "@");
                var urltype = op['url'].substring(op['url'].length - 7);
                var url = op['url'] + '/' + rowobj['club_id']
                if (op['url'].substring(op['url'].length - 4) == 'User')
                    if (op['url'].substring(op['url'].length - 12) == 'transferUser') //转移亲友圈
                        opList.push(String.format("<a href='javascript:;' onclick=\"transFerUser(\'{0}\', \'{1}\', \'{2}\', \'{4}\', \'{5}\');\" class=\"btn btn-sm btn-primary\" >{3}</a> ", url, op['method'], cStr, op['txt'], rowobj['club_id'], urltype));
                    else // 添加玩家、移除玩家 （亲友圈）
                        opList.push(String.format("<a href='javascript:;' onclick=\"AddRemovePlayer(\'{0}\', \'{1}\', \'{2}\', \'{4}\', \'{5}\');\" class=\"btn btn-sm btn-primary\" >{3}</a> ", url, op['method'], cStr, op['txt'], rowobj['club_id'], urltype));
                else //不使用弹出窗口打开页面
                if (op['url'].substring(op['url'].length - 7) == 'delClub') // 提升管理、踢出、解散亲友圈
                    opList.push(String.format("<a href='javascript:;' onclick=\"ChangeClubManager(\'{0}\', \'{1}\', \'{2}\', \'{4}\', \'{5}\');\" class=\"btn btn-danger btn-sm \" >{3}</a> ", url, op['method'], cStr, op['txt'], rowobj['club_id'], urltype));
                else if (op['url'].substring(op['url'].length - 5) == 'audit') // 亲友圈审批
                    opList.push(String.format("<a href='javascript:;' onclick=\"showClubAudit(\'{0}\', \'{1}\', \'{2}\', \'{4}\', \'{5}\');\"  class=\"btn btn-sm btn-primary\" >{3}</a> ", url, op['method'], cStr, op['txt'], rowobj['club_id'], urltype));
                else // 玩家出入记录、同台管理 （弹出新页面）
                    opList.push(String.format("<a href=\"#\" class=\"btn btn-primary btn-sm\" onclick=\"showClubRecord(\'{0}?club={4}\', \'{1}\', \'{2}\')\">{3}</a> ", op['url'], op['method'], rowobj['id'], op['txt'], rowobj['club_id']));
                //opList.push(String.format("<a href=\"{0}?club={1}\" class=\"btn btn-sm btn-primary\">{2}</a>",op['url'],rowobj['club_id'],op['txt']));
            }
            return opList.join('');
        }

        function responseError(status) {
            location.reload();
        }

    }

    function InitSubTable(index, row, $detail) {
        var parentAg = row.club_id;
        var table = String.format('<table table-bordered table-hover definewidth id="child_table{0}"></table>', parentAg)
        var cur_table = $detail.html(table).find('table');
        $(cur_table).bootstrapTable({
            url: '{{ info['serversUrl'] }}',
            method: 'get',
            contentType: "application/json",
            datatype: "json",
            //striped: true,
            toolbar: '#toolbar',
            pagination: true,
            pageSize: 10,
            pageList: [10, 25, 50, 100],
            clickToSelect: true,
            queryParams: getSearchP,
            striped: true,
            minimumCountColumns: 2,
            showFooter: true,
            showRefresh: true,
            //showExport: true,
            //showToggle: true,
            search: true,

            columns: [{
                field: 'number',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '序号',
            }, {
                field: 'user_id',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '用户ID',
            }, {
                field: 'account',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '用户账号',
            }, {
                field: 'nickname',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '昵称',
            }, {
                field: 'avatar_url',
                align: 'center',
                valign: 'middle',
                title: '头像',
                formatter: function (value, row, index) {
                    return '<img style="width: 20px;height: 20px;" src="' + value + '" class="img-rounded">';
                }
            }, {
                field: 'notes',
                align: 'center',
                valign: 'middle',
                title: '备注',
            }, {
                field: 'roomcard_day',
                align: 'center',
                valign: 'middle',
                title: '当日钻石变更',
                formatter: function (value, row, index) {
                    if (parseInt(value) > 0) {
                        infoStr = String.format("<span style=\"color:black;\">+{0}</span>", value);
                    }
                    else {
                        infoStr = String.format("<span style=\"color:black;\">{0}</span>", value);
                    }
                    return [infoStr].join('');
                }

            }, {
                field: 'roomcard_total',
                align: 'center',
                valign: 'middle',
                title: '总钻石数',
                formatter: function (value, row, index) {
                    if (value) {
                        return value
                    }
                    else {
                        return ''
                    }
                }
            }, {
                field: 'online',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '是否在线',
                formatter: function (value, row, index) {
                    if (value == 1) {
                        return "<span style='font-weight:bold'>&radic;</span>"
                    }
                    else {
                        return ''
                    }
                }

            }, {
                field: 'isManager',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '是否管理者',
                formatter: function (value, row, index) {
                    if (value == 1) {
                        return "<span style='font-weight:bold'>&radic;</span>"
                    }
                    else {
                        return ''
                    }
                }
            }, {
                field: 'time',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '登录时间',
            }, {
                field: 'op',
                title: '操作',
                align: 'center',
                valign: 'middle',
                sortable: true,
                formatter: getOpUser
            }],
            onExpandRow: function (index, row, $detail) {
                console.log(index, row, $detail);
                InitSubTable(index, row, $detail);
            }

        });

        function getOpUser(value, row, index) {
            var showDataUrls = [
                '/admin/agent/clublist/showDayd11'
            ];
            eval('rowobj=' + JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({id: rowobj['club_id']});
                var cStr = str.replace(/\"/g, "@");
                var urltype = op['url'].substring(op['url'].length - 10);
                var url = op['url'] + '/' + rowobj['club_id'] + '/' + rowobj['account']
                if (op['url'].substring(op['url'].length - 7) == 'Manager')
                    if (rowobj['isManager'] && urltype == 'delManager') //提升、移除管理者
                        opList.push(String.format("<a href='javascript:;' onclick=\"ChangeClubManager(\'{0}\', \'{1}\', \'{2}\', \'{4}\', \'{5}\');\" class=\"btn btn-danger btn-sm \" >{3}</a> ", url, op['method'], cStr, op['txt'], rowobj['club_id'], urltype));
                    else
                        opList.push(String.format("<a href='javascript:;' onclick=\"ChangeClubManager(\'{0}\', \'{1}\', \'{2}\', \'{4}\', \'{5}\');\" class=\"btn btn-sm btn-primary\" >{3}</a> ", url, op['method'], cStr, op['txt'], rowobj['club_id'], urltype));
                else //不使用弹出窗口打开页面
                    opList.push(String.format("<a href=\"{0}?club={1}\" class=\"btn btn-sm btn-primary\">{2}</a>", op['url'], rowobj['club_id'], op['txt']));
            }
            return opList.join('');
        }


        //定义列操作
        function getSearchP(p) {
            sendParameter = p;
            sendParameter['id'] = parentAg;
            return sendParameter;
        }


    }


</script>
%rebase admin_frame_base
