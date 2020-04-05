<div class="block">
          %include admin_frame_header
          <form class="form-inline definewidth m10"  style='padding: 19px 29px 29px;' action="{{info['searchUrl']}}" method="get">
            <div class='row'>
                <div class='col-sm-12'>
                    <p align='center'>
                      <span style='font-size:22px;font-weight:600;'>{{info['title']}}</span>
                    </p>
                </div>
                <div class='col-sm-12'>
                    <p align='center'><input type='text' name='memberId' style='width:200px;height:35px;' placeholder="请输入玩家编号" value="{{info['memberId']}}" />&nbsp;</p>
                </div>
                <div class='col-sm-12'>
                     <p align='center'><input type='submit' style='width:200px;height:35px;' value='绑定' class='btn btn-sm btn-primary' /></p>
                </div>

                %if message:
                <p align='center'>
                      <span style='color:red'>{{message}}</span>
                </p>
                %end
            </div>
          </form>

            %if binding_info:
                <table id="dataTable" class="table table-bordered table-hover table-striped">
                    <thead>
                    <tr>
                        <th style="text-align: center; vertical-align: middle; " name="memberId">
                            <div class="th-inner ">玩家编号</div>
                            <div class="fht-cell"></div>
                        </th>
                        <th style="text-align: center; vertical-align: middle; " name="bindingTime">
                            <div class="th-inner ">绑定时间</div>
                            <div class="fht-cell"></div>
                        </th>
                        <th style="text-align: center; vertical-align: middle; " name="nickname">
                            <div class="th-inner sortable both">名称</div>
                            <div class="fht-cell"></div>
                        </th>
                        <th style="text-align: center; vertical-align: middle; " name="headImgUrl">
                            <div class="th-inner sortable both">微信头像</div>
                            <div class="fht-cell"></div>
                        </th>
                        <th style="text-align: center; vertical-align: middle; " data-field="op">
                            <div class="th-inner ">操作</div>
                            <div class="fht-cell"></div>
                        </th>
                    </tr>
                    </thead>
                    <tbody>
                        %for i in binding_info:
                            <tr>
                                <td style="text-align: center; vertical-align: middle; ">{{i['memberId']}}</td>
                                <td style="text-align: center; vertical-align: middle; ">{{i['bindingTime']}}</td>
                                <td style="text-align: center; vertical-align: middle; ">{{i['nickname']}}</td>
                                <td style="text-align: center; vertical-align: middle; ">
                                    <img src="{{i['headImgUrl']}}" width="30" height="30">
                                </td>
                                <td style="text-align: center; vertical-align: middle; ">
                                    <button class="btn btn-danger" uid="{{i['memberId']}}" onclick="unbind(this)">解绑</button>
                                </td>
                            </tr>
                        %end
                    </tbody>
                </table>
            %end
  </div>
<script type="text/javascript">
function unbind(ele){
    if (confirm("确定要解绑？")) {
        uid = $(ele).attr('uid')
        $.ajax({
           type : "GET",
           url : "/admin/agent/binding?unbind=1&memberId=" + uid,
           datatype : "html",
           cache : false,
           success : function(data) {
                alert(data)
                location.reload()
           },
           error:function(data){
                alert(data)
           }
        });
    }else{
       return
    }
}
</script>
%rebase admin_frame_base

