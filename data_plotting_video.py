import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

# --- CONFIGURAZIONE ---
ZOOM_Y_MIN = -0.007
ZOOM_Y_MAX = 0.02
FPS_VIDEO = 30 # Framerate del video finale

# --- PUSH 1N ----
# START_TOUCH = [6.84, 12.73, 19.34, 24, 30.80, 37.49, 47.17, 51.26]
# END_TOUCH = [8.71, 14.13, 20.23, 26.37, 33.93, 42.42, 49.69, 56.79]
# --- PULL 1N ----
# START_TOUCH = [5.07, 9.99, 15.90, 20.10, 26.35, 32.88, 40.79]
# END_TOUCH = [5.60, 12.25, 17.21, 23.08, 29.88, 39.08, 42.43]

# --- PULL 1N RIGID ---
START_TOUCH = [11.92, 15.74, 19.29, 26.55, 39.53, 50.08, 52.29, 
               54.56, 57.55, 61.03, 65.02, 69.89, 75.55, 81.22,
               85.92, 88.32]
END_TOUCH = [14.34, 17.69, 23.31, 34.48, 44.01, 50.88, 53.20, 
            55.74, 59.78, 62.36, 68.82, 71.82, 79.59, 83.28,
            87.52, 92.65]

file_name = "1N_Rigid_Pull/SingleTactSampleData_1778229183.csv"

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
ax.set_title(f'Raw SingleTact 1N Data', fontsize=14)
ax.set_xlabel('Time (seconds)', fontsize=12)
ax.set_ylabel('Force (Newton)', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.7)
fig.tight_layout()

cursor_line = ax.axvline(x=tempo_min, color='blue', linestyle='-', linewidth=2)
current_point, = ax.plot([], [], 'bo', markersize=8)
time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, weight='bold', fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

# 5. Funzione di aggiornamento
def update(frame):
    # Calcoliamo a quale istante di tempo corrisponde il frame del video attuale
    t_video = tempo_min + (frame / FPS_VIDEO)
    
    # Troviamo l'indice del dato reale del sensore più vicino a questo istante
    idx = np.searchsorted(tempi_sensore, t_video)
    
    # Gestione dei bordi e ricerca del più vicino (tra l'indice trovato e il precedente)
    if idx == 0:
        pass
    elif idx == len(tempi_sensore):
        idx = len(tempi_sensore) - 1
    else:
        if abs(t_video - tempi_sensore[idx-1]) < abs(t_video - tempi_sensore[idx]):
            idx = idx - 1
            
    # Estraiamo i valori ESATTI e non alterati misurati dal sensore
    x = tempi_sensore[idx]
    y = forze_sensore[idx]
    
    cursor_line.set_xdata([x])
    current_point.set_data([x], [y])
    time_text.set_text(f'Timestamp Sensore: {x:.3f} s | Valore: {y:.4f} N')
    
    return cursor_line, current_point, time_text

# Generiamo il video
ani = FuncAnimation(fig, update, frames=totale_frames, blit=True)

output_filename = 'video_sensore_tempo_reale.mp4'
writer = FFMpegWriter(fps=FPS_VIDEO, metadata=dict(artist='Sensore'), bitrate=2000)

print(f"Generazione video: durata prevista {durata_reale:.1f} sec a {FPS_VIDEO} FPS (Tot. frames: {totale_frames})...")
ani.save(output_filename, writer=writer)
print(f"Salvato: {output_filename}")

plt.close()