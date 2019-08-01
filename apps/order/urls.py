
from django.urls import path
from order.views import OrderPlaceView, OrderCommitView
app_name = 'order'
urlpatterns = [
    path('place', OrderPlaceView.as_view(), name='place'), # 购物车添加
    path('commit', OrderCommitView.as_view(), name='commit'), # 订单创建
]
