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
          showExport: true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          pageList: [15,50,100,'All'],
          search: true,
          clickToSelect: true,
          //sidePagination : "server",
          sortOrder: 'desc',
          sortName: 'date',
          queryParams:getSearchP,
          responseHandler:responseFun,
          showFooter:true, //添加页脚做统计
          //onLoadError:responseError,
          showExport:true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          columns: [
          {
              field: 'dissolutiondate',
              title: '日期',
              align: 'center',
              valign: 'middle',
          },{
              field: 'club_number',
              title: '亲友圈ID',
              align: 'center',
              valign: 'middle',
          },{
              field: 'account',
              title: '创建人',
              align: 'center',
              valign: 'middle',
          }],
          onExpandRow: function (index, row, $detail) {
              console.log(index,row,$detail);
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


        //获得返回的json 数据

        function responseFun(res){
            // $('#numberTotal').html(' 销售总个数: <strong style="color:#6600FF">'+res.numberTotal+'</strong>');
            // $('#rateTotal').html('我的总占额: <strong style="color:#6600FF">'+res.rateTotal+'</strong>');
            // $('#superTotal').html('上线总占额: <strong style="color:#6600FF">'+res.superTotal+'</strong>');
            data = res.data
            return data;
        }
}
</script>
%rebase admin_frame_base
