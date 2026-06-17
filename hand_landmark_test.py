import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

# ── 1. 결과를 저장할 전역 변수 ─────────────────────────────────
# 콜백 함수는 별도 스레드에서 호출되기 때문에,
# 메인 루프와 결과를 공유하려면 바깥에 변수를 둬야 해요.
latest_result = None

def save_result(result, output_image, timestamp_ms):
    """콜백 함수: MediaPipe가 분석을 끝내면 자동으로 이 함수를 호출해요."""
    global latest_result
    latest_result = result

# ── 2. HandLandmarker 옵션 설정 ──────────────────────────────
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,  # 실시간 스트림 모드
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    result_callback=save_result  # 결과가 나오면 save_result를 호출
)

detector = vision.HandLandmarker.create_from_options(options)

# ── 3. 웹캠 열기 ─────────────────────────────────────────────
cap = cv2.VideoCapture(0)

start_time = time.time()   # ← 이 줄 추가
# ── 4. 21개 랜드마크 연결 정보 (손가락 뼈대 그리기용) ──────────
# (시작점 인덱스, 끝점 인덱스) 쌍의 목록이에요.
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # 엄지
    (0, 5), (5, 6), (6, 7), (7, 8),        # 검지
    (0, 9), (9, 10), (10, 11), (11, 12),   # 중지
    (0, 13), (13, 14), (14, 15), (15, 16), # 약지
    (0, 17), (17, 18), (18, 19), (19, 20), # 새끼
    (5, 9), (9, 13), (13, 17)              # 손바닥 가로 연결
]

# ── 5. 메인 루프 ─────────────────────────────────────────────
while True:
    ret, frame = cap.read()
    if not ret:
        print("웹캠을 찾을 수 없어요.")
        break

    # 5-1. BGR → RGB 변환 후 MediaPipe Image 객체로 만들기
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    # 5-2. 타임스탬프 계산 (밀리초 단위, LIVE_STREAM 모드는 필수)
    timestamp_ms = int((time.time() - start_time) * 1000)

    # 5-3. 비동기 분석 요청 (결과는 save_result 콜백으로 옴)
    detector.detect_async(mp_image, timestamp_ms)

    # 5-4. 가장 최근 결과로 랜드마크 그리기
    if latest_result and latest_result.hand_landmarks:
        h, w, _ = frame.shape
        for hand_landmarks in latest_result.hand_landmarks:
            # 점 그리기
            for lm in hand_landmarks:
                x, y = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

            # 연결선 그리기
            for connection in HAND_CONNECTIONS:
                start_idx, end_idx = connection
                x1 = int(hand_landmarks[start_idx].x * w)
                y1 = int(hand_landmarks[start_idx].y * h)
                x2 = int(hand_landmarks[end_idx].x * w)
                y2 = int(hand_landmarks[end_idx].y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)

    # 5-5. 화면 출력
    cv2.imshow("Hand Landmark Test", frame)

    # 5-6. q 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ── 6. 자원 해제 ─────────────────────────────────────────────
cap.release()
cv2.destroyAllWindows()
detector.close()