from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.loginPage,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('register/',views.registerUser,name='register'),

    path('',views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('create-room/',views.createRoom, name="create-room"),
    path('update-room/<str:pk>/',views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/',views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/',views.deleteMessage, name="delete-message"),
    path('update-user/',views.updateUser, name="update-user"),
    path('topics/',views.topicsPage, name="topics"),
    path('activity/',views.activityPage, name="activities"),
    path('join/<str:pk>',views.joinRoom, name="join-room"),
    path('leave/<str:pk>',views.leaveRoom, name="leave-room"),
    path('user/remove',views.removeUser, name="remove-user"),

    path('chat-room/<str:room>/',views.chatRoom, name="chatroom"),
    path('user_active/<str:user_id>/', views.check_remote_user_active, name='active-user'),

]
