import pyaudio
import wave
import scipy.io.wavfile as wav
from speechpy.feature import mfcc
import numpy as np
from tflite_runtime.interpreter import Interpreter

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
seconds = 1
filename = "output.wav"

p = pyaudio.PyAudio()  # Create an interface to PortAudio

print('Recording')

stream = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input=True)

frames = []  # Initialize array to store frames

# Store data in chunks for 3 seconds    
for i in range(0, int(fs / chunk * seconds)):
    data = stream.read(chunk)
    frames.append(data)

# Stop and close the stream 
stream.stop_stream()
stream.close()
# Terminate the PortAudio interface
p.terminate()

print('Finished recording')

# Save the recorded data as a WAV file
wf = wave.open(filename, 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(fs)
wf.writeframes(b''.join(frames))
wf.close()

#Read the WAV file data to predict
fs, data = wav.read('output.wav') 
data = np.max(data, axis=1) if data.ndim == 2 else data

mfccs = mfcc(data, sampling_frequency=fs, frame_length=0.030, frame_stride=0.01,
         num_cepstral=32, num_filters=32, fft_length=512, low_frequency=0, high_frequency=None)

def split_sequence(sequence, timesteps, stride=5):
    result = []
    for i in range(0, len(sequence) - timesteps + 1, stride):
        result.append(sequence[i:i + timesteps])
    return np.array(result)

timesteps = 16
mfccs = np.expand_dims(np.concatenate(np.expand_dims(split_sequence(mfccs, timesteps=timesteps, stride=timesteps), axis=0), axis=0), axis=3)
snore_threshold = 0.5
model_path = "crnn_model_tf2.5.tflite"
interpreter =  Interpreter(model_path)

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# in_tensor = np.float32(mfccs.reshape(1, mfccs.shape[0], mfccs.shape[1], mfccs.shape[2], mfccs.shape[3]))
in_tensor = np.expand_dims(mfccs, axis=0).astype(np.float32)

interpreter.set_tensor(input_details[0]['index'], in_tensor)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])
val = output_data[0][0]
if val >= snore_threshold:
    print('snore')
else:
    print('non-snore')