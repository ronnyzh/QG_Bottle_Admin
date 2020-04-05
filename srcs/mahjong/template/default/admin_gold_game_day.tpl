<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<script type="text/javascript" src="{{ info['STATIC_ADMIN_PATH']}}/js/echarts.min.js"></script>
<div class="cl-mcont">
    <div class="block">
        <div class="header">
            <h3>
                %if info.get('title',None):
                {{ info['title']}}
                %end
            </h3>
        </div>
        <div class="content">
            <div class="table-toolbar" style="float:left;width:100%;position:relative;top:3.2em">
                <div class='col-sm-12' style='margin-left:1em;'>
                    <div style='float:left;margin-left:1em;' class="input-group date datetime col-md-1 col-xs-1"
                         data-min-view="2" data-date-format="yyyy-mm-dd">
                        <input class="form-control" size="12" type="text" style='width:140px;height:28px;'
                               id='pick-date-start' name="startdate" value="{{ lang.INPUT_LABEL_START_DATE_TXT }}"
                               readonly>
                        <span class="input-group-addon btn btn-primary pickdate-btn"><span
                                class="glyphicon pickdate-btn pickdate glyphicon-th"></span>
                    </div>

                    <div style='float:left;margin-left:1em;' class="input-group date datetime col-md-1 col-xs-1"
                         data-min-view="2" data-date-format="yyyy-mm-dd">
                        <input class="form-control" style='width:140px;height:28px;' id='pick-date-end' name="enddate"
                               size="12" type="text" value="{{ lang.INPUT_LABEL_END_DATE_TXT }}" readonly>
                        <span class="input-group-addon btn btn-primary pickdate-btn"><span
                                class="pickdate glyphicon pickdate-btn glyphicon-th"></span></span>
                    </div>
                    <div style='float:left;margin-left:1em;'>
                        <button id="btn_query" class='btn btn-primary btn-sm btn-xs'><i
                                class='fa fa-search'></i>{{ lang.INPUT_LABEL_QUERY }}</button>
                        <button id="btn_lastMonth" class='btn btn-sm btn-xs'>{{ lang.INPUT_LABEL_PREV_MONTH }}</button>
                        <button id="btn_thisMonth" class='btn btn-sm btn-xs '>{{ lang.INPUT_LABEL_CURR_MONTH }}</button>
                        <button id="btn_lastWeek" class='btn btn-sm btn-xs '>{{ lang.INPUT_LABEL_PREV_WEEK }}</button>
                        <button id="btn_thisWeek" class='btn btn-sm btn-xs'>{{ lang.INPUT_LABEL_CURR_WEEK }}</button>
                        <button id="btn_yesterday" class='btn btn-sm btn-xs'>{{ lang.INPUT_LABEL_PREV_DAY }}</button>
                        <button id="btn_today" class='btn btn-sm btn-xs'>{{ lang.INPUT_LABEL_CURR_DAY }}</button>
                        <button id="btn_syday" class='btn btn-sm btn-xs'>所有</button>
                        <div class='clearfix'>
                        </div>
                    </div>
                </div>
            </div>
            <table id="dataTable" class="table table-bordered table-hover"></table>
        </div>
    </div>
</div>


<div class='rows' style='margin-bottom:10px;'>
    <div class='col-md-12'>
        <div class="panel panel-info">
        <div class="panel-heading">
                <span class="panel-title" id="txt">数据统计（默认最近一周）</span>
            </div>
            <div class="panel-body">
                <table id="table2" class="table table-bordered table-hover"></table>
            </div>
               <div class="panel-heading">
                <h3 class="panel-title">数据统计（总数据）</h3>
            </div>
            <div class="panel-body">
                <table id="table1" class="table table-bordered table-hover"></table>
            </div>

        </div>
    </div>
</div>

