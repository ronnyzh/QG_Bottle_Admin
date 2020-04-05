<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<div class="block">
            %include admin_frame_header
          <div class="content">

             <table id="dataTable" class="table table-bordered table-hover"></table>
          </div>
</div>
<script type="text/javascript">

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
          pageSize: 15,
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
          columns: [

          [{
              field: 'account',
              title: '用户',
              align: 'center',
              valign: 'middle',
          },{
              field: 'user_id',
              title: '用户ID',
              align: 'center',
              valign: 'middle',
          },{
              field: 'nickname',
              title: '用户昵称',
              align: 'center',
              valign: 'middle',
          },{
                field: 'avatar_url',
                title: '头像',
		        align: 'center',
                formatter: function(value,row,index){
                 return '<img style="width: 40px;height: 40px;" src="'+value+'" class="img-rounded">';
                 }
          },{
              field: 'reg_date',
              title: '用户注册日期',
              align: 'center',
              valign: 'middle',
          },{
              field: 'status',
              title: '状态',
              align: 'center',
              valign: 'middle',
          },{
              field: 'op',
              title: '操作',
              align: 'center',
              valign: 'middle',
              formatter:getOp
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
                '/admin/statistics/active/showDay11'
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
                opList.push(String.format("<a href=\"{0}\" class=\"btn btn-sm btn-primary\">{2}</a>",op['url'],rowobj['date'],op['txt']));
            }
            return opList.join('');
        }

        //获得返回的json 数据
        function responseFun(res){
            var data = res;
            return data;
        }
}
</script>
%rebase admin_frame_base
