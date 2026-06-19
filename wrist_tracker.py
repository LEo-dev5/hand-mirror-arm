def get_wrist_servo_angles(hand_landmarks):
    wrist = hand_landmarks[0]
    angle_x = wrist.x * 180
    angle_y = wrist.y * 180


    # 0~180도 사이 값만 통과 시키도록 클램핑
    angle_x = max(0, min(180, angle_x))
    angle_y = max(0, min(180, angle_y))
    return angle_x, angle_y

if __name__ == "__main__":
    # 테스트용 가짜 손목 점 (.x, .y 만 가진 가벼운 객체)
    class FakeLandmark:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    test_cases = [
        ("중앙",          (0.5, 0.5),   (90, 90)),
        ("왼쪽 위 끝",     (0.0, 0.0),   (0, 0)),
        ("오른쪽 아래 끝",  (1.0, 1.0),   (180, 180)),
        ("범위 초과",      (1.2, 1.2),   (180, 180)),
        ("음수",          (-0.1, -0.1), (0, 0)),
        ("x·y 비대칭",     (0.5, 1.0),   (90, 180)),
    ]

    for test_case in test_cases:
        name, input_xy, expected = test_case
        x, y = input_xy
        fake_wrist = FakeLandmark(x, y)
        result = get_wrist_servo_angles([fake_wrist])

        if abs(result[0] - expected[0]) < 0.0001 and abs(result[1] - expected[1]) < 0.0001:
            print(f"[{name}] 테스트 통과")
        else:
            print(f"{name} 테스트 실패 (계산각도 : {result})")