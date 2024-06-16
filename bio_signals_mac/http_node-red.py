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
broker = "192.168.2.180"
port = 1883

client = mqtt.Client()


def publish_ecg_signal(ecg_signal, client):
    for i, value in enumerate(ecg_signal):
        client.publish("python_generated_ecg", str(value))
        time.sleep(0.009)
        print(f"ECG: {value}")


def publish_rsp_signal(rsp_signal, client):
    for i, value in enumerate(rsp_signal):
        client.publish("python_generated_rsp", str(value))
        time.sleep(0.009)
        print(f"RSP: {value}")


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


client.on_connect = on_connect
client.connect(broker, port, 60)
client.loop_start()


@app.route('/generate_signal', methods=['POST'])
def generate_signal():
    try:
        data = request.get_json()
        ecg_type = data.get("ecg_type")
        heart_rate = data.get("heart_rate")

        ecg_signal = []

        match ecg_type:
            case "normal":
                ecg_signal = create_bio_signals.normal(heart_rate=heart_rate)
                rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate/4, method="sinusoidal")
            case "tachycardia":
                heart_rate = random.randint(100, 110)
                ecg_signal = create_bio_signals.normal(heart_rate=heart_rate)
                rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate/4, method="sinusoidal")
            case "bradycardia":
                heart_rate = random.randint(50, 60)
                ecg_signal = create_bio_signals.normal(heart_rate=heart_rate)
                rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate/4, method="sinusoidal")
            case "atrial_fibrillation":
                ecg_signal = create_bio_signals.atrial_fibrillation()
                rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate/5.8, method="sinusoidal")
            case "atrial_flutter":
                ecg_signal = create_bio_signals.atrial_flutter()
                rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate/5.6, method="sinusoidal")
            case _:
                return jsonify({"error": "Invalid ECG type"}), 400

        bio_data_frame = pd.DataFrame({"ECG": ecg_signal, "RSP": rsp_signal})
        nk.signal_plot(bio_data_frame, subplots=True)
        plt.show()

        ecg_thread = threading.Thread(target=publish_ecg_signal, args=(ecg_signal, client))
        rsp_thread = threading.Thread(target=publish_rsp_signal, args=(rsp_signal, client))
        ecg_thread.start()
        rsp_thread.start()
        ecg_thread.join()
        rsp_thread.join()

        client.publish("python_generated_ecg", "done")

        return jsonify({"status": "done"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)