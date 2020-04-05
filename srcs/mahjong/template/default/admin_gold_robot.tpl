<script type="text/javascript" src="/assest/default/js/refreshDateInit.js"></script>
<div class="cl-mcont">
  <div class="block">
            <div class="content">
               <table id="dataTable" class="table table-bordered table-hover"></table>
            </div>
  </div>
</div>


<script type="text/javascript">
         $('#dataTable').bootstrapTable({
            cardView: true,
            striped: true,
            method: 'get',
            pageSize: 15,
            showRefresh: true,
            clickToSelect: true,
            showToggle: true,
            columns: [{
                field: 'game_count',
                title: 'game_count'
            }, {
                field: 'headImgUrl',
                title: 'headImgUrl'
            }, {
                field: 'gold',
                title: 'gold'
            }, {
                field: 'openid',
                title: 'openid'
            }, {
                field: 'money',
                title: 'money'
            }, {
                field: 'last_join_date',
                title: 'last_join_date'
            }, {
                field: 'sex',
                title: 'sex'
            }, {
                field: 'currency',
                title: 'currency'
            }, {
                field: 'last_present_date',
                title: 'last_present_date'
            }, {
                field: 'last_logout_ip',
                title: 'last_logout_ip'
            }, {
                field: 'coin',
                title: 'coin'
            }, {
                field: 'last_exit_ip',
                title: 'last_exit_ip'
            }, {
                field: 'parentAg',
                title: 'parentAg'
            }, {
                field: 'reg_date',
                title: 'reg_date'
            }, {
                field: 'charge',
                title: 'charge'
            }, {
                field: 'valid',
                title: 'valid'
            }, {
                field: 'last_login_date',
                title: 'last_login_date'
            }, {
                field: 'vip_level',
                title: 'vip_level'
            }, {
                field: 'eamil',
                title: 'eamil'
            }, {
                field: 'isOnline',
                title: 'isOnline'
            }, {
                field: 'deal_level',
                title: 'deal_level'
            }, {
                field: 'isRobot',
                title: 'isRobot'
            }, {
                field: 'last_exit_date',
                title: 'last_exit_date'
            }, {
                field: 'charge_count',
                title: 'charge_count'
            }, {
                field: 'phone',
                title: 'phone'
            }, {
                field: 'refreshToken',
                title: 'refreshToken'
            }, {
                field: 'playCount',
                title: 'playCount'
            }, {
                field: 'password',
                title: 'password'
            }, {
                field: 'nickname',
                title: 'nickname'
            }, {
                field: 'last_join_ip',
                title: 'last_join_ip'
            }, {
                field: 'account',
                title: 'account'
            }, {
                field: 'reg_ip',
                title: 'reg_ip'
            }, {
                field: 'name',
                title: 'name'
            }, {
                field: 'accessToken',
                title: 'accessToken'
            }, {
                field: 'level',
                title: 'level'
            }, {
                field: 'start_game_time',
                title: 'start_game_time'
            }, {
                field: 'unionID',
                title: 'unionID'
            }, {
                field: 'newcomer_present_date',
                title: 'newcomer_present_date'
            }, {
                field: 'last_login_ip',
                title: 'last_login_ip'
            }, {
                field: 'last_logout_date',
                title: 'last_logout_date'
            }, {
                field: 'wallet',
                title: 'wallet'
            }, {
                field: 'exp',
                title: 'exp'
            }, {
                field: 'coin_delta',
                title: 'coin_delta'
            }],
            %if isbot_data:
            data: [{
                game_count: "{{ isbot_data['game_count'] }}",
                headImgUrl: "{{ isbot_data['headImgUrl'] }}",
                gold: "{{ isbot_data['gold'] }}",
                openid: "{{ isbot_data['openid'] }}",
                money: "{{ isbot_data['money'] }}",
                last_join_date: "{{ isbot_data['last_join_date'] }}",
                sex: "{{ isbot_data['sex'] }}",
                currency: "{{ isbot_data['currency'] }}",
                last_present_date: "{{ isbot_data['last_present_date'] }}",
                last_logout_ip: "{{ isbot_data['last_logout_ip'] }}",
                coin: "{{ isbot_data['coin'] }}",
                last_exit_ip: "{{ isbot_data['last_exit_ip'] }}",

                parentAg: "{{ isbot_data['parentAg'] }}",
                reg_date: "{{ isbot_data['reg_date'] }}",
                charge: "{{ isbot_data['charge'] }}",
                valid: "{{ isbot_data['valid'] }}",
                last_login_date: "{{ isbot_data['last_login_date'] }}",
                vip_level: "{{ isbot_data['vip_level'] }}",

                email: "{{ isbot_data['email'] }}",
                isOnline: "{{ isbot_data['isOnline'] }}",
                deal_level: "{{ isbot_data['deal_level'] }}",
                isRobot: "{{ isbot_data['isRobot'] }}",
                last_exit_date: "{{ isbot_data['last_exit_date'] }}",
                charge_count: "{{ isbot_data['charge_count'] }}",
                phone: "{{ isbot_data['phone'] }}",
                refreshToken: "{{ isbot_data['refreshToken'] }}",
                playCount: "{{ isbot_data['playCount'] }}",

                password: "{{ isbot_data['password'] }}",
                nickname: "{{ isbot_data['nickname'] }}",
                last_join_ip: "{{ isbot_data['last_join_ip'] }}",
                account: "{{ isbot_data['account'] }}",
                reg_ip: "{{ isbot_data['reg_ip'] }}",
                name: "{{ isbot_data['name'] }}",
                accessToken: "{{ isbot_data['accessToken'] }}",
                level: "{{ isbot_data['level'] }}",
                start_game_time: "{{ isbot_data['start_game_time'] }}",
                unionID: "{{ isbot_data['unionID'] }}",

                newcomer_present_date: "{{ isbot_data['newcomer_present_date'] }}",
                last_login_ip: "{{ isbot_data['last_login_ip'] }}",
                last_logout_date: "{{ isbot_data['last_logout_date'] }}",
                wallet: "{{ isbot_data['wallet'] }}",
                exp: "{{ isbot_data['exp'] }}",
                coin_delta: "{{ isbot_data['coin_delta'] }}",

            }]
            %end
        });
</script>
%rebase admin_frame_base