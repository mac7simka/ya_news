from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_note(client, form_data, news_id_for_args):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client,
                                 form_data, news_id_for_args):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    author_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == form_data['news']
    assert new_comment.text == form_data['text']


def test_user_cant_use_bad_words(author_client,
                                 form_data, news_id_for_args):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=news_id_for_args)
    form_data['text'] = {f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, news_id_for_args, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:delete', args=news_id_for_args)
    news_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.delete(url)
    assertRedirects(response, news_url + '#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client, news_id_for_args, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    url = reverse('news:delete', args=news_id_for_args)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client, news_id_for_args, form_data, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    url = reverse('news:edit', args=news_id_for_args)
    news_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, news_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client, news_id_for_args, form_data, comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    url = reverse('news:edit', args=news_id_for_args)
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
