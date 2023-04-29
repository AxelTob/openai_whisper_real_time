import pyaudio
import wave
import openai
import threading
import tkinter as tk
import time
import os

# Set up the OpenAI API key
openai.api_key = "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"

# Set up the microphone and wave file
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# Initialize the GUI
root = tk.Tk()
root.title("Real-time Transcription")
root.geometry("600x400")

# Create the GUI widgets
title_label = tk.Label(
    root, text="Real-time Transcription", font=("Helvetica", 20))
title_label.pack(pady=(30, 20))

button_frame = tk.Frame(root, width=600, height=50)
start_stop_button = tk.Button(
    button_frame, text="Start", width=8, height=1, font=("Helvetica", 14))
start_stop_button.pack(side="left", padx=(40, 20), pady=10)
clear_button = tk.Button(button_frame, text="Clear",
                         width=8, height=1, font=("Helvetica", 14))
clear_button.pack(side="left", pady=10)
button_frame.pack()

output_frame = tk.Frame(root, width=600, height=250)
output_text = tk.Text(output_frame, font=("Helvetica", 14), wrap="word")
output_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
output_scrollbar = tk.Scrollbar(output_frame, command=output_text.yview)
output_scrollbar.pack(side="right", fill="y")
output_text.config(yscrollcommand=output_scrollbar.set)
output_frame.pack()

# Set up the recording and transcription variables
transcription_thread = None
recording = False


def transcribe_audio():
    global output_text
    global CHUNK
    global FORMAT
    global CHANNELS
    global RATE
    global RECORD_SECONDS
    global WAVE_OUTPUT_FILENAME
    global recording

    # Open the audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)

    # Continuously record and send audio to the API for transcription
    while recording:
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        # Write data to wave file
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Send the audio file to OpenAI API for transcription
        # Send the audio file to OpenAI API for transcription
        with open(WAVE_OUTPUT_FILENAME, 'rb') as f:
            try:
                transcript = openai.Audio.transcribe("whisper-1", f)
                output_text.insert(tk.END, transcript["text"]+'\n')
            except:
                output_text.insert(
                    tk.END, "Error occurred while transcribing audio.\n")
            finally:
                # Delete the wave file after transcription is done
                f.close()
                os.remove(WAVE_OUTPUT_FILENAME)

        # Update the GUI
        output_text.see(tk.END)
        output_text.update()

        # Wait for a short while before starting next loop iteration
        time.sleep(0.1)

    # Clean up the audio stream
    print("Closing the audio stream...")
    stream.stop_stream()
    stream.close()
    p.terminate()


def start_stop_transcription():
    global transcription_thread
    global recording

    if not recording:
        # Start the transcription
        start_stop_button.config(text="Stop")
        recording = True
        transcription_thread = threading.Thread(target=transcribe_audio)
        transcription_thread.start()
    else:
        # Stop the transcription
        start_stop_button.config(text="Start")
        recording = False


# Add the button commands
start_stop_button.config(command=lambda: start_stop_transcription())
clear_button.config(command=lambda: output_text.delete(1.0, tk.END))

# Start the GUI
root.mainloop()
