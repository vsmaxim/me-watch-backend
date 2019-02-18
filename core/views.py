from core.utils import (BaseOAuth2CallbackView, BaseOAuth2InitView,
                        VkIntegration)


class VKInitOauth(BaseOAuth2InitView):
    """Initial OAuth2 view, used for retreive code"""
    integration = VkIntegration()


class VKCallbackOAuth(BaseOAuth2CallbackView):
    """Callback OAuth2 view, used for retreive access token"""
    integration = VkIntegration()

