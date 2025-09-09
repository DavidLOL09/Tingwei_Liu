import sys
sys.path.insert(0,'/pub/tingwel4/Tingwei_Liu/NuRadioMC')
from NuRadioReco.modules.base.module import register_run
import numpy as np
import fractions
from icecream import ic
from decimal import Decimal
from NuRadioReco.utilities import units
from scipy import signal
from radiotools import helper as hp
from NuRadioReco.utilities import templates
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import channelParameters as chp
import matplotlib.pyplot as plt
from NuRadioReco.modules.io import NuRadioRecoio
import ToolsPac
import logging
logger = logging.getLogger('custimizedTemplateCorrelation')


class custimizedTemplateCorrelation:
    """
    Calculates correlation of waveform with neutrino/cr templates
    """

    def __init__(self):
        self.__template_trace=[]

    def begin(self, template_directory,debug=False):
        ic(ToolsPac.get_input(template_directory))
        reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(template_directory))
        for evt in reader.get_events():
            stn=evt.get_station(51)
            chn=stn.get_channel(0)
            self.__template_trace.append(chn.get_trace())
        self.__debug = debug

    def get_corr(self,arr1:np.array,arr2:np.array):
        return np.abs(np.dot(arr1,arr2)/np.sqrt(np.dot(arr1,arr1)*np.dot(arr2,arr2)))
    def calculate_xcorr(self,arr2:np.array,arr1:np.array):
        if len(arr1)!=len(arr2):
            raise IndexError('arr1 and arr2 have different length')
        chi_max     = 0
        chi_phase   = 0
        xcorrelation= []
        for i in range(len(arr1)):
            arr_pre = arr1[:i]
            arr_pos = arr1[i:]
            Temp_arr1    = np.concatenate((arr_pos,arr_pre))
            Xcorr   = self.get_corr(Temp_arr1,arr2)
            xcorrelation.append(Xcorr)
                # plot_waveform_compare_pase(arr1,arr2,phase=i,X_max=chi_max,X_now=Xcorr)
            if Xcorr > chi_max:
                chi_max     = Xcorr
                chi_phase   = i
        # plot_waveform_with_phase(arr1,arr2,phase=i,X=chi_max,title='Final')
        return {'xcorrelation':xcorrelation,'chi_max':chi_max,'chi_phase':chi_phase}

    def get_max_xcorr_pac(self,xcorr_lst):
        x_max=0
        x_id=None
        for ix,xcorr in enumerate(xcorr_lst):
            if xcorr['chi_max']>x_max:
                x_max=xcorr['chi_max']
                x_id=ix
        return x_max,xcorr_lst[x_id],x_id
    
    def get_min_xcorr_pac(self,xcorr_lst):
        x_min=1
        x_id=None
        for ix,xcorr in enumerate(xcorr_lst):
            if xcorr['chi_max']<x_min:
                x_min=xcorr['chi_max']
                x_id=ix
        return x_min,xcorr_lst[x_id],x_id
    

    def run(self, evt, channels_to_use=None):
        stn=evt.get_station(51)
        xcorr_chn=[]
        x_id_chn=[]
        for ch_id in channels_to_use:
            chn=stn.get_channel(ch_id)
            trace=chn.get_trace()
            xcorr_chn_temp=[]
            for it,temp in enumerate(self.__template_trace):
                xcorr_chn_temp.append(self.calculate_xcorr(trace,temp))
            _,xcorr_pac,x_id=self.get_max_xcorr_pac(xcorr_chn_temp)
            xcorr_chn.append(xcorr_pac)
            x_id_chn.append(x_id)
        _,_,used_ch_id=self.get_max_xcorr_pac(xcorr_chn)
        used_temp_id=x_id_chn[used_ch_id]
        temp=self.__template_trace[used_temp_id]
        for ch in channels_to_use:
            chn=stn.get_channel(ch)
            trace=chn.get_trace()
            times = chn.get_times()
            dt=times[1]-times[0]
            x_pac=self.calculate_xcorr(trace,temp)
            xcorrelation={}
            xcorrelation['cr_ref_xcorr']=x_pac['chi_max']
            xcorrelation['cr_ref_xcorr_time']=x_pac['chi_phase']*dt
            chn[chp.cr_xcorrelations]=xcorrelation




            

        
