import machine
import network
import time
import json
from umqtt_simple import MQTTClient
from machine import UART, Pin

# WLAN configuration
wlanSSID = 'BioSigSim'
wlanPW = 'MedicalSystemDesign'
network.country('DE')

mqttBroker = '172.21.10.7'
mqttClient = 'pico'
mqttTopic = b"ecg_signal_pico"

uart = UART(0, baudrate=9600, tx=Pin(16), rx=Pin(17))
led_onboard = machine.Pin('LED', machine.Pin.OUT, value=0)

def mqttDo(topic, msg):
    led_onboard.toggle()
    try:
        value = json.loads(msg)
        if isinstance(value, float):
            print("Received value:", value)
            uart.write(str(value) + '\n') 
    except Exception as e:
        print("Failed to decode JSON message:", e)

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
client.subscribe(topic=mqttTopic)

try:
    while True:
        client.check_msg()
        time.sleep(1)
except OSError:
    print('Error: No MQTT connection')