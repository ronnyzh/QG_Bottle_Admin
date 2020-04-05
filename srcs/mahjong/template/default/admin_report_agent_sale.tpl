<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<div class="block">
          %include admin_frame_header
          <div class="content">
             <span id='total' style='position:relative;left:20px;font-size:14px;margin-right:20px'></span>
             %include original_search_bar
             <table id="dataTable" class="table table-bordered table-hover"></table>
          </div>
          <br>

          %if info['selfUid'] == '0':
          <div class="content">
             <div class='header bordered-bottom bordered-themesecondary' id="crumb">
                 <h3 style="font-weight:bold">
                   玩家购钻订单
                </h3>
            </div>
             <table id="memberOLtable1" class="table table-bordered table-hover"></table>
          </div>
          %end

</div>
<script type="text/javascript">

  /**------------------------------------------------
    *  代理操作日志
    -------------------------------------------------
  */
  function initTable() {
    startDate = $("#pick-date-start").val();
    endDate   = $("#pick-date-end").val();
    $('#dataTable').bootstrapTable({
          method: 'get',
          url: '{{info["listUrl"]}}',
          contentType: "application/json",
          datatype: "json",
          cache: false,
          checkboxHeader: true,
          striped: true,
          pagination: true,
          pageSize: 24,
          pageList: [24, 48, 100, 'All'],
          search: true,
          detailView: true,//父子表
          clickToSelect: true,
          //sidePagination : "server",
          sortOrder: 'desc',
          sortName: 'date',
          queryParams:getSearchP,
          responseHandler:responseFun,
          showExport:true,
          showFooter:true,
          exportDataType:'all',
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          columns: [
          [
            {
                    "title": "搜索日期:"+startDate+"至"+endDate,
                    "halign":"center",
                    "align":"center",
                    "colspan": 5
            }
          ],
          [{
              field: 'date',
              title: '日期',
              align: 'center',
              valign: 'middle'
          },{
              field: 'account',
              title: '代理账号',
              align: 'center',
              valign: 'middle'
          },{
              field: 'aId',
              title: '代理ID',
              align: 'center',
              sortable: true,
              valign: 'middle',
              footerFormatter:function(value){
                  return "总计"
              }
          },{
              field: 'cards',
              title: '当前售钻数',
              align: 'center',
              sortable: true,
              valign: 'middle',
              footerFormatter:function(values){
                  var count = 0;
                  for (var val in values)
                    count+=parseInt(values[val].cards);

                  return colorFormat(count)
              }
          },{
              field: 'cardNumsTotal',
              title: '总售钻数',
              align: 'center',
              sortable: true,
              valign: 'middle',
              footerFormatter:function(values){
                  var count = 0;
                  for (var val in values)
                    count+=parseInt(values[val].cardNumsTotal);

                  return colorFormat(count)
              }
          }]],

          //注册加载子表的事件。注意下这里的三个参数！
                onExpandRow: function (index, row, $detail) {
                    console.log(index,row,$detail);
                    InitSubTable(index, row, $detail);
                }
      });

      //定义列操作
      function getSearchP(p){
          startDate = $("#pick-date-start").val();
          endDate   = $("#pick-date-end").val();
          group_id   = $("#group_id").val();

          sendParameter = p;

          sendParameter['startDate'] = startDate;
          sendParameter['endDate']  = endDate;
          sendParameter['group_id']  = group_id;

          return sendParameter;
      }

        //获得返回的json 数据
      function responseFun(res){
            data = res.result
            return data;
      }

       %if info['selfUid'] == '0':
        $('#memberOLtable1').bootstrapTable('refresh');
       %end
}

