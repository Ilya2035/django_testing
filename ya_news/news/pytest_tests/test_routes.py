from http import HTTPStatus

import pytest
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
def test_page_availability_for_anonymous_user(
    client,
    url_generator,
    name,
    args
):
    """
    Проверяет, что страницы (главная, логин, логаут, регистрация) доступны
    для анонимного пользователя.
    """
    response = client.get(url_generator(name, args=args))
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
        (lazy_fixture('client'), HTTPStatus.FOUND),
    )
)
def test_comment_edit_delete_access(
    client_fixture,
    url_generator,
    name,
    args,
    expected_status
):
    """
    Проверяет доступность страниц редактирования
    и удаления комментария для разных пользователей:
    автор, обычный пользователь, анонимный пользователь.
    """
    response = client_fixture.get(url_generator(name, args=args))
    assert response.status_code == expected_status

    # Дополнительная проверка редиректа для анонимного пользователя
    if expected_status == HTTPStatus.FOUND:
        login_url = url_generator('users:login')
        assert response.url.startswith(login_url)


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('comment_id')),
        ('news:delete', lazy_fixture('comment_id')),
    )
)
def test_anonymous_user_redirect_to_login(client, url_generator, name, args):
    """
    Проверяет, что анонимный пользователь перенаправляется
    на страницу логина при попытке доступа к страницам
    редактирования и удаления комментария.
    """
    expected_url = (
        f"{url_generator('users:login')}?next={url_generator(name, args=args)}"
    )
    # так делать можно?
    response = client.get(url_generator(name, args=args))
    assertRedirects(response, expected_url)
