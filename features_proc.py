import scipy.io.wavfile as wav
import numpy as np 
from speechpy.feature import mfcc
import PIL.Image as img
import os

dataDirName = "/home/huong/SoundCalculationData"
resSnoreDir = dataDirName + "/MFCCDatas/Snoring"
resNonSnoreDir = dataDirName + "/MFCCDatas/NonSnoring"

pathSnoring = "/home/huong/SoundCalculationData/Pre_processData/Snoring"
pathNonSnoring = "/home/huong/SoundCalculationData/Pre_processData/Non-snoring"    

if not os.path.exists(resSnoreDir):
    os.makedirs(resSnoreDir)


if not os.path.exists(resNonSnoreDir):
    os.makedirs(resNonSnoreDir)

for filename in os.listdir(pathSnoring):
    if filename.endswith('.wav'):
        (fs, sig) = wav.read(pathSnoring + "/" + filename)

        #extract mfcc features
        mfcc_feat = mfcc(sig, sampling_frequency=fs, frame_length=0.030, frame_stride=0.01,
         num_cepstral=32, num_filters=32, fft_length=512, low_frequency=0, high_frequency=None)

        outputFile = resSnoreDir + "/" + os.path.splitext(filename)[0] + ".jpg"
        mfcc_data = img.fromarray(mfcc_feat)
        mfcc_data.save(outputFile)

for filename in os.listdir(pathNonSnoring):
    if filename.endswith('.wav'):
        (fs, sig) = wav.read(pathNonSnoring + "/" + filename)

        #extract mfcc features
        mfcc_feat = mfcc(sig, sampling_frequency=fs, frame_length=0.030, frame_stride=0.01,
         num_cepstral=32, num_filters=32, fft_length=512, low_frequency=0, high_frequency=None)

        outputFile = resNonSnoreDir + "/" + os.path.splitext(filename)[0] + ".jpg"
        mfcc_data = img.fromarray(mfcc_feat)
        mfcc_data.save(outputFile)