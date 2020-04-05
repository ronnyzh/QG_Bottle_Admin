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
          url: '{{info["listUrl"]}}',
          contentType: "application/json",
          datatype: "json",
          cache: false,
          checkboxHeader: true,
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
              field: 'create_time',
              title: '日期',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'user_id',
              title: '会员ID',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'account',
              title: '会员账号',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'nickname',
              title: '会员昵称',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'room_number',
              title: '房间标识',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
                    field: 'op',
                    title: '操作',
                    align: 'center',
                    valign: 'middle',
                    //formatter:getOp

          }]]
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
                opList.push(String.format("<a href=\"{0}?roomkey={1}\" class=\"btn btn-sm btn-primary\">{2}</a>",op['url'],rowobj['room_number'],op['txt']));
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
</script>
%rebase admin_frame_base
