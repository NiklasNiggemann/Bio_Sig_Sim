**Projekt: Integrierte Herzfrequenz- und Atmungsüberwachung mit Node Red und Raspberry Pi**

Dieses Projekt bietet eine umfassende Plattform zur Untersuchung und Simulation von EKG-Signalen und deren Verarbeitung. Das System basiert auf einem Raspberry Pi 5, der als Node Red Host fungiert und verschiedene Komponenten über MQTT-Protokolle verbindet. Hier ist eine detaillierte Übersicht der Projektstruktur und ihrer Funktionalitäten:

### Systemübersicht

1. **Raspberry Pi 5 als Node Red Host:**
   - Hostet die Node Red Plattform zur Verwaltung und Darstellung von Datenströmen.
   - Verbindet sich per MQTT mit einem ESP32 zur Erfassung und Steuerung von Parametern wie Herzfrequenz und Rhythmusarten (z.B. Tachykardie, normaler Sinusrhythmus).

2. **ESP32 als Eingabegerät:**
   - Ausgestattet mit Buttons und Potentiometern zur Änderung von Herzfrequenz und Rhythmusparametern.
   - Sendet die erfassten Parameter über MQTT an Node Red.

3. **Macbook mit Python-Skript:**
   - Empfängt die Parameter über HTTP von Node Red.
   - Simuliert basierend auf diesen Parametern ein EKG- und ein RSP-Signal.
   - Sendet die simulierten Signale über MQTT zurück an Node Red.

4. **Node Red Dashboard:**
   - Visualisiert die EKG- und RSP-Signale in Echtzeit.
   - Sendet das RSP-Signal über MQTT an den ESP32 zur Darstellung der Atemfrequenz mittels einer LED-Schaltung.

5. **Raspberry Pi Pico für Herzschlagsimulation:**
   - Empfängt das EKG-Signal über MQTT.
   - Simuliert den Herzschlag basierend auf dem EKG-Signal.
   - Über UART ist ein weiterer ESP32 an den Pico angeschlossen, um eingebettete EKG-Verarbeitungstechniken zu ermöglichen.

6. **Zweiter ESP32 mit Embedded ECG Processing:**
   - Verfügt über eine eingebettete Spitzenwertdetektion zur Erkennung von Herzschlägen.
   - Zeigt erkannte Peaks mittels einer LED und eines Piezo-Sensors an.

### Ziele des Projekts

1. **Erkundung von EKG-Signalen:**
   - Darstellung und Analyse verschiedener EKG-Muster (z.B. normaler Sinusrhythmus, Vorhofflattern).
   - Untersuchung der Auswirkungen von Aktivitäten wie Sport oder Rauchen auf die Herzgesundheit.

2. **Erforschung von Embedded ECG Processing:**
   - Entwicklung und Testen von Algorithmen zur Spitzenwertdetektion und anderen Verarbeitungstechniken direkt auf dem ESP32.
   - Langfristiges Ziel, Anwendungen im Bereich Herzschrittmacher und andere medizinische Geräte zu entwickeln.

### Vorteile und Anwendungen

- **Bildungszwecke:** Ideal für den Unterricht und das Selbststudium zur Veranschaulichung der Herzphysiologie und EKG-Analyse.
- **Forschung und Entwicklung:** Plattform für die Entwicklung und Erprobung neuer Algorithmen zur EKG-Verarbeitung.
- **Gesundheitsüberwachung:** Möglichkeit, Langzeitstudien zur Gesundheitsüberwachung durchzuführen und präventive Maßnahmen zu entwickeln.

Dieses Projekt kombiniert modernste Technologie mit praxisorientierter Forschung und bietet eine einzigartige Plattform für die Untersuchung und Entwicklung von EKG- und RSP-Signalen. Es fördert das Verständnis der Herzphysiologie und die Entwicklung neuer medizinischer Anwendungen, was es zu einer wertvollen Ressource für Bildung und Forschung macht.
