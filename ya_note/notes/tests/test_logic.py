from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тесты для проверки создания заметок."""
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        """
        Устанавливает начальные данные для тестов:
        создает пользователя и инициализирует клиента.
        """
        cls.user = User.objects.create(username='TestUser')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.note_data = {
            'title': 'Test Note',
            'text': cls.NOTE_TEXT,
            'slug': 'test-note'
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверяет, что анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Проверяет, что авторизованный пользователь может создать заметку."""
        response = self.auth_client.post(self.url, data=self.note_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.user)

    def test_cannot_create_note_with_duplicate_slug(self):
        """Проверяет, что невозможно создать заметку с дублирующимся slug."""
        Note.objects.create(title='First Note', text='Some text',
                            slug='unique-slug', author=self.user)
        response = self.auth_client.post(reverse('notes:add'), {
            'title': 'Second Note',
            'text': 'Different text',
            'slug': 'unique-slug',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'такой slug уже существует')

    def test_slug_is_auto_generated_if_not_provided(self):
        """Проверяет, что slug автоматически генерируется, если не указан."""
        response = self.auth_client.post(self.url, {
            'title': 'Auto Slug Note',
            'text': 'Text without a slug',
            'slug': '',
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note = Note.objects.get(title='Auto Slug Note')
        self.assertEqual(note.slug, 'auto-slug-note')


class TestNoteEditDelete(TestCase):
    """Тесты для проверки редактирования и удаления заметок."""
    NOTE_TEXT = 'Текст заметки'
    UPDATED_NOTE_TEXT = 'Обновленный текст заметки'

    @classmethod
    def setUpTestData(cls):
        """
        Устанавливает начальные данные для тестов:
        создает автора заметки, другого пользователя и инициализирует клиентов.
        """
        cls.author = User.objects.create(username='AuthorUser')
        cls.reader = User.objects.create(username='ReaderUser')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(title='Editable Note',
                                       text=cls.NOTE_TEXT,
                                       slug='editable-note',
                                       author=cls.author)
        cls.edit_url = reverse('notes:edit', args=[cls.note.slug])
        cls.delete_url = reverse('notes:delete', args=[cls.note.slug])
        cls.form_data = {'title': 'Updated Note',
                         'text': cls.UPDATED_NOTE_TEXT,
                         'slug': 'editable-note'}

    def test_author_can_delete_own_note(self):
        """Проверяет, что автор может удалить свою заметку."""
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cannot_delete_others_note(self):
        """
        Проверяет, что пользователь
        не может удалить заметку другого автора.
        """
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_own_note(self):
        """Проверяет, что автор может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.UPDATED_NOTE_TEXT)

    def test_user_cannot_edit_others_note(self):
        """
        Проверяет, что пользователь
        не может редактировать заметку другого автора.
        """
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
