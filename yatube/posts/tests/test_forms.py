import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()

# Для ревьювера: Я сохраняю комментариий, чтобы потом самому вспомнить,
# что делает данный код
# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем тестовую группу
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        # Create test user
        cls.user = User.objects.create_user(username='test_user')
        # Создаем запись в базе данных для проверки
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()

        form_fields = {
            'text': PostCreateFormTests.post.text,
            'group': PostCreateFormTests.group.pk,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_fields,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{PostCreateFormTests.user.username}'}))

        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)

        # Проверяем, что создалась запись
        self.assertTrue(
            Post.objects.filter(
                group=PostCreateFormTests.group.pk,
                text=PostCreateFormTests.post.text,
            ).exists()
        )

    def test_cant_create_post_without_text(self):
        """Форма не создает запись в Post без текста."""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()

        form_fields = {
            'text': '',
            'group': PostCreateFormTests.group.pk,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_fields,
            follow=True
        )
        # Убедимся, что запись в базе данных не создалась:
        # сравним количество записей в Task до и после отправки формы
        self.assertEqual(Post.objects.count(), post_count)
        # Проверим, что форма вернула ошибку с ожидаемым текстом:
        # из объекта response берём словарь 'form',
        # указываем ожидаемую ошибку для поля 'slug' этого словаря
        self.assertFormError(
            response,
            'form',
            'text',
            'Обязательное поле.'
        )
        # Проверим, что ничего не упало и страница отдаёт код 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.count()

        form_fields = {
            'text': 'Тестовый текст изм',
            'group': PostCreateFormTests.group.pk,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{PostCreateFormTests.post.id}'}),
            data=form_fields,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{PostCreateFormTests.post.id}'}))

        # Проверяем, что не увеличилось число постов
        self.assertEqual(Post.objects.count(), post_count)

        # Проверяем, что запись изменилась
        self.assertTrue(
            Post.objects.filter(
                group=PostCreateFormTests.group.pk,
                text=form_fields['text'], id=PostCreateFormTests.post.id,
            ).exists()
        )
