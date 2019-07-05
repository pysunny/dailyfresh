
from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^tinymce/', include('tinymce.urls')),
    re_path(r'^user/', include('user.urls', namespace='user')),
    re_path(r'^cart/', include('cart.urls', namespace='cart')),
    re_path(r'^order/', include('order.urls', namespace='order')),
    re_path(r'^', include('goods.urls', namespace='goods')),
]
