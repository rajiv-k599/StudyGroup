from django.shortcuts import render, redirect, get_object_or_404
from .models import User, BaseRoomParticipants, Topic
from .models import User, BaseRoomParticipants, Topic
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from .models import Room, Topic, Message, User, Media, Notification
from django.urls import resolve
from django.contrib.auth import authenticate, login, logout
from .constants import NotificationType

from .forms import RoomForm, UserForm, MyUserCreationForm
import magic
import os


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No user found with that email address.')
            return redirect('reset-password')

        # Generate the password reset token
        token = default_token_generator.make_token(user)

        # Build the reset password email
        reset_url = request.build_absolute_uri(
            f'/reset-password/confirm/{user.pk}/{token}/'
        )
        mail_subject = 'Reset your password'
        message = f'Please click the following link to reset your password:\n\n{reset_url}'
        send_mail(mail_subject, message, 'from@example.com', [email])

        messages.success(request, 'Password reset email has been sent.')
        return redirect('login')

    return render(request, 'base/forgot_password.html')

@login_required(login_url='login')
def updatePassword(request):
    notifications = Notification.objects.filter(
        receiver=request.user, seen=False)
              
           
    context = {'notifications': notifications}
    return render(request,'base/forgetPassword/forget_password.html', context)

@login_required(login_url='login')
def changePassword(request):
  if request.method == 'POST': 
        current = request.POST.get('current')
        new = request.POST.get('new')
        confirm = request.POST.get('confirm')
        user = request.user
        if current and new and confirm:
            if user.check_password(current):
                if new == confirm:
                    user.set_password(new)
                    user.save()
                    # It's important to update the session to prevent logout
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Password updated successfully')
                else:
                    messages.error(request, 'New and confirm password do not match')
            else:
                messages.error(request, 'Current password is incorrect')
        else:
            messages.error(request, 'Please fill in all fields')
  return redirect('update-password')          
# forgotpw completed

 # handle user login


def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exists')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "username or password does not exist")

    context = {'page': page}
    return render(request, 'base/login_registration.html', context)

# handle user logout

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')

# handle user registration


def registerUser(request):
    page = 'register'
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            messages.success(request, 'User register successfully')
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'base/login_registration.html', context)


# home page
@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q)
    )
    notifications = Notification.objects.filter(
        receiver=request.user, seen=False)
    topics = Topic.objects.all()[0:4]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[:6]
    print(notifications.count)
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count,
               'room_messages': room_messages, 'notifications': notifications}
    return render(request, 'base/home.html', context)

# room view


@login_required(login_url='login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('created')
    participants = room.participants.all()
    notifications = Notification.objects.filter(receiver=request.user, seen=False )

    if request.method == 'POST':
        file = request.FILES.get('file')
        msg = request.POST.get('body')

        if file is None and msg is "":
            messages.warning(request, 'message is empty')

        message = Message.objects.create(
            user=request.user,
            room=room,
            body=msg
        )
        if file:
            media = Media.objects.create(
                message=message,
                media_name=file.name,
                media_type=file_type(file),
                media_size=file.size,
                media_path=file
            )

        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    user_is_participant = request.user in participants

    # Retrieve messages with associated media
    # messages_with_media = Message.objects.filter(
    #     room=room, media__isnull=False)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants, 'user_is_participant': user_is_participant, 'notifications': notifications}
    return render(request, 'base/room.html', context)

# room messages:

  #  messages_with_media = Message.objects.filter(room=room, media__isnull=False)


# profile view


# @login_required(login_url='login')
# def userProfile(request, pk):
#     user = User.objects.get(id=pk)
#     rooms = user.room_set.all()
#     room_messages = user.message_set.all()
#     topics = Topic.objects.all()
#     context = {'user': user, 'rooms': rooms,
#                'topics': topics, 'room_messages': room_messages}
#     return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    hosted_rooms = Room.objects.filter(host_id=pk)
    joined_rooms = Room.objects.filter(
        participants__id=pk).exclude(host_id=pk)
    notifications = Notification.objects.filter(receiver=request.user, seen=False )

    room_messages = user.message_set.all()[:10]
    roompct = BaseRoomParticipants.objects.all()
    topics = Topic.objects.all()

    context = {
        'user': user,
        'hosted_rooms': hosted_rooms,
        'joined_rooms': joined_rooms,
        'topics': topics,
        'room_messages': room_messages,
        'roompct': roompct,
        'notifications': notifications
    }

    return render(request, 'base/profile.html', context)


# create room


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    notifications = Notification.objects.filter(
        receiver=request.user, seen=False)
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        messages.success(request, 'room created successfully')
        return redirect('home')

    context = {'form': form, 'topics': topics, 'notifications' : notifications}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def usernameRedirect(request, room_id, username): 
    try:
      userMention = User.objects.get(username=username)
    except:
        messages.error(request, 'User does not exists')
        return redirect('room', pk=room_id)

    return redirect('user-profile', pk=userMention.id)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    notifications = Notification.objects.filter(
        receiver=request.user, seen=False)

    if request.user != room.host:
        return HttpResponse('you are not allowed here')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        messages.success(request, 'room updated successfully')
        return redirect('home')

    context = {'form': form, 'topics': topics,
               'room': room, 'notifications': notifications}
    return render(request, 'base/room_form.html', context)

# delete room


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    notifications = Notification.objects.filter(
        receiver=request.user, seen=False)
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'room deleted successfully')
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room, 'notifications': notifications})


