# Real-Time ECG Visualization and Analysis Platform

## Overview

In modern medicine, continuous monitoring and analysis of heart signals are crucial for diagnosing and treating cardiovascular diseases. Understanding and visualizing ECG (Electrocardiogram) data is essential not only for medical professionals but also for educational purposes and the development of new technologies in the healthcare sector.

This project aims to create a comprehensive, interactive platform for real-time visualization and analysis of ECG signals. It enables the visualization and adjustment of heart signals and the simulation of various heart rhythms and frequencies.

## Features

### Node-Red on Raspberry Pi 5
- The Raspberry Pi 5 hosts Node-Red, acting as the central hub for communication between different system components.
- System communication is based on MQTT.
- The dashboard, implemented via Node-Red, visualizes the ECG along with additional information in the user interface, accessible via an internet browser.

### ESP32 Signal Control
- The ESP32 allows for signal parameter adjustments and offers various heart rate control options.
- Heart rate can be set between 60 and 120 beats per minute using a potentiometer.
- Five buttons are available to select different heart rhythms: sinus rhythm, tachycardia (with a random frequency between 120 and 140), bradycardia (with a random frequency between 40 and 60), atrial fibrillation, and atrial flutter.
- A tilt sensor detects body position (standing or lying down) and adjusts the heart rate accordingly.

### Python and NeuroKit2
- The ECG signal is generated using a Python script and the NeuroKit2 library.
- The library functionality has been manually extended to simulate atrial fibrillation and atrial flutter.
- The signal is then transmitted to Node-Red.

### Raspberry Pi Pico and Servomotors
- A Raspberry Pi Pico controls two servomotors that simulate the heart's pumping function, replicating atrial and ventricular activity.
- Future enhancements could include connecting an actual pumping system for a more realistic heart activity simulation.

### LED Visualization with ESP32
- An additional ESP32, programmed with WLED, controls a CJMCU-8x8 LED matrix to visualize the heart rate, with LEDs pulsing synchronously.

## Implementation Success and Future Developments

The project has been successfully implemented, providing users with insights into both biomedical engineering, particularly the function and application of ECGs, and computer science with a focus on embedded systems. The system also offers significant potential for extensions. Future developments could include integrating additional signal parameters and developing an augmented reality app to provide a visual representation of a beating heart. Moreover, the implementation of an advanced pumping system could further enhance the simulation realism.

---

### Getting Started

To get started with this project, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ECG-Visualization-Platform.git
   cd ECG-Visualization-Platform
   ```

2. Set up the Raspberry Pi 5 with Node-Red:
   - Install Node-Red and required nodes.
   - Import the provided Node-Red flow.

3. Configure the ESP32 for signal control:
   - Flash the provided firmware to the ESP32.
   - Connect the potentiometer, buttons, and tilt sensor as described in the documentation.

4. Run the Python script to generate ECG signals:
   ```bash
   python generate_ecg.py
   ```

5. Set up the Raspberry Pi Pico and servomotors:
   - Flash the provided firmware to the Raspberry Pi Pico.
   - Connect the servomotors as described in the documentation.

6. Configure the additional ESP32 for LED visualization:
   - Flash the WLED firmware to the ESP32.
   - Connect the CJMCU-8x8 LED matrix as described in the documentation.

### Contributing

We welcome contributions to this project! Please fork the repository and submit pull requests for any enhancements or bug fixes.

### License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

For more detailed instructions and documentation, please refer to the [Wiki](https://github.com/yourusername/ECG-Visualization-Platform/wiki).

For any questions or support, please open an issue on the [GitHub Issues](https://github.com/yourusername/ECG-Visualization-Platform/issues) page.
