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
                        <input class="form-control" size="12" type="text" style='width:140px;height:28px;'
                               id='pick-date-start' name="startdate" value="{{ lang.INPUT_LABEL_START_DATE_TXT }}"
                               readonly>
                        <span class="input-group-addon btn btn-primary pickdate-btn"><span
                                class="glyphicon pickdate-btn pickdate glyphicon-th"></span>
                    </div>

                    <div style='float:left;margin-left:1em;' class="input-group date datetime col-md-1 col-xs-1"
                         data-min-view="2" data-date-format="yyyy-mm-dd">
                        <input class="form-control" style='width:140px;height:28px;' id='pick-date-end' name="enddate"
                               size="12" type="text" value="{{ lang.INPUT_LABEL_END_DATE_TXT }}" readonly>
                        <span class="input-group-addon btn btn-primary pickdate-btn"><span
                                class="pickdate glyphicon pickdate-btn glyphicon-th"></span></span>
                    </div>
                    <div>
                        <button id="btn_query" class='btn btn-primary btn-sm btn-xs'><i class='fa fa-search'></i>{{ lang.INPUT_LABEL_QUERY }}</button>
                        <button id="btn_lastMonth" class='btn btn-sm btn-xs'>{{ lang.INPUT_LABEL_PREV_MONTH }}</button>
                        <button id="btn_thisMonth" class='btn btn-sm btn-xs '>{{ lang.INPUT_LABEL_CURR_MONTH }}</button>
                        <button id="btn_lastWeek" class='btn btn-sm btn-xs '>{{ lang.INPUT_LABEL_PREV_WEEK }}</button>
                        <button id="btn_thisWeek" class='btn btn-sm btn-xs'>{{ lang.INPUT_LABEL_CURR_WEEK }}</button>
                        <button id="btn_yesterday" class='btn btn-sm btn-xs'>{{ lang.INPUT_LABEL_PREV_DAY }}</button>
                        <button id="btn_today" class='btn btn-sm btn-xs'>{{ lang.INPUT_LABEL_CURR_DAY }}</button>
                        <button id="btn_syday" class='btn btn-sm btn-xs'>所有</button>
                        <div class='clearfix'></div>
                    </div>
                </div>
            </div>
            <table id="dataTable" class="table table-bordered table-hover"></table>
        </div>
    </div>
</div>


<div class='rows' style='margin-bottom:10px;'>
    <div class='col-md-12'>
        <div class="panel panel-info">
        <div class="panel-heading">
                <span class="panel-title" id="txt">数据统计（默认最近一周）</span>
            </div>
            <div class="panel-body">
                <table id="table2" class="table table-bordered table-hover"></table>
            </div>
               <div class="panel-heading">
                <h3 class="panel-title">数据统计（总数据）</h3>
            </div>
            <div class="panel-body">
                <table id="table1" class="table table-bordered table-hover"></table>
            </div>
            <div class="panel-heading">
                <h3 class="panel-title">数据统计（每天总数据）</h3>
            </div>
            <div class="panel-body">
                <table id="table3" class="table table-bordered table-hover"></table>
            </div>
        </div>
    </div>
</div>

<div class='rows' style='margin-bottom:10px;'>
    <div class='col-md-12'>
        <div class="panel panel-info">

            <div class="panel-heading">
               <span class="panel-title" id="txt1">数据统计（默认最近一周）</span>
            </div>
            <div>
                <span>用户编号：<span>
                <input type="text" style='width:10%' id="gameid" name="gameid"  >
                <span>时间：<span>
                <select style='width:10%;height:26px;' id="gameType" name="gameType" >
                    <option value="%Y-%m-%d ">  日 </option>
                    <option value="%Y-%m "> 月 </option>
                    <option value="%Y "> 年</option>
                    <option value="%Y-%m-%d %H">  时 </option>
                    <option value="%Y-%m-%d %H:%i"> 分 </option>
                </select>
                <button value="1" name="button1"  onclick="test()">查询</button>
            </div>
            <div class="panel-body">
                <div id="main" style="width:100%;height:400px;"></div>
            </div>
        </div>
    </div>
