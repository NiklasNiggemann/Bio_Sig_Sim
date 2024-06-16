# Bibliotheken laden
import machine
import network
import time
from umqtt_simple import MQTTClient

# WLAN-Konfiguration
wlanSSID = 'stud-hshl'
wlanPW = 'stud-hshl2024'
network.country('DE')

# MQTT-Konfiguration
mqttBroker = '192.168.0.10'
mqttClient = 'pico'
mqttUser = 'mqttuser'
mqttPW = ''
mqttTopic = b"picotemp"

# Status-LED für die WLAN-Verbindung
led_onboard = machine.Pin('LED', machine.Pin.OUT, value=0)

# Initialisierung des Sensors
sensor_temp = machine.ADC(4)

# Funktion: Temperatur abrufen und umrechnen
def getTemp():
    read = sensor_temp.read_u16()
    spannung = read * 3.3 / (65535)
    temperatur = 27 - (spannung - 0.706) / 0.001721
    return temperatur

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
    client.connect()
    print()
    print('MQTT-Verbindung hergestellt')
    print()
    return client

# WLAN-Verbindung herstellen
wlanConnect()

# Funktion zur Taster-Auswertung
while True:
    myValue = str(getTemp())
    try:
        client = mqttConnect()
        client.publish(mqttTopic, myValue)
        print("An Topic %s gesendet: %s" %  (mqttTopic, myValue))
        print()
        client.disconnect()
        print('MQTT-Verbindung beendet')
        print()
    except OSError:
        print()
        print('Fehler: Keine MQTT-Verbindung')
        print()
    # 60 Sekunden warten
    time.sleep(60)