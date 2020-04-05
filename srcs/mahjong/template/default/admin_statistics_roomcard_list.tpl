<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<div class="block">
        <div class='header bordered-bottom bordered-themesecondary' id="crumb">
             <h3 style="font-weight:bold">
               %if info.get('title',None):
                 {{info['title']}}
               %end
            </h3>
        </div>
        <div class="content">
            <table id="dataTable" class="table table-bordered table-hover"></table>
        </div>
</div>
<script type="text/javascript">

    startDate = $("#pick-date-start").val();
    endDate   = $("#pick-date-end").val();
    $('#dataTable').bootstrapTable({
          method: 'get',
          url: '{{info["listUrl"]}}',
          contentType: "application/json",
          datatype: "json",
          cache: true,
          checkboxHeader: true,
          striped: true,
          pagination: true,
          pageSize: 15,
          showRefresh: true,
          pageList: '{{PAGE_LIST}}',
          search:true,
          // queryParamsType:'',
          // sidePagination:"server",
          minimumCountColumns: 2,
          //smartDisplay: true,
          responseHandler:responseFun,
          //onLoadError:responseError,
          queryParams:getSearchP,
          sortable: true,                     //是否启用排序
          sortOrder: "desc",                   //排序方式
          sortName:'roomcards_day',
          showExport:true,
          showFooter:true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          columns: [
          [{
                    "title": "日期:"+"{{date}}" + "详情列表",
                    "halign":"center",
                    "align":"center",
                    "colspan": 9
          }],
          [{
              field: 'id',
              title: '游戏ID',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'gamename',
              title: '游戏名称',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'roomcards_day',
              title: '钻石消耗',
              align: 'center',
              valign: 'middle',
              sortable: true,
              footerFormatter:function(values){
                  var count = 0 ;
                  for (var val in values)
                      count+=parseInt(values[val].roomcards_day)

                  return colorFormat(count)
              }
           },{
              field: 'GameBaiFenbi',
              title: '当天游戏钻石消耗占比',
              align: 'center',
              valign: 'middle',
              sortable: true,
              footerFormatter:function(values){
                  var count = 0 ;
                  for (var val in values)
                      count+=parseInt(values[val].GameBaiFenbi)

                  return colorFormat(count)
              }

          }]]
    });

        function getSearchP(p){
            // account = $("#account").val();
            // member_level = $('#member_level').val();
            // member_status = $("#member_status").val();
            // userId = $("#userId").val();
            startDate = $("#pick-date-start").val();
            endDate   = $("#pick-date-end").val();

            sendParameter = p;
            sendParameter['startDate'] = startDate;
            sendParameter['endDate']  = endDate;

            return sendParameter;
          }

        //获得返回的json 数据
        function responseFun(res){
            console.log('----------------------data:'+res);
            return res;
        }

        function responseError(status) {
            location.reload();
        }
</script>
%rebase admin_frame_base
