# snoring_problem

1. Every data for feature_proc and cnn_train is on this link: https://drive.google.com/drive/u/0/folders1i5XQfklGI2aEfct5uFPLxDf9El3c0rcC/
2. The RawData through preprocessing (sound edit) become CalculationData and go to feature_proc to get MFCCData for cnn_train
3. With feature_proc.py:
   + Create new environment name "env" (python 3.6): conda create -n env python=3.6
   + Activate environment "env": conda activate env
   + Run script: python feature_proc.py
4. With cnn_train.ipynb, running the code segment one by one on your collab, note that you've modified your data path before running.
5. Do the same with rnn_train.ipynb
6. The model is save with HDF5 type, convert to TFLite file to predict in real world context
7. For the real-time session: 
   + Hardware: RPi 4 Model B
   + Library: PyAudio, Paho MQTT, Runtime Tflite
   + Online Broker: Hivemq (http://www.hivemq.com/demos/websocket-client/)
   + Connect and subcribe topic Lying_posture to the broker
   + Modify your wifi adress and password on the mpureadserial.ino to read the position data and publish to the broker. (ESP8266 work)
   + Run script: python3.7 snoredetect_forever to subcribe the broker and publish both snore status and position information then see the result on the online broker. (RPi work)
