import math

def calculate_angle(a, b, c):
    # a, b, c는 각각 (x, y, z) 좌표 튜플
    # 반환 : 도
    ba_x = a[0] - b[0]
    ba_y = a[1] - b[1]
    ba_z = a[2] - b[2]

    bc_x = c[0] - b[0]
    bc_y = c[1] - b[1]
    bc_z = c[2] - b[2]

    # 내적
    dot_product = (ba_x * bc_x) + (ba_y * bc_y) + (ba_z * bc_z)

    # 벡터의 길이
    len_ba = math.sqrt(ba_x ** 2 + ba_y ** 2 + ba_z ** 2)
    len_bc = math.sqrt(bc_x ** 2 + bc_y ** 2 + bc_z ** 2)

    # 길이 사전검사 (0으로 나누기 방지)
    if len_ba == 0 or len_bc == 0:
        return 0.0

    # cos(theta)
    cos_theta = dot_product / (len_ba * len_bc)
    # 클램핑 (부동소수점 오차 정의역 벗어나는 것 방지)
    cos_theta = max(-1.0, min(1.0, cos_theta))

    # 라디안 -> 도 변환
    angle_radian = math.acos(cos_theta)
    angle_degree = math.degrees(angle_radian)

    return angle_degree

def map_range(value, in_min, in_max, out_min, out_max):
    """
    한 범위의 값을 다른 범위로 비례 변환한다. 결과는 out범위 안으로 클램핑된다.
    """
    result = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    lower = min(out_min, out_max)   # 둘 중 작은 값
    upper = max(out_min, out_max)   # 둘 중 큰 값
    result = max(lower, min(upper, result))
    return result


# 테스트
if __name__ == "__main__":
    test_cases = [
        ("90도", (1, 0, 0), (0, 0, 0), (0, 1, 0), 90),
        ("180도", (0, -1, 0), (0, 0, 0), (0, 1, 0), 180),
    ]

    for test_case in test_cases:
        # 튜플의 값을 위치 순서대로 각 변수에 할당
        name, a, b, c, expected = test_case
        result = calculate_angle(a, b, c)
        if abs(result - expected) < 0.0001:
            print(f"[{name}] 테스트 통과")
        else:
            print(f"{name} 테스트 실패 (계산각도 : {result})")
    
