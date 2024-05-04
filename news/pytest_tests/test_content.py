from django.urls import reverse

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

HOME_URL = reverse('news:home')


def test_news_count(client, all_news):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, all_news):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']    
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, news_id_for_args):
    """
    Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
