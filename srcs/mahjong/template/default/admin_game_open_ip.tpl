<div class="cl-mcont">
    <div class='block'>
         <div class='header'>
             <h3>
             %if info.get('title',None):
               {{info['title']}}
             %end
           </h3>
         </div>
<div class='content'>
      <form class='form-horizontal group-border-dashed' action="{{info['submitUrl']}}" method='POST' id='selfModify'>
       <div class="form-group">
            <label class="col-sm-5 control-label">需要解封的IP</label>
            <div class="col-sm-6">
                  <input type='text' style='width:100%;float:left' name='open_ip' id="open_id" class="form-control" >
            </div>
       </div>

       <div class="modal-footer" style="text-align:center">
           <button type="submit" class="btn btn-sm btn-xs btn-primary btn-mobile">确定解封</button>
       </div>


</form>
</div>
</div>
</div>
%rebase admin_frame_base

<script>
     if("{{post_res}}"=="1"){
        alert("解封成功！")
    }else if("{{post_res}}"=="2"){
        alert("解封失败!")
    }

    function isValidIP(ip) {
        var reg = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/
        return reg.test(ip);
    }

    $("#open_id").blur(funciton(){
        var ip = $(this).val()
        var res = isValidIP(ip)
        if(res){
            alert("ip格式不正确！")
        }
    });
</script>

