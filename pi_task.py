import paho.mqtt.client as mqtt
import wave
import pyaudio
import scipy.io.wavfile as wav
from speechpy.feature import mfcc
import numpy as np
from tflite_runtime.interpreter import Interpreter


MQTT_ADDRESS = '127.0.0.1'
MQTT_TOPIC_POST = 'Lying_posture'
MQTT_TOPIC_SOUND = "Snore_sound"

output_file = 'audio.wav'

def writewavefile(data):
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(data)
        wf.close()


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC_POST)
    client.subscribe(MQTT_TOPIC_SOUND)

sound_data = bytes([])

def on_message(client, userdata, msg):
    global sound_data
    """The callback for when a PUBLISH message is received from the server."""
    if (msg.topic == MQTT_TOPIC_POST):
        print(msg.topic + ' ' + str(msg.payload))
    else:
        # print(int.from_bytes(msg.payload, "big", signed = "True"))
        sound_data += msg.payload
        #print(len(msg.payload))
        if (len(sound_data) == 32000):
            writewavefile(sound_data)
            sound_data = bytes([])
            print("Received one sec")
            predict(output_file)

def split_sequence(sequence, timesteps, stride=5):
    result = []
    for i in range(0, len(sequence) - timesteps + 1, stride):
        result.append(sequence[i:i + timesteps])
    return np.array(result)

timesteps = 16
snore_threshold = 0.5
model_path = "crnn_model_tf2.5.tflite"
interpreter =  Interpreter(model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def predict(file_path):
    fs, data = wav.read(file_path)
    data = np.max(data, axis=1) if data.ndim == 2 else data

    mfccs = mfcc(data, sampling_frequency=fs, frame_length=0.030, frame_stride=0.01,
             num_cepstral=32, num_filters=32, fft_length=512, low_frequency=0, high_frequency=None)
    mfccs = np.expand_dims(np.concatenate(np.expand_dims(split_sequence(mfccs, timesteps=timesteps, stride=timesteps), axis=0), axis=0), axis=3)             
    in_tensor = np.expand_dims(mfccs, axis=0).astype(np.float32)
    interpreter.set_tensor(input_details[0]['index'], in_tensor)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    val = output_data[0][0]
    if val >= snore_threshold:
        print(MQTT_TOPIC_SOUND + ' snore')
    else:
        print(MQTT_TOPIC_SOUND + ' non-snore')


def main():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, port=1883)
    mqtt_client.loop_forever()


if __name__ == '__main__':
    main()