@login_required(login_url='login')
def joinRoom(request, pk):
    room = Room.objects.get(id=pk)
    room.participants.add(request.user)
    Notification.objects.create(
        sender=request.user,
        receiver=room.host,
        type=NotificationType.Join,
        room=room
    )
    return redirect('room', pk=room.id)


@login_required(login_url='login')
def leaveRoom(request, pk):
    room = Room.objects.get(id=pk)

    if room.host != request.user:
        room.participants.remove(request.user)
    return redirect('room', pk=room.id)


@login_required(login_url='login')
def removeUser(request):
    if request.method == 'GET':
        roomId = request.GET.get('room')
        userId = request.GET.get('user')
        user = User.objects.get(id=userId)
        room = Room.objects.get(id=roomId)
        if room.host != user:
            room.participants.remove(user)

    return redirect('room', pk=room.id)

@login_required(login_url='login')
def notificationSeen(request, pk):
    notification = Notification.objects.get(id=pk)
    notification.seen = True
    notification.save()

    return redirect('room', pk=notification.room.id)
# deleted message


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    notifications = Notification.objects.filter(
        receiver=request.user, seen=False)

    if request.user != message.user:
        return HttpResponse('you are not allowed here')

    if request.method == 'POST':
        message.delete()
        messages.success(request, 'message deleted successfully')
        return redirect('room', pk=message.room.id)
    return render(request, 'base/delete.html', {'obj': message, 'notifications': notifications})

# update user


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    notifications = Notification.objects.filter(
        receiver=request.user, seen=False)
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'user updated successfully')
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update_user.html', {'form': form, 'notifications': notifications})

# To get topics


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    notifications = Notification.objects.filter(
        receiver=request.user, seen=False)
    context = {'topics': topics, 'notifications': notifications}
    return render(request, 'base/topics.html', context)

# to get activity


def activityPage(request):
    room_messages = Message.objects.all()[:6]
    notifications = Notification.objects.filter(
        receiver=request.user, seen=False)
    context = {'room_messages': room_messages, 'notifications': notifications}
    return render(request, 'base/activity.html', context)

# redirect to chat room


def chatRoom(request, room):
    roomDetail = Room.objects.get(id=room)
    context = {'roomId': room, 'room': roomDetail}
    return render(request, 'GroupChat/room.html', context)

# to identify file type


def file_type(file):
    file_type = file.content_type
    if file_type.startswith('image'):
        return 'Image'
    elif file_type == 'application/pdf':
        return 'PDF'
    elif file_type == 'application/msword' or file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return 'DOC'
    elif file_type == 'application/xml' or file_type == 'text/xml':
        return 'XML'
    elif file_type == 'application/vnd.ms-excel' or file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return 'Excel'
    elif file_type.startswith('video'):
        return 'Video'
    else:
        return 'Unknown'


def check_remote_user_active(request, user_id):
    try:
        user = User.objects.get(id=user_id)  # Assuming you have the user ID
        is_active = user.is_active
        return JsonResponse({'is_active': is_active})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'})


def open_file(request, file_id):

    # Assuming you have a model called `File` that stores the files.
    file_obj = get_object_or_404(Media, id=file_id)
    file_path = file_obj.media_path.path

    # Use python-magic to detect the file type based on its content
    file_type = magic.from_file(file_path, mime=True)

    # Open and serve the file based on its detected content type
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type=file_type)
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        return response


def download_image(request, image_id):
    # Assuming you have a model called `Image` that stores the images.
    image_obj = get_object_or_404(Media, id=image_id)
    image_path = image_obj.media_path.path

    # Open the image file and serve it as a download
    with open(image_path, 'rb') as image_file:
        # Change content type according to your image type (e.g., 'image/png' for PNG images)
        response = HttpResponse(image_file.read(), content_type='image/jpeg')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(image_path)}"'
        return response
