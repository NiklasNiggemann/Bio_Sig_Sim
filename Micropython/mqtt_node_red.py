import machine
import network
import time
import json
from umqtt_simple import MQTTClient
from machine import UART, Pin

# WLAN-Konfiguration
wlanSSID = 'stud-hshl'
wlanPW = 'stud-hshl2024'
network.country('DE')

mqttBroker = '10.67.193.84'
mqttClient = 'pico'
mqttTopic = b"send_ecg_signal"

uart = UART(0, baudrate=9600, tx=Pin(16), rx=Pin(17))
led_onboard = machine.Pin('LED', machine.Pin.OUT, value=0)

received_signal = None

def mqttDo(topic, msg):
    led_onboard.toggle()
    time.sleep(1)
    print((topic, msg))
    array = json.loads(msg)
    print("Empfangenes Array:", array)
    for value in array:
        print("Einzelner Wert:", value)


def wlanConnect():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('WLAN-Verbindung herstellen:', wlanSSID)
        wlan.active(True)
        wlan.connect(wlanSSID, wlanPW)
        for i in range(10):
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            led_onboard.toggle()
            print('.')
            time.sleep(1)
    if wlan.isconnected():
        print('WLAN-Verbindung hergestellt / WLAN-Status:', wlan.status())
        print()
        led_onboard.on()
    else:
        print('Keine WLAN-Verbindung / WLAN-Status:', wlan.status())
        print()
        led_onboard.off()


def mqttConnect():
    print("MQTT-Verbindung herstellen: %s mit %s" % (mqttClient, mqttBroker))
    client = MQTTClient(mqttClient, mqttBroker, keepalive=60)
    client.set_callback(mqttDo)
    client.connect()
    print()
    print('MQTT-Verbindung hergestellt')
    print()
    return client

wlanConnect()
client = mqttConnect()
client.subscribe(topic=mqttTopic)

def wait_for_array():
    global received_signal
    while received_signal is None:
        client.wait_msg()
    return received_signal

try:
    while True:
        client.check_msg()
        time.sleep(1)
except OSError:
    print('Fehler: Keine MQTT-Verbindung')
    

    