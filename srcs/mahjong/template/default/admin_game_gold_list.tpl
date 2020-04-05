<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
 <div class='block'>
       %include admin_frame_header
       <div class='content'>
          <div id="toolbar" class="btn-group">
               <button id="btn_add" type="button" class="btn btn-sm btn-primary">
                  <span class="glyphicon glyphicon-plus">
                      <a href="{{info['createUrl']}}" style='color:#FFF;text-decoration:none;'>{{info['addTitle']}}</a>
                  </span>
              </button>
          </div>
          <table id='loadDataTable' class="table table-bordered table-hover " ></table>
       </div>
  </div>
<script type="text/javascript">
    /**
      *表格数据
    */
    var editId;        //定义全局操作数据变量
    var isEdit;
    var startDate;
    var endDate;
    $('#loadDataTable').bootstrapTable({
          method: 'get',
          url: "{{info['tableUrl']}}",
          contentType: "application/json",
          datatype: "json",
          cache: false,
          checkboxHeader: true,
          detailView: true,//父子表
          pagination: true,
          pageSize: 15,
          toolbar:'#toolbar',
          pageList: '[15, 50, 100]',
          search: true,
          showRefresh: true,
          minimumCountColumns: 2,
          clickToSelect: true,
          smartDisplay: true,
          //sidePagination : "server",
          sortOrder: 'desc',
          sortName: 'datetime',
          queryParams:getSearchP,
          responseHandler:responseFunc,
          //onLoadError:responseError,
          showExport:true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          //exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          columns: [
          [{
                    halign    : "center",
                    font      :  15,
                    align     :  "left",
                    class     :  "totalTitle",
                    colspan   :  9
          }],
          [{
              checkbox: true
          },{
              field: 'id',
              title: '游戏ID',
              align: 'center',
              valign: 'middle',
              sortable:true
          },{

              field: 'name',
              title: '游戏名称',
              align: 'center',
              valign: 'middle',
              formatter:colorFormat
          },{

              field: 'count',
              title: '场次总数统计',
              align: 'center',
              valign: 'middle',
              formatter:colorFormat
          },{

              field: 'op',
              title: '操作',
              align: 'center',
              valign: 'middle',
              formatter:getOp
          }]],

         //注册加载子表的事件。注意下这里的三个参数！
          onExpandRow: function (index, row, $detail) {
              console.log(index,row,$detail);
              InitSubTable(index, row, $detail);
          }
      });

        //定义列操作
        function getSearchP(p){
          sendParameter = p;

          sendParameter['startDate'] = startDate;
          sendParameter['endDate']  = endDate;

          startDate = $("#data-pick-start").val();
          endDate   = $("data-pick-end").val();

          return sendParameter;
        }

        function comfirmDialog(url,method,jsonStr,text){
            var comfirmTxt = text || '是否确定此操作';

              layer.open({
                  title: [
                     '麻将后台提醒你',
                     'background-color:#204077; color:#fff;'
                  ]
                  ,anim: 'up'
                  ,content:comfirmTxt
                  ,btn: ['确认', '取消']
                  ,fixed:true
                  ,style: 'position:fixed;top:25%;left:50%;margin-left:-250px;'
                  ,yes:function(index){
                    normalAjaxStrData(url,method,jsonStr);
                    layer.close(index);
                  }
              });
        }


        function getOp(value,row,index){
            var comfirmUrls = [ //需要弹框操作的接口地址
                '/admin/game/gold/delete',
            ];
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({id : rowobj['id']});
                var cStr = str.replace(/\"/g, "@");
                if(comfirmUrls.indexOf(op['url'])>=0){  //删除用红色按钮
                    var btn_type = 'primary';
                    if ( (op['url'].substring(op['url'].length-6)) == 'delete')
                         btn_type = 'danger';
                    opList.push(String.format("<a href=\"#\" class=\"btn btn-{4} btn-sm \" onclick=\"comfirmDialog(\'{0}\', \'{1}\', \'{2}\')\">{3}</a> ", op['url'], op['method'], cStr, op['txt'],btn_type));
                }else{
                    opList.push(String.format("<a href=\"{0}?gameId="+rowobj['id']+"\" class=\"btn btn-primary btn-sm\" >{1}</a> ", op['url'],op['txt']));
                }
            }
            return opList.join('');
        }

        function responseFunc(res){
            data = res.data;
            count = res.count;
            $('.totalTitle').html('游戏总数: '+count+" 今日新增: 0");
            return data;
        }

        function responseError(status) {
            location.reload();
        }

        function status(value,row,index){
            eval('var rowobj='+JSON.stringify(row))
            var statusstr = '';
            if(value == '0'){
                statusstr = '<span class="label label-warning">否</span>';
            }else if(value == '1'){
                statusstr = '<span class="label label-success">是</span>';
            }

            return [
                statusstr
            ].join('');
        }

 //初始化子表格(无线循环)
function InitSubTable(index, row, $detail) {
        var parentAg = row.id;
        var cur_table = $detail.html('<table table-bordered table-hover definewidth></table>').find('table');
        $(cur_table).bootstrapTable({
                url: '/admin/game/server/list?list=1',
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
                    field: 'serverUrl',
                    title: '游戏服务器',
                    align: 'center',
                    valign: 'middle'
                },{
                    field: 'desc',
                    title: '描述',
                    align: 'center',
                    valign: 'middle'
                },{
                    field: 'op',
                    title: '操作',
                    align: 'center',
                    valign: 'middle',
                    formatter:getOp
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
              sendParameter['id'] = parentAg;
              return sendParameter;
        }

        function getOp(value,row,index){
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({gameId : rowobj['id']});
                var cStr = str.replace(/\"/g, "@");
                opList.push(String.format("<a href=\"#\" class=\"btn btn-primary btn-sm btn-xs\" onclick=\"comfirmServer(\'{0}\', \'{1}\', \'{2}\')\"><i class=\"fa fa-edit\"> {3} </i></a> ", op['url'], op['method'], cStr, op['txt']));

            }
            return opList.join('');
        }
}


</script>
%rebase admin_frame_base
