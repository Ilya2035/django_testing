import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count_on_home_page(
        reader_logged_in_client,
        multiple_news_items,
        home_url
):
    """
    Проверяет, что количество новостей на главной странице не превышает
    максимальное количество, заданное в настройках приложения.
    """
    response = reader_logged_in_client.get(home_url)
    assert 'news_list' in response.context
    obj_list = response.context['news_list']
    assert obj_list.count() <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order_on_home_page(client, multiple_news_items, home_url):
    """
    Проверяет, что новости на главной странице отсортированы
    по дате публикации от самой свежей к самой старой.
    """
    response = client.get(home_url)
    assert 'news_list' in response.context
    news_list = response.context['news_list']
    dates = [news.date for news in news_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_order_on_news_detail_page(
        client,
        multiple_comments,
        news_item_id,
        news_detail_url
):
    """
    Проверяет, что комментарии на странице отдельной новости отсортированы
    в хронологическом порядке.
    """
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news_obj = response.context['news']
    comments = news_obj.comment_set.all()
    created_times = [comment.created for comment in comments]
    assert created_times == sorted(created_times)


@pytest.mark.django_db
def test_comment_form_for_anonymous_user(
        client,
        single_comment,
        news_detail_url_with_comment
):
    """
    Проверяет, что форма для отправки комментария недоступна
    анонимному пользователю на странице отдельной новости.
    """
    response = client.get(news_detail_url_with_comment)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_comment_form_for_reader(
        reader_logged_in_client,
        single_comment,
        news_detail_url_with_comment
):
    """
    Проверяет, что авторизованному пользователю доступна форма
    для отправки комментария на странице отдельной новости.
    """
    response = reader_logged_in_client.get(news_detail_url_with_comment)
    assert 'form' in response.context
    form_obj = response.context['form']
    assert isinstance(form_obj, CommentForm)
