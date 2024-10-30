from django import forms
from django_filters import FilterSet, CharFilter, DateFilter
from .models import Post


class PostFilter(FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains', label='Название')
    author = CharFilter(field_name='author__user__username', lookup_expr='icontains', label='Имя автора')
    post_date = DateFilter(field_name='time_create', lookup_expr='gt', widget=forms.DateInput(attrs={'type': 'date'}),
                           label='Поиск по дате')

    class Meta:
        model = Post
        fields = []
