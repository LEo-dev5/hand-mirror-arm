#include <WiFi.h>       
#include "secrets.h"    

void setup() {
  Serial.begin(115200);
  delay(1000);   

  // Wi-Fi 연결 시작
  Serial.println();
  Serial.print("Wi-Fi 연결 시도: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);   // 연결 시도

  // 연결될 때까지 기다리기
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("."); 
  }

  // 연결 성공
  Serial.println();
  Serial.println("Wi-Fi 연결 성공!");
  Serial.print("ESP32의 IP 주소: ");
  Serial.println(WiFi.localIP()); 
}

void loop() {

}