<div class='rows' style='margin-bottom:10px;'>
    <div class='col-md-12'>
        <div class="panel panel-info">
            <div class="panel-heading">
               <span class="panel-title" id="txt1">图表数据统计（默认最近一周）</span>
            </div>
            <div>
                <span>游戏ID：<span>
                <input type="text" style='width:10%' id="gameid" name="gameid"  >
                <span>时间：<span>
                <select style='width:10%;height:26px;' id="gameType" name="gameType" >
                    <option value="%Y-%m-%d ">  日 </option>
                    <option value="%Y-%m "> 月 </option>
                    <option value="%Y "> 年</option>
                    <option value="%Y-%m-%d %H">  时 </option>
                    <option value="%Y-%m-%d %H:%i"> 分 </option>
                </select>
                <button value="1" name="button1"  onclick="test()">查询</button>
            </div>
            <div class="panel-body">
                <div id="main" style="width:100%;height:400px;"></div>
            </div>
        </div>
    </div>
</div>

<div class='rows' style='margin-bottom:10px;'>
    <div class='col-md-12'>
        <div class="panel panel-info">
            <div class="panel-heading">
               <span class="panel-title" id="txt2">图表数据统计（默认最近一周）</span>
            </div>
            <div>
                <span>游戏ID：<span>
                <input type="text" style='width:10%' id="gameid1" name="gameid1"  >
                <span>时间：<span>
                <select style='width:10%;height:26px;' id="gameType1" name="gameType1" >
                    <option value="%Y-%m-%d ">  日 </option>
                    <option value="%Y-%m "> 月 </option>
                    <option value="%Y "> 年</option>
                    <option value="%Y-%m-%d %H">  时 </option>
                    <option value="%Y-%m-%d %H:%i"> 分 </option>
                </select>
                <button value="1" name="button1"  onclick="test1()">查询</button>
            </div>
            <div class="panel-body">
                <div id="main1" style="width:100%;height:400px;"></div>
            </div>
        </div>
    </div>
</div>

<script>
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 6);
    $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
    $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));
    var select = document.getElementById("gameType");
    var gameid = document.getElementById('gameid');
    var select1 = document.getElementById("gameType1");
    var gameid1 = document.getElementById('gameid1');
</script>

<script>
    function datalook(){
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        obj_look = document.getElementById("txt");
        obj_look.innerHTML = "数据统计：" + startDate + ' 到 '+ endDate;
        obj_look1 = document.getElementById("txt1");
        obj_look1.innerHTML = "图表数据统计：" + startDate + ' 到 '+ endDate;
        obj_look1 = document.getElementById("txt1");
        obj_look1.innerHTML = "图表数据统计：" + startDate + ' 到 '+ endDate;
    }
    function test(){
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        gametype = select.value;
        gameid = $("#gameid").val();
        loadTwoLine();
    }
    function test1(){
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        gametype1 = select1.value;
        gameid1 = $("#gameid1").val();
        loadLine();
    }
</script>

