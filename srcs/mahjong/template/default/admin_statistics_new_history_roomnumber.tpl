<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<div class="block">
            %include admin_frame_header
          <div class="content">
             <div class="table-toolbar" style="float:left;width:100%;position:relative;top:3.2em">
          <div class='col-sm-12' style='margin-left:1em;'>
                  <div style='float:left;margin-left:1em;' class="input-group date datetime col-md-1 col-xs-1"data-min-view="2" data-date-format="yyyy-mm-dd">
                    <input class="form-control" size="12" type="text" style='width:140px;height:28px;' id='pick-date-start' name="startdate" value="{{lang.INPUT_LABEL_START_DATE_TXT}}" readonly>
                    <span class="input-group-addon btn btn-primary pickdate-btn"><span class="glyphicon pickdate-btn pickdate glyphicon-th"></span>
                  </div>

                  <div style='float:left;margin-left:1em;' class="input-group date datetime col-md-1 col-xs-1"  data-min-view="2" data-date-format="yyyy-mm-dd">
                    <input class="form-control" style='width:140px;height:28px;' id='pick-date-end' name="enddate" size="12" type="text" value="{{lang.INPUT_LABEL_END_DATE_TXT}}" readonly>
                    <span class="input-group-addon btn btn-primary pickdate-btn"><span class="pickdate glyphicon pickdate-btn glyphicon-th"></span></span>
                  </div>
                  <div style='float:left;margin-left:1em;'>
                          <button id="btn_query" class='btn btn-primary btn-sm btn-xs'><i class='fa fa-search'></i>{{lang.INPUT_LABEL_QUERY}}</button>
                          <button id="btn_lastMonth" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_PREV_MONTH}}</button>
                          <button id="btn_thisMonth" class='btn btn-sm btn-xs '>{{lang.INPUT_LABEL_CURR_MONTH}}</button>
                          <button id="btn_lastWeek" class='btn btn-sm btn-xs '>{{lang.INPUT_LABEL_PREV_WEEK}}</button>
                          <button id="btn_thisWeek" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_CURR_WEEK}}</button>
                          <button id="btn_yesterday" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_PREV_DAY}}</button>
                          <button id="btn_today" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_CURR_DAY}}</button>
                         <div class='clearfix'></div>
                  </div>

          </div>

          <div style='float:left;margin-left:1em;'>
                <br>
                <span>会员ID：<span>
                <input type="text" style='width:5%' id="userid" name="userid" >
                <span>公会ID：<span>
                <input type="text" style='width:5%' id="ag" name="ag" >
                <span>省级公会ID：<span>
                <input type="text" style='width:5%' id="parentag" name="parentag" >
                <span>亲友圈ID：<span>
                <input type="text" style='width:5%' id="clubid" name="clubid" >
                <span>房间ID：<span>
                <input type="text" style='width:5%' id="roomid" name="roomid" >
                <span>游戏ID：<span>
                <input type="text" style='width:5%' id="gameid" name="gameid" >
                <span>钻石消耗：<span>
                <input type="text" style='width:5%' id="cards" name="cards" >
                <span>房间标识：<span>
                <input type="text" style='width:12%' id="roomkey" name="roomkey" >
                <button  class='btn btn-primary btn-sm btn-xs' value="1" name="btn_search" id="btn_search">&nbsp搜索&nbsp</button>
                <button  class='btn btn-primary btn-sm btn-xs' name="btn_delsearch" id="btn_delsearch">&nbsp清空搜索&nbsp</button>
            </div>
            <div style='float:left;margin-left:1em;'>
                <br>
                <span>归档数据：</span>
                <a href="/admin/statistics/new/member">
                <button  class='btn btn-primary btn-sm btn-xs' value="1" name="btn_roomkey" id="btn_roomkey">&nbsp会员&nbsp</button>
                </a>
                <a href="/admin/statistics/new/agentid">
                <button  class='btn btn-primary btn-sm btn-xs' value="1" name="btn_roomkey" id="btn_roomkey">&nbsp公会&nbsp</button>
                </a>
                <a href="/admin/statistics/new/clubid">
                <button  class='btn btn-primary btn-sm btn-xs' value="1" name="btn_roomkey" id="btn_roomkey">&nbsp亲友圈&nbsp</button>
                </a>
                <a href="/admin/statistics/new/roomid">
                <button  class='btn btn-primary btn-sm btn-xs' value="1" name="btn_roomkey" id="btn_roomkey">&nbsp房间&nbsp</button>
                </a>
                <a href="/admin/statistics/new/gameid">
                <button  class='btn btn-primary btn-sm btn-xs' value="1" name="btn_roomkey" id="btn_roomkey">&nbsp游戏&nbsp</button>
                </a>
                <a href="/admin/statistics/new/roomnumber">
                <button  class='btn btn-primary btn-sm btn-xs' value="1" name="btn_roomkey" id="btn_roomkey">&nbsp房间标识&nbsp</button>
                </a>
            </div>
