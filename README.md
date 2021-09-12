# snoring_problem

1. Every data for feature_proc and cnn_train is on this link: https://drive.google.com/drive/u/0/folders1i5XQfklGI2aEfct5uFPLxDf9El3c0rcC/
2. The RawData through preprocessing (sound edit) become CalculationData and go to feature_proc to get MFCCData for cnn_train
3. With feature_proc.py:
   + Create new environment name "env" (python 3.6): conda create -n env python=3.6
   + Activate environment "env": conda activate env
   + Run script: python feature_proc.py
4. With cnn_train.ipynb, running the code segment one by one on your collab, note that you've modified your data path before running.
5. Do the same with rnn_train.ipynb
6. The model is save with HDF5 type
