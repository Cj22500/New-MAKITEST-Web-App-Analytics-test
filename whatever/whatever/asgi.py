"""
ASGI config for whatever project.

Serves ordinary HTTP through Django and /ws/ through Channels, so the same
Daphne process delivers the page and the frame stream.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whatever.settings")

# Build the Django application before importing anything that touches models or
# settings — importing consumers first raises AppRegistryNotReady.
django_asgi_app = get_asgi_application()

import camera.routing  # noqa: E402
from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(camera.routing.websocket_urlpatterns))
        ),
    }
)
