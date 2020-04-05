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
                                             <input type="text" style='width:100%;float:left' id="id" name="gameid" readonly="" class="form-control" value="{{ gameid }}">
                                             <label for='id' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                     <tr>
                                        <td class='table-title'>游戏名称</td>
                                        <td>
                                             <input id="gamename"  name="gamename"  type="text" style='width:100%;float:left' class="form-control" lay-verify="required" value="{{ gamename }}" autocomplete="off">
                                             <label for='id' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                        </td>
                                    </tr>
                                    %if info['game_type'] == '0':
                                    <tr>
                                         <td class='table-title'>游戏类型</td>
                                         <td>
                                             <select style='width:100%;float:left' id="gameType" name="gameType" class="form-control">
                                                <option selected="selected" value="0"> 麻将</option>
                                                <option value="1"> 扑克 </option>
                                             </select>
                                             <label for='id' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                    %else:
                                    <tr>
                                         <td class='table-title'>游戏类型</td>
                                         <td>
                                             <select style='width:100%;float:left' id="gameType" name="gameType" class="form-control">
                                                <option value="0"> 麻将</option>
                                                <option  selected="selected" value="1"> 扑克 </option>
                                             </select>
                                             <label for='id' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                    %end
                                    <tr>
                                         <td class='table-title'>游戏版本号</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' id="version" name="version" class="form-control" value="{{ info['version'] }}">
                                             <label for='version' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                    <tr>
                                         <td class='table-title'>排序值<br/>
                                                <small>用于客户端排序,降序排序，值越小越靠前</small>
                                         </td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' id="game_sort" name="game_sort" class="form-control" value="{{ info['game_sort'] }}">
                                             <label for='game_sort' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                    <tr>
                                         <td class='table-title'>其他信息</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' id="other_info" name="other_info" class="form-control" value="{{ info['other_info']}}">
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
                                   %for each_gameinfo in gameInfo:
                                   %num = int(each_gameinfo['id']) + 1
                                   %if num == 1:
                                   <tr>                                                                         
                                         <td>
                                                ID<br><small></small></br>
                                                <input type='text' name="id{{num}}" readonly="" class="form-control"  value='{{ each_gameinfo["id"] }}' style='width:100%;float:left'  />
                                         </td>
                                         %if each_gameinfo['title'] == "新手场":
                                         <td>
                                                场次 (title)<br><small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option selected="selected" value="新手场"> 新手场</option>
                                                <option  value="初级场"> 初级场</option>
                                                <option  value="中级场"> 中级场</option>
                                                <option value="高级场"> 高级场</option>
                                                <option value="土豪场"> 土豪场</option>
                                                <option value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         %if each_gameinfo['title'] == "初级场":
                                         <td>
                                                场次 (title)<br><small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option  value="新手场"> 新手场</option>
                                                <option selected="selected" value="初级场"> 初级场</option>
                                                <option value="中级场"> 中级场</option>
                                                <option value="高级场"> 高级场</option>
                                                <option value="土豪场"> 土豪场</option>
                                                <option value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         %if each_gameinfo['title'] == "中级场":
                                         <td>
                                                场次 (title)<br><small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option  value="新手场"> 新手场</option>
                                                <option  value="初级场"> 初级场</option>
                                                <option selected="selected" value="中级场"> 中级场</option>
                                                <option value="高级场"> 高级场</option>
                                                <option value="土豪场"> 土豪场</option>
                                                <option value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         %if each_gameinfo['title'] == "高级场":
                                         <td>
                                                场次 (title)<br><small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option  value="新手场"> 新手场</option>
                                                <option  value="初级场"> 初级场</option>
                                                <option  value="中级场"> 中级场</option>
                                                <option selected="selected" value="高级场"> 高级场</option>
                                                <option value="土豪场"> 土豪场</option>
                                                <option value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         %if each_gameinfo['title'] == "土豪场":
                                         <td>
                                                场次 (title)<br><small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option  value="新手场"> 新手场</option>
                                                <option  value="初级场"> 初级场</option>
                                                <option  value="中级场"> 中级场</option>
                                                <option value="高级场"> 高级场</option>
                                                <option selected="selected" value="土豪场"> 土豪场</option>
                                                <option value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         %if each_gameinfo['title'] == "至尊场":
                                         <td>
                                                场次 (title)<br><small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option  value="新手场"> 新手场</option>
                                                <option  value="初级场"> 初级场</option>
                                                <option  value="中级场"> 中级场</option>
                                                <option value="高级场"> 高级场</option>
                                                <option value="土豪场"> 土豪场</option>
                                                <option selected="selected" value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         <td>
                                                上限 (need)<br><small></small></br>
                                                <input type='text' name="need{{num}}" class="form-control" value="{{ each_gameinfo["need"] }}" style='width:100%;float:left' />
                                         </td>
                                         <td>
                                                基本 (baseScore)<br><small></small></br>
                                                <input type='text' name="baseScore{{num}}" class="form-control" value="{{ each_gameinfo["baseScore"] }}" style='width:100%;float:left' />
                                         </td>
                                         <td>
                                                准入 (cost)<br><small></small></br>
                                                <input type='text' name="cost{{num}}" class="form-control" value="{{ each_gameinfo["cost"] }}" style='width:100%;float:left' />
                                         </td>

                                          <td>
                                                倍数 (maxMultiples)<br><small></small></br>
                                                <input type='text' name="maxMultiples{{num}}" class="form-control" value="{{ each_gameinfo["maxMultiples"] }}" style='width:100%;float:left' />
                                         </td>
                                    </tr>
                                    %else:
                                    <tr>
                                         <td>
                                                <small></small></br>
                                                <input type='text' name="id{{num}}" readonly="" class="form-control"  value='{{ each_gameinfo["id"] }}' style='width:100%;float:left'  />
                                         </td>
                                         %if each_gameinfo['title'] == "新手场":
                                         <td>
                                                <small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option selected="selected" value="新手场"> 新手场</option>
                                                <option  value="初级场"> 初级场</option>
                                                <option  value="中级场"> 中级场</option>
                                                <option value="高级场"> 高级场</option>
                                                <option value="土豪场"> 土豪场</option>
                                                <option value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         %if each_gameinfo['title'] == "初级场":
                                         <td>
                                                <small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option  value="新手场"> 新手场</option>
                                                <option selected="selected" value="初级场"> 初级场</option>
                                                <option value="中级场"> 中级场</option>
                                                <option value="高级场"> 高级场</option>
                                                <option value="土豪场"> 土豪场</option>
                                                <option value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         %if each_gameinfo['title'] == "中级场":
                                         <td>
                                                <small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option  value="新手场"> 新手场</option>
                                                <option  value="初级场"> 初级场</option>
                                                <option selected="selected" value="中级场"> 中级场</option>
                                                <option value="高级场"> 高级场</option>
                                                <option value="土豪场"> 土豪场</option>
                                                <option value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         %if each_gameinfo['title'] == "高级场":
                                         <td>
                                                <small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option  value="新手场"> 新手场</option>
                                                <option  value="初级场"> 初级场</option>
                                                <option  value="中级场"> 中级场</option>
                                                <option selected="selected" value="高级场"> 高级场</option>
                                                <option value="土豪场"> 土豪场</option>
                                                <option value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         %if each_gameinfo['title'] == "土豪场":
                                         <td>
                                                <small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option  value="新手场"> 新手场</option>
                                                <option  value="初级场"> 初级场</option>
                                                <option  value="中级场"> 中级场</option>
                                                <option value="高级场"> 高级场</option>
                                                <option selected="selected" value="土豪场"> 土豪场</option>
                                                <option value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         %if each_gameinfo['title'] == "至尊场":
                                         <td>
                                                <small></small></br>
                                                <select name="title{{num}}" class="form-control" style='width:200px;float:left'>
                                                <option  value="新手场"> 新手场</option>
                                                <option  value="初级场"> 初级场</option>
                                                <option  value="中级场"> 中级场</option>
                                                <option value="高级场"> 高级场</option>
                                                <option value="土豪场"> 土豪场</option>
                                                <option selected="selected" value="至尊场"> 至尊场</option>
                                                </select>
                                         </td>
                                         %end
                                         <td>
                                                <small></small></br>
                                                <input type='text' name="need{{num}}" class="form-control" value="{{ each_gameinfo["need"] }}" style='width:100%;float:left' />
                                         </td>
                                         <td>
                                               <small></small></br>
                                                <input type='text' name="baseScore{{num}}" class="form-control" value="{{ each_gameinfo["baseScore"] }}" style='width:100%;float:left' />
                                         </td>
                                         <td>
                                                <small></small></br>
                                                <input type='text' name="cost{{num}}" class="form-control" value="{{ each_gameinfo["cost"] }}" style='width:100%;float:left' />
                                         </td>

                                          <td>
                                                <small></small></br>
                                                <input type='text' name="maxMultiples{{num}}" class="form-control" value="{{ each_gameinfo["maxMultiples"] }}" style='width:100%;float:left' />
                                         </td>
                                    </tr>
                                    %end
                                    %end
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
                              content   : '最少保持一条'
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
