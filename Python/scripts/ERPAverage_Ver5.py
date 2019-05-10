from scipy import io
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from BCIToolBox import trigger_downsample

#
#   ERPAverage
#   Author : Simon Kojima
#   Version : 5
#
#   Data : NumSample x NumChannel
#   Time : NumSample x 1
#   Trigger : NumSample x 1
#

PreFileName = "./20181129_B36_Stream/20181129_B36_Stream_"
Files = np.array([1, 3, 5])
#Files = np.array([1])
SelectedTrigger = np.array([4, 8])

Filter = np.array([1, 40])
Filterorder = 2
TimeRange = np.array([-0.1, 0.5])
BaseLineRange = np.array([-0.05, 0])
EEGThreshold = np.array([-100, 100])

DownsampleRate = 2

EOGEnable = True
NumChannel = 64

#PlotDivision = np.array([3, 3])
#PlotPosition = np.array([1, 2, 3, 5, 7, 8, 9])

PlotDivision = np.array([9, 11])
PlotPosition = np.array(
    [4, 8, 13, 15, 17, 19, 21, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47,
     48, 49, 50, 51, 52, 53, 54, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79, 81,
     83, 85, 87, 92, 94, 96])

for i in range(Files.shape[0]):

    #print(i+1)

    filename = PreFileName + '{:0=4}'.format(Files[i])

    print("Loading File : " + filename + ".mat")

    matdata = io.loadmat(filename, squeeze_me=True)

    Data_ = matdata["Data"]
    Fs = matdata["Fs"]
    Trigger_ = matdata["Trigger"]
    nyq = Fs/2

    b, a = signal.butter(Filterorder, Filter/nyq, 'bandpass')
    Data_ = signal.filtfilt(b, a, Data_)

    c, r = Data_.shape
    print("Dimention : " + str(c) + "x" + str(r) + "\n")

    if DownsampleRate != 1:
        Data_ = signal.decimate(Data_, DownsampleRate, axis=1)
        Trigger_ = trigger_downsample(Trigger_, DownsampleRate, 0)
        Fs = Fs/DownsampleRate

    if i == 0:
        Data = Data_
        Trigger = Trigger_
    else:
        Data = np.concatenate((Data, Data_), axis=1)
        Trigger = np.concatenate((Trigger, Trigger_))



nTrigger = [0]*SelectedTrigger.shape[0]
for i in range(SelectedTrigger.shape[0]):
    nTrigger[i] = np.sum(Trigger == SelectedTrigger[i])
    #print(SelectedTrigger[i])


Time = matdata["Time"]
print("Fs : " + str(Fs) + "Hz\n")
EpochData = [0]*SelectedTrigger.shape[0]
BaseLineData = [0]*SelectedTrigger.shape[0]
AveragedData = [0]*SelectedTrigger.shape[0]

if EOGEnable == True:
    #print(Data.shape[-2:])
    EOGData = Data[-2:] # EOG Channel
    Data = Data[:-2] # EEG Channel

if Data.shape[0] != NumChannel:
    print("Error : Number of Channel Does Not Match")
    print("Error : Terminated")
    exit()

for i in range(SelectedTrigger.shape[0]):
    Count = 0
    SingleTriggerEpochData = np.zeros((NumChannel, ((TimeRange[1]-TimeRange[0])*Fs).astype(np.int32), nTrigger[i]))
    BaseLineSingleTriggerEpochData = np.zeros((NumChannel, 1, nTrigger[i]))
    for j in range(Trigger.shape[0]):
        if Trigger[j] == SelectedTrigger[i]:
            SingleTriggerEpochData[:, :, Count] = Data[:, j+(np.floor(TimeRange[0]*Fs)).astype(np.int32):j+(np.floor(TimeRange[1]*Fs)).astype(np.int32)]
            BaseLineSingleTriggerEpochData[:, :, Count] = np.reshape((Data[:, j+(np.floor(BaseLineRange[0]*Fs)).astype(np.int32):j+(np.floor(BaseLineRange[1]*Fs)).astype(np.int32)]).mean(axis=1), (NumChannel, 1))
            Count += 1
        EpochData[i] = SingleTriggerEpochData
        BaseLineData[i] = BaseLineSingleTriggerEpochData
    EpochData[i] = EpochData[i] - BaseLineData[i]

NumAllEpoch = [0]*SelectedTrigger.shape[0]
for i in range(SelectedTrigger.shape[0]):
    #a = np.abs(((EpochData[i]).max(axis=0)).max(axis=0))
    max = ((EpochData[i]).max(axis=0)).max(axis=0)
    min = ((EpochData[i]).min(axis=0)).min(axis=0)
    NumAllEpoch[i] = EpochData[i].shape[2]
    EpochData[i] = np.delete(EpochData[i], np.where((min < EEGThreshold[0]) | (max > EEGThreshold[1])), axis=2)
    print("Trigger No." + str(SelectedTrigger[i]) + ", Accepted Epoch Data : " + str(EpochData[i].shape[2]) + " of " + str(NumAllEpoch[i]))
    #print(EpochData[i].shape)
    #print(a.shape)
    #print(np.where((min < EEGThreshold[0]) | (max > EEGThreshold[1]))[0])
    #print(len(np.where((min < EEGThreshold[0]) | (max > EEGThreshold[1]))[0]))
    #print(EpochData[i].shape)
    AveragedData[i] = (EpochData[i]).mean(axis=2)

SaveMatFile = {}
SaveMatFile["AveragedData"] = AveragedData
io.savemat("AveragedData.mat", SaveMatFile)

#print(len(EpochData))
#print(EpochData[0].shape)
#print(EpochData[0][0].shape)

#print(AveragedData[0].shape)

#exit()

for i in range(NumChannel):
    plt.subplot(PlotDivision[0], PlotDivision[1], PlotPosition[i])
    plt.plot(TimeRange, [0, 0], "black")
    plt.plot([0, 0], [-10, 10], "black")
    plt.plot(np.arange(TimeRange[0], TimeRange[1], 1/Fs), AveragedData[0][i, :], "blue")
    plt.plot(np.arange(TimeRange[0], TimeRange[1], 1/Fs), AveragedData[1][i, :], "red")
    plt.ylim(5, -10)
    plt.xlim(TimeRange[0], TimeRange[1])

plt.show()