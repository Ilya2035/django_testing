from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.tests.fixtures import TestDataContent


class TestContent(TestDataContent, TestCase):

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
            with self.subTest(client=client, expected_in_list=expected_in_list):
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
