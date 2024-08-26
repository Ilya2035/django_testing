from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тесты для проверки доступности маршрутов приложения."""
    @classmethod
    def setUpTestData(cls):
        """
        Устанавливает начальные данные для тестов:
        создает автора заметки и другого пользователя.
        """
        cls.author = User.objects.create_user(username='author',
                                              password='password123')
        cls.other_user = User.objects.create_user(username='other_user',
                                                  password='password123')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Это текст тестовой заметки',
            slug='test-note',
            author=cls.author
        )

    def test_home_page_accessible_to_anonymous(self):
        """Проверяет, что главная страница доступна анонимным пользователям."""
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_accessible_to_authenticated_user(self):
        """Проверяет доступность страниц для авторизованного пользователя."""
        self.client.login(username='author', password='password123')
        authenticated_urls = [
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None)
        ]
        for url_name, args in authenticated_urls:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_access_restricted_to_author(self):
        """
        Проверяет, что доступ к страницам заметок ограничен их авторами,
        возвращая ошибку 404 для других пользователей.
        """
        self.client.login(username='author', password='password123')
        author_only_urls = [
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        ]
        for url_name, args in author_only_urls:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

        self.client.login(username='other_user', password='password123')
        for url_name, args in author_only_urls:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_users_redirected_to_login(self):
        """
        Проверяет, что анонимные пользователи перенаправляются на страницу
        логина при попытке доступа к защищённым страницам.
        """
        protected_urls = [
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        ]
        for url_name, args in protected_urls:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name, args=args))
                expected_url = (f"{reverse('users:login')}?next="
                                f"{reverse(url_name, args=args)}")
                self.assertRedirects(response, expected_url)

    def test_auth_pages_accessible_to_all(self):
        """Проверяет, что страницы авторизации доступны всем пользователям."""
        auth_urls = [
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None)
        ]
        for url_name, args in auth_urls:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, HTTPStatus.OK)
