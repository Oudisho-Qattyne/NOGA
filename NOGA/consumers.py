from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async
import cv2
import pandas as pd
import numpy as np
# from ultralytics import YOLO
from .ImprovedTracker import *
from datetime import date

# model = YOLO('yolov8s2.pt')
# my_file = open("coco.txt", "r")
# data = my_file.read()
# class_list = data.split("\n") 

# Create a properly async version of increment_visitors_count
async def increment_visitors_count(branch_id):
    from branches.models import Branch_Visitors
    today = date.today()
    
    # Use sync_to_async for all database operations
    obj, created = await sync_to_async(
        lambda: Branch_Visitors.objects.get_or_create(branch_id=branch_id, date=today),
        thread_sensitive=True
    )()
    
    obj.visitors_count += 1
    await sync_to_async(obj.save, thread_sensitive=True)()

# class SourceConsumer(AsyncWebsocketConsumer):
#     type = "monitoring"
#     async def connect(self):
#         # Authenticate the ESP32 (e.g., via query token)

#         self.id = self.scope['url_route']['kwargs']['id']
#         self.group_name = f"source_{self.id}"

#         try:
#             from branches.models import Camera
#             obj = await sync_to_async(Camera.objects.get, thread_sensitive=True)(pk=self.id)
#             area_points = obj.area_points
#             if area_points is not None:
#                 self.area1 = [(point['x'], point['y']) for point in area_points['area1']]
#                 self.area2 = [(point['x'], point['y']) for point in area_points['area2']]
#                 self.type = obj.camera_type
#                 self.tracker = Tracker()
#                 self.people_entering = {}
#             obj.is_active = True
#             await sync_to_async(obj.save, thread_sensitive=True)()
#         except ObjectDoesNotExist:
#             await self.close()
#             return
        
#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )

#         await self.accept()


#     async def disconnect(self, close_code):

#         try:
#             from branches.models import Camera
#             obj = await sync_to_async(Camera.objects.get, thread_sensitive=True)(pk=self.id)
#             obj.is_active = False
#             await sync_to_async(obj.save, thread_sensitive=True)()

#         except ObjectDoesNotExist:
#             await self.close()
#             return

#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data=None, bytes_data=None):
#         if bytes_data:
#             nparr = np.frombuffer(bytes_data , np.uint8)
#             frame = cv2.imdecode(nparr , cv2.IMREAD_COLOR)
#              # Define the rotation angle
#             angle = -90  # Rotation angle in degrees (clockwise)
#             # Get image dimensions
#             height, width = frame.shape[:2]
#             # Rotate the image around its center
#             # rotation_matrix = cv2.getRotationMatrix2D((width/2, height/2), angle, 1)

#             # frame = cv2.warpAffine(frame, rotation_matrix, (width, height))
#             height, width = frame.shape[:2]

#             if self.type == "visitors":

#                 # area1=[(233,388),(335,7),(347,327),(247,337)]

#                 # area2=[(75,63),(77,152),(519,146),(516,67)]

#                 area1 = [(int(x * width / 100), int(y * height / 100)) for (x, y) in self.area1]
#                 area2 = [(int(x * width / 100), int(y * height / 100)) for (x, y) in self.area2]

#                 def RGB(event, x, y, flags, param):
#                     if event == cv2.EVENT_MOUSEMOVE :  
#                         colorsBGR = [x, y]
                        
#                 # frame=cv2.resize(frame,(1020,500))

#                 results=model.predict(frame)

#                 a=results[0].boxes.data

#                 px=pd.DataFrame(a).astype("float")

#                 list=[]
                        
#                 for index,row in px.iterrows():
#                     x1=int(row[0])
#                     y1=int(row[1])
#                     x2=int(row[2])
#                     y2=int(row[3])
#                     d=int(row[5])
#                     c=class_list[d]

#                     if 'person' in c:
#                         list.append([x1 , y1 , x2 , y2])
#                 bbox_id = self.tracker.update(list)
#                 for bbox in bbox_id:
#                     x3,y3,x4,y4,id = bbox
#                     results = cv2.pointPolygonTest(np.array(area1,np.int32),(x4,y4), False)
#                     if results >=0:
#                             self.people_entering[id] = (x4 , y4)
#                             cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
#                             print(self.people_entering)
#                     if id in self.people_entering:
#                         results1 = cv2.pointPolygonTest(np.array(area2,np.int32),(x4,y4), False)
#                         if results1 >= 0:
#                             cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
#                             cv2.circle(frame,(x4 , y4) , 4 , (255 , 0 ,255) , -1)
#                             cv2.putText(frame,str(id),(x3,y3),cv2.FONT_HERSHEY_COMPLEX,(0.5),(255,255,255),1)
#                             print("+++++++++++=\n\n\n")
                    
