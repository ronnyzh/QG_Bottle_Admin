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
    startDate = $("#pick-date-start").val();
    endDate   = $("#pick-date-end").val();
    $('#dataTable').bootstrapTable({
          url: '{{info["listUrl"]}}',
          method: 'get',
          contentType: "application/json",
          datatype: "json",
          //striped: true,
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
          //sidePagination:"server",
          clickToSelect: true,
          //responseHandler:responseFun,
          queryParams:getSearchP,
          columns:

          [{
              field: 'date',
              title: '日期',
              align: 'center',
              valign: 'middle',
              footerFormatter:function(values){
                 return '总计'
              }
          },{
              field: 'add_club',
              title: '新增亲友圈总数',
              align: 'center',
              valign: 'middle',
              footerFormatter:function(values){
                  var count = 0 ;
                  for (var val in values)
                      if (values[val].add_club){
                        count+=parseInt(values[val].add_club)
                      }

                  return colorFormat(count)
              }

          },{
              field: 'add_club_list',
              title: '新增亲友圈ID',
              align: 'center',
              valign: 'middle',
          },{
              field: 'del_club',
              title: '解散亲友圈总数',
              align: 'center',
              valign: 'middle',
              footerFormatter:function(values){
                  var count = 0 ;
                  for (var val in values)
                       if (values[val].del_club){
                      count+=parseInt(values[val].del_club)
                      }

                  return colorFormat(count)
              }
          },{
              field: 'del_club_list',
              title: '解散亲友圈ID',
              align: 'center',
              valign: 'middle',
          },{
              field: 'op',
              title: '操作',
              align: 'center',
              valign: 'middle',
              formatter: getOp
          }],
          onExpandRow: function (index, row, $detail) {
              console.log(index,row,$detail);
              InitSubTable(index, row, $detail);
          }
      });

        function getSearchP(p) {
            startDate = $("#pick-date-start").val();
            endDate = $("#pick-date-end").val();

            sendParameter = p;
            sendParameter['startDate'] = startDate;
            sendParameter['endDate'] = endDate;

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
                opList.push(String.format("<a href=\"{0}?day={1}\" class=\"btn btn-sm btn-primary\">{2}</a>",op['url'],rowobj['date'],op['txt']));
            }
            return opList.join('');
        }

        //获得返回的json 数据
        function responseFun(res){
          //count= res.total;
          //实时刷
          //$('.count').text(String.format("会员总人数:{0}",count));
          //pageNumber = parseInt(res.pageNumber);
          return {"rows": res.data,
                  "total": res.count
          };
      }
      function responseError(status) {
          location.reload();
      }

}

function InitSubTable(index, row, $detail) {
        var date = row.date;
        var cur_table = $detail.html('<table table-bordered table-hover definewidth></table>').find('table');
        $(cur_table).bootstrapTable({
                url: '{{info["serversUrl"]}}',
                method: 'get',
                contentType: "application/json",
                datatype: "json",
                cache: false,
                queryParams:getSearchP,
                sortOrder: 'desc',
                sortName: 'regDate',
                pageSize: 15,
                pageList: [15, 25],
                columns: [{
                    field: 'date',
                    title: '日期',
                    align: 'center',
                    valign: 'middle'
                },{
                    field: 'type',
                    title: '新增/解散',
                    align: 'center',
                    valign: 'middle',
                    cellStyle:function(value,row,index){
                    if (value=="新增"){
                        return {css:{"background-color":"#87CEFF"}}
                            }else{
                        	        return {css:{"background-color":"#FF82AB"}}
                        	    }
                        	}
                },{
                    field: 'club_id',
                    title: '亲友圈ID',
                    align: 'center',
                    valign: 'middle'
                },{
                    field: 'club_userid',
                    title: '创建者ID',
                    align: 'center',
                    valign: 'middle'
                },{
                    field: 'club_account',
                    title: '创建者账号',
                    align: 'center',
                    valign: 'middle'
                },{
                    field: 'club_nickname',
                    title: '创建者昵称',
                    align: 'center',
                    valign: 'middle'
                },{
                    field: 'club_agent',
                    title: '工会',
                    align: 'center',
                    valign: 'middle'
                },{
                    field: 'club_member',
                    title: '亲友圈人数',
                    align: 'center',
                    valign: 'middle'
                },{
                    field: 'op',
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

        //定义列操作
        function getSearchP(p){
              sendParameter = p;
              sendParameter['date'] = date;
              return sendParameter;
        }

        function responseFunc(res){
            data = res.data;
            count= res.count;
            //实时刷

            return data;
        }

}
</script>
%rebase admin_frame_base
