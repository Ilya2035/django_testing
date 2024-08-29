import pytest
from django.urls import reverse
from news.models import News, Comment
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_homepage_accessible_to_anonymous(client):
    """Главная страница доступна анонимному пользователю."""
    response = client.get('/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_news_detail_accessible_to_anonymous(client):
    """Страница отдельной новости доступна анонимному пользователю."""
    news = News.objects.create(
        title='Test News',
        text='This is a test news.'
    )
    response = client.get(f'/news/{news.pk}/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_delete_comment_accessible_to_author(client, django_user_model):
    """
    Страницы удаления и редактирования
    комментария доступны автору комментария.
    """
    user = django_user_model.objects.create_user(
        username='author',
        password='password'
    )
    client.force_login(user)
    news = News.objects.create(
        title='Test News',
        text='Test news text.'
    )
    comment = Comment.objects.create(
        news=news,
        author=user,
        text='Test comment'
    )

    edit_url = reverse('news:edit', args=[comment.pk])
    delete_url = reverse('news:delete', args=[comment.pk])

    response_edit = client.get(edit_url)
    response_delete = client.get(delete_url)

    assert response_edit.status_code == 200
    assert response_delete.status_code == 200


@pytest.mark.django_db
@pytest.mark.django_db
def test_edit_delete_comment_redirects_anonymous(client, django_user_model):
    """
    Анонимный пользователь перенаправляется на страницу авторизации
    при попытке редактировать или удалить комментарий.
    """
    author = django_user_model.objects.create_user(
        username='author',
        password='password'
    )

    news = News.objects.create(
        title='Test News',
        text='Test news text.'
    )
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Test comment'
    )

    edit_url = reverse('news:edit', args=[comment.pk])
    delete_url = reverse('news:delete', args=[comment.pk])

    response_edit = client.get(edit_url)
    response_delete = client.get(delete_url)

    login_url = reverse('users:login')
    assertRedirects(response_edit,
                    f'{login_url}?next={edit_url}')
    assertRedirects(response_delete,
                    f'{login_url}?next={delete_url}')


@pytest.mark.django_db
def test_edit_delete_comment_404_for_non_author(client, django_user_model):
    """
    Авторизованный пользователь не может зайти
    на страницы редактирования или удаления чужих комментариев.
    """
    author = django_user_model.objects.create_user(
        username='author',
        password='password'
    )
    another_user = django_user_model.objects.create_user(
        username='reader',
        password='password'
    )
    client.force_login(another_user)
    news = News.objects.create(
        title='Test News',
        text='Test news text.'
    )
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Test comment'
    )

    edit_url = reverse('news:edit', args=[comment.pk])
    delete_url = reverse('news:delete', args=[comment.pk])

    response_edit = client.get(edit_url)
    response_delete = client.get(delete_url)

    assert response_edit.status_code == 404
    assert response_delete.status_code == 404


@pytest.mark.django_db
def test_auth_pages_accessible_to_anonymous(client):
    """
    Страницы регистрации, входа в учетную запись
    и выхода из неё доступны анонимным пользователям.
    """
    login_url = reverse('users:login')
    logout_url = reverse('users:logout')
    signup_url = reverse('users:signup')

    response_login = client.get(login_url)
    response_logout = client.get(logout_url)
    response_signup = client.get(signup_url)

    assert response_login.status_code == 200
    assert response_logout.status_code == 200
    assert response_signup.status_code == 200
