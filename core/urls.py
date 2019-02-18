from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from core import views

app_name = 'core'

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('auth/', obtain_auth_token, name='obtain_auth_token'),
    path('vk/init',  views.VKInitOauth.as_view(), name="oauth_vk_init"),
    path('vk/callback', views.VKCallbackOAuth.as_view(), name="oauth_vk_callback"),
]
