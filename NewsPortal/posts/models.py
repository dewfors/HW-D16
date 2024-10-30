from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Author(models.Model):
    rating = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def update_rating(self):
        posts_rating = 0
        all_posts = Post.objects.filter(author_id=self.pk)
        for post in all_posts:
            posts_rating += post.rating
        posts_rating *= 3

        comments_rating = 0
        all_comments_author = Comment.objects.filter(user_id=self.user.pk)
        for comment in all_comments_author:
            comments_rating += comment.rating

        comments_by_author_posts_rating = 0
        all_comments_by_author_posts = Comment.objects.filter(post__author_id=self.pk)
        for comment in all_comments_by_author_posts:
            comments_by_author_posts_rating += comment.rating

        self.rating = posts_rating + comments_rating + comments_by_author_posts_rating
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    subscribers = models.ManyToManyField(User, related_name='categories', through='CategorySubscribe')

    def __str__(self):
        return self.title.title()


class Post(models.Model):
    post = 'post'
    news = 'news'
    TYPES = [
        (post, 'Статья'),
        (news, 'Новость'),
    ]

    title = models.CharField(max_length=255)
    article_text = models.TextField(default="Новость дня")
    rating = models.IntegerField(default=0)
    type = models.CharField(max_length=4, choices=TYPES, default=news)
    time_create = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, through='PostCategory')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating = (self.rating - 1) if self.rating > 0 else 0
        self.save()

    def preview(self):
        return self.article_text[:124]

    def __str__(self):
        return f'{self.title[:10]}: {self.article_text[:10]}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    comment_text = models.TextField()
    rating = models.IntegerField(default=0)
    time_create = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating = (self.rating - 1) if self.rating > 0 else 0
        self.save()


class CategorySubscribe(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)
