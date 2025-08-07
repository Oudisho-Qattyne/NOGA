# from channels.generic.websocket import AsyncWebsocketConsumer
# import base64
# from global_frame_storage import latest_frame

# class VideoConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

#     async def receive(self, text_data=None, bytes_data=None):
#         if text_data:
#             frame_data = base64.b64decode(text_data)
#             global latest_frame
#             latest_frame = frame_data


from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async
import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO


model=YOLO('yolov8s.pt')
my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n") 

            
            
class SourceConsumer(AsyncWebsocketConsumer):
    type = "monitoring"
    async def connect(self):
        # Authenticate the ESP32 (e.g., via query token)

        self.id = self.scope['url_route']['kwargs']['id']
        self.group_name = f"source_{self.id}"

        try:
            from branches.models import Camera
            obj = await sync_to_async(Camera.objects.get, thread_sensitive=True)(pk=self.id)
            self.type = obj.camera_type
            obj.is_active = True
            await sync_to_async(obj.save, thread_sensitive=True)()
        except ObjectDoesNotExist:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):

        try:
            from branches.models import Camera
            obj = await sync_to_async(Camera.objects.get, thread_sensitive=True)(pk=self.id)
            obj.is_active = False
            await sync_to_async(obj.save, thread_sensitive=True)()

        except ObjectDoesNotExist:
            await self.close()
            return

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            nparr = np.frombuffer(bytes_data , np.uint8)
            frame = cv2.imdecode(nparr , cv2.IMREAD_COLOR)
             # Define the rotation angle
            angle = -90  # Rotation angle in degrees (clockwise)
            # Get image dimensions
            height, width = frame.shape[:2]
            # Rotate the image around its center
            rotation_matrix = cv2.getRotationMatrix2D((width/2, height/2), angle, 1)

            frame = cv2.warpAffine(frame, rotation_matrix, (width, height))

            if self.type == "visitors":
                
                area1=[(312,388),(289,390),(474,469),(497,462)]

                area2=[(279,392),(250,397),(423,477),(454,469)]

                def RGB(event, x, y, flags, param):
                    if event == cv2.EVENT_MOUSEMOVE :  
                        colorsBGR = [x, y]
                        
                frame=cv2.resize(frame,(1020,500))

                results=model.predict(frame)

                a=results[0].boxes.data

                px=pd.DataFrame(a).astype("float")

                list=[]
                        
                for index,row in px.iterrows():
                    x1=int(row[0])
                    y1=int(row[1])
                    x2=int(row[2])
                    y2=int(row[3])
                    d=int(row[5])
                    c=class_list[d]

                    if 'person' in c:
                        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                        cv2.putText(frame,str(c),(x1,y1),cv2.FONT_HERSHEY_COMPLEX,(0.5),(255,255,255),1)
                    
                    
                cv2.polylines(frame,[np.array(area1,np.int32)],True,(255,0,0),2)
                cv2.putText(frame,str('1'),(504,471),cv2.FONT_HERSHEY_COMPLEX,(0.5),(0,0,0),1)
                cv2.polylines(frame,[np.array(area2,np.int32)],True,(255,0,0),2)
                cv2.putText(frame,str('2'),(466,485),cv2.FONT_HERSHEY_COMPLEX,(0.5),(0,0,0),1)

 
                success ,byte_data = cv2.imencode('.jpg' , frame)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "video.frame",
                        "data": byte_data.tobytes()
                    }
                )

            elif self.type == "monitoring":
                success ,byte_data = cv2.imencode('.jpg' , frame)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "video.frame",
                        "data": byte_data.tobytes()
                        # "data": bytes_data
                    }
                )

    async def video_frame(self, event):
        await self.send(bytes_data=event["data"])

class ViewerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Add viewer to the video_stream group
        self.id = self.scope['url_route']['kwargs']['id']
        self.group_name = f"source_{self.id}"

        try:
            from branches.models import Camera
            obj = await sync_to_async(Camera.objects.get, thread_sensitive=True)(pk=self.id)
        except ObjectDoesNotExist:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        
    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def video_frame(self, event):
        # Send video frame to the viewer
        await self.send(bytes_data=event["data"])