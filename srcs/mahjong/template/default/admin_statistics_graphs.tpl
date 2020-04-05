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
        <div class='rows' style='margin-bottom:10px;'>
            <div class='col-md-6'>
                <div class="panel panel-info">
                    <div class="panel-heading">
                        <span class="panel-title" id="txt1">注册人数统计</span>
                    </div>
                    <div class="panel-body">
                        <div id="regMain" style="width:100%;height:400px;"></div>
                    </div>
                </div>
            </div>
            <div class='col-md-6'>
                <div class="panel panel-info">
                    <div class="panel-heading">
                        <span class="panel-title" id="txt1">活跃人数统计</span>
                    </div>
                    <div class="panel-body">
                        <div id="activeMain" style="width:100%;height:400px;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="cl-mcont">
    <div class="block">
            <div class='col-md-6'>
                <div class="panel panel-info">
                    <div class="panel-heading">
                        <span class="panel-title" id="txt1">商城订单统计</span>
                    </div>
                    <div class="panel-body">
                        <div id="orderMain" style="width:100%;height:400px;"></div>
                    </div>
                </div>
            </div>
            <div class='col-md-6'>
                <div class="panel panel-info">
                    <div class="panel-heading">
                        <span class="panel-title" id="txt1">代理订单统计</span>
                    </div>
                    <div class="panel-body">
                        <div id="orderAgentMain" style="width:100%;height:400px;"></div>
                    </div>
                </div>
            </div>
    </div>
</div>

<div class="cl-mcont">
    <div class="block">
            <div class='col-md-12'>
                <div class="panel panel-info">
                    <div class="panel-heading">
                        <span class="panel-title" id="txt1">游戏耗钻统计</span>
                    </div>
                    <div class="panel-body">
                        <div id="gameRoomcardMain" style="width:100%;height:400px;"></div>
                    </div>
                </div>
            </div>
    </div>
</div>

<div class="cl-mcont">
    <div class="block">
            <div class='col-md-12'>
                <div class="panel panel-info">
                    <div class="panel-heading">
                        <span class="panel-title" id="txt1">各游戏耗钻统计</span>
                    </div>
                    <div class="panel-body">
                        <div id="gameRoomcardEachMain" style="width:100%;height:400px;"></div>
                    </div>
                </div>
            </div>
    </div>
</div>

<div class="cl-mcont">
    <div class="block">
            <div class='col-md-12'>
                <div class="panel panel-info">
                    <div class="panel-heading">
                        <span class="panel-title" id="txt1">我的售钻报表</span>
                    </div>
                    <div class="panel-body">
                        <div id="saleReportMain" style="width:100%;height:400px;"></div>
                    </div>
                </div>
            </div>
    </div>
</div>

<div class="cl-mcont">
    <div class="block">
            <div class='col-md-6'>
                <div class="panel panel-info">
                    <div class="panel-heading">
                        <span class="panel-title" id="txt1">下级代理售钻报表</span>
                    </div>
                    <div class="panel-body">
                        <div id="agentSaleReport" style="width:100%;height:400px;"></div>
                    </div>
                </div>
            </div>
            <div class='col-md-6'>
                <div class="panel panel-info">
                    <div class="panel-heading">
                        <span class="panel-title" id="txt1">下级代理购钻报表</span>
                    </div>
                    <div class="panel-body">
                        <div id="agentBuyReport" style="width:100%;height:400px;"></div>
                    </div>
                </div>
            </div>
    </div>
</div>

<div class="cl-mcont">
    <div class="block">
            <div class='col-md-12'>
                <div class="panel panel-info">
                    <div class="panel-heading">
                        <span class="panel-title" id="txt1">利润占成报表</span>
                    </div>
                    <div class="panel-body">
                        <div id="rateReport" style="width:100%;height:400px;"></div>
                    </div>
                </div>
            </div>
    </div>
</div>


<script>
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 6);
    $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
    $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));
</script>

<script type="text/javascript">
    // 基于准备好的dom，初始化echarts实例
    function graphs(arg1, url) {
        var myChart = echarts.init(document.getElementById(arg1));
        var resizeWorldMapContainer = function () {
            document.getElementById(arg1).style.width = $('.panel-body').attr('width');
            document.getElementById(arg1).style.height = $('.panel-body').attr('height');

        };
        resizeWorldMapContainer();
        // 指定图表的配置项和数据
        $.getJSON(url, function (data) {
            myChart.setOption({
                tooltip: {
                    trigger: 'axis'
                },
                legend: {
                    data: data.data.legen
                },
                calculable: true,
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
                xAxis: [
                    {
                        type: 'category',
                        boundaryGap: false,
                        data: data.data.week
                    }
                ],
                yAxis: [
                    {
                        type: 'value'
                    }
                ],
                series: data.data.series
            });
        });


        // 使用刚指定的配置项和数据显示图表。
        window.onresize = function () {
            //重置容器高宽
            resizeWorldMapContainer();
            myChart.resize();
        };
    }

    graphs('regMain', "{{ info['show_regMember_url'] }}");
    graphs('activeMain', "{{ info['show_activeMember_url'] }}");
    graphs('orderMain', "{{ info['show_wechatOrder_url'] }}");
    graphs('orderAgentMain', "{{ info['show_agentOrder_url'] }}");
    graphs('saleReportMain', "{{ info['show_saleReport_url'] }}");
    graphs('agentSaleReport', "{{ info['show_agentSaleReport_url'] }}");
    graphs('agentBuyReport', "{{ info['show_agentBuyReportMain_url'] }}");
    graphs('rateReport', "{{ info['show_rateReport_url'] }}");
    graphs('gameRoomcardMain', '{{ info['show_gameRoomcard_url'] }}');
    graphs('gameRoomcardEachMain', '{{ info['show_gameRoomcardEach_url'] }}');
</script>
%rebase admin_frame_base



