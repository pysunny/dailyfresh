from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from goods.models import GoodsSKU
from user.models import Address
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin

# /order/place
class OrderPlaceView(LoginRequiredMixin, View):
    def post(self, request):

        user = request.user
            
        # 获取参数
        sku_ids = request.POST.getlist('sku_ids') 

        # 检验参数
        if not sku_ids:
            return redirect(reverse('cart:show'))
        
        # 获取Redis信息
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        skus=[]
        total_price = 0
        total_count = 0

        # 遍历sku_ids
        for sku_id in sku_ids:
            # 获取商品id的商品信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取商品数量
            count = conn.hget(cart_key, sku_id)

            amount = sku.price*int(count)

            # 动态添加属性
            sku.count = int(count)
            sku.amount = amount
            # 添加到列表
            skus.append(sku)

            # 累加计算
            total_count += int(count)
            total_price += amount
        
        # 定义运费
        transit_price = 10
        total_pay = total_price + transit_price

        # 获取用户地址
        addrs = Address.objects.filter(user=user)

        sku_ids = ','.join(sku_ids)

        # 组织上下文
        context = { 'skus':skus,
                    'total_count':total_count,
                    'total_price':total_price,
                    'transit_price':transit_price,
                    'total_pay':total_pay,
                    'addrs':addrs,
                    'sku_ids':sku_ids}
        
        return render(request, 'place_order.html', context)







