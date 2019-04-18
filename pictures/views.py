from django.shortcuts import redirect, reverse
from rest_framework import generics, views
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from pictures.models import Link, Picture, Status
from pictures.serializers import LinkSerializer, StatusFinishSerializer, PictureListSerializer
from pictures.utils import YandexParser


class BasePictureListView(generics.ListAPIView):
    """View for returning list of series filtered by name"""

    serializer_class = LinkSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Link.objects.filter(picture__name=self.kwargs["name"])

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            picture = queryset.first().picture
            Status.objects.create(
                picture=picture,
                user=request.user,
                episode=kwargs.get('episode', 1),
                season=kwargs.get('season', 1),
            )
        return super().list(request, *args, **kwargs)


class FilmListView(BasePictureListView):

    def get_queryset(self):
        """Filters queryset by Film type"""
        return super().get_queryset().filter(picture__type=Picture.FILM)


class SeriesListView(BasePictureListView):

    def get_queryset(self):
        """Filters queryset by Series type"""
        queryset = super().get_queryset()
        return queryset.filter(
            picture__type=Picture.SERIES,
            season=self.kwargs["season"],
            episode=self.kwargs["episode"],
        )


class PictureSearchView(views.APIView):
    """Caching view that retrieves source list from desired source and saves in database
    after this, redirects to actual database view list
    """
    picture_parsers = (YandexParser(), )
    permission_classes = (IsAuthenticated, )

    def get(self, request, picture_name):
        """Base get view

        Attributes:
            request -- base drf request
            picture_name -- picture name in "word1_word2_etc" format (e.g. "doctor_house")
        """
        links = Link.objects.filter(picture__name=picture_name)
        if not links.exists():
            links = self.parse_links(picture_name=picture_name)
        else:
            links = links.all()
        return self.redirect(links[0].picture)

    def redirect(self, picture):
        """Redirects to appropriate view using picture instance

        Attributes:
            picture -- database instance of picture
        """
        base_kwargs = {"name": Picture.name}
        if picture.type == Picture.SERIES:
            base_kwargs.update({"season": 1, "episode": 1})
            return redirect(reverse("pictures:series_list", kwargs=base_kwargs))
        else:
            return redirect(reverse("pictures:film_list", kwargs=base_kwargs))

    def parse_links(self, picture_name):
        """Parses links with defined parsers in self.picture_parsers and saves it into database
        with appropriate picture attributes

        Attributes:
            picture_name -- internal picture_name given from request
        """
        sources = [source for parser in self.picture_parsers for source in parser.get_sources(picture_name)]
        picture, _ = Picture.objects.get_or_create(name=sources[0].name, type=sources[0].type)
        links = [Link(source=link.source_url, season=link.season, episode=link.episode, picture=picture)
                 for link in sources]
        return Link.objects.bulk_create(links)


class FinishEpisodeView(generics.UpdateAPIView):
    """View for finishing started instance of episode"""

    queryset = Status.objects
    serializer_class = StatusFinishSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        kwargs = {
            'user': self.request.user,
            'picture__name': self.kwargs['name'],
            'episode': self.kwargs['episode'],
            'season': self.kwargs['season'],
        }
        obj = self.get_queryset().filter(**kwargs).last()

        if obj is None:
            raise NotFound('Film is not started yet')

        return obj


class PictureListView(generics.ListAPIView):
    """View for list all Pictures for current user."""

    queryset = Picture.objects
    serializer_class = PictureListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user, name=self.kwargs['name'])
