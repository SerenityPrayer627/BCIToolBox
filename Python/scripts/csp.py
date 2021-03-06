import numpy as np

Vt = np.random.rand(7,300,100)
Vnt = np.random.rand(7,300,100)

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