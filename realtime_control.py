import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import asyncio
import websockets
import json
from wrist_tracker import get_wrist_servo_angles

ESP32_URI = "ws://192.168.219.106:8080"

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

async def main():
    cap = cv2.VideoCapture(0)
    start_time = time.time()

    print(f"ESP32 연결 시도 : {ESP32_URI}")
    async with websockets.connect(ESP32_URI) as websocket:
        print("연결 성공")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int((time.time() - start_time) * 1000)
            detector.detect_async(mp_image, timestamp_ms)

            # 손 인식 -> 각도계산 -> 전송
            if latest_result and latest_result.hand_landmarks:
                hand_landmarks = latest_result.hand_landmarks[0]
                angle_x, angle_y = get_wrist_servo_angles(hand_landmarks)            
                message = json.dumps({"base": int(angle_x)})
                await websocket.send(message)

            # 화면 표시
            cv2.imshow("Realtime Control", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            await asyncio.sleep(0)

    cap.release()
    cv2.destroyAllWindows()

asyncio.run(main())