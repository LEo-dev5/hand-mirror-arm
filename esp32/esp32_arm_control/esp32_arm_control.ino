#include <WiFi.h>
#include <ArduinoWebsockets.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ArduinoJson.h>
#include "secrets.h"

using namespace websockets;

WebsocketsServer server;
WebsocketsClient client;
bool hasClient = false;
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// 관절 이름 ↔ 채널 번호 목록
struct Joint {
  const char* key;
  uint8_t channel;
};

Joint joints[] = {
  {"base", 0},
  {"shoulder", 1},
  {"elbow", 2},
  {"wrist_pitch", 3},
  {"wrist_roll", 4},
  {"gripper_l", 5},
  {"gripper_r", 6}
};

// ── 서보 설정 (1-4에서 찾은 값) ──
#define SERVOMIN 170
#define SERVOMAX 520
#define SERVO_FREQ 50

// ── 각도 → 서보 (1-4에서 만든 함수) ──
void setServoAngle(uint8_t channel, int angle) {
  int pulse = map(angle, 0, 180, SERVOMIN, SERVOMAX);
  pwm.setPWM(channel, 0, pulse);
}

void onMessage(WebsocketsMessage message) {
  String payload = message.data();
  Serial.print("받은 메시지: ");
  Serial.println(payload);

  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, payload);
  if (error) {
    Serial.print("JSON 파싱 실패: ");
    Serial.println(error.c_str());
    return;
  }

  // 7개 관절 중, JSON에 있는 것만 골라서 서보 구동
  for (int i = 0; i < 7; i++) {
    if (doc[joints[i].key].is<int>()) {
      int angle = doc[joints[i].key];
      setServoAngle(joints[i].channel, angle);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // ── Wi-Fi (1-3 검증 코드) ──
  Serial.print("Wi-Fi 연결 시도: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Wi-Fi 연결 성공!");
  Serial.print("ESP32의 IP 주소: ");
  Serial.println(WiFi.localIP());

  // ── PCA9685 (1-4 검증 코드) ──
  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(SERVO_FREQ);
  delay(10);

  // ── WebSocket 서버 (1-3 검증 코드) ──
  server.listen(8080);
  Serial.println("WebSocket 서버 시작 (포트 8080)");
}

void loop() {
  if (!hasClient && server.poll()) {
    client = server.accept();
    client.onMessage(onMessage);
    hasClient = true;
    Serial.println("클라이언트 연결됨!");
  }
  if (hasClient) {
    client.poll();
    if (!client.available()) {
      hasClient = false;
      Serial.println("클라이언트 연결 끊김");
    }
  }
}