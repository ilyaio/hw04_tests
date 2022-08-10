from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

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
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group_list', kwargs={
                'slug': 'test_slug'})):
            'posts/group_list.html',
            (reverse('posts:profile', kwargs={'username': 'test_user'})):
            'posts/profile.html',
            (reverse('posts:post_detail',
             kwargs={'post_id': f'{PostPagesTests.post.id}'})):
            'posts/post_detail.html',
            (reverse('posts:post_edit',
             kwargs={'post_id': f'{PostPagesTests.post.id}'})):
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
    POSTS_ON_PAGE_1 = 10
    POSTS_ON_PAGE_2 = 8

    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # Создаем посты без Группы
        for post in range(self.TOTAL_POSTS_WITH_GROUP):
            self.post = Post.objects.create(
                author=self.user,
                text=f'Тестовая запись #{post}',
                group=PostsViewsTest.group,

            )

        # Создаем посты без Группы
        for post in range(self.TOTAL_POSTS_WITH_GROUP, self.TOTAL_POSTS_FOR_T):
            self.post = Post.objects.create(
                author=self.user,
                text=f'Тестовая запись #{post}',)

    def test_post_index_correct_context(self):
        """Список постов переданный через контекст в index корректен"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(
            response.context['page_obj']), self.POSTS_ON_PAGE_1)
        # Шаблон index сформирован с корректной паджинацией для
        # следующих 8 постов главной страницы.
        response_2 = self.authorized_client.get(reverse
                                                ('posts:index') + '?page=2')
        self.assertEqual(len(
            response_2.context['page_obj']), self.POSTS_ON_PAGE_2)
        self.assertEqual(first_post.author, self.post.author)
        self.assertEqual(first_post.text, self.post.text)

    # Проверяем паджинацию на странице постов с группами
    def test_first_group_page_contains_ten_records(self):
        """Шаблон group_list сформирован с корректной паджинацией для
        первых 10 постов группы."""
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug': 'test_slug'}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(
            response.context['page_obj']), self.POSTS_ON_PAGE_1)

    def test_second_group_page_contains_four_records(self):
        """Шаблон group_list сформирован с корректной паджинацией для\
        следующих 3 постов группы."""
        # Проверка: на второй странице должно быть 8 постов.
        response = self.client.get(reverse('posts:group_list',
                                   kwargs={'slug': 'test_slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    # Проверяем паджинацию на странице профиля
    def test_first_profile_page_contains_ten_records(self):
        """Шаблон profile сформирован с корректной паджинацией для
        первых 10 постов группы."""
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username': 'test_user'})
                                              )
        # Проверка: количество постов на первой странице равно 10.

        self.assertEqual(len(
            response.context['page_obj']), self.POSTS_ON_PAGE_1)

    def test_second_profile_page_contains_four_records(self):
        """Шаблон group_list сформирован с корректной паджинацией для\
        следующих 4 постов группы."""
        # Проверка: на второй странице должно быть 8 постов.
        response = self.client.get(reverse('posts:profile',
                                   kwargs={'username': 'test_user'})
                                   + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), self.POSTS_ON_PAGE_2)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (
            self.authorized_client.get(reverse('posts:post_detail',
                                       kwargs={'post_id': f'{self.post.id-5}'})
                                       ))
        first_object = response.context['post']
        post_text = first_object.text
        post_group = first_object.group
        post_author = first_object.author
        post_count = response.context['post_count']
        self.assertEqual(post_text, 'Тестовая запись #12')
        self.assertEqual(str(post_group), 'Тестовая группа')
        self.assertEqual(str(post_author), 'test_user')
        self.assertEqual(post_count, self.TOTAL_POSTS_FOR_T)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = (
            self.authorized_client.
            get(reverse('posts:post_edit',
                kwargs={'post_id': f'{self.post.id - 5}'})))
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, 'Тестовая запись #12')
        self.assertEqual(str(post_group_0), 'Тестовая группа')

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
                    kwargs={'slug': 'test_slug'}),
            reverse('posts:profile',
                    kwargs={'username': 'test_user'}),
        )
        for adress in url:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                first_object = response.context['page_obj'][0]
                post_author = first_object.author
                post_text = first_object.text
                post_group = first_object.group
                self.assertEqual(post_author, self.post_last.author)
                self.assertEqual(post_text, self.post_last.text)
                self.assertEqual(post_group, self.post_last.group)
