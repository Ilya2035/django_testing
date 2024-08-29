from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note
from notes.tests.fixtures import (
    TestDataLogicForNoteCreation,
    TestDataLogicForNoteEditDelete
)

User = get_user_model()


class TestNoteCreation(TestDataLogicForNoteCreation, TestCase):

    def test_anonymous_user_cannot_create_note(self):
        """Проверяет, что анонимный пользователь не может создавать заметки."""
        initial_count = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, initial_count)

    def test_logged_in_user_can_create_note(self):
        """Проверяет, что залогиненный пользователь может создать заметку."""
        initial_count = Note.objects.count()
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

        self.assertEqual(Note.objects.count(), initial_count + 1)
        note = Note.objects.last()
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])

    def test_note_slug_uniqueness(self):
        """Проверяет, что нельзя создать заметки с одинаковыми slug."""
        note = Note.objects.create(
            author=self.user,
            title='Note title',
            text='New text',
            slug='new-note'
        )
        initial_count = Note.objects.count()
        self.form_data['slug'] = note.slug
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{note.slug}{WARNING}'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, initial_count)

    def test_auto_slug_generation(self):
        """Проверяет автоматическое создание slug, если поле не заполнено."""
        initial_count = Note.objects.count()
        del self.form_data['slug']
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, initial_count + 1)

        note = Note.objects.get(title=self.form_data['title'])
        self.assertEqual(note.slug, slugify(self.form_data['title']))


class TestNoteEditDelete(TestDataLogicForNoteEditDelete, TestCase):

    def test_author_can_delete_note(self):
        """Проверяет, что автор может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_non_author_cannot_delete_note(self):
        """Проверяет, что неавтор не может удалить чужую заметку."""
        response = self.other_user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Проверяет, что автор может изменять свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])

    def test_non_author_cannot_edit_note(self):
        """Проверяет, что неавтор не может редактировать чужую заметку."""
        original_slug = self.note.slug
        original_title = self.note.title
        original_text = self.note.text
        response = self.other_user_client.post(self.edit_url,
                                               data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.slug, original_slug)
        self.assertEqual(self.note.title, original_title)
        self.assertEqual(self.note.text, original_text)
