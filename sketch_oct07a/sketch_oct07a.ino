/*
   ARM/SAP Singapore Management University Project
   Tutorial code for lecture and learning labs

   Sample project: OplÃ  smart farming irrigation system

   Collects sensor data and submits it to the SAP IoT service

*/

#include "arduino_secrets.h"
#include <ArduinoBearSSL.h>         // For SSL/TLS protocol
#include <Arduino_JSON.h>           // For JSON
#include <ArduinoMqttClient.h>      // For MQTT
#include <WiFiNINA.h>               // For Server-Client connections
#include <Arduino_MKRIoTCarrier.h>  // For controlling components on board

MKRIoTCarrier carrier; 

// Enter your sensitive data in arduino_secrets.h
const char  ssid[]       = SECRET_SSID;
const char  pass[]       = SECRET_PASS;
const char  broker[]     = SECRET_BROKER;
const char* certificate  = SECRET_CERTIFICATE;
const char* key          = SECRET_KEY;

WiFiClient    wifiClient;            // Used for the TCP socket connection
BearSSLClient sslClient(wifiClient); // Used for SSL/TLS connection
MqttClient    mqttClient(sslClient); // Used to connect and communicate with MQTT broker

unsigned long lastMillis = 0;

// Sensor variables
int ambientTemperature;
int ambientPressure;
int ambientHumidity;
int soilMoisture;
int gyroscopeX;
int gyroscopeY;
int gyroscopeZ;
int red, green, blue, ambientLight;
int current_index;
int active_wave;
int moistPin = A5;                   // Analog input from carrier board
int pir = A6;
int pirState = 0;

void setup() {
  Serial.begin(115200);
  //  while (!Serial); // wait for serial monitor to open

  // Set a callback to get the current time
  // used to validate the servers certificate
  ArduinoBearSSL.onGetTime(getTime);

  // Set the private key and the accompanying public 
  // certificate to use for client authencation 
  sslClient.setKey(key, certificate);

  // Optional, set the client id used for MQTT,
  // each device that is connected to the broker
  // must have a unique client id. The MQTTClient will generate
  // a client id for you based  on the millis() value if not set
  // Team specific
  mqttClient.setId("team07-device");

  // Set the message callback, this function is
  // called when the MQTTClient receives a message
  mqttClient.onMessage(onMessageReceived);

  // Initialize the carrier board of the OplÃ  kit
  CARRIER_CASE = false;
  carrier.begin();
  carrier.display.setRotation(0);
  pinMode(A6, INPUT);
  delay(1500);
}

void loop() {

  
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (!mqttClient.connected()) {
    // MQTT client is disconnected, connect
    connectMQTT();
  }

  // poll for new MQTT messages and send keep alives
  mqttClient.poll();

  // publish a message roughly every 5 seconds.
  if (millis() - lastMillis > 5000) {
    lastMillis = millis();

    collectSensorData();
    publishMessage();
    updateScreen();
    updateLED();
    
  }


}

unsigned long getTime() {
  // get the current time from the WiFi module
  return WiFi.getTime();
}

void connectWiFi() {
  Serial.print("Attempting to connect to SSID: ");
  Serial.print(ssid);
  Serial.print(" ");

  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    // failed, retry
    Serial.print(".");
    delay(5000);
  }
  Serial.println();

  Serial.println("You're connected to the network");
  Serial.println();
}

void connectMQTT() {
  Serial.print("Attempting to connect to MQTT broker: ");
  Serial.println(broker);

  while (!mqttClient.connect(broker, 8883)) {
    // failed, retry
    delay(5000);
  }

  Serial.println("You're connected to the MQTT broker");

  // subscribe to a topic
  // Pass Alternate ID
  // Team specific
  mqttClient.subscribe("ack/team07-device");
  mqttClient.subscribe("commands/team07-device");
}

void collectSensorData() {
  // Get sensor data -----------
  // read temperature, humidity and light
  int raw_moisture = analogRead(moistPin);
  carrier.Light.readColor(red, green, blue, ambientLight);

  float gX, gY, gZ;
  carrier.IMUmodule.readGyroscope(gX, gY, gZ);
  gyroscopeX = gX;
  gyroscopeY = gY;
  gyroscopeZ = gZ;
  Serial.println("Collecting sensor data: ");
  ambientTemperature = carrier.Env.readTemperature();
  ambientHumidity = carrier.Env.readHumidity();
  ambientPressure = carrier.Pressure.readPressure();
  soilMoisture = map(raw_moisture, 0, 1023, 100, 0);
  pirState = digitalRead(pir);
}

