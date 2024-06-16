import machine
import network
import time
from umqtt_simple import MQTTClient

wlanSSID = 'hshl-stud'
wlanPW = 'hshl-stud2024'
network.country('DE')

# MQTT-Konfiguration
mqttBroker = '10.67.193.84'
mqttClient = 'pico'
mqttUser = 'mqttuser'
mqttPW = ''
mqttTopic = b"button"

# Status-LED für die WLAN-Verbindung
led_onboard = machine.Pin('LED', machine.Pin.OUT, value=0)

# Callback-Funktion: Empfang einer MQTT-Nachricht
def mqttDo(topic, msg):
    # Onboard-LED-Toggle
    led_onboard.toggle()
    # MQTT-Nachricht ausgeben
    print("Topic: %s, Wert: %s" % (topic, msg))
    print()

# Funktion: WLAN-Verbindung herstellen
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

# Funktion: Verbindung zum MQTT-Server herstellen
def mqttConnect():
    if mqttUser != '' and mqttPW != '':
        print("MQTT-Verbindung herstellen: %s mit %s als %s" % (mqttClient, mqttBroker, mqttUser))
        client = MQTTClient(mqttClient, mqttBroker, user=mqttUser, password=mqttPW, keepalive=60)
    else:
        print("MQTT-Verbindung herstellen: %s mit %s" % (mqttClient, mqttBroker))
        client = MQTTClient(mqttClient, mqttBroker, keepalive=60)
    client.set_callback(mqttDo)
    client.connect()
    print()
    print('MQTT-Verbindung hergestellt')
    print()
    return client

# WLAN-Verbindung herstellen
wlanConnect()

# MQTT-Verbindungsaufbau
try:
    client = mqttConnect()
    client.subscribe(topic=mqttTopic)
    print("Subscribe: %s" %  mqttTopic)
    print()
    # Warten auf Nachrichten
    while True:
        client.check_msg()
        time.sleep(1)
except OSError:
    print('Fehler: Keine MQTT-Verbindung')