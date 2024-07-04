#include <WiFi.h>
#include <PubSubClient.h>

const char *ssid = "stud-hshl"; 
const char *password = "stud-hshl2024";  

const char *mqtt_broker = "10.67.193.127"; 
const int mqtt_port = 1883; 

int heart_rate_pot_pin = 33; 
int heart_rate = 0; 

int tilt_pin = 35; 
int tilt_pin_power = 21; 

int normal_button_pin = 26; 
int tachycardia_button_pin = 27; 
int bradycardia_button_pin = 12; 
int fibrillation_button_pin = 25; 
int flutter_button_pin = 14; 

WiFiClient espClient; 
PubSubClient client(espClient); 

volatile bool normal_button_pressed = false;
volatile bool tachycardia_button_pressed = false;
volatile bool bradycardia_button_pressed = false;
volatile bool fibrillation_button_pressed = false;
volatile bool flutter_button_pressed = false;
volatile bool tilt_changed = false;
volatile bool heart_rate_changed = false;

void setup() 
{
  Serial.begin(115200);
  setup_pins();
  setup_wifi();
  setup_mqtt();
}

void setup_wifi()
{
  WiFi.mode(WIFI_STA);
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  unsigned long startAttemptTime = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) 
  {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }

  if (WiFi.status() != WL_CONNECTED) 
  {
    Serial.println("Failed to connect to WiFi.");
  } 
  else 
  {
    Serial.println("Connected to Wi-Fi");
  }
}

void setup_mqtt()
{
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);
  reconnect_mqtt();
}

void callback(char *topic, byte *payload, unsigned int length) { }

void loop() 
{
  if (WiFi.status() != WL_CONNECTED) 
  {
    setup_wifi();
  }

  if (!client.connected())
  {
    reconnect_mqtt();
  }
  client.loop();

  if (normal_button_pressed) {
    normal_button_pressed = false;
    client.publish("esp32/type_manipulation", "normal"); 
  }

  if (tachycardia_button_pressed) {
    tachycardia_button_pressed = false;
    client.publish("esp32/type_manipulation", "tachycardia"); 
  }

  if (bradycardia_button_pressed) {
    bradycardia_button_pressed = false;
    client.publish("esp32/type_manipulation", "bradycardia"); 
  }

  if (fibrillation_button_pressed) {
    fibrillation_button_pressed = false;
    client.publish("esp32/type_manipulation", "fibrillation"); 
  }

  if (flutter_button_pressed) {
    flutter_button_pressed = false;
    client.publish("esp32/type_manipulation", "flutter"); 
  }

  if (tilt_changed) {
    tilt_changed = false;
    if (digitalRead(tilt_pin) == HIGH) 
    {
      client.publish("esp32/measured_position", "laying"); 
    } 
    else 
    {
      client.publish("esp32/measured_position", "standing"); 
    }
  }
  heart_rate = analogRead(heart_rate_pot_pin);
  int mapped_heart_rate = map(heart_rate, 0, 4095, 60, 120);
  String heart_rate_str = String(mapped_heart_rate);
  client.publish("esp32/heart_rate_manipulation", heart_rate_str.c_str()); 
}

void reconnect_mqtt() 
{
  while (!client.connected()) 
  {
    String client_id = String(WiFi.macAddress());
    Serial.println("Connecting to Broker...");
    if (client.connect(client_id.c_str())) 
    {
      Serial.println("Connected to Broker");
      client.subscribe("esp32/change_position");
    } 
    else 
    {
      Serial.print("failed with state ");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void IRAM_ATTR normal_interrupt()
{
  normal_button_pressed = true;
}

void IRAM_ATTR tachycardia_interrupt()
{
  tachycardia_button_pressed = true;
}

void IRAM_ATTR bradycardia_interrupt()
{
  bradycardia_button_pressed = true;
}

void IRAM_ATTR fibrillation_interrupt()
{
  fibrillation_button_pressed = true;
}

void IRAM_ATTR flutter_interrupt()
{
  flutter_button_pressed = true;
}

void IRAM_ATTR tilt_interrupt()
{
  tilt_changed = true;
}

void setup_pins()
{
  pinMode(normal_button_pin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(normal_button_pin), normal_interrupt, FALLING);
  pinMode(tachycardia_button_pin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(tachycardia_button_pin), tachycardia_interrupt, FALLING);
  pinMode(bradycardia_button_pin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(bradycardia_button_pin), bradycardia_interrupt, FALLING);
  pinMode(fibrillation_button_pin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(fibrillation_button_pin), fibrillation_interrupt, FALLING);
  pinMode(flutter_button_pin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(flutter_button_pin), flutter_interrupt, FALLING);
  pinMode(tilt_pin, INPUT);
  attachInterrupt(digitalPinToInterrupt(tilt_pin), tilt_interrupt, CHANGE);
  pinMode(heart_rate_pot_pin, INPUT);
  pinMode(tilt_pin_power, OUTPUT);
  digitalWrite(tilt_pin_power, HIGH);
}