</div>

             <table id="dataTable" class="table table-bordered table-hover"></table>
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

        </div>
    </div>
</div>

<script>
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 6);
    $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
    $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));
    var gameid = $("#gameid").val();
    function datalook(){
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        obj_look = document.getElementById("txt");
        obj_look.innerHTML = "数据统计：" + startDate + ' 到 '+ endDate;
    }
</script>

<!-- 初始化搜索栏的日期 -->
<script type="text/javascript">
var firstDate=new Date();
    firstDate.setDate(firstDate.getDate()-6);
    $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
    $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));

    $('#btn_search').click(function(){ //查询
        var userid = $("#userid").val();
        var account = $("#account").val();
        var nickname = $("#nickname").val();
        var ag = $("#ag").val();
        var parag = $("#parag").val();
        var clubid = $("#clubid").val();
        var roomid = $("#roomid").val();
        var gameid = $("#gameid").val();
        var gamename = $("#gamename").val();
        var cards = $("#cards").val();
        var roomkey = $("#roomkey").val();
        var parentag = $("#parentag").val();

        var historyUrl = String.format("/admin/statistics/new/roomnumber?islist=1&pageSize=10&pageNumber=1&sortOrder=asc&startDate={0}&endDate={1}&userid={2}&ag={3}&clubid={4}&roomid={5}&gameid={6}&cards={7}&roomkey={8}&account={9}&gamename={10}&parentag={11}", startDate, endDate, userid, ag,clubid,roomid,gameid,cards,roomkey,account,gamename,parentag)
        $('#dataTable').bootstrapTable('refresh',{'url': historyUrl});
        datalook();
        $("#table2").bootstrapTable('refresh');
    });

    $('#btn_delsearch').click(function(){ //查询
        $("#userid").val('');
        $("#account").val('');
        $("#nickname").val('');
        $("#ag").val('');
        $("#parag").val('');
        $("#clubid").val('');
        $("#roomid").val('');
        $("#gameid").val('');
        $("#gamename").val('');
        $("#cards").val('');
        $("#roomkey").val('');
        $("#parentag").val('');
    });
</script>

