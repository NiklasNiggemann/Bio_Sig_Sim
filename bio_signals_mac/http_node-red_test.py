import matplotlib.pyplot as plt
import neurokit2 as nk
import pandas as pd
import random
import create_bio_signals


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

    ecg_df = pd.DataFrame({"ECG Raw": signals["ECG_Raw"]})
    nk.signal_plot(ecg_df)
    plt.show()


generate_signal()
