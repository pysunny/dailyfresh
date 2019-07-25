from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin

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

class CartInfoView(LoginRequiredMixin, View):
    # 购物车页面显示
    # 显示
    def get(self, request):
        # 获取用户购物车商品信息
        user = request.user
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        # {商品id：数量}
        cart_dict = conn.hgetall(cart_key)
        skus = []
        total_count = 0
        total_price = 0
        for sku_id, count in cart_dict.items():
            # 获取商品信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 计算小计
            amount = sku.price*int(count)
            # 动态添加属性
            sku.amount = amount
            sku.count = int(count)
            skus.append(sku)

            # 累加计算
            total_count += int(count)
            total_price += amount

        # 组织上下文
        context = { 'total_count':total_count, 
                    'total_price':total_price,
                    'skus':skus}
        
        # 使用模板
        return render(request, 'cart.html', context)

# /cart/update
class CartUpdateView(View):
    def post(self, request):
        """ 购物车更新 """
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

        if count > sku.stock:
            return JsonResponse({'res':4, 'errmsg':'商品库存不足'})

        conn.hset(cart_key, sku_id, count)

        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        # 返回应答
        return JsonResponse({'res':5, 'total_count':total_count, 'errmsg':'更新成功'})
