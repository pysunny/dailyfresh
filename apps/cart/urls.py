
from django.urls import re_path
from cart.views import CartAddView, CartInfoView, CartUpdateView, CartDeleteView
app_name = 'cart'
urlpatterns = [
    re_path(r'^add$', CartAddView.as_view(), name='cart'), # 购物车添加
    re_path(r'^$', CartInfoView.as_view(), name='show'), # 购物车页面
    re_path(r'^update$', CartUpdateView.as_view(), name='update'), # 购物车更新
    re_path(r'^delete$', CartDeleteView.as_view(), name='delete'), # 购物车删除
]
