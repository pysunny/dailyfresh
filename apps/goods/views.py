from django.shortcuts import render ,redirect, reverse
from django.views.generic import View
from django.core.cache import cache
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner, GoodsSKU
from order.models import OrderGoods
from django_redis import get_redis_connection
# Create your views here.
# Create your views here.

# http://127.0.0.1:8000
class IndexView(View):
    '''首页'''
    def get(self, request):
        '''显示首页'''
        # 获取商品种类信息
        # 从缓存获取数据
        context = cache.get('index_pang_data')
        if context is None:
            print('设置缓存')
            # 没有缓存
            types = GoodsType.objects.all()

            # 获取轮播商品信息
            goods_banners = IndexGoodsBanner.objects.all().order_by('index')

            # 获取促销商品信息
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

            # 获取首页分类商品展示信息
            # type_goods_banners = IndexTypeGoodsBanner.objects.all()
            for type in types:
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
                # 动态添加属性
                type.image_banners = image_banners
                type.title_banners = title_banners

            context = { 'types':types,
                        'goods_banners':goods_banners,
                        'promotion_banners':promotion_banners,}

            cache.set('index_pang_data', context, 3600)

        # 获取购物车商品数量
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)
        
        context.update(cart_count=cart_count)
        
        return render(request, 'index.html', context)

#/good/id
class DetailView(View):
    """ 详情页 """
    def get(self, request, goods_id):
        # 详情页
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return redirect(reverse('goods:index'))

        # 获取商品的种类信息
        types = GoodsType.objects.all()

        # 获取商品评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 获取新品
        New_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]

        # 获取相同spu的商品
        same_spu_skus= GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)


        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)

            # 添加历史浏览记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移除
            conn.lrem(history_key, 0, goods_id)
            # 插入
            conn.lpush(history_key, goods_id)
            # 只保存5条
            conn.ltrim(history_key, 0 ,4)

        context ={  'sku':sku, 'types':types,
                    'sku_orders':sku_orders,
                    'New_skus':New_skus,
                    'same_spu_skus':same_spu_skus,
                    'cart_count':cart_count}
        # 使用模板
        return render(request, 'detail.html' ,context)