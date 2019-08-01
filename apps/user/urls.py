
from django.urls import path
from django.contrib.auth.decorators import login_required
from user.views import RegistreView, ActiveView, LoginView, UserInfoView, UserOrderView, AddressView, LogoutView
app_name = 'user'
urlpatterns = [
    path('register', RegistreView.as_view(), name='register'),# 注册
    path('active/<token>', ActiveView.as_view(), name='active'),# 激活

    path('login', LoginView.as_view(), name='login'),# 登录
    path('logout', LogoutView.as_view(), name='logout'),# 登出

    path('', UserInfoView.as_view(), name='user'),# 用户信息
    path('order/<int:page>', UserOrderView.as_view(), name='order'),# 用户订单
    path('address', AddressView.as_view(), name='address'),# 用户地址
]
