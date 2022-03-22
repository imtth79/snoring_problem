import pyaudio
import wave
import scipy.io.wavfile as wav
from speechpy.feature import mfcc
import numpy as np
from tflite_runtime.interpreter import Interpreter
import paho.mqtt.client as mqtt

MQTT_ADDRESS = 'broker.mqttdashboard.com'
MQTT_TOPIC = 'Lying_posture'


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)

posture = ''
snore_status = ''

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_ADDRESS, 1883)


chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
seconds = 1
filename = "output.wav"


p = pyaudio.PyAudio()  # Create an interface to PortAudio

# model setup
def split_sequence(sequence, timesteps, stride=5):
    result = []
    for i in range(0, len(sequence) - timesteps + 1, stride):
        result.append(sequence[i:i + timesteps])
    return np.array(result)

snore_threshold = 0.5
model_path = "crnn_model_tf2.5.tflite"
interpreter =  Interpreter(model_path)

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
g_quit = False

while not g_quit:
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

    timesteps = 16
    mfccs = np.expand_dims(np.concatenate(np.expand_dims(split_sequence(mfccs, timesteps=timesteps, stride=timesteps), axis=0), axis=0), axis=3)

    # in_tensor = np.float32(mfccs.reshape(1, mfccs.shape[0], mfccs.shape[1], mfccs.shape[2], mfccs.shape[3]))
    in_tensor = np.expand_dims(mfccs, axis=0).astype(np.float32)

    interpreter.set_tensor(input_details[0]['index'], in_tensor)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    val = output_data[0][0]
    if val >= snore_threshold:
        snore_status = 'snore'
    else:
        snore_status = 'non-snore'
    mqtt_client.publish(MQTT_TOPIC, snore_status)

# Terminate the PortAudio interface
p.terminate()