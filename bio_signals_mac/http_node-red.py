import time
from flask import Flask, request, jsonify
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import neurokit2 as nk
import pandas as pd
import random
import create_bio_signals

app = Flask(__name__)
broker = "172.21.10.7"
port = 1883

client = mqtt.Client()

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
        ecg_type = data.get("ecg_type", "normal")
        heart_rate = data.get("heart_rate", 70)

        ecg_signal = []
        rsp_signal = []

        if ecg_type == "normal":
            ecg_signal = create_bio_signals.normal(heart_rate=heart_rate)
            rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate / 4, method="sinusoidal")
        elif ecg_type == "tachycardia":
            heart_rate = random.randint(120, 130)
            ecg_signal = create_bio_signals.normal(heart_rate=heart_rate)
            rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate / 4, method="sinusoidal")
        elif ecg_type == "bradycardia":
            heart_rate = random.randint(50, 60)
            ecg_signal = create_bio_signals.normal(heart_rate=heart_rate)
            rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate / 4, method="sinusoidal")
        elif ecg_type == "atrial_fibrillation":
            ecg_signal = create_bio_signals.atrial_fibrillation()
            rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate / 5.8, method="sinusoidal")
        elif ecg_type == "atrial_flutter":
            ecg_signal = create_bio_signals.atrial_flutter()
            rsp_signal = nk.rsp_simulate(duration=5, respiratory_rate=heart_rate / 5.6, method="sinusoidal")
        else:
            return jsonify({"error": "Invalid ECG type"}), 400

        bio_data_frame = pd.DataFrame({"ECG": ecg_signal, "RSP": rsp_signal})
        nk.signal_plot([bio_data_frame["ECG"], bio_data_frame["RSP"]], subplots=True)
        plt.savefig('/tmp/signal_plot.png')  # Save plot to file to avoid blocking server
        plt.close()

        signals, info = nk.ecg_process(ecg_signal, sampling_rate=1000)

        for i in range(len(signals)):
            client.publish("ecg_data", str(signals['ECG_Raw'][i]))
            client.publish("ecg_rate", str(signals['ECG_Rate'][i]))
            client.publish("p_onset", str(signals['ECG_P_Onsets'][i]))
            client.publish("p_peak", str(signals['ECG_P_Peaks'][i]))
            client.publish("p_offset", str(signals['ECG_P_Offsets'][i]))
            client.publish("q_peak", str(signals['ECG_Q_Peaks'][i]))
            client.publish("r_onset", str(signals['ECG_R_Onsets'][i]))
            client.publish("r_peak", str(signals['ECG_R_Peaks'][i]))
            client.publish("r_offset", str(signals['ECG_R_Offsets'][i]))
            client.publish("s_peak", str(signals['ECG_S_Peaks'][i]))
            client.publish("t_onset", str(signals['ECG_T_Onsets'][i]))
            client.publish("t_peak", str(signals['ECG_T_Peaks'][i]))
            client.publish("t_offset", str(signals['ECG_T_Offsets'][i]))
            client.publish("atrial_phase", str(signals['ECG_Phase_Atrial'][i]))
            client.publish("atrial_phase_completion", str(signals['ECG_Phase_Completion_Atrial'][i]))
            client.publish("ventricular_phase", str(signals['ECG_Phase_Ventricular'][i]))
            client.publish("ventricular_phase_completion", str(signals['ECG_Phase_Completion_Ventricular'][i]))
            time.sleep(0.005)

        client.publish("ecg_data", "done")

        return jsonify({"status": "done"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)