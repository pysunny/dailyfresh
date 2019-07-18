from django.contrib import admin
from django.core.cache import cache
from goods.models import GoodsType, GoodsSKU, Goods, GoodsImage, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner
# Register your models here.

class BasicModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()
        # 清楚缓存
        cache.delete('index_pang_data')


    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()
        cache.delete('index_pang_data')


class GoodsTypeAdmin(BasicModelAdmin):
    pass

class GoodsSKUAdmin(BasicModelAdmin):
    pass

class GoodsAdmin(BasicModelAdmin):
    pass

class GoodsImageAdmin(BasicModelAdmin):
    pass

class IndexGoodsBannerAdmin(BasicModelAdmin):
    pass

class IndexTypeGoodsBannerAdmin(BasicModelAdmin):
    pass

class IndexPromotionBannerAdmin(BasicModelAdmin):
    pass


# 商品种类
admin.site.register(GoodsType, GoodsTypeAdmin)
# 商品SPK
admin.site.register(GoodsSKU, GoodsSKUAdmin)
# 商品SPU
admin.site.register(Goods, GoodsAdmin)
# 商品图片
admin.site.register(GoodsImage, GoodsImageAdmin)
# 首页轮播商品
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
# 首页分类商品
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
# 首页促销活动
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)

