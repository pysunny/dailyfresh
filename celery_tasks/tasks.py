# 使用celery
from django.core.mail import send_mail
from django.conf import settings
from celery import Celery

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
django.setup()

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
    html_massage = '<h1>%s,欢迎你成为天天生鲜会员</h1>请点击一下链接激活你的账号<br/><a href="http://192.168.1.179:8000/user/active/%s">点击激活</a>'%(username, token)
    # 家里IP
    #html_massage = '<h1>%s,欢迎你成为天天生鲜会员</h1>请点击一下链接激活你的账号<br/><a href="http://192.168.31.92:8000/user/active/%s">点击激活</a>'%(username, token)
    send_mail(subject, message, sender, receiver, html_message=html_massage)