<script type="text/javascript">
  /**------------------------------------------------
    *  代理操作日志
    -------------------------------------------------
  */
  function initTable() {
     startDate = $("#pick-date-start").val();
     endDate   = $("#pick-date-end").val();
     gametype = select.value;
     gameid = $("#gameid").val();
     gametype1 = select1.value;
     gameid1 = $("#gameid1").val();
     $("#dataTable").bootstrapTable({
                url: "{{info['listUrl']}}",
                method: 'get',
                contentType: "application/json",
              datatype: "json",
              striped: true,
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
              clickToSelect: true,
              responseHandler:responseFun,
              queryParams:getSearchP,

                columns: [{
                field: 'number',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '序号'
            }, {
                field: 'create_time',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '日期'
            }, {
                field: 'game_id',
                align: 'center',
                valign: 'middle',
                sortable: true,
                title: '游戏ID',
            }, {
                field: 'gamename',
                align: 'center',
                sortable: true,
                valign: 'middle',
                title: '游戏名称',
             }, {
                field: 'count',
                align: 'center',
                sortable: true,
                valign: 'middle',
                title: ' 游戏参与次数',
             }, {
                field: 'single_count',
                align: 'center',
                sortable: true,
                valign: 'middle',
                title: ' 游戏参与人数',
             }, {
                field: 'pre_balance',
                title: '总用户输赢前金额合计',
                align: 'center',
                valign: 'middle',
                sortable: true,
                footerFormatter: function (value) {
                    var count = 0;
                    for (var i in value) {
                        count += value[i].pre_balance;
                    }
                    return '输赢前金额金额总合计：<br>' + count;
                }
            }, {
                field: 'balance',
                title: '总用户输赢金额合计',
                align: 'center',
                valign: 'middle',
                sortable: true,
                footerFormatter: function (value) {
                    var count = 0;
                    for (var i in value) {
                        count += value[i].balance;
                    }
                    return '总用户输赢金额合计总合计：<br>' + count;
                }
            }, {
                field: 'after_balance',
                align: 'center',
                valign: 'middle',
                sortable: true,
                title: '总用户输赢后金额合计',
                footerFormatter: function (value) {
                    var count = 0;
                    for (var i in value) {
                        count += value[i].after_balance;
                    }
                    return '总用户输赢后金额总合计：<br>' + count;
                }
            }, {
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

    function status(value,row,index){
        eval('var rowobj='+JSON.stringify(row))
        var statusstr = '';
        if(rowobj['status'] == '0'){
            statusstr = '<span class="label label-danger">卖钻方未确认</span>';
        }else if(rowobj['status'] == '1'){
            statusstr = '<span class="label label-success">卖钻方已确认</span>';
        }

        return [
            statusstr
        ].join('');
    }

    function getSearchP(p){
          startDate = $("#pick-date-start").val();
          endDate   = $("#pick-date-end").val();
          var searchId = $("#searchId").val();
          var gameid = $("#gameid").val();
          var gametype = select.value;
          var gameid1 = $("#gameid1").val();
          var gametype1 = select1.value;

          sendParameter = p;

          sendParameter['startDate'] = startDate;
          sendParameter['endDate']  = endDate;
          sendParameter['gametype'] = gametype;
          sendParameter['gameid'] = gameid;
          sendParameter['gametype1'] = gametype1;
          sendParameter['gameid1'] = gameid1;

          return sendParameter;
    }

    function getOp(value,row,index){
          eval('rowobj='+JSON.stringify(row))
          var opList = []
          for (var i = 0; i < rowobj['op'].length; ++i) {
              var op = rowobj['op'][i];
              var str = JSON.stringify({orderNo:rowobj["orderNo"]});
              var cStr = str.replace(/\"/g, "@");
             if (rowobj['status'] == '1')
                  continue;
              var contentUrl = op['url'];
              opList.push(String.format("<a href=\"#\" class=\"btn btn-primary btn-sm\" onclick=\"comfirmOrderDialog(\'{0}\',\'{1}\',\'{2}\')\"><i class=\"glyphicon glyphicon-edit\"> {3} </i></a> ",contentUrl,op['method'],cStr,op['txt']));
          }
          return opList.join('');
    }

    //获得返回的json 数据
    function responseFun(res){
        return res
    }
    $("#table2").bootstrapTable('refresh');
     datalook();
     loadTwoLine();
     loadLine();
 }
 sumTable();
 sumDayTable();

 function InitSubTable(index, row, $detail) {
        var parentAg = row.game_id;
        var parentTime = row.create_time;
        var cur_table = $detail.html('<table table-bordered table-hover definewidth></table>').find('table');
        $(cur_table).bootstrapTable({
                url: '{{ info['serversUrl'] }}',
                method: 'get',
                contentType: "application/json",
                datatype: "json",
                striped: true,
                toolbar:'#toolbar',
                pagination: true,
                pageSize: 15,
                pageList: [10, 25, 50, 100],
                clickToSelect: true,
                queryParams: getSearchP,
                striped: true,
                minimumCountColumns: 2,
                showFooter: true,

                columns: [{
                field: 'number',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '序号',

            }, {
                field: 'user_id',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '用户编号'
            }, {
                field: 'game_id',
                align: 'center',
                valign: 'middle',
                sortable: true,
                title: '游戏ID'
            }, {
                field: 'count',
                align: 'center',
                valign: 'middle',
                sortable: true,
                title: '参与局数'
            }, {
                field: 'pre_balance',
                title: '输赢前金额',
                align: 'center',
                valign: 'middle',
                sortable: true,

            }, {
                field: 'balance',
                title: '输赢金额',
                align: 'center',
                valign: 'middle',
                sortable: true,

            }, {
                field: 'after_balance',
                title: '输赢后',
                align: 'center',
                valign: 'middle',
                sortable: true,

            }, {
                field: 'create_time',
                title: '创建时间',
                align: 'center',
                valign: 'middle',
                sortable: true
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
              sendParameter['startDate'] = parentTime;
              return sendParameter;
        }
}
    function sumTable() {
        $("#table1").bootstrapTable({
          url: '{{ info['sumListUrl'] }}',
          method: 'get',
                pagination: true,
                pageSize: 10,
                pageList: [15, 25, 100],
                responseHandler:responseFun,
                queryParams:getSearchP,

            columns: [{
                field: 'game_id',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '游戏ID',
            },{
                field: 'gamename',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '游戏名称',
            },{
                field: 'game_sum',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '游戏参与次数',
            },{
                field: 'game_count',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '游戏参与人数',
            },],

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
    function sumDayTable() {
        $("#table2").bootstrapTable({
          url: '{{ info['dayListUrl'] }}',
          method: 'get',
                pagination: true,
                pageSize: 10,
                pageList: [15, 25, 100],
                responseHandler:responseFun,
                queryParams:getSearchP,

            columns: [{
                field: 'game_id',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '游戏ID',
            },{
                field: 'gamename',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '游戏名称',
            },{
                field: 'game_sum',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '游戏参与次数',
            },{
                field: 'game_count',
                sortable: true,
                align: 'center',
                valign: 'middle',
                title: '游戏参与人数',
            },],

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

    function loadTwoLine() {
        var myChart = echarts.init(document.getElementById('main'));
        var myArray=new Array();

        %for i,y in  enumerate( info['gameidlist'] ):
            myArray[{{i}}] = String({{y}})
        %end
        myChart.setOption({
            title: {
                text: '游戏参与总次数',
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                },
            },
            toolbox: {
                show: true,
                feature: {
                    mark: {show: true},
                    dataView: {show: true, readOnly: false},
                    magicType: {show: true, type: ['line', 'bar', 'tiled']},
                    restore: {show: true},
                    saveAsImage: {show: true}
                }
            },
            legend: {

                data:  myArray
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    data: [],
                    axisLabel :{
                        interval:0
                    },
                }
            ],
            yAxis: [
                {
                    type: 'value'
                }
            ],
            series: [
                   %for i in info['gameidlist']:
                    {
                    name: '{{ i }}',
                    type: 'bar',
                    data: [],
                    itemStyle: {
							normal: {
								label: {
									show: true, //开启显示
									position: 'top', //在上方显示
									textStyle: { //数值样式
										color: 'black',
										fontSize: 12
									}
								}
							}
				    },
                    },
                   %end
            ],
            dataZoom:{
              type: 'slider',
              realtime:true, //拖动滚动条时是否动态的更新图表数据
              height:45,//滚动条高度
              start:20,//滚动条开始位置（共100等份）
              end:60//结束位置（共100等份）
           }
        });
        myChart.showLoading();    //数据加载完之前先显示一段简单的loading动画
        var names = [];    //类别数组（实际用来盛放X轴坐标值）
         %for i in range(len( info['gameidlist'] )):
         var series{{ i }} = [];
        %end
        $.ajax({
            type: 'get',
            url: "{{ info['graphListUrl'] }}" + "&pageSize=10&pageNumber=1&sortOrder=asc&startDate=" + startDate + "&endDate=" + endDate + "&gametype=" + gametype + '&gameid=' + gameid,
            dataType: "json",        //返回数据形式为json
            success: function (result) {
                //请求成功时执行该函数内容，result即为服务器返回的json对象
                $.each(result.graph_data, function (index, item) {
                    names.push(item.datetime);    //挨个取出类别并填入类别数组
                    series0.push(item.game_count);
                });
                %for i,j in enumerate(info['gameidlist']):
                    $.each(result.graph_data, function (index, item) {
                    series{{i}}.push(item.id{{ j }});
                });
                %end

                myChart.hideLoading();
                myChart.setOption({
                    xAxis: {
                        data: names
                    },
                    series: [
                    %for i in range(len( info['gameidlist'] )):
                     {
                        data: series{{ i}}
                     },
                    %end
                    ]
                });
            },
            error: function (errorMsg) {
                //请求失败时执行该函数
                myChart.hideLoading();
            }
        });

    };

     function loadLine() {
        var myChart = echarts.init(document.getElementById('main1'));
        var myArray=new Array();

        %for i,y in  enumerate( info['gameidlist'] ):
            myArray[{{i}}] = String({{y}})
        %end
        myChart.setOption({
            title: {
                text: '游戏参与总人数',
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                },
            },
            toolbox: {
                show: true,
                feature: {
                    mark: {show: true},
                    dataView: {show: true, readOnly: false},
                    magicType: {show: true, type: ['line', 'bar', 'tiled']},
                    restore: {show: true},
                    saveAsImage: {show: true}
                }
            },
            legend: {

                data:  myArray
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    data: [],
                    axisLabel :{
                        interval:0
                    },
                }
            ],
            yAxis: [
                {
                    type: 'value'
                }
            ],
            series: [
                   %for i in info['gameidlist']:
                    {
                    name: '{{ i }}',
                    type: 'bar',
                    data: [],
                    itemStyle: {
							normal: {
								label: {
									show: true, //开启显示
									position: 'top', //在上方显示
									textStyle: { //数值样式
										color: 'black',
										fontSize: 12
									}
								}
							}
				    },
				    },
                   %end
            ],
            dataZoom:{
              type: 'slider',
              realtime:true, //拖动滚动条时是否动态的更新图表数据
              height:45,//滚动条高度
              start:20,//滚动条开始位置（共100等份）
              end:60//结束位置（共100等份）
           }
        });
        myChart.showLoading();    //数据加载完之前先显示一段简单的loading动画
        var names = [];    //类别数组（实际用来盛放X轴坐标值）
         %for i in range(len( info['gameidlist'] )):
         var series{{ i }} = [];
        %end
        $.ajax({
            type: 'get',
            url: "{{ info['graphListCountUrl'] }}" + "&pageSize=10&pageNumber=1&sortOrder=asc&startDate=" + startDate + "&endDate=" + endDate + "&gametype1=" + gametype1 + '&gameid1=' + gameid1,
            dataType: "json",        //返回数据形式为json
            success: function (result) {
                //请求成功时执行该函数内容，result即为服务器返回的json对象
                $.each(result.graph_data, function (index, item) {
                    names.push(item.datetime);    //挨个取出类别并填入类别数组
                    series0.push(item.game_count);
                });
                %for i,j in enumerate(info['gameidlist']):
                    $.each(result.graph_data, function (index, item) {
                    series{{i}}.push(item.id{{ j }});
                });
                %end

                myChart.hideLoading();
                myChart.setOption({
                    xAxis: {
                        data: names
                    },
                    series: [
                    %for i in range(len( info['gameidlist'] )):
                     {
                        data: series{{ i}}
                     },
                    %end
                    ]
                });
            },
            error: function (errorMsg) {
                //请求失败时执行该函数
                myChart.hideLoading();
            }
        });

    };
</script>
%rebase admin_frame_base