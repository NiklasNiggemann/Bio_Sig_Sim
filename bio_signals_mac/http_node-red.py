from flask import Flask, request, jsonify
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import neurokit2 as nk
import pandas as pd
import threading
import random
import time
import create_bio_signals

app = Flask(__name__)
broker = "10.67.193.84"
port = 1883

client = mqtt.Client()


def publish_ecg_signal(ecg_signal, client):
    for i, value in enumerate(ecg_signal):
        client.publish("python_generated_ecg", str(value))
        time.sleep(0.0009)
        print(f"ECG: {value}")


def publish_rsp_signal(rsp_signal, client):
    for i, value in enumerate(rsp_signal):
        client.publish("python_generated_rsp", str(value))
        print(f"RSP: {value}")


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


client.on_connect = on_connect

try:
    client.connect(broker, port, 60)
    client.loop_start()
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")


@app.route('/generate_signal', methods=['POST'])
def generate_signal():
    try:
        data = request.get_json()
        ecg_type = data.get("ecg_type")
        heart_rate = data.get("heart_rate")

        ecg_signal = []
        rsp_signal = []

        if ecg_type == "normal":
            ecg_signal = create_bio_signals.normal(heart_rate=heart_rate)
            rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate/4, method="sinusoidal")
        elif ecg_type == "tachycardia":
            heart_rate = random.randint(120, 130)
            ecg_signal = create_bio_signals.normal(heart_rate=heart_rate)
            rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate/4, method="sinusoidal")
        elif ecg_type == "bradycardia":
            heart_rate = random.randint(50, 60)
            ecg_signal = create_bio_signals.normal(heart_rate=heart_rate)
            rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate/4, method="sinusoidal")
        elif ecg_type == "atrial_fibrillation":
            ecg_signal = create_bio_signals.atrial_fibrillation()
            rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate/5.8, method="sinusoidal")
        elif ecg_type == "atrial_flutter":
            ecg_signal = create_bio_signals.atrial_flutter()
            rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate/5.6, method="sinusoidal")
        else:
            return jsonify({"error": "Invalid ECG type"}), 400

        signals, info = nk.ecg_process(ecg_signal, sampling_rate=1000)
        bio_data_frame = pd.DataFrame({"ECG": ecg_signal, "RSP": rsp_signal})
        nk.signal_plot([bio_data_frame["ECG"], bio_data_frame["RSP"]], subplots=True)

        plt.show()

        ecg_thread = threading.Thread(target=publish_ecg_signal, args=(ecg_signal, client))
        # rsp_thread = threading.Thread(target=publish_rsp_signal, args=(rsp_signal, client))
        ecg_thread.start()
        # rsp_thread.start()
        ecg_thread.join()
        # rsp_thread.join()

        client.publish("python_generated_ecg", "done")

        return jsonify({"status": "done"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)