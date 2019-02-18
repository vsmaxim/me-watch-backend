from typing import Optional
from urllib.parse import urlencode, urljoin
from uuid import uuid4

import requests
from django.contrib.auth.models import User
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from me_watch.settings import OAUTH_SETTINGS

from core.models import SocialInformation


def vk_api_call(token: str, method: str, params: Optional[dict] = None) -> dict:
    """Call VkApi method with defined token.

    Arguments:
    token  -- vk token got from authorizing user via oauth
    method -- method used to call from vk
    params -- parameters passed to method
    """
    API_VERSION = "5.92"
    BASE_API_URL = "https://api.vk.com/method/"
    
    if not params:
        params = {}
    params.update({
        "access_token": token,
        "v": API_VERSION,
    })

    response = requests.get(urljoin(BASE_API_URL, method), params=params)
    return dict(response.json())


class BaseSocialIntegration:
    config_option: str
    social_type: str
    client_id: str
    client_secret: str
    auth_url: str
    client_token_url: str

    def __init__(self):
        """Loads attributes for defined config option from django"""
        configs = OAUTH_SETTINGS.get(self.config_option)
        for config, value in configs.items():
            setattr(self, config, value)
        self.social_type = self.config_option

    def get_redirect_uri(self, request) -> str:
        """Returns redirect uri for OAuth2 protocol"""
        return request.build_absolute_uri(f"/{self.social_type}/callback")

    def get_redirect_params(self, request):
        """Returns param used along with redirect in OAuth2 protocol"""
        return urlencode({
            "client_id": self.client_id,
            "redirect_uri": self.get_redirect_uri(request),
            "response_type": "code",
        })
    
    def get_auth_params(self, request, code):
        """Returns authorization params used by OAuth2 protocol"""
        return urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.get_redirect_uri(request),
            "code": code,
        })
    
    def get_personal_info(self, external_token: str, user_id: str) -> dict:
        """Returns personal information in appropriate format:
        {
            "first_name": "something",
            "last_name": "something_else",
        }

        Arguments:
            external_token -- token, gained from oauth2 authentication
            user_id        -- user id in authorizing system
        """
        raise NotImplementedError("Should be implemented in subclass")


class BaseOAuth2InitView(APIView):
    integration: BaseSocialIntegration

    def get(self, request):
        params = self.integration.get_redirect_params(request)
        return redirect(f"{self.integration.auth_url}?{params}")


class BaseOAuth2CallbackView(APIView):
    integration: BaseSocialIntegration
    
    def generate_token(self, external_token: str, user_id: str) -> Response:
        """Generates token based on external information 

        Arguments:
            external_token -- token, gained from oauth2 authentication
            user_id        -- user id in authorizing system
        """
        social_info = SocialInformation.objects.filter(
            social_type=self.integration.social_type,
            social_user_id=user_id
        )
        if social_info.exists():
            user = social_info.last().user
        else:
            user = User.objects.create(
                username=uuid4(),
                **self.integration.get_personal_info(external_token, user_id)
            )
            SocialInformation.objects.create(
                social_type=self.integration.social_type,
                social_user_id=user_id,
                user=user
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.pk,
        })

    def authorize(self, request) -> Response:
        """Retrieves access token and generates token based
        authorization

        Arguments:
            request -- djangorestframework request
        """
        auth_response = requests.get(
            self.integration.client_token_url,
            params=self.integration.get_auth_params(request, request.query_params["code"]),
        )
        auth_data = auth_response.json()
        if "access_token" in auth_data:
            return self.generate_token(
                auth_data["access_token"],
                auth_data["user_id"],
            )
        else:
            return Response(auth_data, auth_response.status_code)

    def get(self, request):
        """Base DRF get method"""
        if "code" in request.query_params:
            return self.authorize(request)
        else:
            return Response(request.query_params, status=status.HTTP_400_BAD_REQUEST)


class VkIntegration(BaseSocialIntegration):
    config_option = "vk"

    def get_personal_info(self, external_token: str, user_id: str) -> dict:
        """Returns personal information in appropriate format:
        {
            "first_name": "something",
            "last_name": "something_else",
        }

        Arguments:
            external_token -- token, gained from oauth2 authentication
            user_id        -- user id in authorizing system
        """
        user_info = vk_api_call(external_token, "users.get")["response"][0]
        return {"first_name": user_info["first_name"], "last_name": user_info["last_name"]}


class ShikimoriIntegration(BaseSocialIntegration):
    """TODO: Setup over HTTPS due to shikimori api limitations"""
    pass
