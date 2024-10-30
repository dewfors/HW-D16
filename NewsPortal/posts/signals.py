import os

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import Post, PostCategory
from .tasks import send_post_notification


@receiver(post_save, sender=Post)
def notify_managers_appointment(sender, instance, created, **kwargs):

    send_post_notification.delay(instance.pk)

    # post_cats = PostCategory.objects.filter(post=instance)
    # subscribers = []
    # for cat in post_cats:
    #     subs = cat.category.subscribers.all()
    #     for sub in subs:
    #         if sub not in subscribers:
    #             subscribers.append(sub)
    #             print(sub)
    #
    # # здесь должна быть отправка почты
    # post_link = f'{settings.SITE_URL}/post/{instance.pk}'
    #
    # for subscriber in subscribers:
    #     html_content = render_to_string(
    #         'subscribe.html',
    #         {
    #             'user_name': subscriber.username,
    #             'post': instance,
    #             'post_link': post_link,
    #         }
    #     )
    #     msg = EmailMultiAlternatives(
    #         subject=f'{instance.title}',
    #         body=instance.article_text[0:50],
    #         from_email=os.getenv('EMAIL_SENDER'),
    #         to=[subscriber.email],
    #     )
    #     msg.attach_alternative(html_content, 'text/html')
    #     msg.send()
