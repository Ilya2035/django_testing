import pytest
from django.urls import reverse
from news.models import News, Comment


@pytest.mark.django_db
def test_home_page_accessible_by_anonymous_user(client):
    response = client.get(reverse('news:home'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_detail_page_accessible_by_anonymous_user(client):
    news = News.objects.create(title="Test News", text="Test text")
    response = client.get(reverse('news:detail', args=[news.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_delete_comment_accessible_by_author(client, django_user_model):
    author = django_user_model.objects.create_user(
        username='author', password='password'
    )
    client.login(username='author', password='password')
    news = News.objects.create(title="Test News", text="Test text")
    comment = Comment.objects.create(news=news,
                                     author=author,
                                     text="Comment text")

    response = client.get(reverse('news:edit',
                                  args=[comment.pk]))
    assert response.status_code == 200

    response = client.get(reverse('news:delete',
                                  args=[comment.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_redirected_to_login_on_edit_delete(client,
                                                           django_user_model):
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    news = News.objects.create(title="Test News",
                               text="Test text")
    comment = Comment.objects.create(news=news,
                                     author=user,
                                     text="Comment text")

    response = client.get(reverse('news:edit',
                                  args=[comment.pk]))
    login_url = reverse('users:login')
    assert response.status_code == 302
    assert response.url.startswith(login_url)

    response = client.get(reverse('news:delete',
                                  args=[comment.pk]))
    assert response.status_code == 302
    assert response.url.startswith(login_url)


@pytest.mark.django_db
def test_other_user_cannot_access_edit_delete(client,
                                              django_user_model):
    author = django_user_model.objects.create_user(
        username='author', password='password'
    )
    django_user_model.objects.create_user(
        username='another_user', password='password'
    )
    client.login(username='another_user',
                 password='password')
    news = News.objects.create(title="Test News",
                               text="Test text")
    comment = Comment.objects.create(news=news,
                                     author=author,
                                     text="Comment text")

    response = client.get(reverse('news:edit',
                                  args=[comment.pk]))
    assert response.status_code == 404

    response = client.get(reverse('news:delete',
                                  args=[comment.pk]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_auth_pages_accessible_by_anonymous_users(client):
    response = client.get(reverse('users:signup'))
    assert response.status_code == 200

    response = client.get(reverse('users:login'))
    assert response.status_code == 200

    response = client.get(reverse('users:logout'))
    assert response.status_code == 200
