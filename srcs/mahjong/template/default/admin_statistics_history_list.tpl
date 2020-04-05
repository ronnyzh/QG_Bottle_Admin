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


  function initTable() {
    date = getnowtime();
    startDate = $("#pick-date-start").val();
    endDate   = $("#pick-date-end").val();

    $('#dataTable').bootstrapTable({
          method: 'get',
          url: '{{ info["listUrl"] }}',
          contentType: "application/json",
          datatype: "json",
          cache: false,
          checkboxHeader: true,
          detailView: true,//父子表
          striped: true,
          pagination: true,
          pageSize: 15,
          pageList: '{{PAGE_LIST}}',
          search: true,
          showColumns: true,
          showRefresh: true,
          showFooter:true,
          minimumCountColumns: 2,
          clickToSelect: true,
          smartDisplay: true,
          //sidePagination : "server",
          queryParams:getSearchP,
          responseHandler:responseFun,
          //onLoadError:responseError,
          showExport:true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          //onLoadSuccess:function(data){
          //  var myArray=new Array();
          //   for (var i = 0; i < 10; ++i) {
          //      if (data['data'][i].use_count){
          //          myArray[i] = data['data'][i]
          //      };
          //   }
          //   $("#dataTable").bootstrapTable("load", {'data':,'count':10})
          //},
          columns: [
          [{
              field: 'date',
              title: '日期',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'id',
              title: '会员账号',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'parentAg',
              title: '公会ID',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'top_parent_ag',
              title: '省级公会ID',
              align: 'center',
              valign: 'middle',
              sortable: true,
              footerFormatter:function(values){
                  return '总计:'
              }
          },{
              field: 'use_count',
              title: '钻石消耗',
              align: 'center',
              valign: 'middle',
              sortable: true,
              footerFormatter:function(values){
                  var count = 0 ;
                  for (var val in values)
                      count+=parseInt(values[val].use_count)

                  return colorFormat(count)
              }

          }]],
          onExpandRow: function (index, row, $detail) {
                console.log(index, row, $detail);
                InitSubTable(index, row, $detail);
            }
      });

        //定义列操作
        function getSearchP(p){
          startDate = $("#pick-date-start").val();
          endDate   = $("#pick-date-end").val();
          sendParameter = p;

          sendParameter['startDate'] = startDate;
          sendParameter['endDate']  = endDate;

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
                opList.push(String.format("<a href=\"{0}?day={1}\" class=\"btn btn-sm btn-primary\">{2}</a>",op['url'],rowobj['date'],op['txt']));
            }
            return opList.join('');
        }

        //获得返回的json 数据
        function responseFun(res){
            var data = res;
            return data;
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
}
function InitSubTable(index, row, $detail) {
        var parentAg = row.id;
        var startDate = row.date;
        var table = String.format('<table table-bordered table-hover definewidth id="child_table{0}"></table>', parentAg)
        var cur_table = $detail.html(table).find('table');
        $(cur_table).bootstrapTable({
            url: '{{ info['serversUrl'] }}',
            method: 'get',
            contentType: "application/json",
            datatype: "json",
            cache: false,
            queryParams: getSearchP,
            sortOrder: 'desc',
            detailView: true,//父子表
            sortName: 'regDate',
            pagination: true,
            pageSize: 10,
            pageList: [10, 25, 50, 'ALL'],
            search: true,
            showColumns: true,
            showRefresh: true,
            showFooter: true,
            striped: true,
            columns: [
                [{
                    field: 'create_time',
                    title: '房间创建日期',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'end_time',
                    title: '房间解散日期',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'id',
                    title: '会员ID',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }, {
                    field: 'account',
                    title: '会员账号',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }, {
                    field: 'nickname',
                    title: '会员昵称',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }, {
                    field: 'club_id',
                    title: '亲友圈ID',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    footerFormatter: function (values) {
                        return '当前房间耗钻总计:'
                    }
                }, {
                    field: 'room_id',
                    title: '房间ID',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'game_name',
                    title: '游戏名称',
                    align: 'center',
                    valign: 'middle',
                    sortable: true

                }, {
                    field: 'use_count',
                    title: '钻石消耗',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    formatter: function (value, row, index) {
                        infoStr = String.format("<span style=\"color:red;\">{0}</span>", value);
                        return [infoStr].join('');
                    },
                    footerFormatter: function (values) {
                        var count = 0;
                        for (var val in values)
                            count += parseInt(values[val].use_count)
                        return colorFormat(count)
                    }
                }]],
            onExpandRow: function (index, row, $detail) {
                console.log(index, row, $detail);
                InitSubsubTable(index, row, $detail);
            }

        });

        function getSearchP(p) {
            sendParameter = p;
            sendParameter['id'] = parentAg;
            sendParameter['startDate'] = startDate;
            return sendParameter;
        }
    }

    function InitSubsubTable(index, row, $detail) {
        var time = row.time;
        var ag = row.ag;
        var roomId = row.roomId;
        var player = row.player;
        var room_number = row.room_number;
        var table = String.format('<table table-bordered table-hover definewidth id="child_table{0}"></table>', ag)
        var cursub_table = $detail.html(table).find('table');
        $(cursub_table).bootstrapTable({
            url: '{{ info['serversSubUrl'] }}',
            method: 'get',
            contentType: "application/json",
            datatype: "json",
            cache: false,
            queryParams: getSearchP,
            sortOrder: 'desc',
            sortName: 'regDate',
            detailView: true,//父子表
            pagination: true,
            pageSize: 10,
            pageList: [10, 25, 50, 'ALL'],
            search: true,
            showColumns: true,
            showRefresh: true,
            showFooter: true,
            striped: true,
            columns: [
                [{
                    field: 'start_time',
                    title: '开局时间',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'end_time',
                    title: '散局时间',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'room_number',
                    title: '房间ID',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'round',
                    title: '游戏结束局数',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }, {
                    field: 'total_round',
                    title: '游戏最大局数',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,

                }]],
            onExpandRow: function (index, row, $detail) {
                console.log(index, row, $detail);
                InitSubsubsubTable(index, row, $detail);
            }

        });

        function getSearchP(p) {
            sendParameter = p;
            sendParameter['time'] = time;
            sendParameter['roomId'] = roomId;
            sendParameter['player'] = player;
            sendParameter['room_number'] = room_number;
            return sendParameter;
        }

    }

    function InitSubsubsubTable(index, row, $detail) {
        var room_number = row.game_number;
        var table = String.format('<table table-bordered table-hover definewidth id="child_table{0}"></table>', room_number)
        var cursub_table = $detail.html(table).find('table');
        $(cursub_table).bootstrapTable({
            url: '{{ info['serversSubsubUrl'] }}',
            method: 'get',
            contentType: "application/json",
            datatype: "json",
            cache: false,
            queryParams: getSearchP,
            sortOrder: 'desc',
            sortName: 'regDate',
            pagination: true,
            pageSize: 10,
            pageList: [10, 25, 50, 'ALL'],
            search: true,
            showColumns: true,
            showRefresh: true,
            showFooter: true,
            striped: true,
            columns: [
                [{
                    field: 'create_time',
                    title: '日期',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                }, {
                    field: 'user_id',
                    title: '会员ID',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }, {
                    field: 'account',
                    title: '会员账号',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }, {
                    field: 'nickname',
                    title: '会员昵称',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                }]],
        });

        function getSearchP(p) {
            sendParameter = p;
            sendParameter['room_number'] = room_number;
            return sendParameter;
        }

    }
</script>
%rebase admin_frame_base