#                 cv2.polylines(frame,[np.array(area1,np.int32)],True,(255,0,0),2)
#                 cv2.putText(frame,str('1'),(504,471),cv2.FONT_HERSHEY_COMPLEX,(0.5),(0,0,0),1)
#                 cv2.polylines(frame,[np.array(area2,np.int32)],True,(255,0,0),2)
#                 cv2.putText(frame,str('2'),(466,485),cv2.FONT_HERSHEY_COMPLEX,(0.5),(0,0,0),1)

 
#                 success ,byte_data = cv2.imencode('.jpg' , frame)
#                 await self.channel_layer.group_send(
#                     self.group_name,
#                     {
#                         "type": "video.frame",
#                         "data": byte_data.tobytes()
#                     }
#                 )

#             elif self.type == "monitoring":
#                 success ,byte_data = cv2.imencode('.jpg' , frame)
#                 await self.channel_layer.group_send(
#                     self.group_name,
#                     {
#                         "type": "video.frame",
#                         "data": byte_data.tobytes()
#                         # "data": bytes_data
#                     }
#                 )
#         # success ,byte_data = cv2.imencode('.jpg' , frame)
#         # await self.channel_layer.group_send(
#         #     self.group_name,
#         #     {
#         #         "type": "video.frame",
#         #         "data": byte_data.tobytes()
#         #         # "data": bytes_data
#         #     }
#         # )
#     async def video_frame(self, event):
#         await self.send(bytes_data=event["data"])

class SourceConsumer(AsyncWebsocketConsumer):
    type = "monitoring"
    
    async def connect(self):
        self.id = self.scope['url_route']['kwargs']['id']
        self.group_name = f"source_{self.id}"

        try:
            from branches.models import Camera
            obj = await sync_to_async(Camera.objects.get, thread_sensitive=True)(pk=self.id)
            area_points = obj.area_points
            if area_points is not None:
                self.area1 = [(point['x'], point['y']) for point in area_points['area1']]
                self.area2 = [(point['x'], point['y']) for point in area_points['area2']]
                self.type = obj.camera_type
                self.branch_id = await sync_to_async(lambda: obj.branch.id)()
                self.tracker = ImprovedTracker()  # Use the improved tracker
                self.people_entering = {}
                self.counted_ids = set()  # Track which IDs have been counted
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
            pass

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            nparr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            height, width = frame.shape[:2]

            if self.type == "visitors":
                # area1 = [(int(x * width / 100), int(y * height / 100)) for (x, y) in self.area1]
                # area2 = [(int(x * width / 100), int(y * height / 100)) for (x, y) in self.area2]

                # results = model.predict(frame)
                # a = results[0].boxes.data
                # px = pd.DataFrame(a).astype("float")

                # list = []
                # for index, row in px.iterrows():
                #     x1 = int(row[0])
                #     y1 = int(row[1])
                #     x2 = int(row[2])
                #     y2 = int(row[3])
                #     d = int(row[5])
                #     c = class_list[d]

                #     if 'person' in c:
                #         list.append([x1, y1, x2-x1, y2-y1])  # Convert to [x, y, w, h] format
                       
                # bbox_id = self.tracker.update(list)
                
                # for bbox in bbox_id:
                #     x, y, w, h, id = bbox
                #     cx = x + w // 2
                #     cy = y + h // 2
                #     print(cx , cy)
                #     # Check if person is in area1
                #     results = cv2.pointPolygonTest(np.array(area1, np.int32), (cx, cy), False)
                #     if results >= 0:
                #         self.people_entering[id] = (cx, cy)
                #         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                #     # Check if person is in area2 and was previously in area1
                #     if id in self.people_entering:
                #         print(area2)
                #         results1 = cv2.pointPolygonTest(np.array(area2, np.int32), (cx, cy), False)
                #         print(results1)
                #         if results1 >= 0 and id not in self.counted_ids:
                #             cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                #             cv2.circle(frame, (cx, cy), 4, (255, 0, 255), -1)
                #             cv2.putText(frame, str(id), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                #             self.counted_ids.add(id)  # Mark this ID as counted
                #             await increment_visitors_count(self.branch_id)
                #             print(f"Person {id} counted")
                
                # # Draw areas
                # cv2.polylines(frame, [np.array(area1, np.int32)], True, (255, 0, 0), 2)
                # cv2.putText(frame, str('1'), (area1[0][0], area1[0][1]), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)
                # cv2.polylines(frame, [np.array(area2, np.int32)], True, (255, 0, 0), 2)
                # cv2.putText(frame, str('2'), (area2[0][0], area2[0][1]), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)

                # # Display count
                # cv2.putText(frame, f"Count: {len(self.counted_ids)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                success, byte_data = cv2.imencode('.jpg', frame)
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