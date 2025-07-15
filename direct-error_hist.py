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

input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_bef_cut_no_Incorp/sim_bef_cut'
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_3Xcorr/X_33Xcorr'
output_path=''
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
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
readARIANNAData=NuRadioRecoio.NuRadioRecoio(get_input(input_path))
error=[]
weights=[]
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
    weights.append(evt.get_parameter(evtp.event_rate))
fig,ax=plt.subplots(1,1,figsize=(8,8))
ax.set_title('Direction_error_hist')
ax.set_xlabel(r'd${\theta}$')
ax.hist(np.rad2deg(error),bins=1200,weights=weights)
plt.show()