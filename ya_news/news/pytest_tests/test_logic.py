from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_cant_comment(client, single_news_item, comment_data):
    """
    Проверяет, что анонимный пользователь не может отправить комментарий
    к новости.
    """
    url = reverse('news:detail', args=[single_news_item.pk])
    response = client.post(url, comment_data)
    assert Comment.objects.count() == 0
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_reader_can_submit_comment(
        reader_logged_in_client,
        single_news_item,
        comment_data
):
    """
    Проверяет, что авторизованный пользователь
    может отправить комментарий к новости.
    """
    url = reverse('news:detail', args=[single_news_item.pk])
    response = reader_logged_in_client.post(url, comment_data)
    assert Comment.objects.count() == 1
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_bad_words(
        reader_logged_in_client,
        single_news_item,
        bad_word
):
    """
    Проверяет, что комментарий, содержащий запрещенные слова,
    не добавляется и возвращает сообщение об ошибке.
    """
    url = reverse('news:detail', args=[single_news_item.pk])
    response = reader_logged_in_client.post(url, {'text': bad_word})
    assert Comment.objects.count() == 0
    assertFormError(response, 'form', 'text', WARNING)


@pytest.mark.django_db
def test_author_delete_comment(author_logged_in_client, single_comment):
    """
    Проверяет, что автор комментария
    может успешно удалить свой комментарий.
    """
    url = reverse('news:delete', args=[single_comment.pk])
    delete = author_logged_in_client.post(url)
    assert delete.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_edit_comment(
        author_logged_in_client,
        single_comment,
        comment_data
):
    """
    Проверяет, что автор комментария
    может редактировать текст своего комментария.
    """
    url = reverse('news:edit', args=[single_comment.pk])
    response = author_logged_in_client.post(url, comment_data)
    assert response.status_code == HTTPStatus.FOUND
    single_comment.refresh_from_db()
    assert single_comment.text == comment_data['text']


@pytest.mark.django_db
def test_reader_cant_delete_comment(reader_logged_in_client, single_comment):
    """
    Проверяет, что обычный пользователь
    не может удалить чужой комментарий.
    """
    url = reverse('news:delete', args=[single_comment.pk])
    response = reader_logged_in_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_reader_cant_edit_comment(
        reader_logged_in_client,
        single_comment,
        comment_data
):
    """
    Проверяет, что обычный пользователь
    не может редактировать чужой комментарий.
    """
    original_text = single_comment.text
    url = reverse('news:edit', args=[single_comment.pk])
    response = reader_logged_in_client.post(url, comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    single_comment.refresh_from_db()
    assert single_comment.text == original_text
