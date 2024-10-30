from django.urls import path

# Импортируем созданное нами представление
from .views import PostList, NewsDetail, NewsCreate, NewsEdit, NewsDelete, PostCreate, PostEdit, PostDelete, \
    CategoryListView, subscribe
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(60)(PostList.as_view()), name='post_list'),
    path('post/<int:pk>', cache_page(300)(NewsDetail.as_view()), name='post_detail'),

    # новости
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/edit', NewsEdit.as_view(), name='news_edit'),
    path('news/<int:pk>/delete', NewsDelete.as_view(), name='news_delete'),

    # статьи
    path('articles/create/', PostCreate.as_view(), name='article_create'),
    path('articles/<int:pk>/edit', PostEdit.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete', PostDelete.as_view(), name='article_delete'),

    # по категориям
    path('categories/<int:pk>', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/subscribe', subscribe, name='subscribe'),
]
