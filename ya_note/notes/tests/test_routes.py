from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='author', password='password'
        )
        self.client.login(username='author', password='password')

    def test_home_page_accessible_by_anonymous_user(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_accessible_pages(self):
        response = self.client.get('/notes/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/add/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/done/')
        self.assertEqual(response.status_code, 200)

    def test_note_pages_accessible_only_by_author(self):
        note = Note.objects.create(
            title='Test Note', text='Test text', author=self.user
        )
        response = self.client.get(f'/note/{note.slug}/')
        self.assertEqual(response.status_code, 200)

        User.objects.create_user(username='another_user', password='password')
        self.client.login(username='another_user', password='password')
        response = self.client.get(f'/note/{note.slug}/')
        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get('/add/')
        login_url = reverse_lazy('users:login') + '?next=/add/'
        self.assertRedirects(response, login_url)

    def test_auth_pages_accessible_by_all_users(self):
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, 200)
