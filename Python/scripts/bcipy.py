import numpy as np
import mne

def trigger_downsample(x, r, phase):
    for i in range(phase + r, len(x), r):
        if i == phase + r:
            y = np.sum(x[(i-r):i])
        else:
            y = np.append(y, np.sum(x[(i-r):i]))
    return y

def CSP(Vt,Vnt):
    Ra = np.zeros((Vt.shape[0],Vt.shape[0],Vt.shape[2]))
    Rb = np.zeros((Vnt.shape[0],Vnt.shape[0],Vnt.shape[2]))
    
    for i in range(Vt.shape[2]):
        Ra[:,:,i] = np.dot(Vt[:,:,i],Vt[:,:,i].transpose())/np.trace(np.dot(Vt[:,:,i],Vt[:,:,i].transpose()))
        Rb[:,:,i] = np.dot(Vnt[:,:,i],Vnt[:,:,i].transpose())/np.trace(np.dot(Vnt[:,:,i],Vnt[:,:,i].transpose()))
    
    Ra = np.mean(Ra,axis=2)
    Rb = np.mean(Rb,axis=2)
    
    Rc = Ra + Rb
    
    Lambda,Bc = np.linalg.eig(Rc)
    Lambda = np.diag(Lambda)
    
    W = np.dot(np.sqrt(np.linalg.inv(Lambda)),Bc.transpose())
    
    Sa = np.dot(W,Ra)
    Sa = np.dot(Ra,np.linalg.inv(W))
    
    U,S,V = np.linalg.svd(Sa)
    
    H = np.dot(V.transpose(),W)
    
    return H

def Vectorizer(Data):
    temp = [0]*Data.shape[2]
    if Data.shape[2] == 0:
        return np.zeros(Data.shape[0]*Data.shape[1])
    for i in range(Data.shape[2]):
        temp[i] = np.array([]);
        for j in range(Data.shape[0]):
            temp[i] = np.append(temp[i],Data[j,:,i])
    #print(len(temp))
    vec = temp[0]
    for i in range(1,Data.shape[2]):
        vec = np.vstack((vec,temp[i]));
    return vec

def Epoch(Data,Trigger,Range,SelectedTrigger,Fs):
    Count = 0
    NumChannel = Data.shape[0]
    nTrigger = np.sum(Trigger == SelectedTrigger)
    EpochData = np.zeros((NumChannel, ((Range[1]-Range[0])*Fs).astype(np.int32), nTrigger))
    #BaseLineSingleTriggerEpochData = np.zeros((NumChannel, 1, nTrigger))
    for j in range(Trigger.shape[0]):
        if Trigger[j] == SelectedTrigger:
            EpochData[:, :, Count] = Data[:, j+(np.floor(Range[0]*Fs)).astype(np.int32):j+(np.floor(Range[1]*Fs)).astype(np.int32)]
            #BaseLineSingleTriggerEpochData[:, :, Count] = np.reshape((Data[:, j+(np.floor(BaseLineRange[0]*Fs)).astype(np.int32):j+(np.floor(BaseLineRange[1]*Fs)).astype(np.int32)]).mean(axis=1), (NumChannel, 1))
            Count += 1
        #EpochData = SingleTriggerEpochData
        #BaseLineData[i] = BaseLineSingleTriggerEpochData 
    return EpochData
    
def BaseLine(Data,Trigger,Range,SelectedTrigger,Fs):
    Count = 0
    NumChannel = Data.shape[0]
    nTrigger = np.sum(Trigger == SelectedTrigger)
    #SingleTriggerEpochData = np.zeros((NumChannel, ((Range[1]-Range[0])*Fs).astype(np.int32), nTrigger))
    BaseLineSingleTriggerEpochData = np.zeros((NumChannel, 1, nTrigger))
    for j in range(Trigger.shape[0]):
        if Trigger[j] == SelectedTrigger:
            #SingleTriggerEpochData[:, :, Count] = Data[:, j+(np.floor(Range[0]*Fs)).astype(np.int32):j+(np.floor(Range[1]*Fs)).astype(np.int32)]
            BaseLineSingleTriggerEpochData[:, :, Count] = np.reshape((Data[:, j+(np.floor(Range[0]*Fs)).astype(np.int32):j+(np.floor(Range[1]*Fs)).astype(np.int32)]).mean(axis=1), (NumChannel, 1))
            Count += 1
        #EpochData = SingleTriggerEpochData
        BaseLineData = BaseLineSingleTriggerEpochData
    return BaseLineData
    
    
def getTrig(raw,Ns):
    events = mne.events_from_annotations(raw)[0]
    events = events[1:-1,:]
    Trigger = np.zeros(Ns)
    for i in range(events.shape[0]):
        Trigger[events[i,0]] = events[i,2]
    return Trigger