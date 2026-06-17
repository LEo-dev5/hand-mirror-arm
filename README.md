# Hand Mirror Arm

손 동작을 인식해서 6DOF 로봇 팔이 따라 움직이는(미러링) 프로젝트입니다.

## 프로젝트 개요

- **목표**: 카메라로 사람 손동작을 인식하고, 그 동작을 6DOF 로봇 팔 + 2핑거 그리퍼로 실시간 재현
- **비전 처리**: MediaPipe HandLandmarker (Tasks API)
- **제어보드**: ESP32 (서보 PWM 제어)
- **메인 컴퓨터**: Raspberry Pi 5 (8GB)
- **서보모터**: MG996R × 8개 (관절 7개 + 그리퍼 1개)
- **3D 프린팅**: Bambu Lab A1 (PETG)

## 개발 단계 (Phase)

- **Phase 1**: 하드웨어 검증 + 직접 제어 (Python, ROS2 미사용)
  - [x] 1-1. 손 인식 (MediaPipe)
  - [ ] 1-2. 손 랜드마크 → 관절 각도 변환
  - [ ] 1-3. Pi5 ↔ ESP32 Wi-Fi 통신
  - [ ] 1-4. ESP32 서보 제어
  - [ ] 1-5. 6DOF 팔 기구 설계 (Fusion 360)
  - [ ] 1-6. 전체 통합
- **Phase 2**: ROS2 통합 (URDF + MoveIt2)

## 환경 설정

### 요구사항

- Python 3.11.x (MediaPipe가 3.13+ 미지원)
- pyenv 권장

### 설치

```bash
pyenv install 3.11.9
pyenv local 3.11.9
python -m venv venv
source venv/bin/activate
pip install mediapipe opencv-python
```

### 모델 파일 다운로드

`hand_landmarker.task` 모델 파일은 용량 문제로 Git에 포함하지 않았습니다. 아래 명령어로 직접 다운로드해주세요.

```bash
curl -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

## 실행

```bash
source venv/bin/activate
python hand_landmark_test.py
```

`q` 키를 누르면 종료됩니다.

## 참고

- MediaPipe Tasks API (LIVE_STREAM 모드) 사용 — 구식 `mp.solutions` API는 최근 버전에서 호환성 문제가 있어 사용하지 않음
