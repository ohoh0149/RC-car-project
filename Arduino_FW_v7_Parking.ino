#include <Car_Library.h>

#define RIGHTSIDE     105
#define LEFTSIDE      145

int motorS1 = 2;          // IN1 - 조향
int motorS2 = 3;          // IN2 - 조향
int motorR1 = 4;          // IN1 - 모터
int motorR2 = 5;          // IN2 - 모터
int motorL1 = 6;          // IN1 - 모터
int motorL2 = 7;          // IN2 - 모터
int analogPin = A5;         // 가변저항 output pin

int epoch = 0;

int serial_cmd;                   // 시리얼 통신으로 받은 값 (안씀)
int feedback;
int steering_speed = 80;
int driving_speed = 50;
int MIDDLESIDE;

byte cmd;                         // 파이썬으로부터 받은 cmd (단위: byte)

int fix_value = 2000;

void setup() {
    Serial.begin(9600);

    // pin 초기화
    pinMode(motorS1, OUTPUT);
    pinMode(motorS2, OUTPUT);
    pinMode(motorR1, OUTPUT);
    pinMode(motorR2, OUTPUT);
    pinMode(motorL1, OUTPUT);
    pinMode(motorL2, OUTPUT);

    // 6. 바퀴 정렬
    while (1) {
        // 저항값 가져옴
        feedback = potentiometer_Read(analogPin);

        // 조향 (cmd = 5인 것처럼)
        if (feedback < (150 - (5 * 5)) ) {
            motor_forward(motorS1, motorS2, steering_speed);  // 좌로 조향
        }
        else if (feedback > (150 - (5 * 5)) ) {
            motor_backward(motorS1, motorS2, steering_speed); // 우로 조향
        }
        else {
            motor_hold(motorS1, motorS2);
            break;
        }
    }

    // 시작하자마자 전진
    //motor_forward(motorL1,motorL2,driving_speed);
    //motor_forward(motorR1,motorR2,driving_speed);

    // 초기 cmd 설정
    cmd = 5;
}

void hardcoding_rotate() {
    // 1. 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_value);

    // // 2. 뒤로 약간 후진
    // motor_backward(motorR1, motorR2, driving_speed);
    // motor_backward(motorL1, motorL2, driving_speed);
    //delay(500);
    // 2.5 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_value);


    // 3. 왼쪽 끝까지 핸들 돌리기
    motor_forward(motorS1, motorS2, steering_speed);
    delay(fix_value * 2);

    // 4. 45도 맞을때까지 전진
    motor_forward(motorR1, motorR2, driving_speed);
    motor_forward(motorL1, motorL2, driving_speed);
    delay(8000);

    // 5. 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_value);

    // 6. 오른쪽 끝까지 핸들 돌리기
    motor_backward(motorS1, motorS2, steering_speed);
    delay(fix_value * 2);

    // 7. 90도 맞을때까지 후진
    motor_backward(motorR1, motorR2, driving_speed);
    motor_backward(motorL1, motorL2, driving_speed);
    delay(9000);

    // 8. 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_value);

    
    Serial.println("OK");

    int angle=0;
    while(1){
      
      if(Serial.available()){
        angle=Serial.read();
        delay(10);

        if (angle != 0) break;
      }
    }

    // 전진, 후진 결정
    if (angle > 181) {
      motor_forward(motorR1, motorR2, driving_speed);
      motor_forward(motorL1, motorL2, driving_speed);
      delay((angle-180)*100);
    }
    else if(angle<179) {
      motor_backward(motorR1, motorR2, driving_speed);
      motor_backward(motorL1, motorL2, driving_speed);
      delay((180-angle)*100);
    }
    motor_hold(motorR1, motorR2);
    motor_hold(motorL1, motorL2);




    


    // 9. 바퀴 정렬
    while (1) {
        // 저항값 가져옴
        feedback = potentiometer_Read(analogPin);

        // 조향 (cmd = 5인 것처럼)
        if (feedback < (150 - (5 * 5)) ) {
            motor_forward(motorS1, motorS2, steering_speed);  // 좌로 조향
        }
        else if (feedback > (150 - (5 * 5)) ) {
            motor_backward(motorS1, motorS2, steering_speed); // 우로 조향
        }
        else {
            motor_hold(motorS1, motorS2);
            break;
        }
    }

    

    
    // 2. 뒤로 약간 후진
    motor_backward(motorR1, motorR2, driving_speed);
    motor_backward(motorL1, motorL2, driving_speed);



}

