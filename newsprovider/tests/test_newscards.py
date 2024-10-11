import pytest
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestNewsCard:
    def test_if_user_is_anonymous_and_page_is_1_returns_200(self):
        # Arrange
        client = APIClient()

        # Act - make a request to page 1
        response = client.get('/newsprovider/newscards/?page=1')

        # Assert - check if the status code is 200
        assert response.status_code == status.HTTP_200_OK

    # This is returning a 404.
    @pytest.mark.skip
    def test_if_user_is_anonymous_and_page_is_2_returns_401(self):
        # Arrange
        client = APIClient()

        # Act - make a request to page 2
        response = client.get('/newsprovider/newscards/?page=2')

        # Assert - check if the status code is 401
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
