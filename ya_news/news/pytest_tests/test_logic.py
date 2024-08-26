import pytest
from django.urls import reverse
from news.models import News, Comment


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(client):
    news = News.objects.create(title="News", text="Text")
    response = client.post(
        reverse('news:detail', args=[news.pk]), {'text': 'Comment text'}
    )
    login_url = reverse('users:login')
    assert response.status_code == 302
    assert response.url.startswith(login_url)


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(client, django_user_model):
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    client.login(username='user', password='password')
    news = News.objects.create(title="News", text="Text")
    response = client.post(
        reverse('news:detail', args=[news.pk]), {'text': 'Comment text'}
    )
    assert response.status_code == 302
    assert Comment.objects.filter(news=news, author=user).exists()


@pytest.mark.django_db
def test_user_can_edit_delete_own_comment(client, django_user_model):
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    client.login(username='user', password='password')
    news = News.objects.create(title="News", text="Text")
    comment = Comment.objects.create(
        news=news, author=user, text="Original text"
    )

    response = client.post(
        reverse('news:edit', args=[comment.pk]), {'text': 'Updated text'}
    )
    assert response.status_code == 302  # Проверяем успешное редактирование
    comment.refresh_from_db()
    assert comment.text == 'Updated text'

    response = client.post(reverse('news:delete', args=[comment.pk]))
    assert response.status_code == 302  # Проверяем успешное удаление
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_user_cannot_edit_delete_others_comment(client, django_user_model):
    author = django_user_model.objects.create_user(
        username='author', password='password'
    )
    django_user_model.objects.create_user(
        username='another_user', password='password'
    )
    client.login(username='another_user', password='password')
    news = News.objects.create(title="News", text="Text")
    comment = Comment.objects.create(
        news=news, author=author, text="Comment text"
    )

    response = client.post(
        reverse('news:edit', args=[comment.pk]), {'text': 'Updated text'}
    )
    assert response.status_code == 404

    response = client.post(reverse('news:delete', args=[comment.pk]))
    assert response.status_code == 404
