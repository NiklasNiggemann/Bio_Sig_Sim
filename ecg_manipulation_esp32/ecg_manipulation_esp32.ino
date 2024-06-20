#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

Servo servo;

const char *ssid = "BioSigSim"; 
const char *password = "MedicalSystemDesign"; 

const char *mqtt_broker = "172.21.10.7";
const int mqtt_port = 1883;

int heart_rate_pot = 36; 

int servo_angle = 0;     
int servo_pin = 13; 

int breath_led_01 = 33; 
int breath_led_02 = 25; 
int breath_led_03 = 26; 
int breath_led_04 = 27; 
int breath_led_05 = 14; 
int breath_led_06 = 12; 

int normal_button = 15; 
int tachycardia_button = 2; 
int bradycardia_button = 16; 
int fibrillation_button = 18; 
int flutter_button = 21; 
int attack_button = 23; 

String type = "normal";
bool standing = false;
int heart_rate = 0; 

WiFiClient espClient; 
PubSubClient client(espClient);

void setup() 
{
    Serial.begin(115200);

    pinMode(normal_button, INPUT_PULLDOWN);
    pinMode(tachycardia_button, INPUT_PULLDOWN);
    pinMode(bradycardia_button, INPUT_PULLDOWN);
    pinMode(fibrillation_button, INPUT_PULLDOWN);
    pinMode(flutter_button, INPUT_PULLDOWN);
    pinMode(attack_button, INPUT_PULLDOWN);

    pinMode(breath_led_01, OUTPUT);
    pinMode(breath_led_02, OUTPUT);
    pinMode(breath_led_03, OUTPUT);
    pinMode(breath_led_04, OUTPUT);
    pinMode(breath_led_05, OUTPUT);
    pinMode(breath_led_06, OUTPUT);

    ESP32PWM::allocateTimer(0);
    ESP32PWM::allocateTimer(1);
    ESP32PWM::allocateTimer(2);
    ESP32PWM::allocateTimer(3);
    servo.setPeriodHertz(50); 
    servo.attach(servo_pin, 1000, 2000);  
    servo.write(0);

    // Scan for available networks
    Serial.println("Scanning for WiFi networks...");
    int numNetworks = WiFi.scanNetworks();
    if (numNetworks == 0) {
        Serial.println("No networks found.");
    } else {
        Serial.println("Networks found:");
        for (int i = 0; i < numNetworks; ++i) {
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

    while (WiFi.status() != WL_CONNECTED) 
    {
        delay(500);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to Wi-Fi");

    client.setServer(mqtt_broker, mqtt_port);
    client.setCallback(callback);
    while (!client.connected()) {
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
    client.subscribe("change_position");
    client.subscribe("rsp_signal");
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
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);

  char message[length + 1];
  memcpy(message, payload, length);
  message[length] = '\0';

  if (strcmp(topic, "change_position") == 0)  
  {
    change_position(message);
  }
  else if (strcmp(topic, "rsp_signal") == 0)
  {
    float signal_value = atof(message);
    int led_level = mapFloat(signal_value, -0.4, 0.4, 0, 6); 
    breathing_leds(led_level);
  }
}

void change_position(String message)
{
  if (message == "standing")
  {
    if (!standing)
    {
      stand_up();
    }
  }
  else if (message == "laying")
  {
    if (standing)
    {
      lay_down(); 
    }
  }
}

void breathing_leds(int breath_rate)
{
  const int led_pins[] = {breath_led_01, breath_led_02, breath_led_03, breath_led_04, breath_led_05, breath_led_06};
  const int num_leds = sizeof(led_pins) / sizeof(led_pins[0]);
  
  for (int i = 0; i < num_leds; ++i)
  {
    if (i < breath_rate)
    {
      digitalWrite(led_pins[i], HIGH);
    }
    else
    {
      digitalWrite(led_pins[i], LOW);
    }
  }
}

void loop() 
{
  client.loop(); 
  heart_rate = map(analogRead(heart_rate_pot),0,4095,60,120); 
  if (digitalRead(normal_button) == HIGH) {
    type = "Normal";
  } else if (digitalRead(tachycardia_button) == HIGH) {
    type = "Tachycardia";
  } else if (digitalRead(bradycardia_button) == HIGH) {
    type = "Bradycardia";
  } else if (digitalRead(fibrillation_button) == HIGH) {
    type = "Fibrillation";
  } else if (digitalRead(flutter_button) == HIGH) {
    type = "Flutter";
  } else if (digitalRead(attack_button) == HIGH) {
    type = "Attack";
  }
  Serial.println(type);
  client.publish("type_manipulation", type.c_str()); 
  client.publish("heart_rate_manipulation", String(heart_rate).c_str()); 
}