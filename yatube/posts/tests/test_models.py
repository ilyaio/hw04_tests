from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def verbose_name_post(self):
        """verbose_name в полях модели Post совпадает с ожидаемым"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'group': 'Группа',
            'author': 'Автор поста', }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_fieled(field).verbose_name, expected_value)

    def test_object_name_is_text_field(self):
        """__str__  post - это строчка с содержимым post.text."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def verbose_name_group(self):
        """verbose_name в полях модели Group совпадает с ожидаемым"""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Адрес url для группы',
            'description': 'Описание Группы', }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_fieled(field).verbose_name, expected_value)

    def test_group_name_is_text_field(self):
        """__str__  post - это строчка с содержимым post.text."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
