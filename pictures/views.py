from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect, reverse

from pictures.models import Link, Picture
from pictures.serializers import LinkSerializer
from pictures.utils import YandexParser


class BasePictureListView(generics.ListAPIView):
    """View for returning list of series filtered by name"""
    serializer_class = LinkSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Link.objects.filter(picture__name=self.kwargs["name"])


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






