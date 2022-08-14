from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group_list', kwargs={
                'slug': PostPagesTests.group.slug})):
            'posts/group_list.html',
            (reverse('posts:profile', kwargs={
                'username': PostPagesTests.user.username})):
            'posts/profile.html',
            (reverse('posts:post_detail',
             kwargs={'post_id': PostPagesTests.post.id})):
            'posts/post_detail.html',
            (reverse('posts:post_edit',
             kwargs={'post_id': PostPagesTests.post.id})):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',

        }
# Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PostsViewsTest(TestCase):

    TOTAL_POSTS_FOR_T = 18
    TOTAL_POSTS_WITH_GROUP = 13
    TOTAL_POSTS_WITH_GROUP_P2 = TOTAL_POSTS_WITH_GROUP - settings.POST_PER_PAGE
    POSTS_ON_PAGE_2 = 8

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )

        cls.user = User.objects.create_user(username='test_user')
        for post in range(PostsViewsTest.TOTAL_POSTS_WITH_GROUP):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовая запись #{post}',
                group=PostsViewsTest.group,

            )
        for post in range(PostsViewsTest.TOTAL_POSTS_WITH_GROUP,
                          PostsViewsTest.TOTAL_POSTS_FOR_T):
            cls.post = Post.objects.create(
                author=PostsViewsTest.user,
                text=f'Тестовая запись #{post}',)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTest.user)

    def compare_two_posts(self, arg_1, arg_2):
        """Функция для сверки двух постов по text, id, author_id
        arg_1 - проверяемый post, arg_2 - ожидаемый пост"""
        return (self.assertEqual(arg_1.text, arg_2.text),
                self.assertEqual(arg_1.id, arg_2.id),
                self.assertEqual(arg_1.author.id, arg_2.author.id))

    def test_post_index_correct_context(self):
        """Список постов переданный через контекст в index корректен"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(len(
            response.context['page_obj']), settings.POST_PER_PAGE)
        response_2 = self.authorized_client.get(reverse
                                                ('posts:index') + '?page=2')
        self.assertEqual(len(
            response_2.context['page_obj']), self.POSTS_ON_PAGE_2)
        self.compare_two_posts(first_post, self.post)

    def test_first_group_page_contains_ten_records(self):
        """Шаблон group_list сформирован с корректной паджинацией для
        первых 10 постов группы."""
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug':
                                                      PostPagesTests.group.slug
                                                      }))
        self.assertEqual(len(
            response.context['page_obj']), settings.POST_PER_PAGE)

    def test_second_group_page_contains_four_records(self):
        """Шаблон group_list сформирован с корректной паджинацией для\
        следующих 3 постов группы."""
        response = self.client.get(reverse('posts:group_list',
                                   kwargs={'slug': 'test_slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         self.TOTAL_POSTS_WITH_GROUP_P2)

    def test_first_profile_page_contains_ten_records(self):
        """Шаблон profile сформирован с корректной паджинацией для
        первых 10 постов группы."""
        response = (
            self.authorized_client.get(
                reverse('posts:profile',
                        kwargs={'username': PostPagesTests.user.username})))
        self.assertEqual(len(
            response.context['page_obj']), settings.POST_PER_PAGE)

    def test_second_profile_page_contains_four_records(self):
        """Шаблон group_list сформирован с корректной паджинацией для\
        следующих 4 постов группы."""
        # Проверка: на второй странице должно быть 8 постов.
        response = self.client.get(
            reverse('posts:profile',
                    kwargs={'username':
                            PostPagesTests.user.username}) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), self.POSTS_ON_PAGE_2)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        # Вызываем пост для теста
        post_for_test = get_object_or_404(Post, id=self.TOTAL_POSTS_WITH_GROUP)
        response = (
            self.authorized_client.get(reverse('posts:post_detail',
                                       kwargs={'post_id':
                                               self.TOTAL_POSTS_WITH_GROUP})))
        object = response.context['post']
        post_group = object.group
        post_author = object.author
        post_count = response.context['post_count']
        self.compare_two_posts(object, post_for_test)
        self.assertEqual(post_group.id, post_for_test.group.id)
        self.assertEqual(post_author.id, post_for_test.author.id)
        self.assertEqual(post_count, self.TOTAL_POSTS_FOR_T)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        post_for_test = get_object_or_404(Post, id=self.TOTAL_POSTS_WITH_GROUP)
        response = (
            self.authorized_client.
            get(reverse('posts:post_edit',
                kwargs={'post_id': self.TOTAL_POSTS_WITH_GROUP})))
        first_object = response.context['post']
        post_group_0 = first_object.group
        self.compare_two_posts(first_object, post_for_test)
        self.assertEqual(post_group_0.id, post_for_test.group.id)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_home_group_profile_post(self):
        """Проверка, что если при создание поста указать группу, то она
        появляется на главной стр., на стр. выбранной группы,
        в профайле пользователя."""

        # Последний пост для тестов
        self.post_last = Post.objects.create(
            author=self.user,
            text=f'Тестовая запись #{self.post}',
            group=PostsViewsTest.group,)

        url = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': PostPagesTests.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': PostPagesTests.user.username}),
        )
        for adress in url:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                first_object = response.context['page_obj'][0]
                post_group = first_object.group
                self.compare_two_posts(first_object, self.post_last)
                self.assertEqual(post_group.id, self.post_last.group.id)
