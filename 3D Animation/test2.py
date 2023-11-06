import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import h5py




f = h5py.File('/mnt/data0/sEEG_DATA/MCW-FH_006/Imaging/Registered DICOM 10 (Meg)/Electrodes.mat','r') 
test = f['ElecMapRaw']
strs=[]
for i in range(len(test[0])):
    st = test[0][i]
    obj = f[st]
    chrs = []
    for j in range(len(obj[:])):
        chrs.append(chr(obj[:][j][0]))
    str1 = ""
    for x in range(len(chrs)):
        str1 = str1 + chrs[x]
    strs.append(str1)
for i in range(len(strs)):
    print(strs[i][0])
    if len(strs[i])==3 and strs[i][0] != "m":
        strs[i] = strs[i][0]+strs[i][1]+"0"+strs[i][2]
print(strs)


#f[struArray['name'][0, 0]].value  # this is the actual data
