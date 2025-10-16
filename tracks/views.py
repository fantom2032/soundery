from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Track, Like, Comment, Playlist
from .forms import TrackForm, CommentForm , PlaylistForm 
from django.contrib.auth import get_user_model
User = get_user_model()

def home(request):
    return redirect("track_list")  

def user_profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    tracks = Track.objects.filter(uploaded_by=user_obj).order_by('-created_at')
    playlists = Playlist.objects.filter(user=user_obj).order_by('-created_at')

    return render(request, 'tracks/profile.html', {
        'profile_user': user_obj,
        'tracks': tracks,
        'playlists': playlists,
    })

@login_required
def upload_track(request):
    if request.method == 'POST':
        form = TrackForm(request.POST, request.FILES)
        if form.is_valid():
            track = form.save(commit=False)
            track.uploaded_by = request.user  
            track.save()
            return redirect('track_list')
    else:
        form = TrackForm()
    return render(request, 'tracks/upload.html', {'form': form})

def track_list(request):
    tracks = Track.objects.all().order_by("-created_at")
    return render(request, "tracks/track_list.html", {"tracks": tracks})


@login_required
def track_detail(request, pk):
    track = get_object_or_404(Track, pk=pk)
    comments = Comment.objects.filter(track=track, parent__isnull=True).order_by('-created_at')
    user_liked = Like.objects.filter(track=track, user=request.user).exists()

    if request.method == 'POST':
        text = request.POST.get('text')
        parent_id = request.POST.get('parent_id')
        parent = Comment.objects.filter(id=parent_id).first() if parent_id else None
        if text:
            Comment.objects.create(track=track, user=request.user, text=text, parent=parent)
            return redirect('track_detail', pk=pk)

    return render(request, 'tracks/track_detail.html', {
        'track': track,
        'comments': comments,
        'user_liked': user_liked,
    })

@login_required
def like_track(request, pk):
    track = get_object_or_404(Track, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, track=track)

    if not created:
        like.delete()
    return redirect("track_detail", pk=pk)


@login_required
def my_tracks(request):
    tracks = Track.objects.filter(uploaded_by=request.user).order_by("-created_at")
    return render(request, "tracks/my_tracks.html", {"tracks": tracks})


@login_required
def delete_track(request, pk):
    track = get_object_or_404(Track, pk=pk, uploaded_by=request.user)
    if request.method == "POST":
        track.delete()
        return redirect('user_profile', username=request.user.username)
    return redirect('track_detail', pk=pk)

@login_required
def my_likes(request):
    liked_tracks = Track.objects.filter(likes__user=request.user).order_by("-created_at")
    return render(request, "tracks/my_likes.html", {"tracks": liked_tracks})

@login_required
def create_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            form.save_m2m()
            return redirect('my_playlists')
    else:
        form = PlaylistForm()
    return render(request, 'tracks/create_playlist.html', {'form': form})


@login_required
def my_playlists(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'tracks/my_playlists.html', {'playlists': playlists})


@login_required
def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    return render(request, 'tracks/playlist_detail.html', {'playlist': playlist})

@login_required
def add_to_playlist(request, track_id):
    track = get_object_or_404(Track, id=track_id)

    if request.method == "POST":
        playlist_id = request.POST.get("playlist_id")
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        playlist.tracks.add(track)
        return redirect("track_detail", pk=track.id)

    playlists = Playlist.objects.filter(user=request.user)
    return render(request, "tracks/add_to_playlist.html", {
        "track": track,
        "playlists": playlists
    })


@login_required
def remove_from_playlist(request, playlist_id, track_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    track = get_object_or_404(Track, id=track_id)

    if track in playlist.tracks.all():
        playlist.tracks.remove(track)
        messages.success(request, f'Трек "{track.title}" удалён из плейлиста "{playlist.name}".')
    else:
        messages.warning(request, 'Этого трека нет в этом плейлисте.')

    return redirect('playlist_detail', playlist_id=playlist.id)
