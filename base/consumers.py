import json


from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from django.core.files.base import ContentFile
from .models import Room, Message, User, Media
from channels.layers import get_channel_layer


import base64



class ChatConsumer(AsyncWebsocketConsumer):
    
    active_users = set()

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = 'chat_%s' % self.room_name
         # Join the room group
      
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        ChatConsumer.active_users.add(self.username)

        await self.accept()

        await self.send_active_users()
        await self.check_video_channel_status(self.room_name)

    async def disconnect(self, close_code):
        ChatConsumer.active_users.remove(self.username)
        # Code executed on connection close
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.send_active_users()

    async def receive(self, text_data):
        message = json.loads(text_data)
        message_type = message.get('type')
        

        if message_type == 'message':
            content = message.get('content')
            username = message.get('user')
            await self.handle_message(username, content)
        elif message_type == 'file':
            filename = message.get('filename')
            data = message.get('data')
            content = message.get('message')
            username = message.get('user')
            fileSize = message.get('fileSize')
            fileType = message.get('fileType')
            await self.handle_file(username, content, filename,
                                    fileSize, fileType, data)
    
    
    async def send_active_users(self):
        users = list(ChatConsumer.active_users)
        message = {
            'type': 'active_users',
            'users': users,
        }
        # Send the list of active users to the connected clients
        await self.channel_layer.group_send(self.room_group_name,{
            'type': 'active_users_event',
            'message': message
        }) 

    async def active_users_event(self, event):
        # Receive the list of active users and send it to the client
        message = event['message']
       
        await self.send(text_data=json.dumps(message))         

    async def handle_message(self, username, content):
        #room = Room.objects.get(id=self.room_name)  
       # user = User.objects.get(email=username)

        message = await self.save_text_data( username, content)  
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                 'created': str(message.created),
                 'messageId': message.id,
                 'message': content,
                 'user': message.user.username,
                 'userId' :message.user.id,
                 'avatar': str(message.user.avatar),
                 'is_file' : False,
                 'type': 'chat_message'
            }
        )
       
    async def handle_file(self, username, content, filename,
                                    fileSize, fileType, data):

        message = await self.save_file_data(username, content, filename,
                                    fileSize, fileType, data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'created': str(message.created),
                'messageId': message.id,
                'message': content,
                'user': message.user.username,
                'userId' :message.user.id,
                'avatar': str(message.user.avatar),
                'fileType': fileType,
                'filename': filename,               
                'is_file' : True,
                'file': data,
                'type': 'chat_message'
            }
        )
    async def chat_message(self, event): 
        is_file = event.get('is_file')

        if is_file == True:
          message = event.get('message')
          messageId = event['messageId']
          created = event['created']
          avatar = event['avatar']
          fileType = event['fileType']
          filename = event['filename']
          user = event['user']
          userId = event['userId']
          file = event.get('file')
          await self.send(text_data=json.dumps({
                'message': message,
                'created': created,
                'messageId': messageId,
                'fileType': fileType,
                'filename': filename,
                'user': user,
                'userId': userId,
                'avatar': avatar, 
                'is_file' : True,
                'file': file,              
        }))
        if is_file == False:
          messageId = event['messageId']
          created = event['created']
          avatar = event['avatar']
          message = event.get('message')
          user = event['user']
          userId = event['userId']
          await self.send(text_data=json.dumps({
                'created': created,
                'messageId': messageId,
                'message': message,
                'user': user,
                'userId': userId,
                'avatar': avatar, 
                'is_file' : False,              
        }))
        
    @sync_to_async
    def save_text_data(self, username, content):
        room = Room.objects.get(id=self.room_name)  
        user = User.objects.get(username=username)
        message = Message.objects.create(
            user = user,
            room = room,
            body = content
        )
        room.participants.add(user)
        return message
         
    @sync_to_async
    def save_file_data(self,username, content, filename,
                                    fileSize, fileType, data):
        room = Room.objects.get(id=self.room_name)  
        user = User.objects.get(username=username)
        file_format, file_data1 = data.split(';base64,')
        decoded_message = base64.b64decode(file_data1)
        file_data = ContentFile(decoded_message,name=filename)
         
        #print(decoded_message)
        message = Message.objects.create(
            user = user,
            room = room,
            body = content
        )
       
        media = Media.objects.create(
            message = message,
            media_name = filename,
            media_type = fileType,
            media_size = fileSize,
            media_path = file_data
        )
        room.participants.add(user)
        return message
    
    # async def check_video_channel_status(self,room_name):
    #    channel_layer = get_channel_layer()
    #    await channel_layer.send(
    #         "video_channel_status_request",  # Use the route name
    #         {
    #             "type": "video_channel_status_request",
    #             "room_name": room_name,
    #             "reply_channel": self.channel_name,
    #         }
    # )
       
    # async def video_channel_status_response(self, event):
    #     # Receive the video channel status response from the VideoConsumer
    #     is_active = event['is_active']
    #     print(is_active)
    #     # Send the status message to the client
    #     await self.send(text_data=json.dumps({"status": "video_channel", 
    #                                           "active": {is_active}}))  
    async def check_video_channel_status(self, room_name):
        channel_layer = get_channel_layer()
        await channel_layer.send(
            "video_channel_status_request",
            {
                "type": "video_channel_status_request",
                "room_name": room_name,
               
            }
        )
           
        
          

