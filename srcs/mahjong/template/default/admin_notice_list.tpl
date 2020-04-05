  <div class="block">
            %include admin_frame_header
            <div class="content">
            <div class="table-toolbar" style="float:left">
                <a id="add" href='{{info["createUrl"]}}' class="btn btn-primary">
                    <i class="btn-label fa fa-plus"></i>{{info['addTitle']}}
                </a>
            </div>
                <table id="dataTable" class="table table-bordered table-hover"></table>
            </div>
  </div>
<script type="text/javascript">

    startDate = $("#pick-date-start").val();
    endDate   = $("#pick-date-end").val();
    $('#dataTable').bootstrapTable({
          method: 'get',
          url: '{{info["tableUrl"]}}',
          contentType: "application/json",
          datatype: "json",
          cache: true,
          checkboxHeader: true,
          striped: true,
          pagination: true,
          pageSize: 15,
          pageList: [15, 50, 100,'All'],
          // queryParamsType:'',
          // sidePagination:"server",
          showColumns: true,
          sortOrder:"desc",
          sortName: 'status',
          minimumCountColumns: 2,
          clickToSelect: true,
          search:true,
          //smartDisplay: true,
          responseHandler:responseFun,
          //onLoadError:responseError,
          queryParams:getSearchP,
          //sortOrder: 'asc',
          //sortable: true,                     //是否启用排序
          showExport:true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          columns: [
          {
              field: 'time',
              title: '发布时间',
              align: 'center',
              valign: 'middle'
          },{
              field: 'groupId',
              title: '发布人公会号',
              align: 'center',
              valign: 'middle'
          },{
              field: 'title',
              title: '消息标题',
              align: 'center',
              valign: 'middle'
          },{
              field: 'messageType',
              title: '消息类型',
              align: 'center',
              valign: 'middle',
              formatter:msgType
          },{
              field: 'content',
              title: '消息内容',
              align: 'center',
              valign: 'middle'
          },{
              field: 'status',
              title: '消息状态',
              align: 'center',
              valign: 'middle',
              formatter:status
          },{
              field: 'op',
              title: '操作',
              align: 'center',
              valign: 'middle',
              formatter:getOp
          }]
    });


        function status(value,row,index){
            eval('var rowobj='+JSON.stringify(row))
            var statusstr = '';
            if(rowobj['status'] == '0'){
                statusstr = '<span class="label label-danger">未推送</span>';
            }else if(rowobj['status'] == '1'){
                statusstr = '<span class="label label-success">推送中</span>';
            }
            return [
                statusstr
            ].join('');
        }

        function msgType(value,row,index){
            eval('var rowobj='+JSON.stringify(row))
            var statusstr = '';
            if(rowobj['messageType'] == '0'){
                statusstr = '<span class="label label-primary">系统消息</span>';
            }else if(rowobj['messageType'] == '1'){
                statusstr = '<span class="label label-success">活动信息</span>';
            }else{
                statusstr = '<span class="label label-warning">邮件</span>';
            }
            return [
                statusstr
            ].join('');
        }

        function getOp(value,row,index){
              var showComfirUrl = [
                    '/admin/notice/push/HALL',
                    '/admin/notice/push/FISH',
                    '/admin/notice/del',
              ];
              eval('rowobj='+JSON.stringify(row));
              var opList = []
              for (var i = 0; i < rowobj['op'].length; ++i) {
                  var op = rowobj['op'][i];
                  var str = JSON.stringify({id : rowobj['id']});
                  var cStr = str.replace(/\"/g, "@");
                  var param = rowobj['id'] ;
                  if(showComfirUrl.indexOf(op['url'])>-1){
                      opList.push(String.format("<a href=\"#\" class=\"btn btn-primary btn-sm\" onclick=\"comfirmDialog(\'{0}\', \'{1}\', \'{2}\')\"><i class=\"glyphicon glyphicon-edit\"> {3} </i></a> ", op['url'], op['method'], cStr, op['txt']));
                  }else{
                      opList.push(String.format("<a href=\"{0}?noticeId={1}\" class=\"btn btn-primary btn-sm\"><i class=\"glyphicon glyphicon-edit\"> {2}</i></a> ", op['url'], param, op['txt']));
                  }
              }
              return opList.join('');
        }

        //前台查询参数
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

            data = res.data;
            count= res.count;
            //实时刷
            return data;
        }

        function responseError(status) {
            location.reload();
        }
</script>
%rebase admin_frame_base
