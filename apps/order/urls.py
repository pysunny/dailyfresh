
from django.urls import re_path
from order.views import OrderPlaceView, OrderCommitView
app_name = 'order'
urlpatterns = [
    re_path(r'^place$', OrderPlaceView.as_view(), name='place'), # 购物车添加
    re_path(r'^commit$', OrderCommitView.as_view(), name='commit'), # 订单创建
]
