from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture
from pytest_django.asserts import assertRedirects
from django.urls import reverse


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
def test_page_availability_for_anonymous_user(
    client,
    name,
    args
):
    """
    Проверяет, что страницы (главная, логин, логаут, регистрация) доступны
    для анонимного пользователя.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('comment_id')),
        ('news:delete', lazy_fixture('comment_id')),
    )
)
@pytest.mark.parametrize(
    'client_fixture, expected_status',
    (
        (lazy_fixture('author_logged_in_client'), HTTPStatus.OK),
        (lazy_fixture('reader_logged_in_client'), HTTPStatus.NOT_FOUND),
    )
)
def test_comment_edit_delete_access(
    client_fixture,
    name,
    args,
    expected_status
):
    """
    Проверяет доступность страниц редактирования
    и удаления комментария для разных пользователей:
    автор и обычный пользователь.
    """
    url = reverse(name, args=args)
    response = client_fixture.get(url)
    assert response.status_code == expected_status

    if expected_status == HTTPStatus.FOUND:
        login_url = reverse('users:login')
        assert response.url.startswith(login_url)


@pytest.mark.django_db
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
    target_url = reverse(name, args=args)
    expected_url = f'{login_url}?next={target_url}'

    response = client.get(target_url)
    assertRedirects(response, expected_url)
