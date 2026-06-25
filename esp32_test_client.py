import asyncio
import websockets

ESP32_URI = "ws://192.168.219.106:8080"

async def main():
    print(f"연결 시도: {ESP32_URI}")
    async with websockets.connect(ESP32_URI) as websocket:
        print("연결 성공!")

        test_messages = [
            '{"base": 0}',
            '{"base": 90}',
            '{"base": 180}',
            '{"base": 45, "elbow": 120}',
            '{"elbow": 120}',
        ]

        for msg in test_messages:
            await websocket.send(msg)
            print(f"보낸 메세지 : {msg}")
            await asyncio.sleep(2)

        print("테스트 완료.")

asyncio.run(main())