from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestDataRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Создает тестовых пользователей и заметку для проверки маршрутов."""
        cls.note_author = User.objects.create(username='note_author')
        cls.other_user = User.objects.create(username='other_user')
        cls.author_client = Client()
        cls.other_user_client = Client()
        cls.author_client.force_login(cls.note_author)
        cls.other_user_client.force_login(cls.other_user)
        cls.note = Note.objects.create(
            title='Sample Title',
            text='Sample Text',
            slug='sample-slug',
            author=cls.note_author
        )
        cls.note_args = (cls.note.slug,)


class TestRoutes(TestDataRoutes, TestCase):

    def test_page_availability_for_anonymous_user(self):
        """
        Проверяет доступность определенных страниц
        для анонимного пользователя.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_availability_for_authenticated_user(self):
        """
        Проверяет доступность определенных страниц
        для аутентифицированного пользователя.
        """
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.author_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_delete_detail_access_based_on_user_role(self):
        """
        Проверяет доступность страниц редактирования,
        удаления и просмотра заметки. Доступ к этим
        страницам зависит от того, является ли
        пользователь автором заметки.
        """
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.other_user_client, HTTPStatus.NOT_FOUND)
        )

        for client, status in users_statuses:
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(client=client, name=name):
                    response = client.get(reverse(name, args=self.note_args))
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_user_to_login(self):
        """
        Проверяет, что анонимный пользователь
        перенаправляется на страницу логина
        при попытке доступа к защищенным страницам.
        """
        urls = (
            ('notes:edit', self.note_args),
            ('notes:detail', self.note_args),
            ('notes:delete', self.note_args),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                self.assertRedirects(
                    self.client.get(reverse(name, args=args)),
                    f"{reverse('users:login')}?next={reverse(name, args=args)}"
                )