<script type="text/javascript">

  function initTable() {
    date = getnowtime();
    startDate = $("#pick-date-start").val();
    endDate   = $("#pick-date-end").val();
    userid = $("#userid").val();
    account = $("#account").val();
    nickname = $("#nickname").val();
    ag = $("#ag").val();
    parag = $("#parag").val();
    clubid = $("#clubid").val();
    roomid = $("#roomid").val();
    gameid = $("#gameid").val();
    gamename = $("#gamename").val();
    cards = $("#cards").val();
    roomkey = $("#roomkey").val();
    $('#dataTable').bootstrapTable({
          url: '{{info["listUrl"]}}',
          method: 'get',
          contentType: "application/json",
          datatype: "json",
          striped: true,
          minimumCountColumns: 2,
          //search: true,
          toolbar:'#toolbar',
          exportTypes: ['excel', 'csv', 'pdf', 'json'],
          showRefresh: true,
          //showExport: true,
          //showFooter: true,
          //showToggle: true,
          cardView: false,
          pagination: true,
          pageSize: 10,
          pageList: [10, 25, 50, 100],
          queryParamsType:'',
          sidePagination:"server",
          clickToSelect: true,
          responseHandler:responseFun,
          queryParams:getSearchP,
          columns: [
          [{
              field: 'number',
              title: '序号',
              align: 'center',
              valign: 'middle',
              sortable: true,
           },{
              field: 'room_number',
              title: '房间标识',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'id',
              title: '会员ID',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'Ag',
              title: '公会ID',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'parentAg',
              title: '省级工会ID',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'club_id',
              title: '亲友圈ID',
              align: 'center',
              valign: 'middle',
              sortable: true,
              footerFormatter:function(values){
                  return '当前页总计:'
              }
          },{
              field: 'room_id',
              title: '房间ID',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'game_id',
              title: '游戏名称',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'use_count',
              title: '钻石总消耗',
              align: 'center',
              valign: 'middle',
              sortable: true,
              footerFormatter:function(values){
                  var count = 0 ;
                  for (var val in values)
                      count+=parseInt(values[val].use_count)

                  return colorFormat(count)
              }
          },{
                    field: 'op',
                    title: '操作',
                    align: 'center',
                    valign: 'middle',
                    formatter:getOp

          }]]
      });

        //定义列操作
        function getSearchP(p) {
            startDate = $("#pick-date-start").val();
            endDate = $("#pick-date-end").val();
            var searchId = $("#searchId").val();
            var userid = $("#userid").val();
            var account = $("#account").val();
            var nickname = $("#nickname").val();
            var ag = $("#ag").val();
            var clubid = $("#clubid").val();
            var roomid = $("#roomid").val();
            var gameid = $("#gameid").val();
            var gamename = $("#gamename").val();
            var cards = $("#cards").val();
            var roomkey = $("#roomkey").val();
            var parentag = $("#parentag").val();
            sendParameter = p;

            sendParameter['searchId'] = searchId;
            sendParameter['startDate'] = startDate;
            sendParameter['endDate'] = endDate;
            sendParameter['userid'] = userid;
            sendParameter['account'] = account;
            sendParameter['nickname'] = nickname;
            sendParameter['ag'] = ag;
            sendParameter['clubid'] = clubid;
            sendParameter['roomid'] = roomid;
            sendParameter['gameid'] = gameid;
            sendParameter['gamename'] = gamename;
            sendParameter['cards'] = cards;
            sendParameter['roomkey'] = roomkey;
            sendParameter['parentag'] = parentag;
            return sendParameter;
        }

        function getOp(value,row,index){
            var showDataUrls = [
                '/admin/statistics/active/history'
            ];
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({id : rowobj['account']});
                var cStr = str.replace(/\"/g, "@");
                // if(showDataUrls.indexOf(op['url'])>=0)
                    //opList.push(String.format("<a href='javascript:;' onclick=\"showActiveDialog(\'{0}\', \'{1}\', \'{2}\');\" class=\"btn btn-sm btn-primary\" >{3}</a> ", op['url'],op['method'],rowobj['date'],op['txt']));
                //else //不使用弹出窗口打开页面
                opList.push(String.format("<a href=\"{0}?roomkey={1}\" class=\"btn btn-sm btn-primary\">{2}</a>",op['url'],rowobj['room_number'],op['txt']));
            }
            return opList.join('');
        }

        //获得返回的json 数据
        function responseFun(res){
          count= res.total;
          pageNumber = parseInt(res.pageNumber);
          return {"rows": res.data,
                  "total": res.count
          };
      }
        function getnowtime(){
           var now = new Date();
           var year = now.getFullYear();
           var month = now.getMonth();
           var date = now.getDate();
           month = month + 1;
           if (month < 10) month = "0" + month;
           if (date < 10) date = "0" + date;
           var time = "";
           time = year + "-" + month + "-" + date;
           return time;
        }

        $("#table2").bootstrapTable('refresh');
    }
     sumTable();
     datalook();
     sumDayTable();

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
                field: 'use_count',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '总钻石消耗',
            },],

            //注册加载子表的事件。注意下这里的三个参数！
            onExpandRow: function (index, row, $detail) {
                console.log(index, row, $detail);
                InitSubTable(index, row, $detail);
            }
        });

        function getSearchP(p) {
            var startDate = $("#pick-date-start").val();
            var endDate = $("#pick-date-end").val();
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
          url: '{{ info['sumDayListUrl'] }}',
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
                field: 'use_count',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '总钻石消耗',
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
            var userid = $("#userid").val();
            var account = $("#account").val();
            var nickname = $("#nickname").val();
            var ag = $("#ag").val();
            var clubid = $("#clubid").val();
            var roomid = $("#roomid").val();
            var gameid = $("#gameid").val();
            var gamename = $("#gamename").val();
            var cards = $("#cards").val();
            var roomkey = $("#roomkey").val();
            var parentag = $("#parentag").val();
            sendParameter = p;

            sendParameter['searchId'] = searchId;
            sendParameter['startDate'] = startDate;
            sendParameter['endDate'] = endDate;
            sendParameter['userid'] = userid;
            sendParameter['account'] = account;
            sendParameter['nickname'] = nickname;
            sendParameter['ag'] = ag;
            sendParameter['clubid'] = clubid;
            sendParameter['roomid'] = roomid;
            sendParameter['gameid'] = gameid;
            sendParameter['gamename'] = gamename;
            sendParameter['cards'] = cards;
            sendParameter['roomkey'] = roomkey;
            sendParameter['parentag'] = parentag;
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
</script>
%rebase admin_frame_base
