from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных для проверки видимости заметок."""
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

    def test_note_visibility_in_list(self):
        """
        Проверяет видимость заметки в списке заметок для разных пользователей.
        Автор заметки должен видеть её, другие пользователи — нет.
        """
        test_cases = [
            (self.author_client, True),
            (self.other_user_client, False),
        ]

        for client, expected_in_list in test_cases:
            with self.subTest(
                    client=client,
                    expected_in_list=expected_in_list
            ):
                url = reverse('notes:list')
                response = client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, expected_in_list)

    def test_form_presence_on_create_and_edit_pages(self):
        """
        Проверяет наличие и корректность формы
        на страницах создания и редактирования заметки.
        """
        urls = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertIn('form', response.context)
                form_obj = response.context['form']
                self.assertIsInstance(form_obj, NoteForm)
