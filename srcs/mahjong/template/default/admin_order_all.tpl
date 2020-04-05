<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<div class="block">
          %include admin_frame_header
          <div class="content">
             %include original_search_bar
              <table id="dataTable" class="table table-bordered table-hover"></table>
          </div>
</div>
<script type="text/javascript">

  /**------------------------------------------------
    *  微信前端
    -------------------------------------------------
  */
  function initTable() {
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        $("#dataTable").bootstrapTable({
            url: "{{ info['tableUrl'] }}",
            method: 'get',
            pagination: true,
            pageSize: 10,
            search: true,
            showRefresh: true,
            showExport: true,
            showFooter: true,
            exportTypes: ['excel', 'csv', 'pdf', 'json'],
            pageList: [10, 25, 50, 100],
            rowStyle:rowStyle,
            responseHandler: responseFun,
            queryParams: getSearchP,
            columns: [
                [{
                    "title": "搜索日期:" + startDate + "至" + endDate,
                    "halign": "center",
                    "align": "center",
                    "colspan": 30,
                }],
                [{
                    "halign": "center",
                    "align": "center",
                    "class": 'totalMoney',
                    "colspan": 30,
                }],
                [{
                    field: 'orderNo',
                    title: '订单号',
                    valign: "middle",
                    align: "center",
                    colspan: 1,
                    rowspan: 2,
                },{
                    field: 'orderType',
                    title: '订单类型',
                    valign: "middle",
                    align: "center",
                    colspan: 1,
                    rowspan: 2,
                    formatter:function(value,row,index){
                        if (value == '商城订单') {
                            statusstr = '<span class="label label-warning">商城订单</span>';
                        } else {
                            statusstr = '<span class="label label-info">代理订单</span>';
                        }

                        return [
                            statusstr
                        ].join('');
                    }
                }, {
                    field: 'startTime',
                    title: '下单时间',
                    align: 'center',
                    valign: 'middle',
                    colspan: 1,
                    rowspan: 2,
                }, {
                    field: 'time',
                    title: '支付时间',
                    align: 'center',
                    valign: 'middle',
                    colspan: 1,
                    rowspan: 2,
                    formatter:function(value,row,index){
                        if (value == undefined) {
                            tdStr = '<span style="text-align: center; vertical-align: middle;">\\</span>';
                        }else{
                            tdStr = '<span style="text-align: center; vertical-align: middle;">' + value + '</span>';
                        }
                        return [tdStr].join('');
                    }
                }, {
                    field: 'endTime',
                    title: '成交时间',
                    align: 'center',
                    valign: 'middle',
                    colspan: 1,
                    rowspan: 2,
                }, {
                    field: 'type',
                    title: '订单状态',
                    valign: "middle",
                    align: "center",
                    colspan: 1,
                    rowspan: 2,
                    formatter: status,

                }, {
                    field: 'op',
                    title: '更多详情',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    colspan: 1,
                    rowspan: 2,
                    formatter: details,
                }, {
                    title: "代理",
                    valign: "middle",
                    align: "center",
                    colspan: 3,
                    rowspan: 1,
                }, {
                    title: "商城",
                    valign: "middle",
                    align: "center",
                    colspan: 7,
                    rowspan: 1,

                }],
                [{
                    field: 'cardNums',
                    title: '售钻数',
                    valign: "middle",
                    align: "center",
                    formatter:function(value,row,index){
                        if (value == undefined) {
                            tdStr = '<span style="text-align: center; vertical-align: middle;">\\</span>';
                        }else{
                            tdStr = '<span style="text-align: center; vertical-align: middle;">' + value + '</span>';
                        }
                        return [tdStr].join('');
                    }
                }, {
                    field: 'saleAccount',
                    title: '卖钻方',
                    valign: "middle",
                    align: "center",
                    formatter:function(value,row,index){
                        if (value == undefined) {
                            tdStr = '<span style="text-align: center; vertical-align: middle;">\\</span>';
                        }else{
                            tdStr = '<span style="text-align: center; vertical-align: middle;">' + value + '</span>';
                        }
                        return [tdStr].join('');
                    }
                }, {
                    field: 'applyAccount',
                    title: '买钻方',
                    valign: "middle",
                    align: "center",
                    formatter:function(value,row,index){
                        if (value == undefined) {
                            tdStr = '<span style="text-align: center; vertical-align: middle;">\\</span>';
                        }else{
                            tdStr = '<span style="text-align: center; vertical-align: middle;">' + value + '</span>';
                        }
                        return [tdStr].join('');
                    }

                }, {
                    field: 'memberId',
                    title: '用户ID',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    formatter:function(value,row,index){
                        if (value == undefined) {
                            tdStr = '<span style="text-align: center; vertical-align: middle;">\\</span>';
                        }else{
                            tdStr = '<span style="text-align: center; vertical-align: middle;">' + value + '</span>';
                        }
                        return [tdStr].join('');
                    }
                }, {
                    field: 'account',
                    title: '用户账号',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    formatter:function(value,row,index){
                        if (value == undefined) {
                            tdStr = '<span style="text-align: center; vertical-align: middle;">\\</span>';
                        }else{
                            tdStr = '<span style="text-align: center; vertical-align: middle;">' + value + '</span>';
                        }
                        return [tdStr].join('');
                    }
                }, {
                    field: 'groupId',
                    title: '充值的工会ID',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    formatter:function(value,row,index){
                        if (value == undefined) {
                            if (row['orderType'] == '商城订单'){
                                tdStr = '<span style="text-align: center; vertical-align: middle;">-</span>';
                            }else{
                                tdStr = '<span style="text-align: center; vertical-align: middle;">\\</span>';
                            }
                        }else{
                            tdStr = '<span style="text-align: center; vertical-align: middle;">' + value + '</span>';
                        }
                        return [tdStr].join('');
                    }
                }, {
                    field: 'parentId',
                    title: '代理',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    formatter:function(value,row,index){
                        if (value == undefined) {
                            if (row['orderType'] == '商城订单'){
                                tdStr = '<span style="text-align: center; vertical-align: middle;">-</span>';
                            }else{
                                tdStr = '<span style="text-align: center; vertical-align: middle;">\\</span>';
                            }
                        }else{
                            tdStr = '<span style="text-align: center; vertical-align: middle;">' + value + '</span>';
                        }
                        return [tdStr].join('');
                    }
                }, {
                    field: 'roomCards',
                    title: '购买钻石/金币数',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    formatter:function(value,row,index){
                        if (value == undefined) {
                            if (row['orderType'] == '商城订单'){
                                tdStr = '<span style="text-align: center; vertical-align: middle;">-</span>';
                            }else{
                                tdStr = '<span style="text-align: center; vertical-align: middle;">\\</span>';
                            }
                        }else{
                            tdStr = '<span style="text-align: center; vertical-align: middle;">' + value + '</span>';
                        }
                        return [tdStr].join('');
                    }
                }, {
                    field: 'money',
                    title: '总价',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    formatter:function(value,row,index){
                        if (value == undefined) {
                            if (row['orderType'] == '商城订单'){
                                tdStr = '<span style="text-align: center; vertical-align: middle;">-</span>';
                            }else{
                                tdStr = '<span style="text-align: center; vertical-align: middle;">\\</span>';
                            }
                        }else{
                            tdStr = '<span style="text-align: center; vertical-align: middle;">' + value + '</span>';
                        }
                        return [tdStr].join('');
                    }
                }, {
                    field: 'name',
                    title: '商品名称',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    formatter:function(value,row,index){
                        if (value == undefined) {
                            if (row['orderType'] == '商城订单'){
                                tdStr = '<span style="text-align: center; vertical-align: middle;">-</span>';
                            }else{
                                tdStr = '<span style="text-align: center; vertical-align: middle;">\\</span>';
                            }
                        }else{
                            tdStr = '<span style="text-align: center; vertical-align: middle;">' + value + '</span>';
                        }
                        return [tdStr].join('');
                    }
                }],

            ],

            //注册加载子表的事件。注意下这里的三个参数！
            onExpandRow: function (index, row, $detail) {
                console.log(index, row, $detail);
                InitSubTable(index, row, $detail);
            },

        });

        function rowStyle(row, index) {
            var classes = ['active', 'success', 'info', 'warning', 'danger'];
            if (row.time) {
                strclass = 'danger';//还有一个active
            }
            else {
                strclass = 'info';
            }
            return {classes: strclass}
        };

        function getSearchP(p) {
            startDate = $("#pick-date-start").val();
            endDate = $("#pick-date-end").val();

            sendParameter = p;

            sendParameter['startDate'] = startDate;
            sendParameter['endDate'] = endDate;

            return sendParameter;
        }

        function getOp(value, row, index) {
            eval('rowobj=' + JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({orderNo: rowobj["orderNo"]});
                var cStr = str.replace(/\"/g, "@");
                if (rowobj['status'] == '1')
                    continue;
                var contentUrl = op['url'];
                opList.push(String.format("<a href=\"#\" class=\"btn btn-primary btn-sm\" onclick=\"comfirmOrderDialog(\'{0}\',\'{1}\',\'{2}\')\"><i class=\"glyphicon glyphicon-edit\"> {3} </i></a> ", contentUrl, op['method'], cStr, op['txt']));
            }
            return opList.join('');
        }

        //获得返回的json 数据
        function responseFun(res) {
            var count = res.orderCount
                , moneyCount = res.moneyCount
                , successMoney = res.successMoney
                , pendingMoney = res.pendingMoney;

            top_show_str = ''//String.format("订单总金额:{0}&nbsp;交易成功金额:{1}&nbsp;交易挂起金额:{2}", moneyCount, successMoney, pendingMoney);

            $('.totalMoney').html(top_show_str)

            return {"data": res.data, "total": res.orderCount};
        }

        function status(value, row, index) {
            eval('var rowobj=' + JSON.stringify(row))
            var statusstr = '';
            if (rowobj['type'] == 'pending') {
                statusstr = '<span class="label label-danger">交易挂起</span>';
            } else {
                statusstr = '<span class="label label-success">交易成功</span>';
            }

            if (rowobj['status'] == '0') {
                statusstr = '<span class="label label-danger">卖钻方未确认</span>';
            } else if (rowobj['status'] == '1') {
                statusstr = '<span class="label label-success">卖钻方已确认</span>';
            }

            return [
                statusstr
            ].join('');
        }

        function details(value, row, index) {
            eval('rowobj=' + JSON.stringify(row))
            var opList = []
            opList.push(String.format("<a href=\"/admin/order/details/{0}\" class=\"btn btn-primary btn-sm\" >{1}</a> ", rowobj["orderNo"], '查看'));
            return opList.join('');
        }
    }
</script>
%rebase admin_frame_base
