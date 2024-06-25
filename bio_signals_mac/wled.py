import time
import numpy as np
import requests
import json
import create_bio_signals as ecg


def normalize_ecg_data(ecg_data, matrix_height=8):
    min_val = np.min(ecg_data)
    max_val = np.max(ecg_data)
    normalized_data = (ecg_data - min_val) / (max_val - min_val) * (matrix_height - 1)
    return np.round(normalized_data).astype(int)


def map_ecg_to_matrix(normalized_data, matrix_width=8):
    matrix = np.zeros((8, 8), dtype=int)
    for i in range(min(len(normalized_data), matrix_width)):
        row = normalized_data[i]
        matrix[row, i] = 1
    return matrix


def send_matrix_to_wled(matrix, wled_ip):
    payload = {"seg": [{"i": []}]}
    for col in range(matrix.shape[1]):
        for row in range(matrix.shape[0]):
            if matrix[row, col] == 1:
                payload["seg"][0]["i"].append([col + row * matrix.shape[1], 255, 255, 255])
            else:
                payload["seg"][0]["i"].append([col + row * matrix.shape[1], 0, 0, 0])

    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"http://{wled_ip}/json/state", headers=headers, data=json.dumps(payload))
    return response.status_code


def main():
    ecg_data = ecg.normal()
    normalized_data = normalize_ecg_data(ecg_data)
    window_size = 8
    wled_ip = '192.168.1.100'

    for i in range(len(normalized_data) - window_size + 1):
        matrix = map_ecg_to_matrix(normalized_data[i:i + window_size])
        status = send_matrix_to_wled(matrix, wled_ip)
        print(f"Status: {status}")
        time.sleep(1)


if __name__ == "__main__":
    main()