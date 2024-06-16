#include <WiFi.h>
#include <PubSubClient.h>
#include <HardwareSerial.h>

const char *ssid = "stud-hshl"; 
const char *password = "stud-hshl2024"; 

const char *mqtt_broker = "10.67.193.84";
const char *topic = "ecg_signal_esp32_input";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

HardwareSerial SerialPico(2);

int led_pin = 0;
int tilt_power_pin = 23; 
int tilt_pin = 22; 
int piezo_pin = 15; 

void setup() 
{
  pinMode(tilt_power_pin, OUTPUT);
  digitalWrite(tilt_power_pin, HIGH);
  pinMode(tilt_pin, INPUT_PULLUP);
  pinMode(led_pin, OUTPUT);
  Serial.begin(115200);
  SerialPico.begin(9600, SERIAL_8N1, 16, 17); 

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) 
  {
      delay(500);
      Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to Wi-Fi");

  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);
  while (!client.connected()) 
  {
    String client_id = String(WiFi.macAddress());
    Serial.println("Connecting to Broker..");
    if (client.connect(client_id.c_str())) 
    {
        Serial.println("Connected to Broker");
    } 
    else 
    {
        Serial.print("Failed with state ");
        Serial.println(client.state());
        delay(2000);
    }
  }

  client.publish(topic, "ESP32 (ECG signal) Connected");
  client.subscribe(topic);
}

void measure_position()
{
  if (digitalRead(tilt_pin) == 0)
  {
    //client.publish("measured_position", "laying");
  }
  else if (digitalRead(tilt_pin) == 1)
  {
    //client.publish("measured_position", "standing");
  }
}

void callback(char *topic, byte *payload, unsigned int length) 
{
  // Process incoming messages if needed
}

void loop() 
{
  client.loop();
  if (SerialPico.available())
  {
    String ecg_sample_string = SerialPico.readStringUntil('\n'); 
    float ecg_sample_value = ecg_sample_string.toFloat();
    Serial.println("ECG Sample Value: " + String(ecg_sample_value));
    if (ecg_sample_value != 0.0) 
    {
      client.publish(topic, String(ecg_sample_value).c_str());
      if (ecg_sample_value == 4.0)  
      {
        client.publish("ecg_signal_peak_esp32_input", "peak");
        peak_alarm();
      }
    }
  }
  measure_position();
}

void peak_alarm()
{
    tone(piezo_pin, 500);
    digitalWrite(led_pin, HIGH);
    delay(20);
    digitalWrite(led_pin, LOW);
    noTone(piezo_pin);
}