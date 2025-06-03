import sounddevice as sd
import numpy as np
import os
import sys
import time
from scipy.io.wavfile import write
from pydub import AudioSegment
from datetime import datetime
from colorama import init, Fore, Style
from threading import Thread
import pystray
from PIL import Image

init()

# Configuración
THRESHOLD = 0.008
SILENCE_LIMIT = 5
MIN_SILENCE_TRIGGER = 0.5
RATE = 44100
CHUNK = 1024
MICROFONO_INDEX = 2  # Cambiá por el tuyo

# Íconos
icono_idle = Image.open("idle.ico")
icono_recording = Image.open("recording.ico")
icon = pystray.Icon("MonitorNotas", icono_idle, "Monitor de Voz")

# Estados
grabando = False
pausado = False
deteniendo = False
contando_silencio = False

# Buffers y control
audio_buffer = []
segundos_restantes = SILENCE_LIMIT
segundos_silencio_total = 0
segundos_silencio_efectivo = 0

def cambiar_icono_grabando():
    icon.icon = icono_recording
    icon.title = "Grabando..."

def cambiar_icono_idle():
    icon.icon = icono_idle
    icon.title = "Esperando voz..."

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_date_folder():
    return datetime.now().strftime("%Y-%m-%d")

def detect_voice(audio_chunk):
    volume_norm = np.linalg.norm(audio_chunk) / len(audio_chunk)
    return volume_norm > THRESHOLD, volume_norm

def imprimir_en_linea(texto):
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.write(texto)
    sys.stdout.flush()

def guardar_mp3(wav_path):
    sound = AudioSegment.from_wav(wav_path)
    mp3_path = wav_path.replace(".wav", ".mp3")
    sound.export(mp3_path, format="mp3")
    os.remove(wav_path)
    print(Fore.GREEN + f"\nGuardado: {mp3_path}" + Style.RESET_ALL)

def pausar(icon, item):
    global pausado
    pausado = True
    cambiar_icono_idle()
    print(Fore.YELLOW + "\n[PAUSADO]" + Style.RESET_ALL)

def reanudar(icon, item):
    global pausado
    pausado = False
    print(Fore.YELLOW + "\n[REANUDADO]" + Style.RESET_ALL)

def salir(icon, item):
    global deteniendo
    deteniendo = True
    icon.stop()

def iniciar_icono_bandeja():
    icon.menu = pystray.Menu(
        pystray.MenuItem("Pausar", pausar),
        pystray.MenuItem("Reanudar", reanudar),
        pystray.MenuItem("Salir", salir)
    )
    icon.run()

def grabar():
    global grabando, pausado, contando_silencio
    global audio_buffer, segundos_restantes
    global segundos_silencio_total, segundos_silencio_efectivo

    print(Fore.CYAN + "Micrófono en uso: " + sd.query_devices(MICROFONO_INDEX)['name'] + Style.RESET_ALL)
    print(Fore.YELLOW + "Esperando voz..." + Style.RESET_ALL)

    with sd.InputStream(samplerate=RATE, channels=1, dtype='float32', device=MICROFONO_INDEX) as stream:
        while not deteniendo:
            if pausado:
                time.sleep(0.1)
                continue

            audio_chunk, _ = stream.read(CHUNK)
            audio_chunk = audio_chunk.flatten()

            voz_detectada, volumen = detect_voice(audio_chunk)
            imprimir_en_linea(Fore.WHITE + f"Volumen detectado: {volumen:.4f}" + Style.RESET_ALL)

            if voz_detectada:
                segundos_silencio_total = 0
                if not grabando:
                    print(Fore.RED + "\n¡Voz detectada! Comenzando a grabar..." + Style.RESET_ALL)
                    grabando = True
                    audio_buffer = []
                    segundos_restantes = SILENCE_LIMIT
                    segundos_silencio_efectivo = 0
                    contando_silencio = False
                    cambiar_icono_grabando()
                elif contando_silencio:
                    print(Fore.GREEN + "\nVoz retomada. Cancelando cuenta regresiva." + Style.RESET_ALL)
                    segundos_restantes = SILENCE_LIMIT
                    segundos_silencio_efectivo = 0
                    contando_silencio = False

                audio_buffer.append(audio_chunk)

            elif grabando:
                audio_buffer.append(audio_chunk)
                segundos_silencio_total += CHUNK / RATE

                if not contando_silencio and segundos_silencio_total >= MIN_SILENCE_TRIGGER:
                    print(Fore.MAGENTA + f"\nSilencio sostenido detectado. Iniciando cuenta regresiva..." + Style.RESET_ALL)
                    segundos_silencio_efectivo = 0
                    contando_silencio = True

                if contando_silencio:
                    segundos_silencio_efectivo += CHUNK / RATE
                    if int(segundos_silencio_efectivo) >= SILENCE_LIMIT - segundos_restantes + 1:
                        segundos_restantes -= 1
                        imprimir_en_linea(Fore.MAGENTA + f"Silencio... {segundos_restantes} segundos restantes." + Style.RESET_ALL)

                    if segundos_restantes <= 0:
                        print(Fore.BLUE + "\nSilencio prolongado. Guardando archivo..." + Style.RESET_ALL)
                        grabando = False
                        contando_silencio = False
                        segundos_silencio_total = 0
                        segundos_silencio_efectivo = 0
                        segundos_restantes = SILENCE_LIMIT

                        audio_data = np.concatenate(audio_buffer)
                        carpeta = get_date_folder()
                        if not os.path.exists(carpeta):
                            os.makedirs(carpeta)
                        wav_filename = os.path.join(carpeta, f"{get_timestamp()}.wav")
                        write(wav_filename, RATE, audio_data)
                        guardar_mp3(wav_filename)
                        print(Fore.YELLOW + "Esperando nueva voz..." + Style.RESET_ALL)
                        cambiar_icono_idle()

if __name__ == "__main__":
    Thread(target=iniciar_icono_bandeja, daemon=True).start()
    grabar()
