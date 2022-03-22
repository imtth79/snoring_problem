// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <PubSubClient.h> // Connect and publish to the MQTT broker
#include "ESP8266WiFi.h"  // Enables the ESP8266 to connect to the local network (via WiFi)

Adafruit_MPU6050 mpu;

//Wifi information
#define ssid "FPT telecom 4264 2.4GHz"
#define password "0976914619"
#define mqtt_server "broker.hivemq.com"
const uint16_t mqtt_port = 1883; 
#define test_topic "Lying_posture"

WiFiClient wifiClient;
PubSubClient client(wifiClient); 

void setup_wifi() 
{
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) 
{
  Serial.print("Co tin nhan moi tu topic:");
  Serial.println(topic);
  for (int i = 0; i < length; i++) 
    Serial.print((char)payload[i]);
  Serial.println();
}

void reconnect() 
{
  while (!client.connected()) // Chờ tới khi kết nối
  {
    // Thực hiện kết nối với mqtt user và pass
    if (client.connect("ESP8266_id1","ESP_offline",0,0,"ESP8266_id1_offline"))  //kết nối vào broker
    {
      Serial.println("Connected:");
      client.subscribe(test_topic); //đăng kí nhận dữ liệu từ topic 
    }
    else 
    {
      Serial.print("Error:, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Đợi 5s
      delay(5000);
    }
  }
}

void setup(void) {
  Serial.begin(9600);
    while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  Serial.println("Adafruit MPU6050 test!");

  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");
  
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port); 
  client.setCallback(callback);

  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.print("Gyro range set to: ");
  switch (mpu.getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }

  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (mpu.getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }
}

unsigned long tg;
void loop() {
  
  /* Get new sensor events with the readings */
  sensors_event_t a, g, t;
  mpu.getEvent(&a, &g, &t);
  String posture;
  
  /* Print out the values */
  Serial.print("Rotation X: ");
  Serial.print(g.gyro.x);
  Serial.print(", Y: ");
  Serial.print(g.gyro.y);
  Serial.print(", Z: ");
  Serial.print(g.gyro.z);
  Serial.println(" rad/s");

  if (-0.3 <= (float)g.gyro.y && (float)g.gyro.y <= 0.3){
    if (0.75 <= (float)g.gyro.z && (float)g.gyro.z <= 1.25){
        posture = "Supine";
    }
    else {
      posture = "Prone";
    }
  }
  else if (0.75 <= (float)g.gyro.y && (float)g.gyro.y <= 1.25){
    posture = "Right";
  }
  else {
    posture = "Left";
  }

  // MQTT can only transmit strings
  //String ps="Rotation x: "+String((float)g.gyro.x)+", y: "+String((float)g.gyro.y)+", z: "+String((float)g.gyro.z);

  if (!client.connected())
    reconnect();
  client.loop();
  if(millis() - tg > 500) {
     tg=millis();
     client.publish(test_topic, String(posture).c_str()); 
  }
}
