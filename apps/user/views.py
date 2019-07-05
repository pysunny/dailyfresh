from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail
from user.models import User, Address
from celery_tasks.tasks import send_register_email
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from utils.mixin import LoginRequiredMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
import re

# Create your views here.

# /user/register
class RegistreView(View):
    """ 注册类视图 """
    def get(self, request):
        """ 显示注册页面 """
        return render(request, 'register.html')

    def post(self, request):
        """ 进行注册处理 """
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据校验
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg':'数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg':'邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg':'请同意协议'})

        # 检验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            return render(request, 'register.html', {'errmsg':'用户名已经存在'})

        # 进行业务处理
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        """ 发送激活邮件 """
        # 加密用户身份信息 生成激活cookie
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'comfirm':user.id}
        token = serializer.dumps(info)
        token = token.decode()

        # 发送邮件
        send_register_email.delay(email, username, token)

        # 返回应答
        return redirect(reverse('user:login'))

class ActiveView(View):
    """ 用户激活 """
    def get(self, request, token):
        """ 进行用户激活 """
        # 进行解密
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取用户id
            use_id = info['comfirm']
            # 激活用户
            user = User.objects.get(id=use_id)
            user.is_active = 1
            user.save()
            # 跳转到登陆页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse('激活邮件已经过期')

class LoginView(View):
    def get(self, request):
        """ 显示页面 """
        # 判断是否记得用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        return render(request, 'login.html')

    def post(self, request):
        """ 登陆校验 """
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg':'数据不完整'})
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # 获取登陆之后要跳转的地址，默认返回首页
                next_url = request.GET.get('next', reverse('goods:index')) 
                # 跳转next_url
                response = redirect(next_url)
                # 判断是否需要记得用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    # 记得用户名
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response

            else:
                return render(request, 'login.html', {'errmsg':'账号未激活'})
                
        else:
            return render(request, 'login.html', {'errmsg':'用户名或者密码错误'})
# /user/
class UserInfoView(LoginRequiredMixin, View):
    """ 用户信息 """
    def get(self, request):
        # 获取用户的个人信息

        # 获取用户的浏览记录

        return render(request, 'user_center_info.html', {'page':'user'})


# /user/logout
class LogoutView(View):
    def get(self, request):
        """ 退出登录 """
        logout(request)
        return redirect(reverse('goods:index'))


# /user/order
class UserOrderView(LoginRequiredMixin, View):
    """ 用户订单 """
    def get(self, request):
        # 获取用户的订单信息
        return render(request, 'user_center_order.html', {'page':'order'})
# /user/address
class AddressView(LoginRequiredMixin, View):
    """ 用户地址 """
    def get(self, request):
        # 获取用户的默认收货地址
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)
        return render(request, 'user_center_site.html', {'page':'address','address':address})

    def post(self, request):
        """ 地址的添加 """
        # 接收
        receiver = request.POST.get('receiver')
        addr = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg':'数据不完整'})

        if not re.match(r'^[1]([3-9])[0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg':'手机格式不正确'})

        # 业务
        # 如果用户未有默认地址，就添加成默认地址
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)
        if address:
            is_default = False
        else:
            is_default = True
            
        Address.objects.create(user=user, receiver=receiver, addr=addr, zip_code=zip_code, phone=phone, is_default=is_default)

        # 应答
        return redirect(reverse('user:address'))


