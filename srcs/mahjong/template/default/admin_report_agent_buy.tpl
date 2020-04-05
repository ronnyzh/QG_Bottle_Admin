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
    *  代理操作日志
    *
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
          showExport: true,
          pagination: true,
          pageSize: 15,
          pageList: [15, 50, 100, 'All'],
          search: true,
          clickToSelect: true,
          //sidePagination : "server",
          sortOrder: 'desc',
          sortName: 'date',
          showFooter:true,
          queryParams:getSearchP,
          responseHandler:responseFun,
          //onLoadError:responseError,
          showExport:true,
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
              footerFormatter:function(values){
                   return "总计:"
              }
          },{
              field: 'cards',
              title: '当日购钻数',
              align: 'center',
              sortable: true,
              valign: 'middle',
              footerFormatter:function(values){
                   var count = 0;
                   for(var val in values)
                      count+=parseInt(values[val].cards);

                   return colorFormat(count);
              }
          },{
              field: 'cardNumsTotal',
              title: '总购钻数',
              align: 'center',
              sortable: true,
              valign: 'middle',
              footerFormatter:function(values){
                  var count = 0;
                  for (var val in values)
                    count+=parseInt(values[val].cardNumsTotal);

                  return colorFormat(count)
              }
          }]]
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
}
</script>
%rebase admin_frame_base
