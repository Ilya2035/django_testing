from datetime import datetime

import pytest
from django.test.client import Client
from django.urls import reverse
from django.conf import settings

from news.models import News, Comment


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
    news_count = settings.NEWS_COUNT_ON_HOME_PAGE + 5
    for i in range(news_count):
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
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE):
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


@pytest.fixture
def home_url():
    """Возвращает URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news_item_id):
    """Возвращает URL страницы детали конкретной новости по `news_item_id`."""
    return reverse('news:detail', args=news_item_id)


@pytest.fixture
def news_detail_url_with_comment(single_comment):
    """
    Возвращает URL страницы детали новости,
    связанной с определённым комментарием.
    """
    return reverse('news:detail', args=[single_comment.news.pk])


@pytest.fixture
def single_news_detail_url(single_news_item):
    """
    Возвращает URL страницы детали
    конкретной новости по `single_news_item.pk`.
    """
    return reverse('news:detail', args=[single_news_item.pk])


@pytest.fixture
def delete_comment_url(single_comment):
    """Возвращает URL страницы удаления конкретного комментария."""
    return reverse('news:delete', args=[single_comment.pk])


@pytest.fixture
def edit_comment_url(single_comment):
    """Возвращает URL страницы редактирования конкретного комментария."""
    return reverse('news:edit', args=[single_comment.pk])


@pytest.fixture
def url_generator():
    """
    Фикстура для генерации URL на основе имени маршрута и аргументов.
    Использование: url = url_generator('news:edit', [comment_id])
    """
    def _generate_url(name, args=None):
        return reverse(name, args=args)
    return _generate_url
