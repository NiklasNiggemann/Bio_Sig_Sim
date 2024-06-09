#include <WiFi.h>
#include <PubSubClient.h>

const char *ssid = "stud-hshl"; 
const char *password = "stud-hshl2024"; 

const char *mqtt_broker = "10.67.193.36";
const char *topic = "ecg_manipulation_esp32_input";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

void setup() 
{
    Serial.begin(115200);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) 
    {
        delay(500);
        Serial.println("Connecting to WiFi..");
    }
    Serial.println("Connected to Wi-Fi");

    //connecting to a mqtt broker
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

    client.publish(topic, "ESP32 (ECG manipulation) Connected");
    client.subscribe(topic);
}

void callback(char *topic, byte *payload, unsigned int length) 
{
    Serial.print("Message arrived in topic: ");
    Serial.println(topic);
    Serial.print("Message: ");
    for (int i = 0; i < length; i++) 
    {
        Serial.print((char) payload[i]);
    }
    Serial.println();
}

void loop() 
{
    client.loop();
    
}








