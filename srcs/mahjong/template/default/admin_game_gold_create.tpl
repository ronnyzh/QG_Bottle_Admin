<style type="text/css">.config-table td.table-title{text-align:center;font-size:13px;vertical-align:middle}</style>
<div class='block'>
          %include admin_frame_header
          <div class="content" id="game_create_app">
             <!-- <form class="form-horizontal group-border-dashed" id='gameForm' @submit="onSubmit" action="{{info['submitUrl']}}" method="post" style="border-radius: 0px;" enctype="multipart/form-data"> -->
             <form class="form-horizontal group-border-dashed" id='gameForm' @submit="onSubmit" action="{{info['submitUrl']}}" method="post" style="border-radius: 0px;" enctype="multipart/form-data">
               <table class='table config-table'>
                        <tr>
                          <td width='20%' class='table-title'>金币场创建</td>
                        </tr>
                        <tr>
                              <td class='table-title'>`</td>
                              <td>
                                <table class='table config-table' border='1'>
                                    <tr>
                                         <td class='table-title'>游戏ID</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' id="id" name="gameid" class="form-control" placeholder="请输入">
                                             <label for='id' class='hitLabel' style='float:left;line-height:30px'>* 已存在的游戏ID：{{ gamelist }}</label>
                                         </td>
                                    </tr>
                                     <tr>
                                        <td class='table-title'>游戏名称</td>
                                        <td>
                                             <input id="gamename"  name="gamename"  type="text" style='width:100%;float:left' class="form-control" lay-verify="required" placeholder="请输入" autocomplete="off">
                                             <label for='id' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                        </td>
                                    </tr>
                                    <tr>
                                         <td class='table-title'>游戏类型</td>
                                         <td>

                                             <select style='width:100%;float:left' id="gameType" name="gameType" class="form-control">
                                                <option value="0"> 麻将</option>
                                                <option value="1"> 扑克 </option>
                                                <option value="2"> 扑克一 </option>
                                             </select>
                                             <label for='id' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                    <tr>
                                         <td class='table-title'>游戏版本号</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' id="version" name="version" class="form-control">
                                             <label for='version' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                    <tr>
                                         <td class='table-title'>排序值<br/>
                                                <small>用于客户端排序,降序排序，值越小越靠前</small>
                                         </td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' id="game_sort" name="game_sort" class="form-control">
                                             <label for='game_sort' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                    <tr>
                                         <td class='table-title'>其他信息</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' id="other_info" name="other_info" class="form-control">
                                             <label for='other_info' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                </table>
                              </td>
                        </tr>
                        <tr>
                              <td class='table-title'>
                                    金币场配置
                                    <br>
                                    <span><a href="javascript:;" @click="onAdd" class='btn btn-small btn-xs btn-primary'>新增</a></span>
                                    <span><a href="javascript:;" @click="onDel" class='btn btn-small btn-xs btn-primary'>删除</a></span>
                                    </br>
                              </td>
                              <td>
                                <table class='table config-table table1' border='1'>
                                   <tr>                                                                         
                                         <td>
                                                ID<br><small></small></br>
                                                <input type='text' name="id1" readonly="" value="0" class="form-control"  style='width:100%;float:left' />
                                         </td>                                         
                                         <td>
                                                场次 (title)<br><small></small></br>
                                                <select name="title1" class="form-control" style='width:200px;float:left'>
                                                <option value="新手场"> 新手场</option>
                                                <option value="初级场"> 初级场</option>
                                                <option value="中级场"> 中级场</option>
                                                <option value="高级场"> 高级场</option>
                                                <option value="土豪场"> 土豪场</option>
                                                <option value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         <td>
                                                上限 (need)<br><small></small></br>
                                                <input type='text' name="need1" class="form-control" value="" style='width:100%;float:left' />
                                         </td>
                                         <td>
                                                基本 (baseScore)<br><small></small></br>
                                                <input type='text' name="baseScore1" class="form-control" style='width:100%;float:left' />
                                         </td>
                                         <td>
                                                准入 (cost)<br><small></small></br>
                                                <input type='text' name="cost1" class="form-control" value="" style='width:100%;float:left' />
                                         </td>
                                          <td>
                                                倍数 (maxMultiples)<br><small></small></br>
                                                <input type='text' name="maxMultiples1" class="form-control" value="" style='width:100%;float:left' />
                                         </td>
                                    </tr>                                    
                                </table>
                              </td>
                        </tr>
              </table>
              <div class="modal-footer" style="text-align:center">
                   <button type="submit" class="btn btn-primary">{{lang.BTN_SUBMIT_TXT}}</button>
                   <button type="button" class="btn btn-primary" @click="onBack">{{lang.BTN_BACK_TXT}}</button>
              </div>
            </form>
    </div>
</div>
<script type="text/javascript">
    $(function(){   //前端页面配置及渲染
        var game_create_app = new Vue({
               el : '#game_create_app',
               data:{

               },mounted:function(){

               },methods:{
               		// 阻止空表单提交
                   onSubmit : function(e){
                       e.preventDefault();
                       formAjax($('#gameForm').attr("action"), $('#gameForm').attr("method"), $('#gameForm').serialize(),'正在创建...');
                   },

                   onBack : function(e){
                       e.preventDefault();
                       window.location.href="{{info['backUrl']}}";
                   },

                   onAdd : function(e){
                       e.preventDefault();
                       var configTable = $('.table1');
                       var num = parseInt(configTable.find('tr').length);
                       if (num == 6){
                            //信息框
                            layer.open({
                              content   : '暂时最多支持六条'
                              ,btn      : '关闭'
                            });
                       }else{
                            str = '<tr num="'+(num+1)+'">\
                            <td><small></small></br><input type="text" readonly="" value="'+(num)+'" name="id'+(num+1)+'" class="form-control" style="width:100%;float:left" /></td>\
                            <td><small></small></br><select name="title'+(num+1)+'" style="width:200px;float:left" class="form-control" ><option value="新手场"> 新手场</option><option value="初级场"> 初级场</option><option value="中级场"> 中级场</option><option value="高级场"> 高级场</option><option value="土豪场"> 土豪场</option><option value="至尊场"> 至尊场</option></select></td>\
                            <td><small></small></br><input type="text" name="need'+(num+1)+'" class="form-control" style="width:100%;float:left" /></td>\
                            <td><small></small></br><input type="text" name="baseScore'+(num+1)+'" class="form-control" style="width:100%;float:left" /></td>\
                            <td><small></small></br><input type="text" name="cost'+(num+1)+'" class="form-control" style="width:100%;float:left" /></td>\
                            <td><small></small></br><input type="text" name="maxMultiples'+(num+1)+'" class="form-control" style="width:100%;float:left" /></td>\
                            </tr>';

                            //添加到子节点
                            configTable.append(str);
                       }
                   },

                   onDel : function(e){
                       e.preventDefault();
                       var configTable = $('.table1');
                       var num = parseInt(configTable.find('tr').length);
                       if (num == 1){
                            //信息框
                            layer.open({
                              content   : 'DON DEL'
                              ,btn      : '关闭'
                            });
                       }else{
                            $('.table1 tr:last').remove();
                       }
                   },
               }
        });
    })
</script>
%rebase admin_frame_base
