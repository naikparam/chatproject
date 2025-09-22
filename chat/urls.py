from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('chat/<int:user_id>/', views.chat_room, name='chat_room'),
    path('start-chat/<int:user_id>/', views.start_chat, name='start_chat'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
     path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
    path('register/', views.register, name='register'),  # 👈 changed

]
