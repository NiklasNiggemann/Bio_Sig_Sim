import time
from flask import Flask, request, jsonify
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import neurokit2 as nk
import pandas as pd
import random
import create_bio_signals
import socket
import struct

def generate_signal():
    try:
        data = request.get_json()
        ecg_type = data.get("ecg_type", "normal")
        heart_rate = data.get("heart_rate", 70)

        ecg_signal = generate_ecg_signal(ecg_type, heart_rate)

        bio_data_frame = pd.DataFrame({"ECG": ecg_signal})
        nk.signal_plot([bio_data_frame["ECG"]])
        plt.savefig('tmp_pictures/signal_plot.png')
        plt.close()

        signals, info = nk.ecg_process(ecg_signal, sampling_rate=1000)
        plot_custom_ecg(signals, info)

        send_png_via_udp('tmp_pictures/signal_plot.png', ip, 5005)
        send_png_via_udp('tmp_pictures/ecg_plot.png', ip, 5006)

        # Create an empty DataFrame to store ECG data
        ecg_data_df = pd.DataFrame()

        for i in range(len(signals)):
            publish_ecg_data(signals, i, ecg_data_df)
            time.sleep(0.005)

        # Save the DataFrame as a CSV file
        ecg_data_df.to_csv('ecg_data.csv', index=False)

        client.publish("mac/ecg_data", "done")

        return jsonify({"status": "done"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_ecg_signal(ecg_type, heart_rate):
    if ecg_type == "normal":
        return create_bio_signals.normal(heart_rate=heart_rate)
    elif ecg_type == "tachycardia":
        heart_rate = random.randint(120, 140)
        return create_bio_signals.normal(heart_rate=heart_rate)
    elif ecg_type == "bradycardia":
        heart_rate = random.randint(40, 60)
        return create_bio_signals.normal(duration=10, heart_rate=heart_rate)
    elif ecg_type == "atrial_fibrillation":
        return create_bio_signals.atrial_fibrillation(heart_rate=heart_rate)
    elif ecg_type == "atrial_flutter":
        return create_bio_signals.atrial_flutter(heart_rate=heart_rate)
    else:
        raise ValueError("Invalid ECG type")


def plot_custom_ecg(signals, info):
    plt.figure(figsize=(12, 8))
    plt.plot(signals['ECG_Raw'], label='ECG Raw', color='black', linewidth=0.5)
    plt.plot(signals['ECG_Clean'], label='ECG Clean', color='blue', linewidth=1.0)

    plt.scatter(signals.index[signals['ECG_R_Peaks'].notna()], signals['ECG_Clean'][signals['ECG_R_Peaks'].notna()],
                color='red', label='R Peaks', marker='o')
    plt.scatter(signals.index[signals['ECG_T_Peaks'].notna()], signals['ECG_Clean'][signals['ECG_T_Peaks'].notna()],
                color='green', label='T Peaks', marker='x')
    plt.scatter(signals.index[signals['ECG_P_Peaks'].notna()], signals['ECG_Clean'][signals['ECG_P_Peaks'].notna()],
                color='orange', label='P Peaks', marker='^')

    plt.title('ECG Signal with Peaks')
    plt.xlabel('Time (ms)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('tmp_pictures/ecg_plot.png')
    plt.close()


def send_png_via_udp(png_file_path, target_ip, target_port, chunk_size=1024):
    with open(png_file_path, 'rb') as file:
        png_data = file.read()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    total_size = len(png_data)
    num_chunks = total_size // chunk_size + (1 if total_size % chunk_size else 0)

    try:
        for i in range(num_chunks):
            start = i * chunk_size
            end = start + chunk_size
            chunk = png_data[start:end]

            message = struct.pack('!II', i, num_chunks) + chunk

            sock.sendto(message, (target_ip, target_port))

    finally:
        sock.close()


def publish_ecg_data(signals, index, ecg_data_df):
    ecg_data = {
        'ECG_Raw': signals['ECG_Raw'][index],
        'ECG_Rate': round(signals['ECG_Rate'][index]),
        'P_Onset': signals['ECG_P_Onsets'][index],
        'P_Peak': signals['ECG_P_Peaks'][index],
        'P_Offset': signals['ECG_P_Offsets'][index],
        'Q_Peak': signals['ECG_Q_Peaks'][index],
        'R_Onset': signals['ECG_R_Onsets'][index],
        'R_Peak': signals['ECG_R_Peaks'][index],
        'R_Offset': signals['ECG_R_Offsets'][index],
        'S_Peak': signals['ECG_S_Peaks'][index],
        'T_Onset': signals['ECG_T_Onsets'][index],
        'T_Peak': signals['ECG_T_Peaks'][index],
        'T_Offset': signals['ECG_T_Offsets'][index],
        'Atrial_Phase': signals['ECG_Phase_Atrial'][index],
        'Atrial_Phase_Completion': round(signals['ECG_Phase_Completion_Atrial'][index], 2),
        'Ventricular_Phase': signals['ECG_Phase_Ventricular'][index],
        'Ventricular_Phase_Completion': round(signals['ECG_Phase_Completion_Ventricular'][index], 2)
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)