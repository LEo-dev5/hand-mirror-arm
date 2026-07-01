import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import asyncio
import websockets
import json
from wrist_tracker import get_wrist_servo_angles
from collections import deque
from angle_calculator import calculate_angle, map_range

ESP32_URI = "ws://192.168.219.106:8080"

# ── 이동 평균 필터 설정 ──
WINDOW_SIZE = 5     # 평균 용 개수
base_history = deque(maxlen=WINDOW_SIZE)
shoulder_history = deque(maxlen=WINDOW_SIZE)
gripper_history = deque(maxlen=WINDOW_SIZE)
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

            # 손 인식 -> 각도계산 -> 전송 | 이동 평균 값 전송으로 떨림 최소화
            if latest_result and latest_result.hand_landmarks:
                hand_landmarks = latest_result.hand_landmarks[0]
                angle_x, angle_y = get_wrist_servo_angles(hand_landmarks)

                # base (좌우, angle_x)
                base_history.append(angle_x)
                base_avg = sum(base_history) / len(base_history)

                # shoulder (상하, angle_y)
                shoulder_history.append(angle_y)
                shoulder_avg = sum(shoulder_history) / len(shoulder_history)

                # gripper (손가락 굽힘 → 그리퍼 각도)
                world_landmarks = latest_result.hand_world_landmarks[0]
                p5 = world_landmarks[5]
                a = (p5.x, p5.y, p5.z)
                p6 = world_landmarks[6]
                b = (p6.x, p6.y, p6.z)
                p7 = world_landmarks[7]
                c = (p7.x, p7.y, p7.z)

                finger_angle = calculate_angle(a, b, c)
                gripper_history.append(finger_angle)
                gripper_avg = sum(gripper_history) / len(gripper_history)
                gripper_angle = map_range(gripper_avg, 85, 172, 180, 0)

                # 세 관절 다 JSON에 담아 전송
                message = json.dumps({
                    "base": int(base_avg),
                    "shoulder": int(shoulder_avg),
                    "gripper_l": int(gripper_angle),
                    "gripper_r": int(gripper_angle)
                })
                await websocket.send(message)

            # 화면 표시
            cv2.imshow("Realtime Control", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            await asyncio.sleep(0)

    cap.release()
    cv2.destroyAllWindows()

asyncio.run(main())