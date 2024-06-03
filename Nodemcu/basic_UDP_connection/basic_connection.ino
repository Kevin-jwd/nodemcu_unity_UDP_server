#include <WiFi.h>
#include <WifiUDP.h>

#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"

#define WIFI_SSID "DoJae Woo"
#define WIFI_PASSWORD "dddddddd"

WiFiUDP Udp;
MPU6050 mpu;

#define INTERRUPT_PIN 2
#define LED_PIN 13
bool blinkState = false;

bool dmpReady = false;
uint8_t mpuIntStatus;
uint8_t devStatus;
uint16_t packetSize;
uint16_t fifoCount;
uint8_t fifoBuffer[64];
Quaternion q;

volatile bool mpuInterrupt = false;

void dmpDataReady() {
    mpuInterrupt = true;
}

const char* remote_ip = "172.20.10.3";
int remote_port = 12000;

const uint8_t message[] = "okgoogle";

// Wifi 연결 함수
void connectWifi(){
  Serial.print("Connecting to ");
  Serial.print(WIFI_SSID);

  WiFi.disconnect(true);
  delay(1000);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP Address: ");
  Serial.print(WiFi.localIP());
  Serial.println("");
}

void mpuInitialize(){
  mpu.initialize();
    pinMode(INTERRUPT_PIN, INPUT);
    devStatus = mpu.dmpInitialize();

    if (devStatus == 0) {
        mpu.CalibrateAccel(6);
        mpu.CalibrateGyro(6);
        mpu.setDMPEnabled(true);
        attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN), dmpDataReady, RISING);
        mpuIntStatus = mpu.getIntStatus();
        dmpReady = true;
        packetSize = mpu.dmpGetFIFOPacketSize();
    } else {
        Serial.print("DMP Initialization failed (code ");
        Serial.print(devStatus);
        Serial.println(")");
    }

    pinMode(LED_PIN, OUTPUT);
}
// setup 함수
void setup() {
  Serial.begin(115200);
  Serial.println("Setup started.");
  //wifi연결
  connectWifi();
  mpuInitialize();
  Serial.println("Setup completed.");
}

// 루프문
void loop() {
   if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
        mpu.dmpGetQuaternion(&q, fifoBuffer);

        const uint8_t* jsonPayload = (const uint8_t*)("{\"q_w\":" + String(q.w) + ",\"q_x\":" + String(q.x) + ",\"q_y\":" + String(q.y) + ",\"q_z\":" + String(q.z) + "}").c_str();

        // 소켓통신으로 패킷을 전송한다.
        Udp.beginPacket(remote_ip, remote_port);
        Udp.write(jsonPayload, strlen((const char*)jsonPayload));
        Udp.endPacket();
        Serial.println("Message sent.");
        delay(100);
   }
  delay(10);
}
