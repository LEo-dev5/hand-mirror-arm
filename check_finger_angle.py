import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
from angle_calculator import calculate_angle, map_range

latest_result = None

def save_result(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result

base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    result_callback=save_result
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
start_time = time.time()

#-------------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    timestamp_ms = int((time.time() - start_time) * 1000)
    detector.detect_async(mp_image, timestamp_ms)

    if latest_result and latest_result.hand_world_landmarks:
        world_landmarks = latest_result.hand_world_landmarks[0]
        p5 = world_landmarks[5]
        a = (p5.x, p5.y, p5.z)
        p6 = world_landmarks[6]
        b = (p6.x, p6.y, p6.z)
        p7 = world_landmarks[7]
        c = (p7.x, p7.y, p7.z)

        angle = calculate_angle(a, b, c)
        gripper_angle = map_range(angle, 85, 172, 180, 0)
        cv2.putText(frame, f"Angle: {angle:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Gripper: {gripper_angle:.1f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Finger Angle Check", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
detector.close()