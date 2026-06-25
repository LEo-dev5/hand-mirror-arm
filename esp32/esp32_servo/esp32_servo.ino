#include <Wire.h>                    
#include <Adafruit_PWMServoDriver.h>  

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN 170
#define SERVOMAX 520   
#define SERVO_FREQ 50 

void setServoAngle(uint8_t channel, int angle) {
  int pulse = map(angle, 0, 180, SERVOMIN, SERVOMAX);
  pwm.setPWM(channel, 0, pulse);
}

void setup() {
  Serial.begin(115200);
  Serial.println("PCA9685 서보 테스트 시작");

  pwm.begin();                          
  pwm.setOscillatorFrequency(27000000); 
  pwm.setPWMFreq(SERVO_FREQ);          
  delay(10);

  Serial.println("채널 0 서보 → 90도");
  setServoAngle(0, 90);
}

void loop() {
  setServoAngle(0, 0);
  delay(1000);
  setServoAngle(0, 90);
  delay(1000);
  setServoAngle(0, 180);
  delay(1000);            
}