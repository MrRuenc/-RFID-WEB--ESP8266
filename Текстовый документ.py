#include <Wire.h>
#include <PN532_I2C.h>
#include <PN532.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

PN532_I2C pn532i2c(Wire);
PN532 nfc(pn532i2c);

const int relayPin = D5;
const String allowedUID = "12 34 56 78"; // Разрешённая карта

const char* ssid = "Ваша_сеть_WiFi";
const char* password = "Ваш_пароль";

ESP8266WebServer server(80);

void handleRoot() {
  String html = "<html><body>";
  html += "<h1>Управление ПК</h1>";
  html += "<p><a href='/power_on'><button>Включить ПК</button></a></p>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void handlePowerOn() {
  digitalWrite(relayPin, HIGH);
  delay(500);
  digitalWrite(relayPin, LOW);
  server.send(200, "text/plain", "ПК включён!");
}

void setup() {
  Serial.begin(115200);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);

  // Подключение к Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Настройка WEB-сервера
  server.on("/", handleRoot);
  server.on("/power_on", handlePowerOn);
  server.begin();

  // Инициализация NFC
  nfc.begin();
  nfc.SAMConfig();
}

void loop() {
  server.handleClient(); // Обработка HTTP-запросов

  // Проверка RFID-карты
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };
  uint8_t uidLength;
  
  if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength)) {
    String currentUID = "";
    for (uint8_t i = 0; i < uidLength; i++) {
      currentUID += String(uid[i], HEX);
      if (i < uidLength - 1) currentUID += " ";
    }
    
    Serial.print("UID: "); Serial.println(currentUID);
    
    if (currentUID == allowedUID) {
      Serial.println("Доступ разрешён! Включаю ПК...");
      digitalWrite(relayPin, HIGH);
      delay(500);
      digitalWrite(relayPin, LOW);
    }
    delay(1000);
  }
}
