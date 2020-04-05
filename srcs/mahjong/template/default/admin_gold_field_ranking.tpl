<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/js/echarts.min.js"></script>
<div class="cl-mcont">
    <div class="block">
        <div class="header">
            <h3>
                %if info.get('title',None):
                {{ info['title']}}
                %end
            </h3>
        </div>
        <div class="content">
            <div class="table-toolbar" style="float:left;width:100%;position:relative;top:3.2em">
                <div class='col-sm-12' style='margin-left:1em;'>
                    <div style='float:left;margin-left:1em;' class="input-group date datetime col-md-1 col-xs-1"
                         data-min-view="2" data-date-format="yyyy-mm-dd">
                        <input class="form-control" style='width:140px;height:28px;' id='pick-date-end' name="enddate"
                               size="12" type="text" value="{{ lang.INPUT_LABEL_END_DATE_TXT }}" readonly>
                        <span class="input-group-addon btn btn-primary pickdate-btn"><span
                                class="pickdate glyphicon pickdate-btn glyphicon-th"></span></span>
                    </div>
                    <div>
                        <button id="btn_query" class='btn btn-primary btn-sm btn-xs'><i class='fa fa-search'></i>{{ lang.INPUT_LABEL_QUERY }}</button>
                        <button id="btn_lastMonthday" class='btn btn-sm btn-xs'>{{ lang.INPUT_LABEL_PREV_MONTH }}</button>
                        <button id="btn_lastWeekday" class='btn btn-sm btn-xs '>{{ lang.INPUT_LABEL_PREV_WEEK }}</button>
                        <button id="btn_bigyesterday" class='btn btn-sm btn-xs'>三天前</button>
                        <button id="btn_yesterday" class='btn btn-sm btn-xs'>{{ lang.INPUT_LABEL_PREV_DAY }}</button>
                        <button id="btn_today" class='btn btn-sm btn-xs'>{{ lang.INPUT_LABEL_CURR_DAY }}</button>
                        <button id="btn_onday" class='btn btn-sm btn-xs'>上一天</button>
                        <button id="btn_upday" class='btn btn-sm btn-xs'>下一天</button>
                        <div class='clearfix'></div>
                    </div>
                </div>
            </div>
            <table id="dataTable" class="table table-bordered table-hover"></table>
        </div>
    </div>
</div>

<script>
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 6);
    $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
    $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));
</script>


