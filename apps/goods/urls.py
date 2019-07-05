
from django.urls import path, re_path
from goods.views import IndexView
app_name = 'goods'
urlpatterns = [
    re_path(r'^$', IndexView.as_view(), name='index'), # 首页
]
