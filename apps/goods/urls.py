
from django.urls import path
from goods.views import IndexView, DetailView, ListView
app_name = 'goods'
urlpatterns = [
    path('', IndexView.as_view(), name='index'), # 首页
    path('goods/<int:goods_id>', DetailView.as_view(), name='detail'), # 详情页
    path('list/<int:type_id>/<int:page>', ListView.as_view(), name='list'), # 列表页
]