class VideoConsumer(AsyncWebsocketConsumer):
    connected_users = {}
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.userId = self.scope['url_route']['kwargs']['userId']
        self.room_group_name = 'video_%s' % self.room_name
        
        self.add_user_to_channel(self.room_name, self.userId)
        # and send the channel status as a message to the client
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        if self.is_channel_active(self.room_name):
            await self.channel_layer.send(self.channel_name, {
                "type": "video_channel_status_response",
                "is_active": True,
            })
        else:
            await self.channel_layer.send(self.channel_name, {
                "type": "video_channel_status_response",
                "is_active": False,
            })
        

    async def disconnect(self, close_code):
        self.remove_user_from_channel(self.room_name, self.userId)
        # Perform any necessary cleanup here
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        if self.is_channel_active(self.room_name):
            await self.channel_layer.send(self.channel_name, {
                "type": "video_channel_status_response",
                "is_active": True,
            })
        else:
            await self.channel_layer.send(self.channel_name, {
                "type": "video_channel_status_response",
                "is_active": False,
            })
    async def receive(self, text_data):
        # Process incoming video messages here
        pass

    def add_user_to_channel(self, room_name, userId):
        if room_name not in self.connected_users:
            self.connected_users[room_name] = set()
        self.connected_users[room_name].add(userId)

    def remove_user_from_channel(self, room_name, userId):
        if room_name in self.connected_users:
            self.connected_users[room_name].remove(userId)

    def is_channel_active(self, room_name):
        return len(self.connected_users.get(room_name, set())) > 0
    
    # async def video_channel_status_request(self, event):
    #     # Receive the video channel status request from the ChatConsumer
    #     print("Received status request!")
    #     room_name = event["room_name"]
    #     reply_channel = event['reply_channel']
    #     is_active = self.is_channel_active(room_name)

    #     # Send the status response message to the ChatConsumer
    #     await self.channel_layer.send(reply_channel, {
    #         "type": "video_channel_status_response",
    #         "is_active": is_active,
    #     })  
    async def video_channel_status_request(self, event):
        print("here i am")
        # Receive the video channel status request from the ChatConsumer
        room_name = event["room_name"]
       
        is_active = self.is_channel_active(room_name)

        # Send the status response message to the ChatConsumer
        await self.channel_layer.send(reply_channel, {
            "type": "video_channel_status_response",
            "is_active": is_active,
        })

    async def video_channel_status_response(self, event):
        # Receive the video channel status response from the ChatConsumer
        is_active = event['is_active']
        # Send the status message to the client
        await self.send(text_data=json.dumps({"status": "video_channel", "active": is_active}))    
# to identify file type
