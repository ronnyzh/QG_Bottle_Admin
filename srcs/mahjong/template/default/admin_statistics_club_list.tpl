<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/js/echarts.min.js"></script>
<div class="block">
    %include admin_frame_header
    <div class="content">
        <table id="dataTable" class="table table-bordered table-hover"></table>
    </div>
</div>


<script>
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 6);
    $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
    $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));
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
            sortable: true,                     //是否启用排序
            sortOrder: "desc",                   //排序方式
            sortName: 'roomcards_day',
            pagination: true,
            pageSize: 10,
            pageList: [10, 25, 50, 100],
            queryParamsType: '',
            //sidePagination:"server",
            clickToSelect: true,
            //responseHandler:responseFun,
            //queryParams:getSearchP,
            columns: [
                [{
                    "title": "日期: " + "{{date}} " + " 详情列表",
                    "halign": "center",
                    "align": "center",
                    "colspan": 9
                }],
                [{
                    field: 'id',
                    title: '亲友圈ID',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }, {
                    field: 'club_agent',
                    title: '工会',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }, {
                    field: 'club_name',
                    title: '亲友圈名称',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }, {
                    field: 'club_user',
                    title: '亲友圈创建者',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }, {
                    field: 'club_nickname',
                    title: '创建者昵称',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }, {
                    field: 'roomcards_day',
                    title: '钻石消耗',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    footerFormatter: function (values) {
                        var count = 0;
                        for (var val in values)
                            count += parseInt(values[val].roomcards_day)

                        return colorFormat(count)
                    }
                }, {
                    field: 'club_member',
                    title: '亲友圈人数',
                    align: 'center',
                    valign: 'middle',
                    sortable: true

                }]],
            //注册加载子表的事件。注意下这里的三个参数！
            onExpandRow: function (index, row, $detail) {
                console.log(index, row, $detail);
                InitSubTable(index, row, $detail);
            }
        });

        function colorFormat(value, color) {  //颜色格式化
            fontColor = color || '#1E9FFF'; //#1E9FFF
            statusstr = String.format('<span style="color:{0}">{1}</span>', fontColor, value);

            return [statusstr].join('');
        }

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

        function responseError(status) {
            location.reload();
        }
    }

    function InitSubTable(index, row, $detail) {
        var parentAg = row.id;
        var cur_table = $detail.html('<table table-bordered table-hover definewidth></table>').find('table');
        $(cur_table).bootstrapTable({
            url: '{{ info['serversUrl'] }}',
            method: 'get',
            contentType: "application/json",
            datatype: "json",
            //striped: true,
            toolbar: '#toolbar',
            pagination: true,
            pageSize: 15,
            pageList: [10, 25, 50, 100],
            clickToSelect: true,
            queryParams: getSearchP,
            striped: true,
            minimumCountColumns: 2,
            showFooter: true,

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
                field: 'account_type',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '用户类型',
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
                field: 'creator',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '是否创建者',
                formatter: function (value, row, index) {
                    if (value == 1) {
                        return "<span style='font-weight:bold'>&radic;</span>"
                    }
                    else {
                        return ""
                    }
                }
            }, {
                field: 'time',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '登录时间',
            }],
            //注册加载子表的事件。注意下这里的三个参数！
            onExpandRow: function (index, row, $detail) {
                console.log(index, row, $detail);
                InitSubTable(index, row, $detail);
            }

        });

        //定义列操作
        function getSearchP(p) {
            endDate = $("#pick-date-end").val();

            sendParameter = p;
            sendParameter['id'] = parentAg;
            sendParameter['endDate'] = endDate;
            return sendParameter;
        }
    }
</script>
%rebase admin_frame_base
