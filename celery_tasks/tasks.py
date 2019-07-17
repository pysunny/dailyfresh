# 使用celery
from django.core.mail import send_mail
from django.conf import settings
from celery import Celery

from django.template import loader

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
django.setup()

from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner

# 创建celery对象
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/8')

# 定义任务函数
@app.task
def send_register_email(to_email, username, token):
    # 发送激活邮件
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_massage = '<h1>%s,欢迎你成为天天生鲜会员</h1>请点击一下链接激活你的账号<br/><a href="http://192.168.1.192:8000/user/active/%s">点击激活</a>'%(username, token)
    # 家里IP
    #html_massage = '<h1>%s,欢迎你成为天天生鲜会员</h1>请点击一下链接激活你的账号<br/><a href="http://192.168.31.92:8000/user/active/%s">点击激活</a>'%(username, token)
    send_mail(subject, message, sender, receiver, html_message=html_massage)

@app.task
def generate_static_index_html():

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
                'promotion_banners':promotion_banners}

    temp = loader.get_template('static_index.html')

    static_index_html = temp.render(context)

    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')

    with open(save_path , 'w') as f:
        f.write(static_index_html)
    
    # return render(request, 'index.html', context)
