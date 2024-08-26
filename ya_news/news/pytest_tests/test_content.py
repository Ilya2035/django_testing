import pytest
from django.urls import reverse
from news.models import News, Comment


@pytest.mark.django_db
def test_news_count_on_home_page(client):
    for i in range(12):
        News.objects.create(title=f"News {i}", text="Text")

    response = client.get(reverse('news:home'))
    assert len(response.context['news_list']) <= 10


@pytest.mark.django_db
def test_news_sorted_by_date(client):
    news1 = News.objects.create(
        title="Older News", text="Text", date="2023-01-01"
    )
    news2 = News.objects.create(
        title="Newer News", text="Text", date="2023-02-01"
    )

    response = client.get(reverse('news:home'))
    assert list(response.context['news_list']) == [news2, news1]


@pytest.mark.django_db
def test_comments_sorted_by_date(client, django_user_model):
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    news = News.objects.create(title="News", text="Text")
    Comment.objects.create(
        news=news, author=user, text="Old Comment", created="2023-01-01"
    )
    Comment.objects.create(
        news=news, author=user, text="New Comment", created="2023-02-01"
    )

    response = client.get(reverse('news:detail', args=[news.pk]))
    comments = response.context['news'].comment_set.all()
    assert comments[0].text == "Old Comment"
    assert comments[1].text == "New Comment"


@pytest.mark.django_db
def test_comment_form_availability(client, django_user_model):
    django_user_model.objects.create_user(
        username='user', password='password'
    )
    news = News.objects.create(title="News", text="Text")

    response = client.get(reverse('news:detail', args=[news.pk]))
    assert 'form' not in response.context

    client.login(username='user', password='password')
    response = client.get(reverse('news:detail', args=[news.pk]))
    assert 'form' in response.context
