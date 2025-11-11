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
    # path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('<int:pk>/delete/', views.delete_track, name='delete_track'),
    path('playlists/<int:playlist_id>/remove/<int:track_id>/', views.remove_from_playlist, name='remove_from_playlist'),
    path('albums/<int:album_id>/like/', views.like_album, name='like_album'),
    path('albums/create/', views.create_album, name='create_album'),
    path('albums/<int:id>/', views.album_detail, name='album_detail'),
    path('albums/', views.album_list, name='album_list'),
    path('albums/delete/<int:album_id>/', views.delete_album, name='delete_album'),
    path('tracks/<int:track_id>/report/', views.report_track, name='report_track'),
    path('my-albums/', views.my_albums, name='my_albums'),
    path('albums/<int:album_id>/save/', views.toggle_save_album, name='toggle_save_album'),
    path('library/', views.library_view, name='library'),
    path('albums/<int:album_id>/report/', views.report_album, name='report_album'),

]