void hardcoding_exit() {
    // 1. 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_value*2);

    // 1.5 바퀴 정렬
    while (1) {
        // 저항값 가져옴
        feedback = potentiometer_Read(analogPin);

        // 조향 (cmd = 5인 것처럼)
        if (feedback < (150 - (5 * 5)) ) {
            motor_forward(motorS1, motorS2, steering_speed);  // 좌로 조향
        }
        else if (feedback > (150 - (5 * 5)) ) {
            motor_backward(motorS1, motorS2, steering_speed); // 우로 조향
        }
        else {
            motor_hold(motorS1, motorS2);
            break;
        }
    }

    // 2. 앞으로 약간 가기
    motor_forward(motorR1, motorR2, driving_speed);
    motor_forward(motorL1, motorL2, driving_speed);
    delay(5000);

    // 3. 오른쪽 끝까지 핸들 돌리기
    motor_backward(motorS1, motorS2, steering_speed);
    delay(fix_value * 2);

    // 4. 90도 맞을때까지 전진
    motor_forward(motorR1, motorR2, driving_speed);
    motor_forward(motorL1, motorL2, driving_speed);
    delay(13500);

    // 5. 정지
    motor_forward(motorR1, motorR2, 0);
    motor_forward(motorL1, motorL2, 0);
    delay(fix_value);

    // 6. 바퀴 정렬
    while (1) {
        // 저항값 가져옴
        feedback = potentiometer_Read(analogPin);

        // 조향 (cmd = 5인 것처럼)
        if (feedback < (150 - (5 * 5)) ) {
            motor_forward(motorS1, motorS2, steering_speed);  // 좌로 조향
        }
        else if (feedback > (150 - (5 * 5)) ) {
            motor_backward(motorS1, motorS2, steering_speed); // 우로 조향
        }
        else {
            motor_hold(motorS1, motorS2);
            break;
        }
    }

    // 7. 전진
    motor_forward(motorR1, motorR2, driving_speed);
    motor_forward(motorL1, motorL2, driving_speed);

    while (1) {
      if (Serial.available()) {
            // 수신
            cmd = Serial.read();
            delay(10);

            if (cmd == 12) {
                 motor_forward(motorR1, motorR2, 0);
                 motor_forward(motorL1, motorL2, 0);
            }
        }
      
    }
    delay(20000); // 무한히 둬도 됨
}

void loop() {
    while (1) {
        if (Serial.available()) {
            // 수신
            cmd = Serial.read();
            delay(10);

            if (cmd == 1) {
                // 하드코딩: 90도 돌리기
                hardcoding_rotate();

                // 발신
                Serial.println("OK");
                break;
            }
            else if (cmd == 13) {
                 motor_forward(motorR1, motorR2, driving_speed);
                 motor_forward(motorL1, motorL2, driving_speed);

                 // 발신
                Serial.println("OK");
                cmd = 5;
            }
        }
      // // 6. 바퀴 정렬
      // while (1) {
      //     // 저항값 가져옴
      //     feedback = potentiometer_Read(analogPin);

      //     // 조향 (cmd = 5인 것처럼)
      //     if (feedback < (150 - (5 * 5)) ) {
      //         motor_forward(motorS1, motorS2, steering_speed);  // 좌로 조향
      //     }
      //     else if (feedback > (150 - (5 * 5)) ) {
      //         motor_backward(motorS1, motorS2, steering_speed); // 우로 조향
      //     }
      //     else {
      //         motor_hold(motorS1, motorS2);
      //         break;
      //     }
      // }


    }

    // 주차시도 (후진) - 속도 느리게 해야 인식 편할듯?
    motor_backward(motorR1, motorR2, 50);
    motor_backward(motorL1, motorL2, 50);

    while (1) {
        if (Serial.available()) {
            // 수신
            cmd = Serial.read();
            delay(10);

            if (cmd == 2) {
                // 하드코딩: 탈출
                hardcoding_exit();

                // 발신
                Serial.println("OK");
            }
        }
    }

    delay(1000000);
}

