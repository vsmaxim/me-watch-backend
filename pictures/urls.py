from django.urls import path

from pictures import views

app_name = 'pictures'

urlpatterns = [
    path(
        'series/<str:name>/<int:season>/<int:episode>/',
        views.SeriesListView.as_view(),
        name="series_list",
    ),
    path(
        'films/<str:name>/',
        views.FilmListView.as_view(),
        name="film_list",
    ),
    path(
        'search/<str:picture_name>/',
        views.PictureSearchView.as_view(),
        name="picture_search",
    ),
]