
from django.urls import path, re_path
from goods import views
app_name = 'goods'
urlpatterns = [
    re_path(r'^$', views.index , name='index')
]