void publishMessage() {

  JSONVar message;

  // Team specific
  message["sensorAlternateId"] = "team07_sensor";
  message["capabilityAlternateId"] = "TEAM07_CAPABILITY";

  JSONVar payload;
  payload["ambientTemperature"] = ambientTemperature;
  payload["ambientHumidity"] = ambientHumidity;
  payload["ambientLight"] = ambientLight;
  payload["ambientPressure"] = ambientPressure;
  payload["soilMoisture"] = soilMoisture;
  payload["gyroscopeX"] = gyroscopeX;
  payload["gyroscopeY"] = gyroscopeY;
  payload["gyroscopeZ"] = gyroscopeZ;
  //payload["accelerationX"] = 5;
  //cannot have more than 8  payloads
  message["measures"][0] = payload;

  Serial.println("Publishing message: ");
  Serial.println(message);

  // send message, the Print interface can be used to set the message contents
  // Pass the alternate id
  // Team specific
  mqttClient.beginMessage("measures/team07-device");
  mqttClient.print(message);
  mqttClient.endMessage();

}

void onMessageReceived(int messageSize) {
  // we received a message, print out the topic and contents
  String payload;
  Serial.print("Received a message with topic '");
  Serial.print(mqttClient.messageTopic());
  Serial.print("', length ");
  Serial.print(messageSize);
  Serial.println(" bytes:");

  // use the Stream interface to print the contents
  while (mqttClient.available()) {
    payload += (char)mqttClient.read();     
  }

  Serial.println(payload);
  if (payload.indexOf("waveStatus") > -1) {
    if (payload.indexOf("activate") > -1) {
      active_wave = 1;
    } else if (payload.indexOf("close") > -1) {
      active_wave = 0;

    }
  }

  carrier.leds.show();                     // Refresh strip
  Serial.println();
}


//Update displayed Info
void updateScreen() {

  String dispMsg1 = "Temp: ";
  String dispMsg2 = "RelH: ";
  String dispMsg3 = "Soil: ";

  dispMsg1 = dispMsg1 + ambientTemperature;
  dispMsg2 = dispMsg2 + ambientHumidity;
  dispMsg3 = dispMsg3 + soilMoisture;

  carrier.display.fillScreen(ST77XX_BLACK);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(2);
  carrier.display.setCursor(70, 20);
  carrier.display.print("SMU IoT");
  carrier.display.setCursor(40, 50);
  carrier.display.print(dispMsg1);
  carrier.display.setCursor(40, 90);
  carrier.display.print(dispMsg2);
  carrier.display.setCursor(40, 130);
  carrier.display.print(dispMsg3);
}

void updateLED(){
  if(active_wave == 1){
    if(current_index%2==0){
      carrier.leds.setPixelColor(0, 0, 255, 0);
      carrier.leds.setPixelColor(1, 0, 255, 0);
      carrier.leds.setPixelColor(2, 0, 255, 0);
      carrier.leds.setPixelColor(3, 0, 255, 0);
      carrier.leds.setPixelColor(4, 0, 255, 0);    
    }
    else{
      carrier.leds.setPixelColor(0, 0, 0, 0);
      carrier.leds.setPixelColor(1, 0, 0, 0);
      carrier.leds.setPixelColor(2, 0, 0, 0);
      carrier.leds.setPixelColor(3, 0, 0, 0);
      carrier.leds.setPixelColor(4, 0, 0, 0);       
    }
  }
  else{
      carrier.leds.setPixelColor(0, 0, 0, 0);
      carrier.leds.setPixelColor(1, 0, 0, 0);
      carrier.leds.setPixelColor(2, 0, 0, 0);
      carrier.leds.setPixelColor(3, 0, 0, 0);
      carrier.leds.setPixelColor(4, 0, 0, 0);      
  }
  carrier.leds.show();
  current_index = current_index + 1;  
}
