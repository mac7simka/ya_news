# conftest.py
from datetime import timedelta
import pytest

# Импортируем класс клиента.
from django.utils import timezone
from django.test.client import Client

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import Comment, News
from yanews import settings

NUMBER_OF_COMMENTS = 5


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок', text='Текст'
    )
    return news


@pytest.fixture
def all_news():
    now = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=now - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария.',
        author=author,
    )
    return comment


@pytest.fixture
def all_comments(not_author_client, news):
    now = timezone.now()
    all_comments = [
        Comment(
            news=news,
            text=f'Текст комментария {index}.',
            author=not_author_client,
            created=now - timedelta(days=index)
        )
        for index in range(NUMBER_OF_COMMENTS)
    ]
    News.objects.bulk_create(all_comments)


#@pytest.fixture
#def comment_id_for_args(comment):
#    return (comment.id,)
