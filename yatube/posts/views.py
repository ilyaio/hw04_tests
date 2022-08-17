from django.contrib.auth.decorators import login_required
from django.shortcuts import (get_object_or_404, redirect,
                              render, get_list_or_404)
# from django.views.decorators.cache import cache_page
from posts.utils.paginator import get_page_context

from .forms import PostForm, CommentForm
from .models import Group, Post, User


# @cache_page(20, key_prefix = 'index_page')
def index(request):
    '''Main page'''
    post_list = (Post.objects.select_related("group", "author")
                 .order_by('-pub_date'))
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = get_page_context(post_list, request)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    '''Page with posts of the group'''
    # Функция get_object_or_404 получает по заданным критериям объект
    # из базы данных или возвращает сообщение об ошибке, если объект не найден.
    # В нашем случае в переменную group будут переданы объекты модели Group,
    # поле slug у которых соответствует значению slug в запросе
    group = get_object_or_404(Group, slug=slug)
    # Метод .filter позволяет ограничить поиск по критериям.
    # Это аналог добавления
    # условия WHERE group_id = {group_id}
    # posts = get_list_or_404(Post.objects.order_by('-pub_date'), group=group)
    posts = Post.objects.order_by('-pub_date').filter(group=group)
    page_obj = get_page_context(posts, request)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related("group", "author").order_by('-pub_date')
    count_post = posts.count()

    page_obj = get_page_context(posts, request)

    context = {
        'author': user,
        'page_obj': page_obj,
        'count_post': count_post,

    }
    return render(request, 'posts/profile.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.filter(author_id=post.author.id).count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post_count': post_count,
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect('posts:profile', post.author)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)

    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)
