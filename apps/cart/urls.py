
from django.urls import path
from cart.views import CartAddView, CartInfoView, CartUpdateView, CartDeleteView
app_name = 'cart'
urlpatterns = [
    path('add', CartAddView.as_view(), name='cart'), # 购物车添加
    path('', CartInfoView.as_view(), name='show'), # 购物车页面
    path('update', CartUpdateView.as_view(), name='update'), # 购物车更新
    path('delete', CartDeleteView.as_view(), name='delete'), # 购物车删除
]
