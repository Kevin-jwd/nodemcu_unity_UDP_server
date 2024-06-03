#include <WiFi.h>
#include <WifiUDP.h>

#define WIFI_SSID ""
#define WIFI_PASSWORD ""

WiFiUDP Udp;

const char* remote_ip = "";
int remote_port = ;

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

// setup 함수
void setup() {
  Serial.begin(115200);
  Serial.println("Setup started.");
  //wifi연결
  connectWifi();
  Serial.println("Setup completed.");
}

// 루프문
void loop() {

  // 소켓통신으로 패킷을 전송한다.
  Udp.beginPacket(remote_ip, remote_port);
  Udp.write(message, sizeof(message) - 1);
  Udp.endPacket();
  Serial.println("Message sent.");

  delay(10);
}
