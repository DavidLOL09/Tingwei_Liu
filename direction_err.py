import math
import numpy as np
from NuRadioReco.modules.io import NuRadioRecoio
from NuRadioReco.framework.parameters import eventParameters as evtp
from NuRadioReco.utilities import units
from NuRadioReco.framework.parameters import channelParameters as chp
from icecream import ic
import os
import send2trash
from NuRadioReco.framework.parameters import stationParameters as stnp
import matplotlib.pyplot as plt

def space_angle(loc1,loc2):
    # A*B/|A||B|
    def Sph2Carti(dirct_sp):
        # dirct_sp:[zen,azi]
        zen=dirct_sp[0]
        azi=dirct_sp[1]
        z=np.cos(zen)
        x=np.sin(zen)*np.cos(azi)
        y=np.sin(zen)*np.sin(azi)
        return np.array([x,y,z])
    dir1=Sph2Carti(loc1)
    dir2=Sph2Carti(loc2)
    diff=np.acos(np.dot(dir1,dir2))
    return diff
A=np.array([10,180])
B=np.array([10,0])
ic(np.rad2deg(space_angle(np.deg2rad(A),np.deg2rad(B))))
Zen_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_3Xcorr/X_Ratio_Zen'
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
readARIANNAData = NuRadioRecoio.NuRadioRecoio(get_input(Zen_sim))
error=[]
fig,Axes = plt.subplots(1,2,figsize=(10,8),layout='constrained',subplot_kw={'projection': 'polar'})
ax1=Axes[0]
ax1.set_rlim(0,90)
ax2=Axes[1]
ax2.set_rlim(0,90)
for evt in readARIANNAData.get_events():
    stn = evt.get_station(51)
    run=evt.get_run_number()
    id=evt.get_id()
    zen = stn.get_parameter(stnp.zenith)/units.rad
    azi = stn.get_parameter(stnp.azimuth)/units.rad
    loc1=[zen,azi]
    sim_stn = stn.get_sim_station()
    sim_zen = sim_stn[stnp.zenith]/units.rad
    sim_azi = sim_stn[stnp.azimuth]/units.rad
    loc2=[sim_zen,sim_azi]
    err=space_angle(loc1,loc2)
    error.append(err)
    if err>=np.pi*0.2:
        print(f'R{run}E{id}')
        ic(np.rad2deg(err),np.rad2deg(np.array([zen,azi])),np.rad2deg(np.array([sim_zen,sim_azi])))
        ax1.plot(np.array([sim_azi,azi]),np.rad2deg(np.array([sim_zen,zen])))
        ax1.scatter(np.deg2rad(A[1]),A[0])
        ax1.scatter(np.deg2rad(B[1]),A[0])
        ax1.scatter(sim_azi,np.rad2deg(sim_zen))
        ax1.scatter(azi,np.rad2deg(zen))
    ax2.plot(np.array([sim_azi,azi]),np.rad2deg(np.array([sim_zen,zen])),alpha=0.1)
error=np.rad2deg(np.array(error))
ic(np.max(error),np.min(error),np.mean(error))
plt.show()

# 81 280 recon
# 32 169 sim

# Ratio:
# ic| np.rad2deg(space_angle(np.deg2rad(A),np.deg2rad(B))): np.float64(20.00000000000001)
# ic| np.max(error): np.float64(38.04556554644983)
#     np.min(error): np.float64(0.027367227778181326)
#     np.mean(error): np.float64(5.282495443652419)