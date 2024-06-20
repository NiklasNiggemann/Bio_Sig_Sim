import matplotlib.pyplot as plt
import neurokit2 as nk
import pandas as pd
import random
import create_bio_signals
import socket
import struct


def generate_signal(ecg_type="normal", heart_rate=70):
    ecg_signal = []
    rsp_signal = []

    if ecg_type == "normal":
        ecg_signal = create_bio_signals.normal(heart_rate=heart_rate)
        rsp_signal = nk.rsp_simulate(duration=2, respiratory_rate=heart_rate/4, method="sinusoidal")
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

    signals, info = nk.ecg_process(ecg_signal, sampling_rate=1000)
    for i in range(len(signals)):
        print("ECG: " + str(signals["ECG_Raw"][i]))
        print("Atrial: " + str(signals["ECG_Phase_Completion_Atrial"][i]))
        print("Ventricular: " + str(signals["ECG_Phase_Completion_Ventricular"][i]))
        print("ECG_P_Onsets: " + str(signals["ECG_P_Onsets"][i]))
        print("ECG_P_Peaks: " + str(signals["ECG_P_Peaks"][i]))
        print("ECG_P_Offsets: " + str(signals["ECG_P_Offsets"][i]))
        print("ECG_Q_Peaks: " + str(signals["ECG_Q_Peaks"][i]))
        print("ECG_R_Onsets: " + str(signals["ECG_R_Onsets"][i]))
        print("ECG_R_Peaks: " + str(signals["ECG_R_Peaks"][i]))
        print("ECG_R_Offsets: " + str(signals["ECG_R_Offsets"][i]))
        print("ECG_S_Peaks: " + str(signals["ECG_S_Peaks"][i]))
        print("ECG_T_Onsets: " + str(signals["ECG_T_Onsets"][i]))
        print("ECG_T_Peaks: " + str(signals["ECG_T_Peaks"][i]))
        print("ECG_T_Offsets: " + str(signals["ECG_T_Offsets"][i]))
        print("ECG_Rate: " + str(signals["ECG_Rate"][i]))

    bio_data_frame = pd.DataFrame({"ECG": ecg_signal})
    nk.signal_plot([bio_data_frame["ECG"]])
    plt.savefig('tmp_pictures/signal_plot.png')
    plt.close()

    signals, info = nk.ecg_process(ecg_signal, sampling_rate=1000)
    plot_custom_ecg(signals, info)

    #send_png_via_udp('signal_plot.png', '127.0.0.1', 5005)
    #send_png_via_udp('ecg_plot.png', '127.0.0.1', 5006)


def plot_custom_ecg(signals, info):
    plt.figure(figsize=(12, 8))
    plt.plot(signals['ECG_Raw'], label='ECG Raw', color='black', linewidth=0.5)
    plt.plot(signals['ECG_Clean'], label='ECG Clean', color='blue', linewidth=1.0)

    # Mark important points
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
    plt.savefig('ecg_plot.png')
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
            print(f"Sent chunk {i+1}/{num_chunks} ({len(chunk)} bytes)")

    finally:
        sock.close()


generate_signal()
