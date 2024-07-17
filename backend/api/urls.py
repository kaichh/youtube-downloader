from django.urls import path
from .views import ping, get_video_info, download_video

urlpatterns = [
    path('ping/', ping, name='ping'),
    path('video-info/', get_video_info, name='get_video_info'),
    path('download/', download_video, name='download_video'),
]