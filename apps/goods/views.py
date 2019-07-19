from django.shortcuts import render ,redirect, reverse
from django.views.generic import View
from django.core.cache import cache
from django.core.paginator import Paginator
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner, GoodsSKU
from order.models import OrderGoods
from django_redis import get_redis_connection
# Create your views here.
# Create your views here.

# /index
class IndexView(View):
    '''首页'''
    def get(self, request):
        '''显示首页'''
        # 获取商品种类信息
        # 从缓存获取数据
        context = cache.get('index_pang_data')
        if context is None:
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

# id 页码 排序方式
# /list/id/页码?sort=排列方式
class ListView(View):
    """ 列表页 """
    def get(self, request, type_id, page):
        # 获取种类信息
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            # 种类不存在
            return redirect(reverse('goods:index'))

        # 获取商品的种类信息
        types = GoodsType.objects.all()

        # 获取排序方式：
        # sort = default    默认排序
        # sort = price      价钱
        # sort = hot        销量
        sort = request.GET.get('sort')
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')


        paginator = Paginator(skus, 1)

        # 获取页码
        try:
            page = int(page)
        except expression as e:
            page = 1

        if page > paginator.num_pages:
            page = 1
        
        # 获取page的skus
        skus_page = paginator.page(page)

        # 页码控制
        # 总页码小于5页，显示全部
        # 当前是前3页，显示1-5
        # 如当前页是后3页，显示后5页
        # 其他情况，显示当前页前2，后2
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages+1)
        elif page <= 3:
            pages = range(1, 5)
        elif num_pages - page <= 2:
            pages = range(num_pages-4, num_pages+1)
        else:
            pages = range(num_pages-2, num_pages+3)

        # 获取新品
        New_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)
        

        # 组织上下文
        context ={  'type':type, 'types':types,
                    'skus_page':skus_page,
                    'New_skus':New_skus,
                    'cart_count':cart_count,
                    'pages':pages,
                    'sort':sort}

        return render(request, 'list.html', context)