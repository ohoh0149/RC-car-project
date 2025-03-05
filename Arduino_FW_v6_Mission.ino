// 아두이노 장애물 회피 + 신호등 코드

#include <Car_Library.h>

#define RIGHTSIDE     105
#define MIDDLESIDE    125
#define LEFTSIDE      145

int motorS1 = 2;          // IN1 - 조향
int motorS2 = 3;          // IN2 - 조향
int motorR1 = 4;          // IN1 - 모터
int motorR2 = 5;          // IN2 - 모터
int motorL1 = 6;          // IN1 - 모터
int motorL2 = 7;          // IN2 - 모터
int analogPin = A5;         // 가변저항 output pin

int ECHO = 8; // 초음파 1
int TRIG = 9; // 초음파 2

int feedback; // 가져온 저항값
int steering_speed = 150; // 조향 속도
int driving_speed = 100; // 미션주행 속도

byte cmd; // 파이썬으로부터 받은 cmd (단위: byte)

long ultra_distance; // 초음파 거리
int ultra_flag = 0; // 초음파 미션 수행했는지 여부

void setup() {
    // 조향, 모터 초기화
    Serial.begin(9600);
    pinMode(motorS1, OUTPUT);
    pinMode(motorS2, OUTPUT);
    pinMode(motorR1, OUTPUT);
    pinMode(motorR2, OUTPUT);
    pinMode(motorL1, OUTPUT);
    pinMode(motorL2, OUTPUT);

    // 초음파 초기화
    pinMode(TRIG, OUTPUT);
    pinMode(ECHO, INPUT);

    // 시작하자마자 전진하면 안될듯
    // motor_forward(motorL1, motorL2, 100);
    // motor_forward(motorR1, motorR2, 100);

    // 초기 cmd 설정 (12: 정지)
    cmd = 12;
}

void hardcoding() {
    // 고정된 delay시간 (2초)
    int fix_val = 2000;

    // 1. 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_val * 0.5);

    // 2. 핸들 왼쪽으로 끝까지 꺾기
    motor_forward(motorS1, motorS2, steering_speed);
    delay(fix_val * 2);

    // 3. 앞으로 약간 가기
    motor_forward(motorR1, motorR2, driving_speed);
    motor_forward(motorL1, motorL2, driving_speed);

    delay(4400); // 이 값을 조절해야함

    // 4. 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_val);

    // 5. 핸들 오른쪽으로 끝까지 꺾기
    motor_backward(motorS1, motorS2, steering_speed);
    delay(fix_val * 2);

    // 6. 앞으로 약간 가기
    motor_forward(motorR1, motorR2, driving_speed);
    motor_forward(motorL1, motorL2, driving_speed);

    delay(3740); // 이 값을 조절해야함

    // 7. 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_val);

    // 8. 바퀴 가운데 정렬
    while (1) {
        // 저항값 가져옴
        feedback = potentiometer_Read(analogPin);

        // 조향 (cmd = 5인 것처럼)
        if (feedback < (150 - (5 * 5)) - 2) {
            motor_forward(motorS1, motorS2, steering_speed);  // 좌로 조향
        }
        else if (feedback > (150 - (5 * 5)) + 2) {
            motor_backward(motorS1, motorS2, steering_speed); // 우로 조향
        }
        else {
            motor_hold(motorS1, motorS2);
            break;
        }
    }

    // 9. 앞으로 n초 가기
    motor_forward(motorR1, motorR2, driving_speed);
    motor_forward(motorL1, motorL2, driving_speed);

    delay(2000); // 이 값을 조절해야함

    // 11. 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_val);

    // 12. 핸들 오른쪽으로 끝까지 꺾기
    motor_backward(motorS1, motorS2, steering_speed);
    delay(fix_val * 2);

    // 13. 앞으로 약간 가기
    motor_forward(motorR1, motorR2, driving_speed);
    motor_forward(motorL1, motorL2, driving_speed);

    delay(2000); // 이 값을 조절해야함

    // 14. 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_val);
/*
    // 15. 핸들 왼쪽으로 끝까지 꺾기
    motor_forward(motorS1, motorS2, steering_speed);
    delay(fix_val * 2);

    // 16. 앞으로 약간 가기
    motor_forward(motorR1, motorR2, driving_speed);
    motor_forward(motorL1, motorL2, driving_speed);

    delay(3400); // 이 값을 조절해야함

    // 17. 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_val);
  */

    // 18. 바퀴 가운데 정렬
    while (1) {
        // 저항값 가져옴
        feedback = potentiometer_Read(analogPin);

        // 조향 (cmd = 5인 것처럼)
        if (feedback < (150 - (5 * 5)) - 2) {
            motor_forward(motorS1, motorS2, steering_speed);  // 좌로 조향
        }
        else if (feedback > (150 - (5 * 5)) + 2) {
            motor_backward(motorS1, motorS2, steering_speed); // 우로 조향
        }
        else {
            motor_hold(motorS1, motorS2);
            break;
        }
    }
}

void loop() {
    if (Serial.available()) {
        // 수신
        cmd = Serial.read();
        delay(10);

        // 초음파 미션 한 번도 안했다면
        if (ultra_flag == 0) {
            // 초음파 보냄
            digitalWrite(TRIG, LOW); // TRIG 핀을 LOW로 설정 (안정화)
            delayMicroseconds(2);    // 2μs 동안 대기
            digitalWrite(TRIG, HIGH); // TRIG 핀을 HIGH로 설정 (초음파 신호 전송 시작)
            delayMicroseconds(10);    // 10μs 동안 신호를 유지 (초음파 펄스 전송)
            digitalWrite(TRIG, LOW);  // TRIG 핀을 다시 LOW로 설정 (신호 전송 종료)

            // 초음파 가져옴
            ultra_distance = (pulseIn(ECHO, HIGH) * 17) / 1000;

            if (ultra_distance < 100) {
                // 하드 코딩
                hardcoding();

                // 초음파 미션 끝
                ultra_flag = 1;
            }
        }

        // 가져온 cmd가 11 (횡단보도 3초간 정지)라면
        if (cmd == 11) {
            // 정지
            motor_forward(motorR1, motorR2, 0);
            motor_forward(motorL1, motorL2, 0);

            // 3초 대기
            delay(3000);
        }

        // 발신
        Serial.println("OK");
    }

    // 저항값 가져옴
    feedback = potentiometer_Read(analogPin);

    // 1부터 9 사이의 cmd일 때만 앞으로 움직임
    if (cmd >= 1 && cmd <= 9) {
        // 전진
        motor_forward(motorR1, motorR2, driving_speed);
        motor_forward(motorL1, motorL2, driving_speed);

        // 조향 (저항값에 따른 피드백)
        if (feedback < (150 - (5 * cmd)) - 2) {
            motor_forward(motorS1, motorS2, steering_speed);  // 좌로 조향
        }
        else if (feedback > (150 - (5 * cmd)) + 2) {
            motor_backward(motorS1, motorS2, steering_speed); // 우로 조향
        }
        else {
            motor_hold(motorS1, motorS2); // 조향 필요 x
        }
    }
    else if (cmd == 12) { // 12를 받으면 정지
        // 정지
        motor_forward(motorR1, motorR2, 0);
        motor_forward(motorL1, motorL2, 0);
    }
}