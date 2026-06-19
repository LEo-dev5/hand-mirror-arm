#include <WiFi.h>          
#include <ArduinoWebsockets.h>   
#include "secrets.h"              

using namespace websockets;       

WebsocketsServer server;          
WebsocketsClient client;     
bool hasClient = false;      

// ── 메시지가 오면 실행될 콜백 함수 ──
void onMessage(WebsocketsMessage message) {
  Serial.print("받은 메시지: ");
  Serial.println(message.data());
}


void setup() {
  Serial.begin(115200);
  delay(1000);

  // Wi-Fi 연결 
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

  // WebSocket 서버 시작
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