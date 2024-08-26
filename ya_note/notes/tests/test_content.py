from django.test import TestCase
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user', password='password'
        )
        self.client.login(username='user', password='password')

    def test_note_in_object_list(self):
        note = Note.objects.create(
            title='Test Note', text='Test text', author=self.user
        )
        response = self.client.get('/notes/')
        self.assertIn(note, response.context['object_list'])

    def test_note_not_in_other_users_list(self):
        another_user = User.objects.create_user(
            username='user2', password='password'
        )
        note = Note.objects.create(
            title='Test Note', text='Test text', author=another_user
        )
        response = self.client.get('/notes/')
        self.assertNotIn(note, response.context['object_list'])

    def test_forms_in_create_and_edit_pages(self):
        response = self.client.get('/add/')
        self.assertIsInstance(response.context['form'], NoteForm)
        note = Note.objects.create(
            title='Test Note', text='Test text', author=self.user
        )
        response = self.client.get(f'/edit/{note.slug}/')
        self.assertIsInstance(response.context['form'], NoteForm)
