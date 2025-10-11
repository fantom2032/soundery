from django.urls import path
from . import views

urlpatterns = [
    path("", views.track_list, name="track_list"),
    path("upload/", views.upload_track, name="upload_track"),
    path("<int:pk>/", views.track_detail, name="track_detail"),
    path("<int:pk>/like/", views.like_track, name="like_track"),
    path("my/", views.my_tracks, name="my_tracks"),
    path("likes/", views.my_likes, name="my_likes"), 
    path('playlists/', views.my_playlists, name='my_playlists'),
    path('playlists/create/', views.create_playlist, name='create_playlist'),
    path('playlists/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path("<int:track_id>/add_to_playlist/", views.add_to_playlist, name="add_to_playlist"),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('<int:pk>/delete/', views.delete_track, name='delete_track'),

]
