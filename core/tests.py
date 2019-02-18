from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

TEST_USERNAME = 'mock-me-please'
TEST_PASSWORD = 'PaSsW0rD123'


class BaseAuthorizedTestCase(APITestCase):
    """Base test class to provide authorization to client

    Should only be used when authorization doesn't matters
    """
    def setUp(self):
        super().setUp()
        self.client = APIClient(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    @classmethod
    def setUpClass(cls):
        super(BaseAuthorizedTestCase, cls).setUpClass()
        cls.user, _ = User.objects.get_or_create(username=TEST_USERNAME)
        cls.token, _ = Token.objects.get_or_create(user=cls.user)

