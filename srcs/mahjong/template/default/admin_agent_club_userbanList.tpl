<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<div class="block">
        <div class='header bordered-bottom bordered-themesecondary' id="crumb">
             <h3 style="font-weight:bold">
               %if info.get('title',None):
                 {{info['title']}}
               %end
            </h3>
        </div>
        <div>
          <button id="btn_add" onclick="createUserban({{date}})" type="button" class="btn btn-sm btn-primary">
            <span class="glyphicon glyphicon-plus">
                 添加同桌禁止用户&nbsp;&nbsp;
            </span>
          </button>
        </div>
        <div class="content">
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
          columns: [{
              field: 'id',
              title: '用户ID',
              align: 'center',
              valign: 'middle',
              sortable: true
           },{
              field: 'nickname',
              title: '用户昵称',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'username',
              title: '用户账号',
              align: 'center',
              valign: 'middle',
              sortable: true
           },{
              field: 'op',
              title: '操作',
              align: 'center',
              valign: 'middle',
              sortable: true,
              formatter:getOp
          }],
          onExpandRow: function (index, row, $detail) {
              console.log(index,row,$detail);
              InitSubTable(index, row, $detail);
          }

    });
        function getOp(value,row,index){
            var showDataUrls = [
                '/admin/agent/clublist/showDayd11'
            ];
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({id : rowobj['id']});
                var cStr = str.replace(/\"/g, "@");
                var urltype = op['url'].substring(op['url'].length-7);
                var url =  op['url'] + '/' + rowobj['clubid'] + '/' + rowobj['id']
                if (op['url'].substring(op['url'].length-4) == 'User')
                    if ( urltype == 'remUser' )
                         opList.push(String.format("<a href='javascript:;' onclick=\"remUserDialog(\'{0}\', \'{1}\', \'{2}\', \'{4}\', \'{5}\');\" class=\"btn btn-danger btn-sm \"  >{3}</a> ", url,op['method'],cStr,op['txt'],rowobj['id'],urltype));
                    else
                        opList.push(String.format("<a href='javascript:;' onclick=\"showActiveDialog(\'{0}\', \'{1}\', \'{2}\', \'{4}\', \'{5}\');\" class=\"btn btn-sm btn-primary\" >{3}</a> ", url,op['method'],cStr,op['txt'],rowobj['id'],urltype));
                else //不使用弹出窗口打开页面
                    opList.push(String.format("<a href=\"{0}?club={1}\" class=\"btn btn-sm btn-primary\">{2}</a>",op['url'],rowobj['club_id'],op['txt']));
            }
            return opList.join('');
        }

        function getSearchP(p) {
            startDate = $("#pick-date-start").val();
            endDate = $("#pick-date-end").val();

            sendParameter = p;
            sendParameter['startDate'] = startDate;
            sendParameter['endDate'] = endDate;

            return sendParameter;
        }

      function responseFun(res){
          count= res.total;
          //实时刷
          //$('.count').text(String.format("会员总人数:{0}",count));
          pageNumber = parseInt(res.pageNumber);
          return {"rows": res.data,
                  "total": res.count
          };
      }

        function responseError(status) {
            location.reload();
        }
}

