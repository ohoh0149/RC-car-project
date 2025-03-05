#include <Car_Library.h>

#define RIGHTSIDE     105
#define LEFTSIDE      145

int motorS1         = 2;          // IN1 - 조향
int motorS2         = 3;          // IN2 - 조향
int motorR1         = 4;          // IN1 - 모터
int motorR2         = 5;          // IN2 - 모터
int motorL1         = 6;          // IN1 - 모터
int motorL2         = 7;          // IN2 - 모터
int analogPin       = A5;         // 가변저항 output pin

int epoch = 0;

int serial_cmd;                   // 시리얼 통신으로 받은 값 (안씀)
int feedback;
int steering_speed  = 80;
int driving_speed   = 250;
int MIDDLESIDE;
byte cmd;                         // 파이썬으로부터 받은 cmd (단위: byte)

void setup() {
  Serial.begin(9600);
  pinMode(motorS1, OUTPUT);
  pinMode(motorS2, OUTPUT);
  pinMode(motorR1, OUTPUT);
  pinMode(motorR2, OUTPUT);
  pinMode(motorL1, OUTPUT);
  pinMode(motorL2, OUTPUT);

  // 시작하자마자 전진
  // motor_forward(motorL1,motorL2,150);
  // motor_forward(motorR1,motorR2,150);

  // 초기 cmd 설정
  cmd = 12;
}

void loop() {
  if (Serial.available()) {
    // 수신
    cmd = Serial.read();
    // Serial.setTimeout(200);
    delay(10);
        
    // 발신
    //Serial.write("OK");
    Serial.println("OK"); 
  }

  // 저항값 가져옴
  feedback = potentiometer_Read(analogPin);

  if (cmd >= 1 && cmd <= 9) {
    // 전진
    motor_forward(motorR1, motorR2, driving_speed);
    motor_forward(motorL1, motorL2, driving_speed);
    // 조향
    if (feedback < (150 - (5 * cmd)) - 2) {
      motor_forward(motorS1, motorS2, steering_speed);  // 좌로 조향
    }
    else if (feedback > (150 - (5 * cmd)) + 2) {
      motor_backward(motorS1, motorS2, steering_speed); // 우로 조향
    }
    else {
      motor_hold(motorS1, motorS2);
    }
  }
  else if (cmd == 12) {
    // 정지
        motor_forward(motorR1, motorR2, 0);
        motor_forward(motorL1, motorL2, 0);

  }
}