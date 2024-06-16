#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

Servo my_servo_01;

const char *ssid = "stud-hshl"; 
const char *password = "stud-hshl2024"; 

const char *mqtt_broker = "10.67.193.84";
const int mqtt_port = 1883;

int angle = 0;    
int servo_01 = 13;
int servo_02 = 12;
bool standing = false;

WiFiClient espClient;
PubSubClient client(espClient);

void setup() 
{
    Serial.begin(115200);

    ESP32PWM::allocateTimer(0);
	  ESP32PWM::allocateTimer(1);
	  ESP32PWM::allocateTimer(2);
	  ESP32PWM::allocateTimer(3);
	  my_servo_01.setPeriodHertz(50);    
	  my_servo_01.attach(servo_01, 1000, 2000); 
    my_servo_01.write(0);

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
    client.subscribe("position");
}

void stand_up()
{
  for (angle = 180; angle >= 0; angle -= 1) 
  { 
		my_servo_01.write(angle);   
		delay(5);             
	}
  standing = true;
}

void lay_down()
{
  for (angle = 0; angle <= 180; angle += 1) 
  {  
		my_servo_01.write(angle);   
		delay(5);             
	}
  standing = false;
}

void callback(char *topic, byte *payload, unsigned int length) 
{
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);

  char message[length + 1];  
  memcpy(message, payload, length);
  message[length] = '\0';    

  String strPayload = String(message);
  Serial.print("Message: ");
  Serial.println(strPayload);

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

void loop() 
{
  client.loop();

}








