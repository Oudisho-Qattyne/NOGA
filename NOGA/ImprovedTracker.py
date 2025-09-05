import math

class ImprovedTracker:
    def __init__(self):
        self.center_points = {}
        self.id_count = 0
        self.disappeared = {}  # Track how long an ID hasn't been detected
        self.max_disappeared = 10  # Frames to wait before considering an object gone

    def update(self, objects_rect):
        objects_bbs_ids = []

        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = x + w // 2
            cy = y + h // 2

            # Find out if that object was detected already
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 200:
                    self.center_points[id] = (cx, cy)
                    self.disappeared[id] = 0  # Reset disappearance counter
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    break

            # New object is detected we assign the ID to that object
            if same_object_detected is False:
                self.center_points[self.id_count] = (cx, cy)
                self.disappeared[self.id_count] = 0
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        # Check for disappeared objects
        for id in list(self.disappeared.keys()):
            if id not in [bbox[4] for bbox in objects_bbs_ids]:
                self.disappeared[id] += 1
                if self.disappeared[id] > self.max_disappeared:
                    # Remove the object from our dictionaries
                    if id in self.center_points:
                        del self.center_points[id]
                    if id in self.disappeared:
                        del self.disappeared[id]

        return objects_bbs_ids