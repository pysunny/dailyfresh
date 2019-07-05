
from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from user.views import RegistreView, ActiveView, LoginView, UserInfoView, UserOrderView, AddressView, LogoutView
app_name = 'user'
urlpatterns = [
    re_path(r'^register$', RegistreView.as_view(), name='register'),# 注册
    re_path(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),# 激活

    re_path(r'^login$', LoginView.as_view(), name='login'),# 登录
    re_path(r'^logout$', LogoutView.as_view(), name='logout'),# 登出

    re_path(r'^$', UserInfoView.as_view(), name='user'),# 用户信息
    re_path(r'^order$', UserOrderView.as_view(), name='order'),# 用户订单
    re_path(r'^address$', AddressView.as_view(), name='address'),# 用户地址
]
