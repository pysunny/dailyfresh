from django.contrib import admin
from goods.models import GoodsType, GoodsSKU, Goods, GoodsImage, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner
# Register your models here.
# 商品种类
admin.site.register(GoodsType)
# 商品SPK
admin.site.register(GoodsSKU)
# 商品SPU
admin.site.register(Goods)
# 商品图片
admin.site.register(GoodsImage)
# 首页轮播商品
admin.site.register(IndexGoodsBanner)
# 首页分类商品
admin.site.register(IndexTypeGoodsBanner)
# 首页促销活动
admin.site.register(IndexPromotionBanner)
