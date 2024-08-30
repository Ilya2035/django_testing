from datetime import datetime

import pytest
from django.test.client import Client

from news.models import News, Comment


MAX_NEWS_ITEMS = 10  # Предельное количество новостей для тестирования


@pytest.fixture
def news_author(django_user_model):
    """
    Создает и возвращает тестового пользователя с именем 'news_author',
    который выступает в роли автора новостей и комментариев.
    """
    return django_user_model.objects.create(username='news_author')


@pytest.fixture
def regular_user(django_user_model):
    """
    Создает и возвращает тестового пользователя с именем 'regular_user',
    который будет использоваться для тестирования в качестве читателя.
    """
    return django_user_model.objects.create(username='regular_user')


@pytest.fixture
def author_logged_in_client(news_author):
    """
    Создает и возвращает клиента с авторизацией
    под пользователем 'news_author'.
    Используется для тестирования действий, доступных автору.
    """
    client = Client()
    client.force_login(news_author)
    return client


@pytest.fixture
def reader_logged_in_client(regular_user):
    """
    Создает и возвращает клиента с авторизацией
    под пользователем 'regular_user'.
    Используется для тестирования действий, доступных обычным читателям.
    """
    client = Client()
    client.force_login(regular_user)
    return client


@pytest.fixture
def single_news_item():
    """
    Создает и возвращает один объект новости
    с фиксированным заголовком
    и текстом для использования в тестах.
    """
    return News.objects.create(
        title='Sample News Title',
        text='Sample news content',
        date=datetime.today()
    )


@pytest.fixture
def multiple_news_items():
    """
    Создает 10 объектов новостей для тестирования функциональности,
    связанной с отображением и сортировкой новостей.
    """
    for i in range(MAX_NEWS_ITEMS):
        News.objects.create(
            title=f'Sample News {i}',
            text=f'Sample news content {i}',
            date=datetime.today()
        )


@pytest.fixture
def single_comment(news_author, single_news_item):
    """
    Создает и возвращает комментарий к созданной новости,
    написанный пользователем 'news_author'.
    """
    return Comment.objects.create(
        news=single_news_item,
        author=news_author,
        text='Sample comment text'
    )


@pytest.fixture
def multiple_comments(news_author, single_news_item):
    """
    Создает 10 комментариев для одной новости,
    написанных пользователем 'news_author',
    для проверки отображения и сортировки.
    """
    for i in range(MAX_NEWS_ITEMS):
        Comment.objects.create(
            news=single_news_item,
            author=news_author,
            text=f'Sample comment {i}'
        )


@pytest.fixture
def news_item_id(single_news_item):
    """
    Возвращает первичный ключ созданной новости.
    Используется для упрощения доступа к этой новости в тестах.
    """
    return (single_news_item.pk,)


@pytest.fixture
def comment_id(single_comment):
    """
    Возвращает первичный ключ созданного комментария.
    Используется для упрощения доступа к этому комментарию в тестах.
    """
    return (single_comment.pk,)


@pytest.fixture
def comment_data():
    """
    Возвращает данные формы комментария, которые могут быть
    использованы в тестах для проверки создания и валидации комментариев.
    """
    return {'text': 'This is a sample comment'}
