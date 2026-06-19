import asyncio
import websockets

ESP32_URI = "ws://192.168.219.104:8080"

async def main():
    # 1. ESP32 서버에 연결
    print(f"연결 시도: {ESP32_URI}")
    async with websockets.connect(ESP32_URI) as websocket:
        print("연결 성공! 메시지를 보냅니다.")

        # 2. 테스트 메시지 보내기
        test_message = '{"base": 90, "elbow": 120}'
        await websocket.send(test_message)
        print(f"보낸 메시지: {test_message}")
        await asyncio.sleep(1)
        print("전송 완료.")

# 비동기 함수 실행
asyncio.run(main())