import numpy as np
import speech_recognition as sr
import torch
import wave
import pyaudio

from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform
import string

from faster_whisper import WhisperModel

from threading import Thread, Lock
from queue import Queue

import threading

def playback_thread_func(playback_stream, playback_queue, playback_lock):
    while True:
        if not playback_queue.empty():
            with playback_lock:
                audio_data = playback_queue.get()
            playback_stream.write(audio_data)
        else:
            sleep(0.01)  # Small delay to prevent CPU overuse when queue is empty

# Modified function to add audio data to the playback queue instead of direct playback
def enqueue_audio_for_playback(audio_data, playback_queue, playback_lock):
    with playback_lock:
        playback_queue.put(audio_data)

def play_audio_in_background(audio_data, playback_stream):
    def play_audio():
        playback_stream.write(audio_data)
    # Run the play_audio function in a separate thread
    playback_thread = threading.Thread(target=play_audio)
    playback_thread.start()

def apply_fade(audio_np, fade_in_start, fade_in_end, fade_out_start, fade_out_end):
    # Apply fade in
    fade_in_duration = fade_in_end - fade_in_start
    fade_in_coefficients = np.linspace(0, 1, fade_in_duration)
    audio_np[fade_in_start:fade_in_end] *= fade_in_coefficients

    # Apply fade out
    fade_out_duration = fade_out_end - fade_out_start
    fade_out_coefficients = np.linspace(1, 0, fade_out_duration)
    audio_np[fade_out_start:fade_out_end] *= fade_out_coefficients
    
    return audio_np

def start_recording(playback_queue, playback_lock, keywords, model='medium', non_english='false', energy_threshold=690, record_timeout=1, phrase_timeout=1, default_microphone='pulse', output_filename='output_audio.wav'):
    phrase_time = None
    data_queue = Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = energy_threshold
    recorder.dynamic_energy_threshold = False

    if 'linux' in platform:
        mic_name = default_microphone
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            if mic_name in name:
                source = sr.Microphone(sample_rate=16000, device_index=index)
                break
    else:
        source = sr.Microphone(sample_rate=16000)
        

    model = model if model == "large" or non_english == 'true' else model + ".en"
    audio_model = WhisperModel(model, device="cuda", compute_type="float16")

    transcription = ['']

    # PyAudio setup for playback
    p = pyaudio.PyAudio()
    playback_stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
    
    playback_thread = Thread(target=playback_thread_func, args=(playback_stream, playback_queue, playback_lock))
    playback_thread.start()

    # Open a wave file for writing
    wave_file = wave.open(output_filename, 'wb')
    wave_file.setnchannels(1)  # Mono audio
    wave_file.setsampwidth(2)  # Sample width in bytes
    wave_file.setframerate(16000)  # Frame rate

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData):
        data = audio.get_raw_data()
        data_queue.put(data)
        wave_file.writeframes(data)  # Write audio data to wave file
        

    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    print("Model loaded and recording to", output_filename)


    while True:
        try:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now
                
                # Combine audio data from queue
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()
                
                # Convert in-ram buffer to something the model can use directly without needing a temp file.
                # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
                # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                print('--------------------------------')
                segments, _ = audio_model.transcribe(audio_np)
                
                for segment in segments:
                    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
                    
                    text_arr = [word.lower().strip(string.punctuation) for word in segment.text.split()]
                    
                    found_word = False
                    for word in text_arr:
                        if word in keywords:
                            found_word = True
                            break
 
                if not found_word:
                    # play_audio_in_background(audio_data, playback_stream)
                    # playback_stream.write(audio_data)
                    enqueue_audio_for_playback(audio_data, playback_queue, playback_lock)

                # Infinite loops are bad for processors, must sleep.
                sleep(0.05)
        except KeyboardInterrupt:
            break

    print("\n\nTranscription:")
    for line in transcription:
        print(line)

    # Clean up
    playback_stream.stop_stream()
    playback_stream.close()
    p.terminate()
    print("Recording complete. Check the output directory for audio files.")


def run(keywords, debug=False):
    if debug:
        print('Running in debug mode')
        print('CUDA available:', torch.cuda.is_available())
        
    # Initialize a queue and a lock for thread-safe operations
    playback_queue = Queue()
    playback_lock = Lock()
    
    start_recording(playback_queue, playback_lock, keywords)