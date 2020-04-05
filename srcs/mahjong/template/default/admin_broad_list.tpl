  <div class="block">
            %include admin_frame_header
            <div class="content">
                <div class="table-toolbar" style="float:left">
                     <button id="btn_add" type="button" class="btn btn-sm btn-primary">
                        <span class="glyphicon glyphicon-plus">
                            <a href="{{info['createUrl']}}" style='color:#FFF;text-decoration:none;'>{{info['addTitle']}}</a>
                        </span>
                    </button>
                    <button id="btn_add" onclick="_settingBatchDel();" type="button" class="btn btn-sm btn-primary">
                        <span class="glyphicon glyphicon-asterisk">
                            <a href="javascript:;" style='color:#FFF;text-decoration:none;'>批量清除</a>
                        </span>
                    </button>
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
          pageList: '{{PAGE_LIST}}',
          // queryParamsType:'',
          // sidePagination:"server",
          showColumns: true,
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
              checkbox: true
          },
          {
              field: 'start_date',
              title: '起始时间',
              align: 'center',
              valign: 'middle'
          },{
              field: 'end_date',
              title: '结束时间',
              align: 'center',
              valign: 'middle'
          },{
              field: 'parent_ag',
              title: '创建公会',
              align: 'center',
              valign: 'middle'
          },{
              field: 'content',
              title: '内容',
              align: 'center',
              valign: 'middle'
          },{
              field: 'per_sec',
              title: '间隔/s',
              align: 'center',
              valign: 'middle'
          },{
              field: 'broad_type',
              title: '所属类型',
              align: 'center',
              valign: 'middle',
              formatter:getType
          },{
              field: 'status',
              title: '当前状态',
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
              statusstr = '<span class="label label-warning">预推送</span>';
          }else if(rowobj['status'] == '1'){
              statusstr = '<span class="label label-success">推送中</span>';
          }else if(rowobj['status'] == '2'){
              statusstr = '<span class="label label-danger">已结束</span>';
          }
          return [
              statusstr
          ].join('');
      }

      function getType(value,row,index){
          eval('var rowobj='+JSON.stringify(row))
          var statusstr = '';
          if(rowobj['broad_type'] == '0'){
              statusstr = '<span class="label label-success">全服维护广播</span>';
          }else if(rowobj['broad_type'] == '1'){
              statusstr = '<span class="label label-success">全服循环广播</span>';
          }else if(rowobj['broad_type'] == '2'){
              statusstr = '<span class="label label-success">地区维护广播</span>';
          }else{
              statusstr = '<span class="label label-success">地区循环广播</span>';
          }
          return [
              statusstr
          ].join('');
      }

        function getOp(value,row,index){
            var comfirUrl = [
                '/admin/game/broadcast/batch_del'
            ];
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({broadIds : rowobj['broad_id'],broad_belone:"{{info['broad_belone']}}"});
                var cStr = str.replace(/\"/g, "@");
                var param = rowobj['id'] ;
                if(comfirUrl.indexOf(op['url'])>=0)
                    opList.push(String.format("<a href=\"#\" class=\"btn btn-primary btn-sm\" onclick=\"comfirmDialog(\'{0}\', \'{1}\', \'{2}\',\'清除后广播将无法还原，是否继续？\')\"><i class=\"glyphicon glyphicon-edit\"> {3} </i></a> ", op['url'], op['method'], cStr, op['txt']));
                else
                    opList.push(String.format("<a href=\"{0}?id={1}\" class=\"btn btn-primary btn-sm\"><i class=\"glyphicon glyphicon-edit\"> {2}</i></a> ", op['url'], param, op['txt']));
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

        function _settingBatchDel(){
          var broadIds = $.map($('#dataTable').bootstrapTable('getSelections'),function(row){
              return row.broad_id;
          });

          if (!broadIds.length){    //如果没选择直接return
              console.log('---------------had not selected.. return');
              return;
          }

          var remoteUrl = "{{info['batchDelUrl']}}",
              method    = "POST",
              jsonStr   = {'broadIds':broadIds.join(','),'broad_belone':"{{info['broad_belone']}}"}

          console.log('----------------select broadIds['+broadIds+']');
          formAjax(remoteUrl,method,jsonStr,'正在执行...,');
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