<script type="text/javascript">
    /**------------------------------------------------
     *  代理操作日志
     -------------------------------------------------
     */
    function initTable() {
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        $("#dataTable").bootstrapTable({
          url: '{{info["listUrl"]}}',
          method: 'get',
                pagination: true,
                pageSize: 10,
                search: true,
                showRefresh: true,
                showExport: true,
                detailView: true,//父子表
                exportTypes:['excel', 'csv', 'pdf', 'json'],
                pageList: [15, 25, 100],
                responseHandler:responseFunc,
                queryParams:getSearchP,

            columns: [{
                field: 'number',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '排名'
            },{
            field: 'create_time',
                title: '时间',
                align: 'center',
                valign: 'middle',
                sortable: true
            }, {
                field: 'user_id',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '用户编号'
            }, {
                field: 'account',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '用户账号'
            }, {
                field: 'balance',
                title: '日输赢总金额',
                align: 'center',
                valign: 'middle',
                sortable: true,

            }, {
                field: 'after_balance',
                title: '日输赢后总金额',
                align: 'center',
                valign: 'middle',
                sortable: true,
            },{
                field: 'action',
                title: '操作',
                align: 'center',
                valign: 'middle',
                //formatter:getOp
            }],

                //注册加载子表的事件。注意下这里的三个参数！
                onExpandRow: function (index, row, $detail) {
                    console.log(index,row,$detail);
                    InitSubTable(index, row, $detail);
                }
      });
    function getOp(value,row,index){
            var showDataUrls = [
                '/admin/statistics/active/showDay11'
            ];
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({id : rowobj['account']});
                var cStr = str.replace(/\"/g, "@");
                //<a href=\"{0}?islist=1&pageSize=10&pageNumber=5&searchText=258&sortOrder=asc&startDate=2018-01-01&endDate=2018-08-06\">{1}</a>"
                opList.push(String.format("<a href=\"{0}?islist=1&pageSize=10&pageNumber=1&sortOrder=asc&startDate=2018-01-01&endDate=2018-08-06\" class=\"btn btn-sm btn-primary\">{1}</a>", op['url'],op['txt']));
                //opList.push(String.format("<a href=\"{0}?day={1}\" class=\"btn btn-sm btn-primary\">{2}</a>",op['url'],rowobj['user_id'],op['txt']));
            }
            return opList.join('');
        }


    function getSearchP(p){
          startDate = $("#pick-date-start").val();
          endDate   = $("#pick-date-end").val();

          sendParameter = p;

          sendParameter['startDate'] = startDate;
          sendParameter['endDate']  = endDate;

          return sendParameter;
    }


        function responseFunc(res){
            data = res.data;
            count= res.count;
            //实时刷

            return data;
        }
 }
 function InitSubTable(index, row, $detail) {
        var parentAg = row.user_id;
        var endDate = $("#pick-date-end").val();
        var cur_table = $detail.html('<table table-bordered table-hover definewidth></table>').find('table');
        $(cur_table).bootstrapTable({
                url: '{{ info['serversUrl'] }}',
                method: 'get',
                contentType: "application/json",
                datatype: "json",
                striped: true,
                toolbar:'#toolbar',
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
                title: '用户编号'
            }, {
                field: 'trans_id',
                align: 'center',
                valign: 'middle',
                sortable: true,
                title: '唯一标识'
            }, {
                field: 'game_id',
                align: 'center',
                valign: 'middle',
                sortable: true,
                title: '游戏ID'
            }, {
                field: 'gameName',
                align: 'center',
                valign: 'middle',
                sortable: true,
                title: '游戏名称'
            }, {
                field: 'pre_balance',
                title: '输赢前金额',
                align: 'center',
                valign: 'middle',
                sortable: true,

            }, {
                field: 'balance',
                title: '输赢金额',
                align: 'center',
                valign: 'middle',
                sortable: true,

            }, {
                field: 'after_balance',
                title: '输赢后',
                align: 'center',
                valign: 'middle',
                sortable: true,

            }, {
                field: 'banker',
                align: 'center',
                valign: 'middle',
                sortable: true,
                title: '庄家/闲家',
                titleTooltip: '表中对应结构：\n1: 庄家 \n0: 闲家 ',
            }, {
                field: 'room_id',
                title: '房间号',
                align: 'center',
                valign: 'middle',
                sortable: true
            }, {
                field: 'playid',
                align: 'center',
                valign: 'middle',
                sortable: true,
                title: '场次',
                titleTooltip: '表中对应结构：\n0: 新手场 \n1: 初级场 \n2: 中级场 \n3: 高级场 \n4: 土豪场 \n5: 至尊场',
            }, {
                field: 'chair',
                title: '座位号',
                align: 'center',
                valign: 'middle',
                sortable: true,
            }, {
                field: 'status',
                title: '状态',
                align: 'center',
                valign: 'middle',
                sortable: true,
                titleTooltip: '表中对应结构：\n-1: 异常 \n1: 正常 ',
            }, {
                field: 'create_time',
                title: '创建时间',
                align: 'center',
                valign: 'middle',
                sortable: true
            }],
                //注册加载子表的事件。注意下这里的三个参数！
                onExpandRow: function (index, row, $detail) {
                    console.log(index,row,$detail);
                    InitSubTable(index, row, $detail);
                }

        });
        //定义列操作
        function getSearchP(p){
              sendParameter = p;
              sendParameter['id'] = parentAg;
              sendParameter['endDate'] = endDate;
              return sendParameter;
        }
}


</script>
%rebase admin_frame_base