from django.shortcuts import render
from django.views.generic import View
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django_redis import get_redis_connection
# Create your views here.
# Create your views here.

# http://127.0.0.1:8000
class IndexView(View):
    '''首页'''
    def get(self, request):
        '''显示首页'''
        # 获取商品种类信息
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

        # 获取购物车商品数量
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)
        
        context = { 'types':types,
                    'goods_banners':goods_banners,
                    'promotion_banners':promotion_banners,
                    'cart_count':cart_count}

        return render(request, 'index.html', context)