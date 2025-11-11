from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from tracks.models import Track, Playlist, Album
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.paginator import Paginator
User = get_user_model()
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile", username=user.username)
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("profile", username=user.username) 
    else:
        form = CustomAuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")




def profile_view(request, username=None):
    """
    Показывает профиль пользователя (по username).
    Поддерживает поиск по трекам и альбомам через GET ?q=...
    Пагинация треков (опционально).
    """
    profile_user = get_object_or_404(User, username=username)

    q = (request.GET.get('q') or "").strip()

    tracks_qs = Track.objects.filter(uploaded_by=profile_user).order_by('-created_at')
    albums_qs = Album.objects.filter(artist=profile_user).order_by('-created_at')
    playlists_qs = Playlist.objects.filter(user=profile_user).order_by('-created_at') if 'Playlist' in globals() else []

    if q:
        tracks_qs = tracks_qs.filter(
            Q(title__icontains=q) |
            Q(uploaded_by__username__icontains=q)
        )

        albums_qs = albums_qs.filter(
            Q(title__icontains=q) |
            Q(artist__username__icontains=q)
        )

    paginator = Paginator(tracks_qs, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': profile_user,
        'tracks': page_obj,        
        'albums': albums_qs,
        'playlists': playlists_qs,
        'q': q,                   
        'page_obj': page_obj,     
    }
    return render(request, 'users/profile.html', context)

