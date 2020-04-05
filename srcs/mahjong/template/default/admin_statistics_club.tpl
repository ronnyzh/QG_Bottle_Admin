<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<div class="block">
    %include admin_frame_header
    <div class="content">
        <div class="table-toolbar" style="float:left;width:100%;position:relative;top:3.2em">
            <div class='col-sm-12' style='margin-left:1em;'>
                <div style='float:left;margin-left:1em;' class="input-group date datetime col-md-1 col-xs-1"
                     data-min-view="2" data-date-format="yyyy-mm-dd">
                    <input class="form-control" size="12" type="text" style='width:140px;height:28px;'
                           id='pick-date-start' name="startdate" value="{{lang.INPUT_LABEL_START_DATE_TXT}}" readonly>
                    <span class="input-group-addon btn btn-primary pickdate-btn"><span
                            class="glyphicon pickdate-btn pickdate glyphicon-th"></span>
                </div>

                <div style='float:left;margin-left:1em;' class="input-group date datetime col-md-1 col-xs-1"
                     data-min-view="2" data-date-format="yyyy-mm-dd">
                    <input class="form-control" style='width:140px;height:28px;' id='pick-date-end' name="enddate"
                           size="12" type="text" value="{{lang.INPUT_LABEL_END_DATE_TXT}}" readonly>
                    <span class="input-group-addon btn btn-primary pickdate-btn"><span
                            class="pickdate glyphicon pickdate-btn glyphicon-th"></span></span>
                </div>
                <div style='float:left;margin-left:1em;'>
                    <button id="btn_query" class='btn btn-primary btn-sm btn-xs'><i class='fa fa-search'></i>{{lang.INPUT_LABEL_QUERY}}
                    </button>
                    <button id="btn_lastMonth" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_PREV_MONTH}}</button>
                    <button id="btn_thisMonth" class='btn btn-sm btn-xs '>{{lang.INPUT_LABEL_CURR_MONTH}}</button>
                    <button id="btn_lastWeek" class='btn btn-sm btn-xs '>{{lang.INPUT_LABEL_PREV_WEEK}}</button>
                    <button id="btn_thisWeek" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_CURR_WEEK}}</button>
                    <button id="btn_yesterday" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_PREV_DAY}}</button>
                    <button id="btn_today" class='btn btn-sm btn-xs'>{{lang.INPUT_LABEL_CURR_DAY}}</button>
                    <div class='clearfix'></div>
                </div>
            </div>
            <div>
                <a href="/admin/statistics/clubrcday">
                    <button id="dissolution_club" class='btn btn-primary btn-sm btn-xs'><i class='fa fa-search'></i>各亲友圈耗钻合计列表&nbsp;&nbsp;
                    </button>
                </a>
            </div>
        </div>
        <table id="dataTable" class="table table-bordered table-hover"></table>
    </div>
</div>

<!-- 初始化搜索栏的日期 -->
<script type="text/javascript">
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 6);
    $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
    $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));
</script>

<script type="text/javascript">

    function initTable() {
        startDate = $("#pick-date-start").val();
        endDate = $("#pick-date-end").val();
        $('#dataTable').bootstrapTable({
            method: 'get',
            url: '{{info["listUrl"]}}',
            contentType: "application/json",
            datatype: "json",
            cache: false,
            checkboxHeader: true,
            striped: true,
            pagination: true,
            pageSize: 15,
            pageList: '{{PAGE_LIST}}',
            search: true,
            showColumns: true,
            showRefresh: true,
            showFooter: true,
            minimumCountColumns: 2,
            clickToSelect: true,
            smartDisplay: true,
            //sidePagination : "server",
            queryParams: getSearchP,
            responseHandler: responseFun,
            //onLoadError:responseError,
            showExport: true,
            exportTypes: ['excel', 'csv', 'pdf', 'json'],
            // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
            columns: [

                [{
                    field: 'date',
                    title: '日期',
                    align: 'center',
                    valign: 'middle',
                    footerFormatter: function (values) {
                        return '总计'
                    }
                }, {
                    field: 'clubroom_day',
                    title: '当日亲友圈耗钻总数',
                    align: 'center',
                    valign: 'middle',
                    footerFormatter: function (values) {
                        var count = 0;
                        for (var val in values)
                            count += values[val].clubroom_day

                        return colorFormat(count);
                    }
                }, {
                    field: 'op',
                    title: '操作',
                    align: 'center',
                    valign: 'middle',
                    formatter: getOp
                }]]
        });

        //定义列操作
        function getSearchP(p) {
            startDate = $("#pick-date-start").val();
            endDate = $("#pick-date-end").val();

            sendParameter = p;

            sendParameter['startDate'] = startDate;
            sendParameter['endDate'] = endDate;

            return sendParameter;
        }

        function getOp(value, row, index) {
            var showDataUrls = [
                '/admin/statistics/active/showDay11'
            ];
            eval('rowobj=' + JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({id: rowobj['account']});
                var cStr = str.replace(/\"/g, "@");
                // if(showDataUrls.indexOf(op['url'])>=0)
                //opList.push(String.format("<a href='javascript:;' onclick=\"showActiveDialog(\'{0}\', \'{1}\', \'{2}\');\" class=\"btn btn-sm btn-primary\" >{3}</a> ", op['url'],op['method'],rowobj['date'],op['txt']));
                //else //不使用弹出窗口打开页面
                opList.push(String.format("<a href=\"{0}?day={1}\" class=\"btn btn-sm btn-primary\">{2}</a>", op['url'], rowobj['date'], op['txt']));
            }
            return opList.join('');
        }

        //获得返回的json 数据
        function responseFun(res) {
            var data = res;
            return data;
        }
    }
</script>
%rebase admin_frame_base
