import time
import cv2 # type: ignore
import mediapipe as mp # type: ignore
from mediapipe.tasks import python # type: ignore
from mediapipe.tasks.python import vision # type: ignore
import numpy as np # type: ignore
from collections import deque
import face_distanceprocessor as fdp

class FaceLandmarkerProcessor:
        def __init__(self, model_path: str = "face_landmarker.task"):
            # Initialize the FaceLandmarkerProcessor with the specified model path.
            self.model_path = model_path
            
            # Intialize FaceLandmarker attributes
            BaseOptions = python.BaseOptions
            VisionRunningMode = vision.RunningMode
            FaceLandmarker = vision.FaceLandmarker
            FaceLandmarkerOptions = vision.FaceLandmarkerOptions
            
            self.ray_origins = deque(maxlen=10)
            self.ray_directions = deque(maxlen=10)
            self.ray_lengths = 50
            self._last_timestamp_ms = 0
            
            options = FaceLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=str(self.model_path)),
                running_mode=VisionRunningMode.VIDEO,
                num_faces=1
            )
            
            self.face_landmarker = FaceLandmarker.create_from_options(options)
            
            self.KEY_FACE_LANDMARKS = {"left": 234, "right": 454, "front": 10, "bottom": 152, "top": 1}
        
        def process_frame(self, frame):
            # Convert the frame to RGB format for processing.
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = max(int(time.time() * 1000), self._last_timestamp_ms + 1)
            self._last_timestamp_ms = timestamp_ms
            try:
                results = self.face_landmarker.detect_for_video(mp_image, timestamp_ms)
            except Exception:
                return None
            return results
        
        def _draw_landmarks(self, frame, results):
            if not results.face_landmarks:
                cv2.putText(frame, "No face detected", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                return frame, None, None
            
            elif results.face_landmarks:
                def landmark_to_np(landmark, w, h):
                    return np.array([landmark.x * w, landmark.y * h, landmark.z * w], dtype=np.float32)

                def project(pt3d):
                    return (int(pt3d[0]), int(pt3d[1]))

                h, w = frame.shape[:2]
                landmarks = results.face_landmarks[0]
                
                # Convert left and right eye landmarks to numpy arrays and store in a dictionary for easy access.
                fdp_processor = fdp.FaceDistanceProcessor()
                left_eye = landmark_to_np(landmarks[145], w, h)
                right_eye = landmark_to_np(landmarks[374], w, h)
                distance = fdp_processor.estimate_distance(left_eye, right_eye)
                
                # Draw the distance on the frame.
                #cv2.putText(frame, f"Distance: {distance:.2f} cm", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
                key_points = {}
                for name, idx in self.KEY_FACE_LANDMARKS.items():
                    pt = landmark_to_np(landmarks[idx], w, h)
                    key_points[name] = pt
                    x, y = int(pt[0]), int(pt[1])
                    #cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
                
                # Draw axes and rays based on the key points
                left_pt = key_points['left']
                right_pt = key_points['right']
                bottom_pt = key_points['bottom']
                top_pt = key_points['top']
                front_pt = key_points['front']

                # Oriented axes based on head geometry.
                right_axis = (right_pt - left_pt)
                right_axis /= np.linalg.norm(right_axis)

                up_axis = (top_pt - bottom_pt)
                up_axis /= np.linalg.norm(up_axis)

                forward_axis = np.cross(right_axis, up_axis)
                forward_axis /= np.linalg.norm(forward_axis)

                # Flip to ensure forward vector comes out of the face.
                forward_axis = -forward_axis

                # Compute center of the head.
                center = (left_pt + right_pt + top_pt + bottom_pt + front_pt) / 5

                # Half-sizes (width, height, depth).
                half_width = np.linalg.norm(right_pt - left_pt) / 2
                half_height = np.linalg.norm(top_pt - bottom_pt) / 2
                half_depth = 80

                self.ray_origins.append(center)
                self.ray_directions.append(forward_axis)

                avg_origin = np.mean(self.ray_origins, axis=0)
                avg_direction = np.mean(self.ray_directions, axis=0)
                avg_direction /= np.linalg.norm(avg_direction)

                # Draw smoothed ray.
                ray_length = 1.5 * half_depth
                ray_end = avg_origin - avg_direction * ray_length

                ray_padding_y = 25
                avg_origin_x, avg_origin_y = project(avg_origin)
                ray_end_x, ray_end_y = project(ray_end)

                # Add mean eye y to smooth the vertical anchor of the ray.
                avg_origin_y = int((front_pt[1] + avg_origin_y) / 2)
                ray_end_y = int((front_pt[1] + ray_end_y) / 2)

                # Draw ray in frame.
                # cv2.line(
                #     frame,
                #     (avg_origin_x, avg_origin_y - ray_padding_y),
                #     (ray_end_x, ray_end_y - ray_padding_y),
                #     (0, 0, 255),
                #     2,
                # )
            face_cx = (key_points['left'][0] + key_points['right'][0]) / 2
            face_cy = (key_points['top'][1] + key_points['bottom'][1]) / 2
            if avg_direction is not None:
                return frame, avg_direction, (face_cx, face_cy)
            else:
                return frame, None, (face_cx, face_cy)

