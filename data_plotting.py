import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURAZIONE ---
ZOOM_Y_MIN = -0.02
ZOOM_Y_MAX = 0.02
FPS_VIDEO = 30 # Framerate del video finale

# --- PUSH 1N ----
# START_TOUCH = [6.84, 12.73, 19.34, 24, 30.80, 37.49, 47.17, 51.26]
# END_TOUCH = [8.71, 14.13, 20.23, 26.37, 33.93, 42.42, 49.69, 56.79]
# --- PULL 1N ----
# START_TOUCH = [5.07, 9.99, 15.90, 20.10, 26.35, 32.88, 40.79]
# END_TOUCH = [5.60, 12.25, 17.21, 23.08, 29.88, 39.08, 42.43]

# --- PULL 1N RIGID ---
# START_TOUCH = [11.92, 15.74, 19.29, 26.55, 39.53, 50.08, 52.29, 
#                54.56, 57.55, 61.03, 65.02, 69.89, 75.55, 81.22,
#                85.92, 88.32]
# END_TOUCH = [14.34, 17.69, 23.31, 34.48, 44.01, 50.88, 53.20, 
#             55.74, 59.78, 62.36, 68.82, 71.82, 79.59, 83.28,
#             87.52, 92.65]

START_TOUCH = []
END_TOUCH = []

file_name = "noise/noise_1N_rigid_down.csv"

# 1. Lettura dati e pulizia
df = pd.read_csv(file_name, sep=";", skiprows=2, decimal=",")
df.columns = [c.strip() for c in df.columns]

col_tempo = 'Time(s)'
col_forza = 'COM5 - PPS Sensor (N)'
df = df.dropna(subset=[col_tempo, col_forza])

# 2. Taglio dei dati prima del reset
time_diff = df[col_tempo].diff()
reset_indices = df.index[time_diff < 0].tolist()

if reset_indices:
    start_idx = reset_indices[-1]
    df = df.iloc[start_idx:].reset_index(drop=True)

# Estraiamo i dati grezzi
tempi_sensore = df[col_tempo].values
forze_sensore = df[col_forza].values

# 3. CALCOLO DURATA REALE E FRAME TOTALI
tempo_min = tempi_sensore[0]
tempo_max = tempi_sensore[-1]
durata_reale = tempo_max - tempo_min

# Il numero di frame dipende dalla durata reale dei dati
totale_frames = int(durata_reale * FPS_VIDEO)

# 4. Creazione Grafico
fig, ax = plt.subplots(figsize=(12, 6))

# --- NUOVA AGGIUNTA: Sfondo verde per i tocchi ---
# Zippiamo le due liste per avere le coppie di inizio e fine
for i, (inizio, fine) in enumerate(zip(START_TOUCH, END_TOUCH)):
    # Aggiungiamo la label solo al primo per evitare duplicati nella legenda
    label = 'Touch Interval' if i == 0 else None
    ax.axvspan(inizio, fine, color='lightgreen', alpha=0.4, label=label)
# --------------------------------------------------

ax.plot(tempi_sensore, forze_sensore, label='Sensor (N)', color='red', linewidth=1.5, alpha=0.6)

ax.set_xlim(tempo_min, tempo_max)
ax.set_ylim(ZOOM_Y_MIN, ZOOM_Y_MAX)
ax.set_title('Raw SingleTact 1N Data', fontsize=14)
ax.set_xlabel('Time (seconds)', fontsize=12)
ax.set_ylabel('Force (Newton)', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.7)

# Aggiungiamo la legenda per rendere chiaro il significato della banda verde
ax.legend(loc='upper right')

fig.tight_layout()

# 5. Mostra il grafico
plt.show()