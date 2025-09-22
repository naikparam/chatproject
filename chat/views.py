# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from .models import ChatRoom, Message, UserStatus
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

@login_required
def chat_list(request):
    # Get all chat rooms for the current user
    chat_rooms = ChatRoom.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1', 'user2').prefetch_related('messages')
    
    # Get all users except current user
    users = User.objects.exclude(id=request.user.id)
    
    context = {
        'chat_rooms': chat_rooms,
        'users': users,
    }
    return render(request, 'chat_list.html', context)

@login_required
def chat_room(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Create or get existing chat room
    room, created = ChatRoom.objects.get_or_create(
        user1=min(request.user, other_user, key=lambda u: u.id),
        user2=max(request.user, other_user, key=lambda u: u.id)
    )
    
    # Mark messages as read
    Message.objects.filter(
        room=room,
        sender=other_user
    ).update(is_read=True)
    
    # Get messages
    messages = room.messages.all().select_related('sender')
    
    context = {
        'room': room,
        'other_user': other_user,
        'messages': messages,
    }
    return render(request, 'chat_room.html', context)

@login_required
def start_chat(request, user_id):
    return redirect('chat_room', user_id=user_id)

class CustomLoginView(auth_views.LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('chat_list')
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after registration
            return redirect('chat_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})
