#include <Wire.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include "MPU6050_6Axis_MotionApps20.h"

// WiFi 설정
#define WIFI_SSID "DoJae Woo"
#define WIFI_PASSWORD "dddddddd"

// TCP 서버 설정
#define SERVER_IP "172.20.10.3"  // 서버의 IP 주소
#define SERVER_PORT 12000           // 서버의 포트 번호

// PCA9548A I2C 주소
#define TCA9548A_ADDRESS 0x70

// MPU6050 인스턴스 생성
MPU6050 mpu1;
MPU6050 mpu2;

// 센서 데이터를 저장할 변수
uint8_t fifoBuffer[64];
Quaternion q1, q2;

// WiFi 클라이언트
WiFiClient client;

// PCA9548A에서 채널을 선택하는 함수
void selectChannel(uint8_t channel) {
  if (channel > 7) return;
  Wire.beginTransmission(TCA9548A_ADDRESS);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

// MPU6050 초기화 함수
void initializeMPU(MPU6050 &mpu, uint8_t channel) {
  selectChannel(channel);
  mpu.initialize();
  if (mpu.dmpInitialize() == 0) {
    mpu.CalibrateAccel(6);
    mpu.CalibrateGyro(6);
    mpu.setDMPEnabled(true);
    Serial.print("MPU6050 ");
    Serial.print(channel + 1);
    Serial.println(" 연결 및 초기화 완료!");
  } else {
    Serial.print("MPU6050 ");
    Serial.print(channel + 1);
    Serial.println(" 초기화 실패");
    while (1);
  }
}

void setup() {
  Wire.begin();
  Serial.begin(115200);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("WiFi 연결 중...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println(" 연결 완료");

  // 채널 0 및 1의 MPU6050 초기화
  initializeMPU(mpu1, 0);
  initializeMPU(mpu2, 1);
}

void loop() {
  if (!client.connected()) {
    Serial.println("서버에 연결 시도 중...");
    while (!client.connect(SERVER_IP, SERVER_PORT)) {
      Serial.println("서버에 연결할 수 없습니다. 재시도 중...");
      delay(1000); // 1초마다 재시도
    }
    Serial.println("서버에 연결됨.");
  }

  char buffer1[64];
  char buffer2[64];
  char combinedBuffer[256];

  // 채널 0의 MPU6050에서 데이터 읽기
  selectChannel(0);
  if (mpu1.dmpGetCurrentFIFOPacket(fifoBuffer)) {
    mpu1.dmpGetQuaternion(&q1, fifoBuffer);
    sprintf(buffer1, "w:%f, x:%f, y:%f, z:%f", q1.w, q1.x, q1.y, q1.z);
  }

  // 채널 1의 MPU6050에서 데이터 읽기
  selectChannel(1);
  if (mpu2.dmpGetCurrentFIFOPacket(fifoBuffer)) {
    mpu2.dmpGetQuaternion(&q2, fifoBuffer);
    sprintf(buffer2, "w:%f, x:%f, y:%f, z:%f", q2.w, q2.x, q2.y, q2.z);
  }

  // 두 센서의 데이터를 하나의 문자열로 결합
  sprintf(combinedBuffer, "{\"mpu1\": \"%s\", \"mpu2\": \"%s\"}", buffer1, buffer2);

  // 서버로 데이터 전송
  if (client.connected()) {
    client.println(combinedBuffer);
  } else {
    Serial.println("서버 연결이 끊어졌습니다. 재시도 중...");
    while (!client.connect(SERVER_IP, SERVER_PORT)) {
      Serial.println("서버에 연결할 수 없습니다. 재시도 중...");
      delay(10); // 1초마다 재시도
    }
    Serial.println("서버에 연결됨.");
  }

  delay(10); // 1초마다 데이터 전송
}