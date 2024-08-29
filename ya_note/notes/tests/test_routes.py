from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.tests.fixtures import TestDataRoutes

User = get_user_model()


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
                url = reverse(name)
                response = self.client.get(url)
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
                url = reverse(name)
                response = self.author_client.get(url)
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
                    url = reverse(name, args=(self.note.slug,))
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_user_to_login(self):
        """
        Проверяет, что анонимный пользователь
        перенаправляется на страницу логина
        при попытке доступа к защищенным страницам.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
#конец
