import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.core.mail import send_mail, EmailMultiAlternatives
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .filters import PostFilter
from .forms import PostForm
from .models import Post, Category, Author, PostCategory


class PostList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-time_create'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'posts.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset

        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    # pk_url_kwarg = 'id'

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'new_detail-{self.kwargs["pk"]}', None)

        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'new_detail-{self.kwargs["pk"]}', obj)

        return obj


class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('posts.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'news'
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        title = request.POST['title']
        article_text = request.POST['article_text']
        author = Author.objects.get(pk=int(request.POST['author']))
        category = Category.objects.get(pk=int(request.POST['category']))
        type = 'news'

        new = Post(
            title=title,
            article_text=article_text,
            author=author,
            # category=category,
            type=type,
        )
        new.save()
        PostCategory.objects.create(category=category, post=new)
        new.save()

        return redirect('post_list')


class NewsEdit(PermissionRequiredMixin, UpdateView):
    permission_required = ('posts.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'news'
        return super().form_valid(form)


class NewsDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    # pk_url_kwarg = 'id'

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'post_detail-{self.kwargs["pk"]}', None)

        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post_detail-{self.kwargs["pk"]}', obj)

        return obj


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('posts.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'post'
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        title = request.POST['title']
        article_text = request.POST['article_text']
        author = Author.objects.get(pk=int(request.POST['author']))
        category = Category.objects.get(pk=int(request.POST['category']))
        type = 'post'

        new_post = Post(
            title=title,
            article_text=article_text,
            author=author,
            # category=category,
            type=type,
        )
        new_post.save()
        PostCategory.objects.create(category=category, post=new_post)

        subscribers = category.subscribers.all()

        send_email(subscribers=subscribers, new_post=new_post)

        return redirect('post_list')


class PostEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('posts.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'post'
        return super().form_valid(form)


class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class CategoryListView(ListView):
    model = Post
    template_name = 'category_list.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.category).order_by('-time_create')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category

        return context


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    print(request)

    # Отправка письма
    subject = f'Вы подписались на рассылку категории: {category.title}'
    message = f'Здравствуйте, {user.username}! \nВы подписались на рассылку категории: {category.title}'
    from_email = os.getenv('EMAIL_SENDER')

    send_mail(subject, message, from_email, [user.email])

    return redirect(f'/categories/{pk}')
