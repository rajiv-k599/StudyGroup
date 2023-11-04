from django.urls import re_path
from . import consumers

# websocket_urlpatterns = [
#     re_path('ws/<str:room_name>/<str:username>/', consumers.ChatConsumer.as_asgi()),
#     re_path('ws/<str:room_name>/<str:username>/vs/<str:userId>/', consumers.VideoConsumer.as_asgi()),
#     re_path(r'ws/video/status-request/$', consumers.VideoConsumer.as_asgi()),
# ]

websocket_urlpatterns = [
    re_path(r'ws/(?P<room_name>\w+)/(?P<username>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/(?P<room_name>\w+)/(?P<username>\w+)/vs/(?P<userId>\w+)/$', consumers.VideoConsumer.as_asgi()),
    re_path(r'ws/video/status-request/$', consumers.VideoConsumer.as_asgi()),
]