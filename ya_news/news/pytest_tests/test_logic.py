from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client):
    """
    Анонимный пользователь
    не может отправить комментарий.
    """
    news = News.objects.create(
        title='Test News',
        text='This is a test news.'
    )
    url = reverse(
        'news:detail',
        args=[news.pk]
    )
    response = client.post(
        url,
        data={'text': 'Anonymous comment'}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(reverse('users:login'))
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorized_user_can_create_comment(client, django_user_model):
    """Авторизованный пользователь может отправить комментарий."""
    user = django_user_model.objects.create_user(
        username='user',
        password='password'
    )
    client.force_login(user)
    news = News.objects.create(
        title='Test News',
        text='This is a test news.'
    )
    url = reverse(
        'news:detail',
        args=[news.pk]
    )
    response = client.post(
        url,
        data={'text': 'User comment'}
    )
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == 'User comment'
    assert comment.author == user


@pytest.mark.django_db
def test_comment_with_bad_words_is_not_published(client, django_user_model):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    user = django_user_model.objects.create_user(
        username='user',
        password='password'
    )
    client.force_login(user)
    news = News.objects.create(
        title='Test News',
        text='This is a test news.'
    )
    url = reverse(
        'news:detail',
        args=[news.pk]
    )
    bad_word = BAD_WORDS[0]
    response = client.post(
        url,
        data={'text': f'Comment with {bad_word}'}
    )
    assertFormError(
        response,
        'form',
        'text', WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_delete_own_comment(client, django_user_model):
    """
    Авторизованный пользователь может
    редактировать или удалять свои комментарии.
    """
    user = django_user_model.objects.create_user(
        username='author',
        password='password'
    )
    client.force_login(user)
    news = News.objects.create(
        title='Test News',
        text='This is a test news.'
    )
    comment = Comment.objects.create(
        news=news,
        author=user,
        text='Original comment'
    )

    # Редактирование комментария
    edit_url = reverse(
        'news:edit',
        args=[comment.pk]
    )
    response = client.post(
        edit_url,
        data={'text': 'Edited comment'}
    )
    assertRedirects(
        response,
        f'{reverse("news:detail", args=[news.pk])}#comments')
    comment.refresh_from_db()
    assert comment.text == 'Edited comment'

    # Удаление комментария
    delete_url = reverse(
        'news:delete',
        args=[comment.pk]
    )
    response = client.post(delete_url)
    assertRedirects(
        response,
        f'{reverse("news:detail", args=[news.pk])}#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_edit_delete_others_comment(client, django_user_model):
    """
    Авторизованный пользователь не может
    редактировать или удалять чужие комментарии.
    """
    author = django_user_model.objects.create_user(
        username='author',
        password='password'
    )
    other_user = django_user_model.objects.create_user(
        username='other',
        password='password'
    )
    client.force_login(other_user)
    news = News.objects.create(
        title='Test News',
        text='This is a test news.'
    )
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Original comment'
    )

    # Попытка редактирования чужого комментария
    edit_url = reverse('news:edit', args=[comment.pk])
    response = client.post(edit_url, data={'text': 'Attempted edit'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Original comment'

    # Попытка удаления чужого комментария
    delete_url = reverse('news:delete', args=[comment.pk])
    response = client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
