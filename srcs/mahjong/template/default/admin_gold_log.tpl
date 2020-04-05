<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<div class="cl-mcont">
  <div class="block">
            <div class="header">
              <h3>
                %if info.get('title',None):
                  {{info['title']}}
                %end
              </h3>
            </div>
            <div class="content">
               %include original_search_bar
               <table id="dataTable" class="table table-bordered table-hover"></table>
            </div>
  </div>
</div>
<script type="text/javascript">
  var firstDate=new Date();
  firstDate.setDate(firstDate.getDate()-6);
  $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
  $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));

  /**------------------------------------------------
    *  代理操作日志
    -------------------------------------------------
  */
  function initTable() {
     startDate = $("#pick-date-start").val();
     endDate   = $("#pick-date-end").val();
     $("#dataTable").bootstrapTable({
                url: "{{info['listUrl']}}",
                method: 'get',
                pagination: true,
                pageSize: 15,
                search: true,
                showRefresh: true,
                showExport: true,
                exportTypes:['excel', 'csv', 'pdf', 'json'],
                pageList: [15, 25, 100],
                responseHandler:responseFun,
                queryParams:getSearchP,
                columns: [{
                    field: 'user_id',
                    sortable: true,
                    align: 'center',
                    valign: 'middle',
                    title: '玩家编号'
                },{
                    field: 'name',
                    align: 'center',
                    valign: 'middle',
                    title: '玩家名称'
                },{
                    field: 'game_id',
                    align: 'center',
                    valign: 'middle',
                    title: '游戏ID'
                },{
                    field: 'isRobot',
                    align: 'center',
                    valign: 'middle',
                    title: '是否机器人'
                }, {
                    field: 'createtime',
                    title: '记录时间',
                    align: 'center',
                    valign: 'middle',
                    sortable: true

                },{
                    field: 'pre_gold',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                    title: '改变前金币'
                },{
                    field: 'changed',
                    title: '改变量',
                    align: 'center',
                    valign: 'middle',
                    sortable: true

                },{
                    field: 'now_gold',
                    title: '改变后金币',
                    align: 'center',
                    valign: 'middle',
                    sortable: true

                },{
                    field: 'action',
                    title: '操作',
                    align: 'center',
                    valign: 'middle'

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
</script>
%rebase admin_frame_base