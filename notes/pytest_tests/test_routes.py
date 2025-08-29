import pytest
from http import HTTPStatus

from django.urls import reverse


def test_home_availability_for_annonymous_user(client):
    url = reverse('notes:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('notes:home', 'users:login', 'users:signup')
)
def test_pages_availability_for_annonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
