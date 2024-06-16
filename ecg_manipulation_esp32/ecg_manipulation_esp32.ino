#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

Servo servo;

const char *ssid = "stud-hshl"; 
const char *password = "stud-hshl2024"; 

const char *mqtt_broker = "10.67.193.84";
const int mqtt_port = 1883;

int heart_rate_pot = 15; 

int servo_angle = 0;     
int servo_pin = 13; 

int breath_led_01 = 12; 
int breath_led_02 = 14; 
int breath_led_03 = 27; 
int breath_led_04 = 26; 
int breath_led_05 = 25; 
int breath_led_06 = 33; 

int normal_button = 6; 
int tachycardia_button = 7; 
int bradycardia_button = 8; 
int fibrillation_button = 15; 
int flutter_button = 2; 

bool normal = true; 
bool tachycardia = false; 
bool bradycardia = false; 
bool fibrillation = false; 
bool flutter = false; 

String type = "normal";
bool standing = false;
int heart_rate = 0; 

WiFiClient espClient; 
PubSubClient client(espClient);

void setup() 
{
    Serial.begin(115200);

    ESP32PWM::allocateTimer(0);
	  ESP32PWM::allocateTimer(1);
	  ESP32PWM::allocateTimer(2);
	  ESP32PWM::allocateTimer(3);
	  servo.setPeriodHertz(50); 
	  servo.attach(servo_pin, 1000, 2000);  
    servo.write(0);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) 
    {
        delay(500);
        Serial.println("Connecting to WiFi..");
    }
    Serial.println("Connected to Wi-Fi");

    client.setServer(mqtt_broker, mqtt_port);
    client.setCallback(callback);
    while (!client.connected()) {
        String client_id = String(WiFi.macAddress());
        Serial.println("Connecting to Broker..");
        if (client.connect(client_id.c_str())) 
        {
            Serial.println("Connected to Broker");
        } 
        else 
        {
            Serial.print("failed with state ");
            Serial.print(client.state());
            delay(2000);
        }
    }
    client.subscribe("position");
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
  String strPayload = String(message);
    if (strPayload == "standing")
    {
      if (!standing)
      {
        stand_up();
      }
    }
    else if (strPayload == "laying")
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

String check_type()
{
  if (normal)
  {
    return "normal";
  }
  if (tachycardia_button)
  {
    return "tachycardia";
  }
  if (bradycardia_button)
  {
    return "bradycardia";
  }
  if (fibrillation_button)
  {
    return "fibrillation";
  }
  if (flutter_button)
  {
    return "flutter";
  }
}

void loop() 
{
  client.loop(); 
  heart_rate = map(analogRead(heart_rate_pot),0,1023,60,120); 
  if (normal_button || tachycardia_button || bradycardia_button || fibrillation_button || flutter_button == 1)
  {
    type = check_type();
  }
  client.publish("type_manipulation", type.c_str()); 
  client.publish("heart_rate_manipulation", String(heart_rate).c_str()); 
}








