from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNoteContent(TestCase):
    """
    Тесты для проверки содержания заметок и их видимости для пользователей.
    Проверяет видимость заметок в списке и наличие форм в контексте.
    """
    @classmethod
    def setUpTestData(cls):
        """
        Устанавливает начальные данные для тестов:
        создает автора заметки и другого пользователя.
        """
        cls.author = User.objects.create_user(
            username='author',
            password='password123'
        )
        cls.other_user = User.objects.create_user(
            username='other_user',
            password='password123'
        )
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Это текст тестовой заметки',
            slug='test-note',
            author=cls.author
        )
        cls.other_note = Note.objects.create(
            title='Другая заметка',
            text='Это текст другой заметки',
            slug='other-note',
            author=cls.other_user
        )

    def test_note_in_object_list_and_user_visibility(self):
        """
        Проверяет, что заметка отображается в списке для авторизованного
        пользователя и что каждый пользователь видит только свои заметки.
        """
        self.client.login(username='author', password='password123')
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.note, response.context['object_list'])

        object_list = response.context['object_list']
        for note in object_list:
            self.assertEqual(note.author, self.author)

        self.client.login(username='other_user', password='password123')
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        for note in object_list:
            self.assertEqual(note.author, self.other_user)

    def test_create_and_edit_forms_in_context(self):
        """
        Проверяет наличие форм создания и
        редактирования заметок в контексте.
        """
        self.client.login(username='author', password='password123')

        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

        response = self.client.get(reverse('notes:edit',
                                           args=(self.note.slug,)))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_anonymous_user_redirect_to_login(self):
        """
        Проверяет, что анонимные пользователи перенаправляются на страницу
        логина при попытке доступа к защищённым страницам.
        """
        protected_urls = [
            reverse('notes:list'),
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
            reverse('notes:detail', args=(self.note.slug,))
        ]
        login_url = reverse('users:login')
        for url in protected_urls:
            response = self.client.get(url)
            expected_url = f"{login_url}?next={url}"
            self.assertRedirects(response, expected_url)
