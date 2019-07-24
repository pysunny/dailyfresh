from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection

# Create your views here.
# /cart/add
class CartAddView(View):
    def post(self, request):
        # 接收数据
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res':0, 'errmsg':'请登录'})

        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res':1, 'errmsg':'数据不完整'})

        # 校验count
        try:
            count = int(count)
        except expression as e:
            return JsonResponse({'res':2, 'errmsg':'商品数目出错'})

        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res':3, 'errmsg':'商品不存在'})

        # 业务
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            count += int(cart_count)

        # 校验商品库存

        if count > sku.stock:
            return JsonResponse({'res':4, 'errmsg':'商品库存不足'})

        conn.hset(cart_key, sku_id, count)
        total_count = conn.hlen(cart_key)

        # 返回应答
        return JsonResponse({'res':5, 'total_count':total_count, 'errmsg':'添加成功'})