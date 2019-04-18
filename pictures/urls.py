from django.urls import path

from pictures import views

app_name = 'pictures'

urlpatterns = [
    path(
        'series/<str:name>/<int:season>/<int:episode>/',
        views.SeriesListView.as_view(),
        name="series-list",
    ),
    path(
        'films/<str:name>/',
        views.FilmListView.as_view(),
        name="film-list",
    ),
    path(
        'search/<str:picture_name>/',
        views.PictureSearchView.as_view(),
        name="picture-search",
    ),
    path(
        'pictures/<str:name>/<int:season>/<int:episode>/finish/',
        views.FinishEpisodeView.as_view(),
        name='episode-finish'
    ),
    path(
        'pictures/<str:name>/',
        views.PictureListView.as_view(),
        name='watched-picture-list',
    ),
]