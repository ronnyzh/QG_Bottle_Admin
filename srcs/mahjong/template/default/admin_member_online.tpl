<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/checkEvent.js?{{RES_VERSION}}"></script>

<div class="block">
%include admin_frame_header
</div>

<div class="rows">
<div class='col-md-12'>
        <div class="panel panel-info">
        <div class="panel-heading">
                <span class="panel-title" id="txt">房卡模式在线</span>
            </div>
        <div class="content">
            <table id="memberOLtable" class="table table-bordered table-hover"></table>
        </div>
            </div>
</div>
</div>

<div class="block">
<div class='header bordered-bottom bordered-themesecondary' id="crumb">
     <h3 style="font-weight:bold">
        &nbsp;
    </h3>
</div>
</div>


<div class='rows' style='margin-bottom:10px;'>
    <div class='col-md-12'>
        <div class="panel panel-info">
        <div class="panel-heading">
                <span class="panel-title" id="txt">金币场模式在线</span>
            </div>
        <div class="content_gold">
            <table id="memberOLtable1" class="table table-bordered table-hover"></table>
        </div>
        </div>
    </div>
</div>

<script type="text/javascript">
    /**
      * 服务端刷新表格
      --------------------------------------------
    */
    $(function () {
        $('#memberOLtable').bootstrapTable({
            method:'get',
            url   :'{{info["listUrl"]}}',
            smartDisplay: true,
            pagination: true,
            pageSize: 15,
            pageList: [15,50,100],
            showRefresh: true,
            search: true,
            responseHandler:responseFunc,
            columns: [
                      [{
                          "halign":"left",
                          "align":"left",
                          "class": 'count',
                          "colspan": 13
                      }],
                      [{
                          field: 'id',
                          title: '玩家编号',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'name',
                          title: '玩家名称',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'gameid',
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
                          field: 'parentAg',
                          title: '所属公会',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'clientKind',
                          title: '客户端类型',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'roomCard',
                          title: '钻石余额',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'roomTag',
                          title: '房间号',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'date',
                          title: '登录时间',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'login_ip',
                          title: '登录IP',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'serverTag',
                          title: '服务器标识',
                          align: 'center',
                          valign: 'middle',
                          sortable: false
                      },{
                          field: 'op',
                          title: '操作',
                          align: 'center',
                          valign: 'middle',
                          sortable: false,
                          formatter:getOp
                }]]
        });

        function getOp(value,row,index){
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            opList.push("<a href='javascript:;' onClick=\"comfirmDialog('/admin/member/kicks?account="+rowobj['account']+"&groupId="+rowobj['parentAg']+"','GET','{}')\" class=\"btn btn-sm btn-primary\" <i class=\"fa fa-edit\"> </i>踢出</a> ");
            return opList.join('');
        }

        function responseFunc(res){
            data = res.data;
            count= res.count;
            //实时刷
            $('.count').text(String.format("当前在线人数: {0}",count));
            return data;
        }
    });
     $(function () {
        $('#memberOLtable1').bootstrapTable({
            method:'get',
            url   :'{{info["listUrl"]}}',
            smartDisplay: true,
            pagination: true,
            pageSize: 15,
            pageList: [15,50,100],
            showRefresh: true,
            search: true,
            responseHandler:responseFunc,
            columns: [
                      [{
                          "halign":"left",
                          "align":"left",
                          "class": 'gold_count',
                          "colspan": 13
                      }],
                      [{
                          field: 'id',
                          title: '玩家编号',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'name',
                          title: '玩家名称',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'gameid',
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
                          field: 'parentAg',
                          title: '所属公会',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'clientKind',
                          title: '客户端类型',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'roomCard',
                          title: '钻石余额',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'roomTag',
                          title: '房间号',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'date',
                          title: '登录时间',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'login_ip',
                          title: '登录IP',
                          align: 'center',
                          valign: 'middle',
                          sortable: true
                      },{
                          field: 'serverTag',
                          title: '服务器标识',
                          align: 'center',
                          valign: 'middle',
                          sortable: false
                      },{
                          field: 'op',
                          title: '操作',
                          align: 'center',
                          valign: 'middle',
                          sortable: false,
                          formatter:getOp
                }]]
        });

        function getOp(value,row,index){
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            opList.push("<a href='javascript:;' onClick=\"comfirmDialog('/admin/member/kicks?account="+rowobj['account']+"&groupId="+rowobj['parentAg']+"','GET','{}')\" class=\"btn btn-sm btn-primary\" <i class=\"fa fa-edit\"> </i>踢出</a> ");
            return opList.join('');
        }

        function responseFunc(res){
            data = res.data_gold;
            count_gold= res.count_gold;
            //实时刷
            $('.gold_count').text(String.format("当前在线人数: {0}",count_gold));
            return data;
        }
    });
</script>
<script type="text/javascript">
    checker.refreshMemberOlTable();
</script>
%rebase admin_frame_base