function InitSubTable(index, row, $detail) {
        var parentAg = row.id;
        var table = String.format('<table table-bordered table-hover definewidth id="child_table{0}"></table>', parentAg)
        var cur_table = $detail.html(table).find('table');
        $(cur_table).bootstrapTable({
                url: '{{ info['serversUrl'] }}',
                method: 'get',
                contentType: "application/json",
                datatype: "json",
                //striped: true,
                toolbar:'#toolbar',
                pagination: true,
                pageSize: 15,
                showRefresh: true,
                pageList: [10, 25, 50, 100],
                clickToSelect: true,
                queryParams: getSearchP,
                striped: true,
                minimumCountColumns: 2,
                showFooter: true,

                columns: [{
                      field: 'id',
                      title: '用户ID',
                      align: 'center',
                      valign: 'middle',
                      sortable: true
                   },{
                      field: 'nickname',
                      title: '用户昵称',
                      align: 'center',
                      valign: 'middle',
                      sortable: true
                  },{
                      field: 'username',
                      title: '用户账号',
                      align: 'center',
                      valign: 'middle',
                      sortable: true
                  },{
                      field: 'usertype',
                      title: '用户类型',
                      align: 'center',
                      valign: 'middle',
                      sortable: true,
                  },{
                      field: 'op',
                      title: '操作',
                      align: 'center',
                      valign: 'middle',
                      sortable: true,
                      formatter:getOpUserBan
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

        function getOpUserBan(value,row,index){
            var showDataUrls = [
                '/admin/agent/clublist/showDayd11'
            ];
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({id : rowobj['id']});
                var cStr = str.replace(/\"/g, "@");
                var urltype = op['url'].substring(op['url'].length-7);
                var url =  op['url'] + '/' + rowobj['clubid'] + '/' + rowobj['id'] + '/' + rowobj['userid']
                if (op['url'].substring(op['url'].length-4) == 'User')
                    if ( urltype == 'delUser' )
                         opList.push(String.format("<a href='javascript:;' onclick=\"remUserDialog(\'{0}\', \'{1}\', \'{2}\', \'{4}\', \'{5}\');\" class=\"btn btn-danger btn-sm \"  >{3}</a> ", url,op['method'],cStr,op['txt'],rowobj['id'],urltype));
                    else
                        opList.push(String.format("<a href='javascript:;' onclick=\"showActiveDialog(\'{0}\', \'{1}\', \'{2}\', \'{4}\', \'{5}\');\" class=\"btn btn-sm btn-primary\" >{3}</a> ", url,op['method'],cStr,op['txt'],rowobj['club_id'],urltype));
                else //不使用弹出窗口打开页面
                    opList.push(String.format("<a href=\"{0}?club={1}\" class=\"btn btn-sm btn-primary\">{2}</a>",op['url'],rowobj['club_id'],op['txt']));
            }
            return opList.join('');
        }
}
</script>

<script>
    function createUserban(clubid){
      layer.open({
    	    id:1,
            type: 1,
            title: '请输入要新增的同桌禁止信息。',
            skin:'layui-layer-rim',
            area:['450px', 'auto'],
            content: ' <div class="row" style="width: 420px;  margin-left:7px; margin-top:10px;">'
            +'<div class="col-sm-12">'
            +'<div class="input-group">'
            +'<span class="input-group-addon">用户ID:</span>'
            +'<input id="userid" style="width:280px;" type="input" class="form-control" placeholder="请输入用户ID">'
            +'</div>'
            +'</div>'
              +'<div class="col-sm-12" style="margin-top: 10px">'
              +'<div class="input-group">'
              +'<span class="input-group-addon">禁止ID:</span>'
              +'<input id="userbanid" style="width:280px;" type="input" class="form-control" placeholder="请输入禁止用户ID，多用户以逗号分隔。">'
              +'</div>'
              +'</div>'
              +'</div>'
              +'<div class="col-sm-12" style="margin-top: 10px">'
              +'<div class="input-group">'
              +'</div>'
              +'</div>'
            ,
            btn:['确认','取消'],
            yes:function(index){
                var userid = $('#userid').val();
                var userbanid = $('#userbanid').val();
                var urls =  '/admin/agent/clublist_userban/list/createUserBan/' +  clubid  +'/' +  userid + '/' +  userbanid;
                var method = "POST";
                var jsonStr = '{@id@:@2202@}';
                normalAjaxStrData(urls,method,jsonStr);
                layer.close(index);
                $('#dataTable').bootstrapTable('refresh');
            },

        });
    };

    function showActiveDialog(url,method,jsonStr,text,utype){
        var playid = text.toString();
        layer.open({
    	    id:1,
            type: 1,
            title: '请输入要同桌禁止/移除的用户（多用户以逗号隔开）',
            skin:'layui-layer-rim',
            area:['450px', 'auto'],
            content: ' <div class="row" style="width: 420px;  margin-left:7px; margin-top:10px;">'
                +'<div class="col-sm-12">'
                +'<div class="input-group">'
                +'<span class="input-group-addon">请输入:</span>'
                +'<input id="clubplayid" type="input"  style="width:280px;" class="form-control" placeholder="请输入玩家的ID">'
                +'</div>'
                +'</div>'
                  +'<div class="col-sm-12" style="margin-top: 10px">'
                  +'<div class="input-group">'
                  +'</div>'
                  +'</div>'
                  +'</div>'
            ,
            btn:['确认','取消'],
            yes:function(index){
                var clubid = url.split('/').slice(-2,-1);
                var playaccont = $('#clubplayid').val();
                var urls =  url  + '/' + playaccont;
                normalAjaxStrData(urls,method,jsonStr);
                layer.close(index);
                var child_table = String.format("#child_table{0}", playid);
                $(child_table).bootstrapTable('refresh',{'url': String.format('/admin/agent/clublist_userban/list?list=1&club={0}&id={1}',clubid,playid)});
            },
        });
    };

    function remUserDialog(url,method,jsonStr,text,utype){
              if (utype == 'remUser')
                  txt = '删除该玩家的同桌禁止记录。'
              else
                  txt = '删除该玩家。'
              var comfirmTxt = '是否确定此操作。<br>' + txt;
              layer.open({
                  title: [
                     '后台提醒你',
                     'background-color:#204077; color:#fff;'
                  ]
                  ,anim: 'up'
                  ,content: comfirmTxt
                  ,btn: ['确认', '取消']
                  ,fixed:true
                  ,style: 'width:550px;position:fixed;top:25%;left:50%;margin-left:-250px;'
                  ,yes:function(index){
                       normalAjaxStrData(url,method,jsonStr);
                       layer.close(index);
                       var clubid = url.split('/').slice(-3,-2);
                       var playid = url.split('/').slice(-1);
                       var child_table = String.format("#child_table{0}", playid);
                       if (utype == 'remUser'){
                           $('#dataTable').bootstrapTable('refresh');
                           }
                       else{
                           $(child_table).bootstrapTable('refresh',{'url': String.format('/admin/agent/clublist_userban/list?list=1&club={0}&id={1}',clubid,playid)});
                  }}
              });
        }
</script>
%rebase admin_frame_base
