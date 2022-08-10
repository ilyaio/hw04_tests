from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Group, Post
from .test_models import PostModelTest
from http import HTTPStatus

User = get_user_model()


class PostsURLTests(TestCase):
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
        )
        cls.non_author = User.objects.create_user(username='non_author')

    def setUp(self):
        self.guest_client = Client()
        # Create client for authorized user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Create client for non-author
        self.non_author_client = Client()
        self.non_author_client.force_login(self.non_author)

    def test_for_public_pages(self):
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/profile.html': '/profile/test_user/',
            'posts/post_detail.html': f'/posts/{PostModelTest.post.id}/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_only_authorized(self):
        templates_url_names = {
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.non_author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_only_author(self):
        templates_url_names = {
            f'/posts/{PostModelTest.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_null_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