function InitSubTable(index, row, $detail) {
        var parentAg = row.aId;
        var cur_table = $detail.html('<table table-bordered table-hover definewidth></table>').find('table');
        $(cur_table).bootstrapTable({
                url: '{{info["tableUrl"]}}',
                method: 'get',
                contentType: "application/json",
                datatype: "json",
                cache: false,
                queryParams:getSearchP,
                sortOrder: 'desc',
                sortName: 'regDate',
                pagination: true,
                pageSize: 10,
                pageList: [10, 15, 25],
                columns: [{
                    field: 'cardNums',
                    sortable: true,
                    align: 'center',
                    valign: 'middle',
                    title: '售钻数(张)'
                },{
                    field: 'applyAccount',
                    align: 'center',
                    valign: 'middle',
                    title: '买钻方'
                },{
                    field: 'saleAccount',
                    align: 'center',
                    valign: 'middle',
                    title: '卖钻方'
                }, {
                    field: 'status',
                    title: '订单状态',
                    align: 'center',
                    valign: 'middle',
                    formatter:status
                },{
                    field: 'finish_date',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    title: '系统确认时间'

                }],

                //注册加载子表的事件。注意下这里的三个参数！
                onExpandRow: function (index, row, $detail) {
                    console.log(index,row,$detail);
                    InitSubTable(index, row, $detail);
                }
      });

    function status(value,row,index){
        eval('var rowobj='+JSON.stringify(row))
        var statusstr = '';
        if(rowobj['status'] == '0'){
            statusstr = '<span class="label label-danger">卖钻方未确认</span>';
        }else if(rowobj['status'] == '1'){
            statusstr = '<span class="label label-success">卖钻方已确认</span>';
        }

        return [
            statusstr
        ].join('');
    }

    function getSearchP(p){
          startDate = $("#pick-date-start").val();
          endDate   = $("#pick-date-end").val();

          sendParameter = p;

          sendParameter['startDate'] = startDate;
          sendParameter['endDate']  = endDate;
          sendParameter['parentAg']  = parentAg;

          return sendParameter;
    }

    function getOp(value,row,index){
          eval('rowobj='+JSON.stringify(row))
          var opList = []
          for (var i = 0; i < rowobj['op'].length; ++i) {
              var op = rowobj['op'][i];
              var str = JSON.stringify({orderNo:rowobj["orderNo"]});
              var cStr = str.replace(/\"/g, "@");
             if (rowobj['status'] == '1')
                  continue;
              var contentUrl = op['url'];
              opList.push(String.format("<a href=\"#\" class=\"btn btn-primary btn-sm\" onclick=\"comfirmOrderDialog(\'{0}\',\'{1}\',\'{2}\')\"><i class=\"glyphicon glyphicon-edit\"> {3} </i></a> ",contentUrl,op['method'],cStr,op['txt']));
          }
          return opList.join('');
    }

    //获得返回的json 数据
    function responseFun(res){
        return res
    }
 }

%if info['selfUid'] == '0':
 $(function () {
        startDate = $("#pick-date-start").val();
        endDate   = $("#pick-date-end").val();
        $('#memberOLtable1').bootstrapTable({
            method:'get',
            url   :'{{info["tableUrl"]}}',
            smartDisplay: true,
            pagination: true,
            pageSize: 10,
            pageList: [10,20,50],
            showRefresh: true,
            queryParams:getSearchP,
            search: true,
            columns: [{
                    field: 'cardNums',
                    sortable: true,
                    align: 'center',
                    valign: 'middle',
                    title: '售钻数(张)'
                },{
                    field: 'applyAccount',
                    align: 'center',
                    valign: 'middle',
                    title: '买钻方'
                },{
                    field: 'saleAccount',
                    align: 'center',
                    valign: 'middle',
                    title: '卖钻方'
                }, {
                    field: 'status',
                    title: '订单状态',
                    align: 'center',
                    valign: 'middle',
                    formatter:status
                },{
                    field: 'finish_date',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    title: '系统确认时间'

                }],
        });

        function status(value,row,index){
        eval('var rowobj='+JSON.stringify(row))
        var statusstr = '';
        if(rowobj['status'] == '0'){
            statusstr = '<span class="label label-danger">卖钻方未确认</span>';
        }else if(rowobj['status'] == '1'){
            statusstr = '<span class="label label-success">卖钻方已确认</span>';
        }

        return [
            statusstr
        ].join('');
        }

        function getOp(value,row,index){
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            opList.push("<a href='javascript:;' onClick=\"comfirmDialog('/admin/member/kicks?account="+rowobj['account']+"&groupId="+rowobj['parentAg']+"','GET','{}')\" class=\"btn btn-sm btn-primary\" <i class=\"fa fa-edit\"> </i>踢出</a> ");
            return opList.join('');
        }

        function responseFunc(res){
            data = res.data_gold;
            count_gold= res.count_gold;
            //实时刷
            $('.gold_count').text(String.format("当前在线人数: {0}",count_gold));
            return data;
        }

        function getSearchP(p){
          startDate = $("#pick-date-start").val();
          endDate   = $("#pick-date-end").val();

          sendParameter = p;

          sendParameter['startDate'] = startDate;
          sendParameter['endDate']  = endDate;
          sendParameter['play']  = '1';

          return sendParameter;
        }
    });
%end
</script>
%rebase admin_frame_base
