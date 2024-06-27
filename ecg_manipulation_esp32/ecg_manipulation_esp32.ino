#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

Servo servo;

const char *ssid = "stud-hshl"; 
const char *password = "stud-hshl2024"; 

const char *mqtt_broker = "10.67.193.127";
const int mqtt_port = 1883;

int heart_rate_pot = 33; 
int heart_rate = 0; 

int servo_angle = 0; 
int servo_pin = 32; 
bool standing = false; 

int normal_button = 32; 
int tachycardia_button = 33; 
int bradycardia_button = 25; 
int fibrillation_button = 26; 
int flutter_button = 27; 
String type = "normal"; 

WiFiClient espClient; 
PubSubClient client(espClient); 

void setup() 
{
  Serial.begin(115200);
  setup_pins();
  setup_servo();
  setup_wifi();
  setup_mqtt();
}

void setup_pins()
{
  pinMode(normal_button, INPUT_PULLDOWN);
  pinMode(tachycardia_button, INPUT_PULLDOWN);
  pinMode(bradycardia_button, INPUT_PULLDOWN);
  pinMode(fibrillation_button, INPUT_PULLDOWN);
  pinMode(flutter_button, INPUT_PULLDOWN);
}

void setup_servo()
{
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  servo.setPeriodHertz(50); 
  servo.attach(servo_pin, 1000, 2000);  
  servo.write(0);
}

void setup_wifi()
{
  WiFi.mode(WIFI_STA);
  Serial.println("Scanning for WiFi networks...");
  int numNetworks = WiFi.scanNetworks();
  if (numNetworks == 0) 
  {
      Serial.println("No networks found.");
  } 
  else 
  {
    Serial.println("Networks found:");
    for (int i = 0; i < numNetworks; ++i) 
    {
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i));
      Serial.println(" dBm)");
    }
  }

  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  unsigned long startAttemptTime = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) 
  {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Failed to connect to WiFi.");
  } else {
    Serial.println("Connected to Wi-Fi");
  }
}

void setup_mqtt()
{
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);
  while (!client.connected()) 
  {
    String client_id = String(WiFi.macAddress());
    Serial.println("Connecting to Broker...");
    if (client.connect(client_id.c_str())) 
    {
      Serial.println("Connected to Broker");
    } 
    else 
    {
      Serial.print("failed with state ");
      Serial.println(client.state());
      delay(2000);
    }
  }
  client.subscribe("esp32/change_position");
}

void move_servo(int start_angle, int end_angle, int step)
{
  for (int angle = start_angle; angle != end_angle; angle += step) 
  { 
    servo.write(angle);   
    delay(5);             
  }
}

void stand_up()
{
  move_servo(180, 0, -1);
  standing = true;
}

void lay_down()
{
  move_servo(0, 180, 1);
  standing = false;
}

float mapFloat(float x, float in_min, float in_max, float out_min, float out_max) 
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void callback(char *topic, byte *payload, unsigned int length) 
{
  change_position(payload, length);
}

void change_position(byte *payload, unsigned int length)
{
  char message[length + 1];
  memcpy(message, payload, length);
  message[length] = '\0';
  if (strcmp(message, "standing") == 0)
  {
    if (!standing)
    {
      stand_up();
    }
  }
  else if (strcmp(message, "laying") == 0)
  {
    if (standing)
    {
      lay_down(); 
    }
  }
}

void loop() 
{
  client.loop(); 
  heart_rate = map(analogRead(heart_rate_pot), 0, 4095, 60, 120); 
  Serial.println(heart_rate);
  client.publish("esp32/type_manipulation", type.c_str()); 
  client.publish("esp32/heart_rate_manipulation", String(heart_rate).c_str()); 
  delay(500);
}