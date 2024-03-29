<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no" />
    <meta name="renderer" content="webkit|ie-comp|ie-stand">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta http-equiv="Cache-Control" content="no-siteapp" />
    <meta name="keywords" content="scclui框架">
    <meta name="description" content="scclui为轻量级的网站后台管理系统模版。">
    <title>首页</title>
    
    <link rel="stylesheet" href="{{info['STATIC_ADMIN_PATH']}}/layui/css/layui.css">
    <link rel="stylesheet" href="{{info['STATIC_ADMIN_PATH']}}/js/layerMobile/layer.css">
    <link rel="stylesheet" href="{{info['STATIC_ADMIN_PATH']}}/css/sccl.css">
    
  </head>
  
  <body class="login-bg">
    <div class="login-box">
        <header>
            <h1>{{lang.MAHJONG_LOGIN_TITLE_TXT}}</h1>
        </header>
        <div class="login-main">
            <form action="{{info['submitUrl']}}" class="layui-form" method="post">
                <input name="__RequestVerificationToken" type="hidden" value="">                
                <div class="layui-form-item">
                    <input type="text" name="userName" value="{{info['account']}}" lay-verify="userName" autocomplete="off" placeholder="这里输入登录名" class="layui-input">
                </div>
                <div class="layui-form-item">
                    <input type="password" name="password" value="{{info['passwd']}}" lay-verify="password" autocomplete="off" placeholder="这里输入密码" class="layui-input">
                </div>
                    <div class="layui-form-item">
                        <div class="login-code-box">
                            <input type="text" class="layui-input" name="code" />
                            <img id="valiCode" src="{{info['vcodeUrl']}}" alt="验证码" />
                        </div>
                    </div>
                    <div class="clear"></div>
                </div>
                <div class="login-code-box" style='text-align:center'>
                    <button class="layui-btn  layui-btn-normal" lay-submit="" lay-filter="login">
                        登录
                    </button>&nbsp;
                    %if message:
                        <span class='error-message' style='color:red;font-size:13px;'>{{message}}</span>
                    %end
                </div>
            </form>        
        </div>
        <footer style='margin-top:10px;'>
            <p>{{lang.COPY_RIGHT_TXT}}</p>
        </footer>
    </div>
    <script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/lib/jquery-2.1.4.min.js?{{RES_VERSION}}"></script>
    <script src="{{info['STATIC_ADMIN_PATH']}}/layui/layui.js"></script>
    <script src="{{info['STATIC_ADMIN_PATH']}}/js/layerMobile/layer.js"></script>
    <script type="text/javascript">
          $("#valiCode").click(function(){
                      var ms = new Date().getTime();
                      urlStr = "/admin/vcode?v="+ms;
                      $("#valiCode").attr("src", urlStr);
           });
    </script>
  </body>
</html>
