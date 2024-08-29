from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestDataContent(TestCase):
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


class TestDataLogicForNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестирования создания заметок."""
        cls.user = User.objects.create(username='test_user')
        cls.url = reverse('notes:add')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.form_data = {
            'title': 'New Note',
            'text': 'Some text',
            'slug': 'new-note'
        }


class TestDataLogicForNoteEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Подготовка данных для тестирования
        редактирования и удаления заметок.
        """
        cls.note_author = User.objects.create(username='note_author')
        cls.other_user = User.objects.create(username='other_user')
        cls.author_client = Client()
        cls.author_client.force_login(cls.note_author)
        cls.other_user_client = Client()
        cls.other_user_client.force_login(cls.other_user)
        cls.note = Note.objects.create(
            title='Sample Title',
            text='Sample Text',
            slug='sample-slug',
            author=cls.note_author
        )
        cls.url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': 'Updated Note',
            'text': 'Updated text',
            'slug': 'updated-note'
        }


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
#конец
