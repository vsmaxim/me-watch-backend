from django.urls import reverse_lazy, reverse
from rest_framework import status

from core.tests import BaseAuthorizedTestCase
from pictures.models import Picture, Link, Status

FILM_NAME = "Test film"
SERIES_NAME = "Test series"


class BasePictureTestSuite(object):
    """Provides base tests for Pictures list views"""
    assert_name: bool = True
    success_url: str
    wrong_url: str
    right_name: str

    def test_success_get_with_right_names(self):
        self.client.force_login(self.user)
        response = self.client.get(self.success_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertNotEqual(len(results), 0)
        if hasattr(self, 'right_name'):
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

        for _ in range(10):
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
    success_url = reverse_lazy("pictures:series-list", kwargs={"name": SERIES_NAME, "episode": 1, "season": 1})
    wrong_url = reverse_lazy("pictures:series-list", kwargs={"name": FILM_NAME, "episode": 1, "season": 1})
    right_name = SERIES_NAME


class ListFilmsTestCase(BasePictureTestCase, BasePictureTestSuite):
    success_url = reverse_lazy("pictures:film-list", kwargs={"name": FILM_NAME})
    wrong_url = reverse_lazy("pictures:film-list", kwargs={"name": SERIES_NAME})
    right_name = FILM_NAME


class WatchedPicturesListTestCase(BasePictureTestCase, BasePictureTestSuite):
    success_url = reverse_lazy("pictures:watched-picture-list", kwargs={"name": FILM_NAME})
    wrong_url = reverse_lazy("pictures:film-list", kwargs={"name": SERIES_NAME})

    def setUp(self):
        super().setUp()
        for _ in range(10):
            Status.objects.create(picture=self.film, user=self.user, finished=True)


class StatusLifecycleTestCase(BaseAuthorizedTestCase):
    def setUp(self):
        super().setUp()
        self.picture = Picture.objects.create(
            name='very-famous-series',
            type=Picture.SERIES,

        )
        self.link = Link.objects.create(
            picture=self.picture,
            episode=2,
            season=3,
            source='http://very-famous-url.com/',
        )
        self.picture_kwargs = {
            'name': self.picture.name,
            'episode': self.link.episode,
            'season': self.link.season,
        }

    def test_start_watch(self):
        url = reverse('pictures:series-list', kwargs=self.picture_kwargs)

        response = self.client.get(url)

        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(self.picture.status_set.exists())
        picture_status = self.picture.status_set.first()
        self.assertFalse(picture_status.finished)

    def test_finish_watch(self):
        picture_status = Status.objects.create(
            episode=self.picture_kwargs['episode'],
            season=self.picture_kwargs['season'],
            picture=self.picture,
            user=self.user,
        )

        url = reverse('pictures:episode-finish', kwargs=self.picture_kwargs)

        response = self.client.patch(url)

        picture_status.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(picture_status.finished)


