import pytest

from django.urls import reverse

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count_on_home_page(reader_logged_in_client, multiple_news_items):
    """
    Проверяет, что количество новостей на главной странице не превышает
    максимальное количество, заданное в настройках приложения.
    """
    url = reverse('news:home')
    response = reader_logged_in_client.get(url)
    assert 'news_list' in response.context
    obj_list = response.context['news_list']
    assert len(obj_list) <= NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order_on_home_page(client, multiple_news_items):
    """
    Проверяет, что новости на главной странице отсортированы
    по дате публикации от самой свежей к самой старой.
    """
    url = reverse('news:home')
    response = client.get(url)
    assert 'news_list' in response.context
    news_list = response.context['news_list']
    dates = [news.date for news in news_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_order_on_news_detail_page(
        client,
        multiple_comments,
        news_item_id
):
    """
    Проверяет, что комментарии на странице отдельной новости отсортированы
    в хронологическом порядке.
    """
    url = reverse('news:detail', args=news_item_id)
    response = client.get(url)
    assert 'news' in response.context
    news_obj = response.context['news']
    comments = news_obj.comment_set.all()
    created_times = [comment.created for comment in comments]
    assert created_times == sorted(created_times)


@pytest.mark.django_db
def test_comment_form_for_anonymous_user(client, single_comment):
    """
    Проверяет, что форма для отправки комментария недоступна
    анонимному пользователю на странице отдельной новости.
    """
    url = reverse('news:detail', args=[single_comment.news.pk])
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_comment_form_for_reader(reader_logged_in_client, single_comment):
    """
    Проверяет, что авторизованному пользователю доступна форма
    для отправки комментария на странице отдельной новости.
    """
    url = reverse('news:detail', args=[single_comment.news.pk])
    response = reader_logged_in_client.get(url)
    assert 'form' in response.context
    form_obj = response.context['form']
    assert isinstance(form_obj, CommentForm)
