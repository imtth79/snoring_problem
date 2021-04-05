import scipy.io.wavfile as wav
import speechpy
import numpy as np 
import matplotlib.pyplot as plt
import os

pathSnoring = "/home/huong/SoundCalculationData/Pre_processData/Snoring"
pathNonSnoring = "/home/huong/SoundCalculationData/Pre_processData/Non-snoring"    

def loadOneWavFile():
    fs, sig = wav.read(file_name)
    sig = sig[:,0]
    mfcc = speechpy.feature.mfcc(signal, sampling_frequency = fs, frame_length = 0.030, frame_stride = 0.01, num_cepstral = 32,
                        num_filters = 32, fft_length = 512, low_frequency = 0, high_frequency = None)
    return mfcc


def loadRawData():
    label = np.empty((0, 0), dtype=np.uint8)
    features = np.empty((0,2))
    num_feat = 0

    listSnore = os.listdir(pathSnoring)
    listNonSnore = os.listdir(pathNonSnoring)
    
    num_feat = 0
    for id in range(0, len(listSnore)): 
        file_path = os.path.join(pathSnoring, listSnore[id])
        file_name = os.path.join(file_path, 'snoring.wav')
        mfcc_feat = loadOneWavFile(file_name)
        features = np.append(features, mfcc_feat, axis = 0)
        num_feat += mfcc_feat.shape[0]
    label = np.append(label, np.zeros(num_feat))
    
    num_feat = 0
    for id in range(0, len(listNonSnore)): 
        file_path = os.path.join(pathNonSnoring, listNonSnore[id])
        file_name = os.path.join(file_path, 'nonsnoring.wav')
        mfcc_feat = loadOneWavFile(file_name)
        features = np.append(features, mfcc_feat, axis = 0)
        num_feat += mfcc_feat.shape[0]
    label = np.append(label, np.zeros(num_feat))

    index = list(range(features.shape[0]))

    return index, features, label

if __name__ == "__main__":
    index, features, label = loadRawData()
    print(label.shape)
    print(features.shape)