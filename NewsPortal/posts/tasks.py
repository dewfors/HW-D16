import datetime
import os

from celery import shared_task
import time
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Post, Category


@shared_task
def send_post_notification(post_pk):
    post = Post.objects.select_related('category').get(id=post_pk)
    categories = post.category.all()

    emails = set()
    for category in categories:
        emails.update(category.subscribe.values_list('email', flat=True))

    post_link = f'{settings.SITE_URL}/post/{post_pk}'
    html_content = render_to_string(
        'subscribe.html',
        {
            'user_name': '',
            'post': post,
            'post_link': post_link,
        }
    )
    msg = EmailMultiAlternatives(
        subject=f'{post.title}',
        body=post.article_text[0:50],
        from_email=os.getenv('EMAIL_SENDER'),
        to=list(emails),
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task
def weekly_notifications():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(time_create__gte=last_week)  # __gte - больше или равно
    categories = set(posts.values_list('category__title', flat=True))
    subscribers = set(Category.objects.filter(title__in=categories).values_list('subscribers__email', flat=True))
    print(subscribers)

    html_content = render_to_string(
        'weekly_posts.html',
        {
            'link': settings.SITE_URL,
            'posts': posts,
        }
    )

    msg = EmailMultiAlternatives(
        subject='Статьи за прошедшую неделю',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()

