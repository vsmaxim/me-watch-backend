from django.urls import reverse_lazy
from rest_framework import status

from core.tests import BaseAuthorizedTestCase
from pictures.models import Picture, Link

FILM_NAME = "Test film"
SERIES_NAME = "Test series"


class BasePictureTestSuite(object):
    """Provides base tests for Pictures list views"""
    success_url: str
    wrong_url: str
    right_name: str

    def test_success_get_with_right_names(self):
        self.client.force_login(self.user)
        response = self.client.get(self.success_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertNotEqual(len(results), 0)
        for result in results:
            self.assertEqual(result["picture"], self.right_name)

    def test_fail_get_with_wrong_name(self):
        self.client.force_login(self.user)
        response = self.client.get(self.wrong_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)


class BasePictureTestCase(BaseAuthorizedTestCase):
    def setUp(self):
        super().setUp()
        self.film = Picture.objects.create(name=FILM_NAME, type=Picture.FILM)
        self.series = Picture.objects.create(name=SERIES_NAME, type=Picture.SERIES)
        for i in range(10):
            Link.objects.create(
                source="http://mock.url",
                season=1,
                episode=1,
                picture=self.series
            )
            Link.objects.create(
                source="http://mock.url",
                picture=self.film
            )


class ListSeriesTestCase(BasePictureTestCase, BasePictureTestSuite):
    success_url = reverse_lazy("pictures:series_list", kwargs={"name": SERIES_NAME, "episode": 1, "season": 1})
    wrong_url = reverse_lazy("pictures:series_list", kwargs={"name": FILM_NAME, "episode": 1, "season": 1})
    right_name = SERIES_NAME


class ListFilmsTestCase(BasePictureTestCase, BasePictureTestSuite):
    success_url = reverse_lazy("pictures:film_list", kwargs={"name": FILM_NAME})
    wrong_url = reverse_lazy("pictures:film_list", kwargs={"name": SERIES_NAME})
    right_name = FILM_NAME
