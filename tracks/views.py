from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from .models import Track, Like, Comment, Playlist, Album
from .forms import TrackForm, CommentForm , PlaylistForm, AlbumForm, TrackInAlbumForm, ReportForm
from django.forms import modelformset_factory
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
User = get_user_model()

def home(request):
    return redirect("track_list")  

# def user_profile(request, username):
#     user_obj = get_object_or_404(User, username=username)
    
#     tracks = Track.objects.filter(uploaded_by=user_obj).order_by('-created_at')
#     playlists = Playlist.objects.filter(user=user_obj).order_by('-created_at')
#     albums = Album.objects.filter(artist=user_obj).order_by('-created_at')  

#     return render(request, 'tracks/profile.html', {
#         'profile_user': user_obj,
#         'tracks': tracks,
#         'playlists': playlists,
#         'albums': albums,  #
#     })

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
    query = request.GET.get('q', '')  
    tracks = Track.objects.all()

    if query.strip():
        tracks = tracks.filter(
            Q(title__icontains=query) |
            Q(uploaded_by__username__icontains=query) |
            Q(album__title__icontains=query) |
            Q(genre__icontains=query) |          
            Q(album__genre__icontains=query) 
        )

    paginator = Paginator(tracks.order_by('-created_at'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tracks/track_list.html', {
        'page_obj': page_obj,
        'request': request,
    })


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
    q = request.GET.get("q", "")
    tracks = Track.objects.filter(uploaded_by=request.user).order_by("-created_at")

    if q:
        tracks = tracks.filter(title__icontains=q)

    return render(request, "tracks/my_tracks.html", {"tracks": tracks, "q": q})


@login_required
def delete_track(request, pk):
    track = get_object_or_404(Track, pk=pk, uploaded_by=request.user)
    if request.method == "POST":
        track.delete()
        return redirect('profile', username=request.user.username)
    return redirect('track_detail', pk=pk)

@login_required
def my_likes(request):
    q = request.GET.get("q", "")
    liked_tracks = Track.objects.filter(likes__user=request.user).order_by("-created_at")

    if q:
        liked_tracks = liked_tracks.filter(
            Q(title__icontains=q) | Q(album__title__icontains=q)
        )

    return render(request, "tracks/my_likes.html", {"tracks": liked_tracks, "q": q})

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

@login_required
def create_album(request):
    num_tracks = int(request.GET.get('num_tracks', 0))  
    if request.method == 'POST':
        album_form = AlbumForm(request.POST, request.FILES)
        num_tracks = int(request.POST.get('num_tracks', 0))
        track_forms = [TrackInAlbumForm(request.POST, request.FILES, prefix=str(i)) for i in range(num_tracks)]

        if album_form.is_valid() and all(tf.is_valid() for tf in track_forms):
            album = album_form.save(commit=False)
            album.artist = request.user
            album.save()

            for tf in track_forms:
                track = tf.save(commit=False)
                track.album = album
                track.uploaded_by = request.user
                track.cover = album.cover 
                track.save()

            return redirect('album_detail', id=album.id)

    else:
        album_form = AlbumForm()
        track_forms = [TrackInAlbumForm(prefix=str(i)) for i in range(num_tracks)] if num_tracks else []

    return render(request, 'tracks/create_album.html', {
        'album_form': album_form,
        'track_forms': track_forms,
        'num_tracks': num_tracks,
    })

@login_required
def like_album(request, album_id):
    album = Album.objects.get(id=album_id)
    if request.user in album.likes.all():
        album.likes.remove(request.user)
        liked = False
    else:
        album.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': album.likes.count()})

@login_required
def album_detail(request, id):
    album = get_object_or_404(Album, id=id)
    comments = album.comments.filter(parent__isnull=True).order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id')
            parent = Comment.objects.filter(id=parent_id).first() if parent_id else None

            Comment.objects.create(
                album=album,
                user=request.user,
                text=form.cleaned_data['text'],
                parent=parent
            )
            return redirect('album_detail', id=album.id)
    else:
        form = CommentForm()

    return render(request, 'tracks/album_detail.html', {
        'album': album,
        'comments': comments,
        'form': form,
    })
def album_list(request):
    query = request.GET.get('q', '').strip()
    albums = Album.objects.all().order_by('-created_at')

    if query:
        albums = albums.filter(
            Q(title__icontains=query) |
            Q(artist__username__icontains=query) |
            Q(description__icontains=query)    |
            Q(genre__icontains=query)
        )

    paginator = Paginator(albums, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tracks/album_list.html', {
        'page_obj': page_obj,
        'query': query,
    })

@login_required
def delete_album(request, album_id):
    album = get_object_or_404(Album, id=album_id, artist=request.user)
    album.delete()
    return redirect('profile', username=request.user.username)


@login_required
def report_track(request, track_id):
    track = get_object_or_404(Track, id=track_id)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.track = track
            report.user = request.user
            report.save()

            send_mail(
                subject=f'Жалоба на трек: {track.title}',
                message=f'Пользователь: {request.user.username}\n\nТекст жалобы:\n{report.message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL], 
                fail_silently=False,
            )

            messages.success(request, 'Жалоба успешно отправлена.')
            return redirect('track_detail', pk=track.id)
    else:
        form = ReportForm()

    return render(request, 'tracks/report_form.html', {'form': form, 'track': track})

@login_required
def my_albums(request):
    """Показ всех альбомов текущего пользователя"""
    q = request.GET.get('q', '')
    albums = Album.objects.filter(artist=request.user).order_by("-created_at")

    if q:
        albums = albums.filter(title__icontains=q)

    context = {
        'albums': albums,
        'q': q,
    }
    return render(request, 'tracks/my_albums.html', context)


@login_required
def toggle_save_album(request, album_id):
    """Добавить/убрать альбом из сохранённых"""
    album = Album.objects.get(id=album_id)
    user = request.user

    if user in album.saved_by.all():
        album.saved_by.remove(user)
        saved = False
    else:
        album.saved_by.add(user)
        saved = True

    return JsonResponse({'saved': saved, 'count': album.saved_by.count()})

@login_required
def library_view(request):
    q = request.GET.get("q", "")
    saved_albums = request.user.saved_albums.all()

    if q:
        saved_albums = saved_albums.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )

    return render(request, "tracks/library.html", {
        "saved_albums": saved_albums,
        "q": q,
    })


@login_required
def report_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.album = album
            report.user = request.user
            report.save()
            send_mail(
                subject=f'Новая жалоба на альбом: {album.title}',
                message=f'Пользователь {request.user.username} оставил жалобу:\n\n{report.message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],  
                fail_silently=False,
            )

            return redirect('album_detail', id=album.id)
    else:
        form = ReportForm()

    return render(request, 'tracks/report_album.html', {'form': form, 'album': album})