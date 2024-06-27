import machine
import network
import time
import json
from umqtt_simple import MQTTClient
from machine import UART, Pin

# WLAN configuration
wlanSSID = 'stud-hshl'
wlanPW = 'stud-hshl2024'
network.country('DE')

heart_rate = 0
atrial_completion = 0.0
ventricular_completion = 0.0

mqttBroker = '172.21.10.7'
mqttClient = 'pico'

uart = UART(0, baudrate=9600, tx=Pin(16), rx=Pin(17))
led_onboard = machine.Pin('LED', machine.Pin.OUT, value=0)

def mqttDo(topic, msg):
    led_onboard.toggle()
    if (topic == "pico/wled_control"):
        print("wled")
    elif (topic == "pico/heart_rate"):
        heart_rate = json.loads(msg)
    elif (topic == "pico/atrial_completion"):
        atrial_completion = json.loads(msg)
        print("atrial_completion")
    elif (topic == "pico/ventricular_completion"):
        ventricular_completion = json.loads(msg)
        print("ventricular_completion")

def wlanConnect():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('Connecting to WLAN:', wlanSSID)
        wlan.active(True)
        wlan.connect(wlanSSID, wlanPW)
        for i in range(10):
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            led_onboard.toggle()
            print('.')
            time.sleep(1)
    if wlan.isconnected():
        print('WLAN connection established / WLAN status:', wlan.status())
        led_onboard.on()
    else:
        print('No WLAN connection / WLAN status:', wlan.status())
        led_onboard.off()

def mqttConnect():
    print("Connecting to MQTT broker: %s with client ID: %s" % (mqttBroker, mqttClient))
    client = MQTTClient(mqttClient, mqttBroker, keepalive=60)
    client.set_callback(mqttDo)
    client.connect()
    print('MQTT connection established')
    return client

wlanConnect()
client = mqttConnect()
client.subscribe("pico/wled_control")
client.subscribe("pico/heart_rate")
client.subscribe("pico/atrial_completion")
client.subscribe("pico/ventricular_completion")

try:
    while True:
        client.check_msg()
        time.sleep(heart_rate / 60)
except OSError:
    print('Error: No MQTT connection')
    