<style type="text/css">.config-table td.table-title{text-align:center;font-size:13px;vertical-align:middle}</style>
<div class="block">
          %include admin_frame_header
          <div class="content" id="goods_create_app">
             <form class="form-horizontal group-border-dashed" id='gameForm' @submit.prevent="onSubmit" method="post" style="border-radius: 0px;" enctype="multipart/form-data">
               <span v-if="system == 'FISH'">
                         <input type='hidden' name="goods_type" :value='goodsType' />
               </span>
               <table class='table config-table'>
                        <tr>
                          <td width='20%' class='table-title'>{{lang.GOODS_CREATE_TXT}}</td>
                        </tr>
                        <tr>
                              <td class='table-title'>`</td>
                              <td>
                                <table class='table config-table' border='1'>
                                    <tr>
                                         <td class='table-title'>{{lang.GOODS_NAME_TXT}}</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' id="name" name="name" class="form-control">
                                             <label for='name' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                    <tr  v-if="system == 'HALL'">
                                        <td class='table-title'>商品类型</td>
                                         <td>
                                                <input type="radio" name="goods_type" value='0' checked='checked' />钻石
                                                <input type="radio" name="goods_type" value='2' />金币场金币
                                         </td>
                                    </tr>
                                    <tr>
                                        <td class='table-title' v-if="system == 'HALL'">{{lang.GOODS_CARD_TXT}}</td>
                                        <td class='table-title' v-if="system == 'FISH'">{{lang.GOODS_COIN_TXT}}</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' id="cards" name="cards" class="form-control">
                                             <label for='cards' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                     <tr>
                                         <td class='table-title' v-if="system=='HALL'">{{lang.GOODS_CARD_PRESENT_TXT}}</td>
                                         <td class='table-title' v-if="system=='FISH'">{{lang.GOODS_COIN_PRESENT_TXT}}</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' id="present_cards" name="present_cards" class="form-control">
                                             <label for='present_cards' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                    <tr>
                                         <td class='table-title'>{{lang.GOODS_PRICE_TXT}}</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' id="price" name="price" class="form-control">
                                             <label for='price' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                        </tr>
              </table>
              <div class="modal-footer" style="text-align:center">
                   <button type="submit" class="btn btn-primary">{{lang.BTN_SUBMIT_TXT}}</button>
                  <button type="button" class="btn btn-primary" @click.prevent="onBack">{{lang.BTN_BACK_TXT}}</button>
              </div>
            </form>
          </div>
</div>
</div>
<script type="text/javascript">

    var goods_create_app = new Vue({
                'el': '#goods_create_app',
                'data': {
                        'system': '',
                        'goodsType': '',
                },mounted: function(){
                    this.$data.system = '{{system}}',
                    this.$data.goodsType = '{{goods_type}}'
                },methods: {
                    onSubmit:function(){
                          formAjax($('#gameForm').attr("action"), $('#gameForm').attr("method"), $('#gameForm').serialize(),'正在创建...');
                    },
                    onBack: function(){
                        window.location.href="{{info['backUrl']}}";
                    }
                }
    });
</script>
%rebase admin_frame_base