</div>

<script>
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 6);
    $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
    $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));
    var select = document.getElementById("gameType");
    var gameid = document.getElementById('gameid');
</script>

<script>
    function datalook(){
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        obj_look = document.getElementById("txt");
        obj_look.innerHTML = "数据统计：" + startDate + ' 到 '+ endDate;
        obj_look1 = document.getElementById("txt1");
        obj_look1.innerHTML = "图表数据统计：" + startDate + ' 到 '+ endDate;
    }
    function test(){
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        gametype = select.value;
        gameid = $("#gameid").val();
        loadTwoLine();
    }
</script>

<script type="text/javascript">
    /**------------------------------------------------
     *  代理操作日志
     -------------------------------------------------
     */
    function initTable() {
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        gametype = select.value;
        gameid = $("#gameid").val();
        $("#dataTable").bootstrapTable({
          url: '{{info["listUrl"]}}',
          method: 'get',
          contentType: "application/json",
          datatype: "json",
          striped: true,
          minimumCountColumns: 2,
          search: true,
          toolbar:'#toolbar',
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
          queryParamsType:'',
          sidePagination:"server",
          clickToSelect: true,
          responseHandler:responseFun,
          queryParams:getSearchP,

            columns: [{
                field: 'number',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '序号'
            }, {
                field: 'user_id',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '用户编号'
            }, {
                field: 'is_robot',
                title: '是否机器人',
                align: 'center',
                valign: 'middle',
                sortable: true,
                titleTooltip: '表中对应结构：\n1：机器人 \n0：用户',
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
                footerFormatter: function (value) {
                    var count = 0;
                    var user = 0;
                    var rebot = 0;
                    for (var i in value) {
                        count += value[i].pre_balance;
                        if (value[i].is_robot == '用户') {
                            user += value[i].pre_balance;
                        }
                        else{
                            rebot += value[i].pre_balance;
                        }
                    }
                    var counttxt  = '输赢前金额总合计：' + count
                    var usertxt  = '用户输赢前金额总合计：' + user
                    var rebottxt = '机器人输赢前金额总合计：' + rebot
                    return counttxt +  '<br>' + usertxt + '<br>' +rebottxt
                }
            }, {
                field: 'balance',
                title: '输赢金额',
                align: 'center',
                valign: 'middle',
                sortable: true,
                footerFormatter: function (value) {
                    var count = 0;
                    var user = 0;
                    var rebot = 0;
                    for (var i in value) {
                        count += value[i].balance;
                        if (value[i].is_robot == '用户') {
                            user += value[i].balance;
                        }
                        else{
                            rebot += value[i].balance;
                        }
                    }
                    var counttxt  = '输赢金额总合计：：' + count
                    var usertxt  = '用户输赢金额总合计：：' + user
                    var rebottxt = '机器人输赢金额总合计：：' + rebot
                    return counttxt +  '<br>' + usertxt + '<br>' +rebottxt
                }
            }, {
                field: 'betting_balance',
                title: '投注金额',
                align: 'center',
                valign: 'middle',
                sortable: true,
                footerFormatter: function (value) {
                    var count = 0;
                    var user = 0;
                    var rebot = 0;
                    for (var i in value) {
                        count += value[i].betting_balance;
                        if (value[i].is_robot == '用户') {
                            user += value[i].betting_balance;
                        }
                        else{
                            rebot += value[i].betting_balance;
                        }
                    }
                    var counttxt  = '投注金额总合计：：' + count
                    var usertxt  = '用户投注金额总合计：：' + user
                    var rebottxt = '机器人投注金额总合计：：' + rebot
                    return counttxt +  '<br>' + usertxt + '<br>' +rebottxt
                }
            }, {
                field: 'after_balance',
                title: '输赢后',
                align: 'center',
                valign: 'middle',
                sortable: true,
                footerFormatter: function (value) {
                    var count = 0;
                    var user = 0;
                    var rebot = 0;
                    for (var i in value) {
                        count += value[i].after_balance;
                        if (value[i].is_robot == '用户') {
                            user += value[i].after_balance;
                        }
                        else{
                            rebot += value[i].after_balance;
                        }
                    }
                    var counttxt  = '输赢后总合计：：' + count
                    var usertxt  = '用户输赢后总合计：：' + user
                    var rebottxt = '机器人输赢后总合计：：' + rebot
                    return counttxt +  '<br>' + usertxt + '<br>' +rebottxt
                }
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
                field: 'tiles',
                title: '手牌信息',
                align: 'center',
                valign: 'middle',
                sortable: true
            }, {
                field: 'reason',
                title: '说明',
                align: 'center',
                valign: 'middle',
                sortable: true


            }, {
                field: 'create_time',
                title: '创建时间',
                align: 'center',
                valign: 'middle',
                sortable: true
            }, {
                field: 'update_time',
                title: '更新时间',
                align: 'center',
                valign: 'middle',
                sortable: true
            }, {
                field: 'is_deleted',
                title: '是否删除',
                align: 'center',
                valign: 'middle',
                sortable: true
            }],

            //注册加载子表的事件。注意下这里的三个参数！
            onExpandRow: function (index, row, $detail) {
                console.log(index, row, $detail);
                InitSubTable(index, row, $detail);
            }
        });


       function getSearchP(p) {
            startDate = $("#pick-date-start").val();
            endDate = $("#pick-date-end").val();
            gametype = select.value;
            var searchId = $("#searchId").val();
            var gameid = $("#gameid").val();

            sendParameter = p;
            sendParameter['searchId'] = searchId;
            sendParameter['startDate'] = startDate;
            sendParameter['endDate'] = endDate;
            sendParameter['gametype'] = gametype;
            sendParameter['gameid'] = gameid;

            return sendParameter;
        }

      function responseFun(res){
          count= res.total;
          //实时刷
          //$('.count').text(String.format("会员总人数:{0}",count));
          pageNumber = parseInt(res.pageNumber);
          return {"rows": res.data,
                  "total": res.count
          };
      }

      function responseError(status) {
          location.reload();
      }

      $("#table2").bootstrapTable('refresh');
      datalook();
      loadTwoLine();

    }

    sumTable();
    sumDayTable();
    dailyTable();


    function sumTable() {
        $("#table1").bootstrapTable({
          url: '{{ info['sumListUrl'] }}',
          method: 'get',
          contentType: "application/json",
          datatype: "json",
          striped: true,
          minimumCountColumns: 2,
          toolbar:'#toolbar',
          cardView: false,
          //pagination: true,
          pageSize: 10,
          pageList: [15, 50, 100],
          queryParamsType:'',
          sidePagination:"server",
          clickToSelect: true,
          responseHandler:responseFun,
          queryParams:getSearchP,

            columns: [{
                field: 'type',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '用户类型',
            },{
                field: 'pre_balance',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '输赢前总金额',
            },{
                field: 'balance',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '输赢总金额',
            },{
                field: 'after_balance',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '输赢后总金额',
            },],

            //注册加载子表的事件。注意下这里的三个参数！
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

      function responseFun(res){
          count= res.total;
          pageNumber = parseInt(res.pageNumber);
          return {"rows": res.data,
                  "total": res.count
          };
      }

      function responseError(status) {
          location.reload();
      }
    }

    function sumDayTable() {
        $("#table2").bootstrapTable({
          url: '{{info["dayListUrl"]}}',
          method: 'get',
          contentType: "application/json",
          datatype: "json",
          striped: true,
          minimumCountColumns: 2,
          toolbar:'#toolbar',
          cardView: false,
          //pagination: true,
          pageSize: 10,
          pageList: [15, 50, 100],
          queryParamsType:'',
          sidePagination:"server",
          clickToSelect: true,
          responseHandler:responseFun,
          queryParams:getSearchP,

            columns: [{
                field: 'type',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '用户类型',
            },{
                field: 'pre_balance',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '输赢前总金额',
            },{
                field: 'balance',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '输赢总金额',
            },{
                field: 'after_balance',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '输赢后总金额',
            },],

            //注册加载子表的事件。注意下这里的三个参数！
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

      function responseFun(res){
          count= res.total;
          pageNumber = parseInt(res.pageNumber);
          return {"rows": res.data,
                  "total": res.count
          };
      }

      function responseError(status) {
          location.reload();
      }
    }

    function dailyTable() {
        $("#table3").bootstrapTable({
          url: '{{ info['dailyListUrl'] }}',
          method: 'get',
                pagination: true,
                pageSize: 10,
                search: true,
                showRefresh: true,
                showExport: true,
                exportTypes:['excel', 'csv', 'pdf', 'json'],
                pageList: [15, 25, 100],
                responseHandler:responseFun,
                queryParams:getSearchP,

            columns: [{
                field: 'datetime',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '日期',
            },{
                field: 'pay_ment',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '用户输赢金额',
            }],

                //注册加载子表的事件。注意下这里的三个参数！
                onExpandRow: function (index, row, $detail) {
                    console.log(index,row,$detail);
                    InitSubTable(index, row, $detail);
                }
      });


    function getSearchP(p){
          startDate = $("#pick-date-start").val();
          endDate   = $("#pick-date-end").val();

          sendParameter = p;

          sendParameter['startDate'] = startDate;
          sendParameter['endDate']  = endDate;

          return sendParameter;
    }


    //获得返回的json 数据
    function responseFun(res){
        return res
    }
 }

    function InitSubTable(index, row, $detail) {
        var parentAg = row.trans_id;
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
                field: 'is_robot',
                title: '是否机器人',
                align: 'center',
                valign: 'middle',
                sortable: true,
                titleTooltip: '表中对应结构：\n1：机器人 \n0：用户',
                cellStyle:function(value,row,index){
                    if (value=="用户"){
                        return {css:{"background-color":"#87CEFF"}}
                            }else{
                        	        return {css:{"background-color":"#FF82AB"}}
                        	    }
                        	}
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
                field: 'pre_balance',
                title: '输赢前金额',
                align: 'center',
                valign: 'middle',
                sortable: true,
                footerFormatter: function (value) {
                    var count = 0;
                    var user = 0;
                    var rebot = 0;
                    for (var i in value) {
                        count += value[i].pre_balance;
                        if (value[i].is_robot == '用户') {
                            user += value[i].pre_balance;
                        }
                        else{
                            rebot += value[i].pre_balance;
                        }
                    }
                    var counttxt  = '输赢前金额总合计：' + count
                    var usertxt  = '用户输赢前金额总合计：' + user
                    var rebottxt = '机器人输赢前金额总合计：' + rebot
                    return counttxt +  '<br>' + usertxt + '<br>' +rebottxt
                }
            }, {
                field: 'balance',
                title: '输赢金额',
                align: 'center',
                valign: 'middle',
                sortable: true,
                footerFormatter: function (value) {
                    var count = 0;
                    var user = 0;
                    var rebot = 0;
                    for (var i in value) {
                        count += value[i].balance;
                        if (value[i].is_robot == '用户') {
                            user += value[i].balance;
                        }
                        else{
                            rebot += value[i].balance;
                        }
                    }
                    var counttxt  = '输赢金额总合计：：' + count
                    var usertxt  = '用户输赢金额总合计：：' + user
                    var rebottxt = '机器人输赢金额总合计：：' + rebot
                    return counttxt +  '<br>' + usertxt + '<br>' +rebottxt
                }
            }, {
                field: 'betting_balance',
                title: '投注金额',
                align: 'center',
                valign: 'middle',
                sortable: true,
                footerFormatter: function (value) {
                    var count = 0;
                    var user = 0;
                    var rebot = 0;
                    for (var i in value) {
                        count += value[i].betting_balance;
                        if (value[i].is_robot == '用户') {
                            user += value[i].betting_balance;
                        }
                        else{
                            rebot += value[i].betting_balance;
                        }
                    }
                    var counttxt  = '投注金额总合计：：' + count
                    var usertxt  = '用户投注金额总合计：：' + user
                    var rebottxt = '机器人投注金额总合计：：' + rebot
                    return counttxt +  '<br>' + usertxt + '<br>' +rebottxt
                }
            }, {
                field: 'after_balance',
                title: '输赢后',
                align: 'center',
                valign: 'middle',
                sortable: true,
                footerFormatter: function (value) {
                    var count = 0;
                    var user = 0;
                    var rebot = 0;
                    for (var i in value) {
                        count += value[i].after_balance;
                        if (value[i].is_robot == '用户') {
                            user += value[i].after_balance;
                        }
                        else{
                            rebot += value[i].after_balance;
                        }
                    }
                    var counttxt  = '输赢后总合计：：' + count
                    var usertxt  = '用户输赢后总合计：：' + user
                    var rebottxt = '机器人输赢后总合计：：' + rebot
                    return counttxt +  '<br>' + usertxt + '<br>' +rebottxt
                }
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
                field: 'tiles',
                title: '手牌信息',
                align: 'center',
                valign: 'middle',
                sortable: true
            }, {
                field: 'reason',
                title: '说明',
                align: 'center',
                valign: 'middle',
                sortable: true
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
              return sendParameter;
        }
}
        function loadTwoLine() {
        var myChart = echarts.init(document.getElementById('main'));
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        myChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                },
            },
            toolbox: {
                show: true,
                feature: {
                    mark: {show: true},
                    dataView: {show: true, readOnly: false},
                    magicType: {show: true, type: ['line', 'bar', 'tiled']},
                    restore: {show: true},
                    saveAsImage: {show: true}
                }
            },
            legend: {
                data: ['输赢前总金额', '用户输赢前总金额','机器人输赢前总金额','输赢总金额','用户输赢总金额','机器人输赢总金额','输赢后总金额','用户输赢后','机器人输赢后']
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    data: [],
                    axisLabel :{
                        interval:0
                    },
                    dataZoom:{
                      type: 'slider',
                      show: true,
                      xAxisIndex: [0],
                      left: '9%',
                      bottom: -25,
                      start: 10,
                      end: 90 //初始化滚动条
                   },
                }
            ],
            yAxis: [
                {
                    type: 'value'
                }
            ],
            series: [
                {
                    name: '输赢前总金额',
                    type: 'bar',
                    data: [],
                    itemStyle: {
							normal: {
								label: {
									show: true, //开启显示
									position: 'top', //在上方显示
									textStyle: { //数值样式
										color: 'black',
										fontSize: 12
									}
								}
							}
				    },
                },
                {
                    name: '用户输赢前总金额',
                    type: 'bar',
                    stack: 'zong',
                    data: [],
                    itemStyle: {
							normal: {
								label: {
									show: true, //开启显示
									position: 'top', //在上方显示
									textStyle: { //数值样式
										color: 'black',
										fontSize: 12
									}
								}
							}
				    },
                },
                {
                    name: '机器人输赢前总金额',
                    type: 'bar',
                    stack: 'zong',
                    data: [],
                    itemStyle: {
							normal: {
								label: {
									show: true, //开启显示
									position: 'top', //在上方显示
									textStyle: { //数值样式
										color: 'black',
										fontSize: 12
									}
								}
							}
				    },
                },

                {
                    name: '输赢总金额',
                    type: 'bar',
                    stack: 'a',
                    data: [],
                    itemStyle: {
							normal: {
								label: {
									show: true, //开启显示
									position: 'top', //在上方显示
									textStyle: { //数值样式
										color: 'black',
										fontSize: 12
									}
								}
							}
				    },
                },
                {
                    name: '用户输赢总金额',
                    type: 'bar',
                    stack: 'zonga',
                    data: [],
                    itemStyle: {
							normal: {
								label: {
									show: true, //开启显示
									position: 'top', //在上方显示
									textStyle: { //数值样式
										color: 'black',
										fontSize: 12
									}
								}
							}
				    },
                },
                {
                    name: '机器人输赢总金额',
                    type: 'bar',
                    stack: 'zonga',
                    data: [],
                    itemStyle: {
							normal: {
								label: {
									show: true, //开启显示
									position: 'top', //在上方显示
									textStyle: { //数值样式
										color: 'black',
										fontSize: 12
									}
								}
							}
				    },
                },
                {
                    name: '输赢后总金额',
                    type: 'bar',
                    data: [],
                    itemStyle: {
							normal: {
								label: {
									show: true, //开启显示
									position: 'top', //在上方显示
									textStyle: { //数值样式
										color: 'black',
										fontSize: 12
									}
								}
							}
				    },
                },
                {
                    name: '用户输赢后',
                    type: 'bar',
                    stack: 'after',
                    data: [],
                    itemStyle: {
							normal: {
								label: {
									show: true, //开启显示
									position: 'top', //在上方显示
									textStyle: { //数值样式
										color: 'black',
										fontSize: 12
									}
								}
							}
				    },
                },
                 {
                    name: '机器人输赢后',
                    type: 'bar',
                    stack: 'after',
                    data: [],
                    itemStyle: {
							normal: {
								label: {
									show: true, //开启显示
									position: 'top', //在上方显示
									textStyle: { //数值样式
										color: 'black',
										fontSize: 12
									}
								}
							}
				    },
                },
            ],
            dataZoom:{
              type: 'slider',
              realtime:true, //拖动滚动条时是否动态的更新图表数据
              height:45,//滚动条高度
              start:20,//滚动条开始位置（共100等份）
              end:60//结束位置（共100等份）
           }
        });
        myChart.showLoading();    //数据加载完之前先显示一段简单的loading动画
        var names = [];    //类别数组（实际用来盛放X轴坐标值）
        var series1 = [];
        var series2 = [];
        var series3 = [];
        var series4 = [];
        var series5 = [];
        var series6 = [];
        var series7 = [];
        var series8 = [];
        var series9 = [];
        $.ajax({
            type: 'get',
            url: "{{ info['graphListUrl'] }}" + "&pageSize=10&pageNumber=1&sortOrder=asc&startDate=" + startDate + "&endDate=" + endDate  + "&gametype=" + gametype + '&gameid=' + gameid,
            dataType: "json",        //返回数据形式为json
            success: function (result) {
                //请求成功时执行该函数内容，result即为服务器返回的json对象
                $.each(result.graph_data, function (index, item) {
                    names.push(item.datetime);    //挨个取出类别并填入类别数组
                    series1.push(item.graph_pre_balance);
                });
                $.each(result.graph_data, function (index, item) {
                    series2.push(item.graph_user_pre_balance);
                });
                $.each(result.graph_data, function (index, item) {
                    series3.push(item.graph_root_pre_balance);
                });
                $.each(result.graph_data, function (index, item) {
                    series4.push(item.graph_balance);
                });
                $.each(result.graph_data, function (index, item) {
                    series5.push(item.graph_user_balance);
                });
                $.each(result.graph_data, function (index, item) {
                    series6.push(item.graph_root_balance);
                });
                $.each(result.graph_data, function (index, item) {
                    series7.push(item.graph_after_balance);
                });
                $.each(result.graph_data, function (index, item) {
                    series8.push(item.graph_user_after_balance);
                });
                $.each(result.graph_data, function (index, item) {
                    series9.push(item.graph_robot_after_balance);
                });

                myChart.hideLoading();
                myChart.setOption({
                    xAxis: {
                        data: names
                    },
                    series: [{
                        data: series1
                    },
                        {
                            data: series2
                        },
                        {
                            data: series3
                        },
                        {
                            data: series4
                        },
                        {
                            data: series5
                        },
                        {
                            data: series6
                        },
                        {
                            data: series7
                        },
                        {
                            data: series8
                        },
                        {
                            data: series9
                        },]
                });
            },
            error: function (errorMsg) {
                //请求失败时执行该函数
                myChart.hideLoading();
            }
        });

    };
</script>
%rebase admin_frame_base