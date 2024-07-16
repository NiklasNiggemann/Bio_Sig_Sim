import machine
import network
import time
import json
from umqtt_simple import MQTTClient
from machine import UART, Pin, PWM

# WiFi and MQTT configuration
wlanSSID = 'BioSigSim'
wlanPW = 'BioSigSim'
network.country('DE')

mqttBroker = '192.168.1.146'
mqttClientID = 'pico'

# Servo setup
servo_position_control = Pin(28, Pin.OUT)
servo_position = PWM(servo_position_control)
servo_position.freq(50)

servo_atrial_control = Pin(27, Pin.OUT)
servo_atrial = PWM(servo_atrial_control)
servo_atrial.freq(50)

servo_ventricular_control = Pin(26, Pin.OUT)
servo_ventricular = PWM(servo_ventricular_control)
servo_ventricular.freq(50)

# Servo angle mapping
grad000 = 500000
grad180 = 2500000

def map_value(x, in_min=0, in_max=1, out_min=grad000, out_max=grad180):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Onboard LED setup
led_onboard = machine.Pin('LED', machine.Pin.OUT, value=0)

# MQTT message callback
def callback(topic, msg):
    global atrial_completion, ventricular_completion
    led_onboard.toggle()
    print(f"Received message on topic {topic}: {msg}")
    data = json.loads(msg)
    msg_decoded = msg.decode('utf-8')
    if topic == b'pico/change_position':
        if msg_decoded == 'standing':
            servo_position.duty_ns(grad000)
        elif msg_decoded == 'laying':
            servo_position.duty_ns(grad180 / 2)
    elif topic == b'pico/atrial_completion':
        atrial_completion = float(data['atrial_completion'])
        atrial_completion_mapped = int(map_value(atrial_completion))
        servo_atrial.duty_ns(atrial_completion_mapped)
    elif topic == b'pico/ventricular_completion':
        ventricular_completion = float(data['ventricular_completion'])
        ventricular_completion_mapped = int(map_value(ventricular_completion))
        servo_ventricular.duty_ns(ventricular_completion_mapped)

# Connect to WiFi
def wlan_connect():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print(f'Connecting to WLAN: {wlanSSID}')
        wlan.active(True)
        wlan.connect(wlanSSID, wlanPW)
        for _ in range(10):
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            led_onboard.toggle()
            print('.')
            time.sleep(1)
    if wlan.isconnected():
        print(f'WLAN connection established / WLAN status: {wlan.status()}')
        led_onboard.on()
    else:
        print(f'No WLAN connection / WLAN status: {wlan.status()}')
        led_onboard.off()

# Connect to MQTT broker
def mqtt_connect():
    print(f"Connecting to MQTT broker: {mqttBroker} with client ID: {mqttClientID}")
    client = MQTTClient(mqttClientID, mqttBroker, keepalive=60)
    client.set_callback(callback)
    client.connect()
    print('MQTT connection established')
    return client

# Reconnect to WiFi and MQTT
def reconnect():
    wlan_connect()
    client = mqtt_connect()
    client.subscribe("pico/change_position")
    client.subscribe("pico/atrial_completion")
    client.subscribe("pico/ventricular_completion")
    return client

# Initialize connections
wlan_connect()
client = mqtt_connect()
client.subscribe("pico/change_position")
client.subscribe("pico/atrial_completion")
client.subscribe("pico/ventricular_completion")

# Main loop
def main(client):
    try:
        client.check_msg()
    except OSError as e:
        print(f'Error: {e}')
        print('No MQTT connection, attempting to reconnect...')
        time.sleep(5)
        client = reconnect()
    return client

try:
    while True:
        client = main(client)
except KeyboardInterrupt:
    print("Program terminated")