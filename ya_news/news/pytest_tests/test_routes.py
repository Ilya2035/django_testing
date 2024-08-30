from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_lazyfixture import lazy_fixture
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', lazy_fixture('news_item_id')),
    ),
)
def test_page_availability_for_anonymous_user(client, name, args):
    """
    Проверяет, что страницы (главная, логин, логаут, регистрация) доступны
    для анонимного пользователя.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('comment_id')),
        ('news:delete', lazy_fixture('comment_id')),
    )
)
def test_comment_edit_delete_pages_for_author(
        author_logged_in_client,
        name,
        args
):
    """
    Проверяет, что автор комментария имеет доступ к страницам
    редактирования и удаления своего комментария.
    """
    url = reverse(name, args=args)
    response = author_logged_in_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('comment_id')),
        ('news:delete', lazy_fixture('comment_id')),
    )
)
def test_anonymous_user_redirect_to_login(client, name, args):
    """
    Проверяет, что анонимный пользователь перенаправляется
    на страницу логина при попытке доступа к страницам
    редактирования и удаления комментария.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('comment_id')),
        ('news:delete', lazy_fixture('comment_id')),
    )
)
def test_reader_cant_edit_delete_comment(reader_logged_in_client, name, args):
    """
    Проверяет, что обычный пользователь не может получить доступ
    к страницам редактирования и удаления чужого комментария.
    """
    url = reverse(name, args=args)
    response = reader_logged_in_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
