/*
 * --------------------------------------
 * Typical pin layout used:
 * --------------------------------------
 *             MFRC522
 *             Reader/PCD   ESP32
 * Signal      Pin          Pin
 * --------------------------------------
 * RST/Reset   RST          13
 * SPI SS      SDA(SS)      5
 * SPI MOSI    MOSI         23
 * SPI MISO    MISO         19
 * SPI SCK     SCK          18
 * --------------------------------------
 */


// MQTT COMMUNICATION LIBRARIES
#include <PubSubClient.h>
#include <WiFi.h>
// RFID READER LIBRARIES
#include <SPI.h>
#include <MFRC522.h>
// SSD1306 OLED display LIBRARIES
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ===========================
// Enter your WiFi credentials
// ===========================
// const char* ssid = "TIM-95565169";
// const char* password = "1oywWPQNkCUGvC4BMHAMtUK4";
const char* ssid = "iPhone Pro di Mattia";
const char* password = "agvzzzzzz";
// const char* ssid = "Redmi Note 11 Pro";
// const char* password = "Alessandro2001";
// const char* ssid = "Tim-wifi";
// const char* password = "Pippo2015+";

// ===========================
// Enter your broker credentials
// ===========================
const char* broker_ip = "broker.hivemq.com";
const int broker_port = 1883;

WiFiClient wifi_client;
PubSubClient mqtt_client(wifi_client);

// ===========================
// RFID configuration
// ===========================
#define SS_PIN 5
#define RST_PIN 13
MFRC522 rfid(SS_PIN, RST_PIN);  // Instance of the class
MFRC522::MIFARE_Key key;
char nuidPICC[4];  // Init array that will store new NUID

// ===========================
// SSD1306 OLED display config
// ===========================
#define SCREEN_WIDTH 128  // OLED display width, in pixels
#define SCREEN_HEIGHT 64  // OLED display height, in pixels
#define SCL 22
#define SDA 21
// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET -1  // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ===========================
// variables to prevent unwanted sensor readings
// ===========================
String read_RFID = String("");
unsigned long last_time;
#define DELAY 2000

// ===========================
// MQTT topics
// ===========================
const char* mqtt_topic_pub_ip_refs = "BertacchiniPanseraRistori/ip_refs/rfid/A0001";
const char* mqtt_topic_pub_data = "BertacchiniPanseraRistori/data/rfid/A0001";
const char* mqtt_topic_sub = "BertacchiniPanseraRistori/data/future/A0001";

void setup() {
  Serial.begin(115200);

  /* Initialize RFID */
  SPI.begin();      // Init SPI bus
  rfid.PCD_Init();  // Init MFRC522

  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  /* Initialize MQTT publisher */
  Serial.setDebugOutput(true);
  Serial.println();


  /* Initialize MQTT subscriber callback function */
  mqtt_client.setCallback(callback);


  // WiFiClient wifi_client;
  // PubSubClient mqtt_client(wifi_client);
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  connect();

  char ip_char_array[255];
  WiFi.localIP().toString().toCharArray(ip_char_array, 255);
  int status = mqtt_client.publish(mqtt_topic_pub_ip_refs, ip_char_array);
  print_log(status, mqtt_topic_pub_ip_refs, ip_char_array);
  last_time = millis();

  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;)
      ;  // Don't proceed, loop forever
  }
  SSD1306display(F("PROCEED"), 2);
}

void loop() {
  if (!mqtt_client.loop()) {
    String ERROR = "Client disconnected";
    Serial.println(ERROR);
    SSD1306display(ERROR, 2);
    connect();
  }

  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if (!rfid.PICC_IsNewCardPresent())
    return;

  // Verify if the NUID has been readed
  if (!rfid.PICC_ReadCardSerial())
    return;

  // Store NUID into nuidPICC array
  for (byte i = 0; i < 4; i++) {
    nuidPICC[i] = rfid.uid.uidByte[i];
  }
  // sending data to MQTT broker
  send_data(rfid.uid.uidByte, rfid.uid.size);

  // Halt PICC
  rfid.PICC_HaltA();

  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();
}

String IpAddress2String(const IPAddress& ipAddress) {
  return String(ipAddress[0]) + String(".") + String(ipAddress[1]) + String(".") + String(ipAddress[2]) + String(".") + String(ipAddress[3]);
}

/**
 * Helper routine to dump a byte array as dec values to Serial.
 */
void send_data(byte* buffer, byte bufferSize) {
  String body = "";
  for (byte i = 0; i < bufferSize; i++) {
    body += String(buffer[i], DEC);
    // body += (i + 1) < bufferSize ? String(" ") : String("");
  }

  unsigned long now = millis();
  unsigned long elapsed = now - last_time;

  if (elapsed > DELAY || read_RFID != body) {
    read_RFID = body;
    last_time = now;

    // 1) String -> char* convertion
    int str_len = body.length() + 1;
    char* body_to_char = (char*)calloc(str_len, sizeof(char));
    body.toCharArray(body_to_char, str_len);

    // 2) publishing
    int status = mqtt_client.publish(mqtt_topic_pub_data, body_to_char);

    // 3) printing log
    print_log(status, mqtt_topic_pub_data, body_to_char);
  }
}

/**
 * Prints status, topic and body of MQTT publish.
 */
void print_log(int status, const char* topic, char* body) {
  Serial.print(F("\n--------------------\nPICC type: "));
  MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
  Serial.println(rfid.PICC_GetTypeName(piccType));

  Serial.print("Ip config sent with status: ");
  Serial.println(status);
  Serial.print("Topic: ");
  Serial.println(topic);
  Serial.print("Body: ");
  Serial.println(body);
}

/**
 * Prints given String on OLED display.
 */
void SSD1306display(String str, int size) {
  display.clearDisplay();
  display.setTextSize(size);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println(str);
  display.display();
}

/**
 * Functions is called when message arrives. Prints it on Serial monitor and on OLED display.
 */
void callback(char* topic, byte* payload, unsigned int length) {
  char message[length + 1];
  memcpy(message, payload, length);
  message[length] = 0;  // Null termination.

  SSD1306display(message, 1);
  // Serial.print("Message received on topic: ");
  // Serial.println(topic);
  // Serial.print("Message: ");
  // Serial.println(message);
}

/**
 * Following function keeps trying to connect to broker, then keeps trying to subscribe to topic mqtt_topic_sub.
 * When everything's set up it ends and program can proceed.
 */
void connect() {
  // connecting to mqtt broker
  mqtt_client.setServer(broker_ip, broker_port);
  String client_id = "esp32-client-";
  client_id += String(WiFi.macAddress());

  while (!mqtt_client.connected()) {
    Serial.println("Connecting to MQTT...");

    Serial.println(client_id.c_str());
    if (mqtt_client.connect(client_id.c_str())) {
      Serial.println("Mqtt-connected");

      // Subscribtion to given topic
      Serial.print("Trying to subscribe to topic ");
      Serial.println(mqtt_topic_sub);
      while (!mqtt_client.subscribe(mqtt_topic_sub)) {
        Serial.print(".");
      }
      Serial.print("Success!");
    } else {

      Serial.print("failed with state ");
      Serial.println(mqtt_client.state());
      delay(2000);
    }
  }
}
