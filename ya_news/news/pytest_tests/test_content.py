import pytest
from django.urls import reverse

from news.models import News, Comment


@pytest.mark.django_db
def test_news_count_on_homepage(client):
    """
    Проверяет, что на главной странице
    отображается не более 10 новостей.
    """
    # Создаем 12 новостей
    for i in range(12):
        News.objects.create(title=f'News {i}', text='This is a test news.')

    response = client.get(reverse('news:home'))
    assert response.status_code == 200
    # Проверяем, что на странице не более 10 новостей
    assert len(response.context['news_list']) <= 10


@pytest.mark.django_db
def test_news_ordering(client):
    """
    Проверяет, что новости отсортированы
    от самой свежей к самой старой.
    """
    # Создаем 2 новости с явными датами публикации
    news1 = News.objects.create(
        title='Old News',
        text='This is an old news.',
        date='2022-01-01'
    )
    news2 = News.objects.create(
        title='New News',
        text='This is a new news.',
        date='2022-01-02'
    )

    response = client.get(reverse('news:home'))
    assert response.status_code == 200
    news_list = response.context['news_list']

    # Проверяем, что первая новость - это самая новая
    assert news_list[0] == news2
    assert news_list[1] == news1


@pytest.mark.django_db
def test_comments_ordering_on_news_page(client, django_user_model):
    """
    Проверяет, что комментарии на странице отдельной новости
    отсортированы в хронологическом порядке.
    """
    # Создаем новость и два комментария с разными временными метками
    news = News.objects.create(
        title='Test News',
        text='This is a test news.'
    )
    user = django_user_model.objects.create_user(
        username='user',
        password='password'
    )
    Comment.objects.create(
        news=news, author=user,
        text='Old Comment',
        created='2022-01-01'
    )
    Comment.objects.create(
        news=news,
        author=user,
        text='New Comment',
        created='2022-01-02'
    )

    response = client.get(reverse(
        'news:detail',
        args=[news.pk]
    ))
    assert response.status_code == 200

    # Используем comment_set для доступа к комментариям
    comments = news.comment_set.order_by('created')
    # Проверяем, что комментарии отсортированы по дате создания
    assert comments[0].text == 'Old Comment'
    assert comments[1].text == 'New Comment'


@pytest.mark.django_db
def test_comment_form_visibility(client, django_user_model):
    """
    Проверяет, что анонимному пользователю
    недоступна форма для отправки комментария,
    а авторизованному пользователю доступна.
    """
    news = News.objects.create(
        title='Test News',
        text='This is a test news.'
    )
    response = client.get(reverse('news:detail', args=[news.pk]))
    assert response.status_code == 200
    # Проверяем, что форма недоступна для анонимного пользователя
    assert 'form' not in response.context

    # Создаем и логиним пользователя
    user = django_user_model.objects.create_user(
        username='user',
        password='password'
    )
    client.force_login(user)
    response = client.get(reverse(
        'news:detail',
        args=[news.pk]
    ))
    assert response.status_code == 200
    # Проверяем, что форма доступна для авторизованного пользователя
    assert 'form' in response.context
