
from django.urls import re_path
from cart.views import CartAddView, CartInfoView
app_name = 'cart'
urlpatterns = [
    re_path(r'^add$', CartAddView.as_view(), name='cart'), # 购物车
    re_path(r'^$', CartInfoView.as_view(), name='show'), # 购物车
]
