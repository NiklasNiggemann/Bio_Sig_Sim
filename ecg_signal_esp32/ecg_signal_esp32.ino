#include <WiFi.h>
#include <PubSubClient.h>
#include <HardwareSerial.h>

const char *ssid = "stud-hshl"; 
const char *password = "stud-hshl2024"; 

const char *mqtt_broker = "10.67.193.36";
const char *topic = "ecg_signal_esp32_input";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

HardwareSerial SerialPico(2);

int led_pin = 23;
int tilt_pin = 22; 

void setup() 
{
    pinMode(led_pin, OUTPUT);
    pinMode(tilt_pin, INPUT_PULLUP);
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

    client.publish(topic, "ESP32 (ECG signal) Connected");
    client.subscribe(topic);
}

void callback(char *topic, byte *payload, unsigned int length) 
{
    /*Serial.print("Message arrived in topic: ");
    Serial.println(topic);
    Serial.print("Message: ");
    for (int i = 0; i < length; i++) 
    {
        Serial.print((char) payload[i]);
    }
    Serial.println();*/
}

void loop() 
{
  client.loop();
  Serial.println(digitalRead(tilt_pin));
  if (SerialPico.available())
  {
    String ecg_sample_string = String(SerialPico.read());
    float ecg_sample_value = ecg_sample_string.toFloat() - 48;
    ecg_sample_string = String(ecg_sample_value);
    if (ecg_sample_value != -38)
    {
      client.publish(topic, ecg_sample_string.c_str());
      if (ecg_sample_value == 4)
      {
        client.publish("ecg_signal_peak_esp32_input", "peak");
        peak_led();
      }
    }
  }
  delay(10); 
}

void peak_led()
{
  digitalWrite(led_pin, HIGH);
  delay(50);
  digitalWrite(led_pin, LOW);
}

