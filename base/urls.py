from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerUser, name='register'),

    # Password reset views
    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name='base/reset_password.html'), name='reset-password'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='base/reset_password_done.html'), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='base/reset_password_confirm.html'), name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='base/reset_password_complete.html'), name='password_reset_complete'),
    path('profile/password/update', views.updatePassword, name="update-password"),
    path('profile/password/change', views.changePassword, name="change-password"),


    # forgot password finished

    path('home/', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
    path('update-user/', views.updateUser, name="update-user"),
    path('topics/', views.topicsPage, name="topics"),
    path('activity/', views.activityPage, name="activities"),
    path('join/<str:pk>', views.joinRoom, name="join-room"),
    path('leave/<str:pk>', views.leaveRoom, name="leave-room"),
    path('user/remove', views.removeUser, name="remove-user"),
    path('open_file/<int:file_id>/', views.open_file, name='open-file'),
    path('download_image/<int:image_id>/',
         views.download_image, name='download-image'),
    path('notification/seen/<str:pk>',
         views.notificationSeen, name='seen-notification'),

    path('chat-room/<str:room>/', views.chatRoom, name="chatroom"),
    path('user_active/<str:user_id>/',
         views.check_remote_user_active, name='active-user'),
    path('user/profile/<int:room_id>/<str:username>', views.usernameRedirect, name="username"),

]
