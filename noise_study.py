import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# --- GLOBAL VARIABLES ---
# Define your sensor's maximum range here (used for percentage calculations)
SENSOR_RANGE = 1.0  # Example: 500 N 

# 1. Upload CSV file
# file_path = 'data/noise_down_face.csv'
file_path = 'noise/noise_1N_down.csv'

try:
    df = pd.read_csv(file_path, sep=';', skiprows=2, decimal=',')
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found. Please check the file path and try again.")
    exit()

# Rename the columns for easier access
time_col = df.columns[0]
sensor_col = df.columns[1]

# Drop rows with NaN values
df = df.dropna(subset=[time_col, sensor_col]).reset_index(drop=True)


# 2. Timer Reset Logic
# Detect where the timer drops (e.g., from a high value back to 0 or close to it)
time_diff = df[time_col].diff()
reset_points = df[time_diff < 0].index

if len(reset_points) > 0:
    first_reset_idx = reset_points[0]
    print(f"[*] Timer reset detected at index {first_reset_idx}. Dropping prior samples.")
    # Keep only data from the reset point onwards
    df = df.iloc[first_reset_idx:].reset_index(drop=True)
else:
    print("[*] No timer reset detected. Proceeding from the beginning.")

# Normalize time so the new "Start" is exactly at t = 0s
df[time_col] = df[time_col] - df[time_col].iloc[0]


# 3. First Noise Study (Uncalibrated Data)
# Skip first 5s, analyze the next 10s (from t=5s to t=15s)
# study1_start = 5.0
# study1_end = 15.0

# df_study1 = df[(df[time_col] >= study1_start) & (df[time_col] <= study1_end)]
# y1 = df_study1[sensor_col].values

# if len(y1) == 0:
#     print("Error: No data found in the first study window (5s - 15s).")
#     exit()

# # Compute initial baseline parameters
# mean_baseline = np.mean(y1)
# std_baseline = np.std(y1, ddof=1)
# std_baseline_pct = (std_baseline / SENSOR_RANGE) * 100

# print("\n--- PHASE 1: BASELINE NOISE STUDY (5s to 15s) ---")
# print(f"Samples analyzed     : {len(y1)}")
# print(f"Mean (Baseline)      : {mean_baseline:.6f} N")
# print(f"Std Dev              : {std_baseline:.6f} N")
# print(f"Std Dev (% of Range) : {std_baseline_pct:.4f} %")


# 4. Calibration & Second Noise Study
# Apply calibration: Subtract the baseline mean (Offset Zeroing)
# df['calibrated_sensor'] = df[sensor_col] - mean_baseline
df['calibrated_sensor'] = df[sensor_col]

# Analyze the next 2 minutes (120 seconds) after the first study ends (from t=15s to t=135s)
study2_start = 5.0
study2_end = 135.0 

df_study2 = df[(df[time_col] >= study2_start) & (df[time_col] <= study2_end)]
y2_cal = df_study2['calibrated_sensor'].values

if len(y2_cal) == 0:
    print("Error: No data found in the second study window (15s - 135s).")
    exit()

mean_calibrated = np.mean(y2_cal)
std_calibrated = np.std(y2_cal, ddof=1)
std_calibrated_pct = (std_calibrated / SENSOR_RANGE) * 100
threshold_3sigma_pct = ((3 * std_calibrated) / SENSOR_RANGE) * 100

print(f"\n--- PHASE 2: CALIBRATED NOISE STUDY ({study2_start}s to {study2_end}s) ---")
print(f"Samples analyzed     : {len(y2_cal)}")
print(f"Mean (Should be ~0)  : {mean_calibrated:.6f} N")
print(f"Std Dev              : {std_calibrated:.6f} N")
print(f"Std Dev (% of Range) : {std_calibrated_pct:.4f} %")
print(f"Noise Threshold (3 Sigma): {3 * std_calibrated:.6f} N ({threshold_3sigma_pct:.4f} %)")


# 5. Visualizations
plt.figure(figsize=(14, 8))

# Background: Show the full uncalibrated raw data as a faded line
plt.plot(df[time_col], df[sensor_col], color='lightgray', linewidth=1, label='Raw Data (Full)')

# Highlight Study 1 (Raw Baseline)
# plt.plot(df_study1[time_col], df_study1[sensor_col], color='#d62728', linewidth=1.5, 
#          label='Phase 1: Baseline Extraction')

# Highlight Study 2 (Calibrated Data)
# Note: We plot it on the same graph to visually see the drop to Zero
plt.plot(df_study2[time_col], df_study2['calibrated_sensor'], color='#2ca02c', linewidth=1.5, 
         label='Phase 2: Calibrated Data (~0 N)')

# Delineation Lines
# plt.axvline(study1_start, color='black', linestyle='--', alpha=0.6, label='5s: Start Baseline')
# plt.axvline(study1_end, color='blue', linestyle='--', alpha=0.6, label='15s: Apply Calibration')
plt.axvline(study2_end, color='purple', linestyle='--', alpha=0.6, label='135s: End Study')

plt.title('Sensor Calibration Pipeline & Noise Analysis')
plt.xlabel('Time (s) [From Timer Reset]')
plt.ylabel('Force (N)')
plt.xlim(0, study2_end + 10)
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc='upper right')

plt.tight_layout()
plt.show()