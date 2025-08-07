from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # path("ws/source/", consumers.receive.as_asgi()),
     path("ws/source/<int:id>", consumers.SourceConsumer.as_asgi()),
    path("ws/view/<int:id>", consumers.ViewerConsumer.as_asgi()),
]
