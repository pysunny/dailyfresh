from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
from django.http import JsonResponse
from user.models import Address
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from datetime import datetime

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


class OrderCommitView(View):
    def post(self, request):
        """ 订单创建 """
        # 验证用户
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res':0, 'errmsg':'请登录'})

        # 接收参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')

        # 验证参数
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res':1, 'errmsg':'数据不完整'})

        if pay_method not in OrderInfo.PAY_METHODS:
            return JsonResponse({'res':2, 'errmsg':'非法支付方式'})

        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({'res':3, 'errmsg':'非法地址'})

        # todo:创建订单核心业务
        # 组织参数
        # 订单id
        order_id = datetime.now().strftime('%y%m%d%H%M%S')+str(user.id)
        # 运费
        transit_price = 10
        total_count = 0
        total_price = 0

        order = OrderInfo.objects.create(order_id=order_id,
                                        user=user,
                                        addr=addr,
                                        pay_method=pay_method,
                                        total_count=total_count,
                                        total_price=total_price,
                                        transit_price=transit_price)
        # todo:创建订单核心业务
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        sku_ids = sku_ids.split(',')
        for sku_id in sku_ids:
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except GoodsSKU.DoesNotExist:
                # 商品不存在
                return JsonResponse({'res':4, 'errmsg':'商品不存在'})

            count = conn.hget(cart_key, sku_id)

            OrderGoods.objects.create(order=order,
                                        sku=sku,
                                        count=count,
                                        price=sku.price)

            # todo:更新库存
            sku.stock -= int(count)
            sku.sales += int(count)
            sku.save()

            amount = sku.price*int(count)
            total_count += int(count)
            total_price += amount

        order.total_count = total_count
        order.total_price = total_price
        order.save()

        # 清除用户Redis记录
        conn.hdel(cart_key, *sku_ids)

        # 返回应答
        return JsonResponse({'res':5, 'massage':'创建成功'})








        




        








