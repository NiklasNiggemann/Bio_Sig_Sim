import neurokit2 as nk
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt


def get_indices(signal_list):
    indices = []
    for i, value in enumerate(signal_list):
        if value == 1:
            indices.append(i)
    return indices


def normal(duration=5, sampling_rate=1000, noise=0.1, heart_rate=70):
    return nk.ecg_simulate(duration=duration, sampling_rate=sampling_rate, noise=noise, heart_rate=heart_rate)


def atrial_fibrillation(duration=5, sampling_rate=1000, noise=0.1, heart_rate=70, mean=0.001, stddev=0.01):
    ecg_signal = nk.ecg_simulate(duration=duration, sampling_rate=sampling_rate, noise=noise * 2, heart_rate=heart_rate)
    signals, info = nk.ecg_process(ecg_signal)

    ecg_p_onsets = get_indices(signals["ECG_P_Onsets"])
    ecg_p_offsets = get_indices(signals["ECG_P_Offsets"])
    ecg_t_onsets = get_indices(signals["ECG_T_Onsets"])
    ecg_t_offsets = get_indices(signals["ECG_T_Offsets"])

    for i, (p_onset, p_offset) in enumerate(zip(ecg_p_onsets, ecg_p_offsets)):
        ecg_signal[p_onset:p_offset] = np.random.normal(mean, stddev, p_offset - p_onset)

        if i < len(ecg_p_onsets) - 1:
            next_p_onset = ecg_p_onsets[i + 1]
            rr_interval = random.uniform(-0.4, 0.2)
            irregular_interval = int((next_p_onset - p_offset) * rr_interval)
            if irregular_interval > 0:
                ecg_signal[p_offset:p_offset + irregular_interval] = 0

    for t_onset, t_offset in zip(ecg_t_onsets, ecg_t_offsets):
        ecg_signal[t_onset:t_offset] = np.random.normal(mean, stddev, t_offset - t_onset)

    return ecg_signal


def atrial_flutter(duration=5, sampling_rate=1000, noise=0.1, heart_rate=70, mean=0.001, stddev=0.1):

    ecg_signal = nk.ecg_simulate(duration=duration, sampling_rate=sampling_rate, noise=noise * 3, heart_rate=heart_rate)
    signals, info = nk.ecg_process(ecg_signal)

    ecg_p_onsets = get_indices(signals["ECG_P_Onsets"])
    ecg_p_offsets = get_indices(signals["ECG_P_Offsets"])
    ecg_t_onsets = get_indices(signals["ECG_T_Onsets"])
    ecg_t_offsets = get_indices(signals["ECG_T_Offsets"])
    ecg_s_peaks = get_indices(signals["ECG_S_Peaks"])

    for i, p_onset in enumerate(ecg_p_onsets):
        p_offset = ecg_p_offsets[i]
        flutter_wave_length = p_offset - p_onset
        flutter_frequency = 20

        for j in range(p_onset, p_offset):
            time = (j - p_onset) / flutter_wave_length
            flutter_wave = np.sin(2 * np.pi * flutter_frequency * time)
            ecg_signal[j] = flutter_wave * np.random.normal(mean, stddev)

    for i, t_onset in enumerate(ecg_t_onsets):
        t_offset = ecg_t_offsets[i]
        flutter_wave_length = t_offset - t_onset
        flutter_frequency = 14

        for j in range(t_onset, t_offset):
            time = (j - t_onset) / flutter_wave_length
            flutter_wave = np.sin(2 * np.pi * flutter_frequency * time)
            ecg_signal[j] = flutter_wave * np.random.normal(mean, stddev)

    for s_peak in ecg_s_peaks:
        ecg_signal[s_peak] = np.random.normal(mean, stddev)

    return ecg_signal


def heart_attack(duration=5, sampling_rate=1000, noise=0.1, heart_rate=70):
    return nk.ecg_simulate(duration=duration, sampling_rate=sampling_rate, noise=noise, heart_rate=heart_rate)


bio_data_frame = pd.DataFrame({"ECG": atrial_fibrillation()})
nk.signal_plot([bio_data_frame["ECG"]],)
plt.show()