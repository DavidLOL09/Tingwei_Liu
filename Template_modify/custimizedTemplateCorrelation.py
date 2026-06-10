import sys
from NuRadioReco.modules.base.module import register_run
import numpy as np
import fractions
from decimal import Decimal
from NuRadioReco.utilities import units
from scipy import signal
from radiotools import helper as hp
from NuRadioReco.utilities import templates
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import channelParameters as chp
import matplotlib.pyplot as plt
from NuRadioReco.modules.io import NuRadioRecoio
import NuRadioReco
import ToolsPac
import logging
from scipy.optimize import curve_fit
from icecream import ic
import os
logger = logging.getLogger('custimizedTemplateCorrelation')


class custimizedTemplateCorrelation:
    """
    Calculates correlation of waveform with neutrino/cr templates
    """

    def __init__(self):
        self.__template_trace=[]

    def begin(self, template_directory,debug=False):
        reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(template_directory))
        self.__template_trace=[]
        for evt in reader.get_events():
            stn=evt.get_station(51)
            chn=stn.get_channel(0)
            self.__template_trace.append(chn.get_trace())
        self.__debug = debug
    def get_template_size(self):
        return len(self.__template_trace)
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

    

    def run(self, evt, channels_to_use=None, gauss_check=False):
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
            xcorrelation['cr_ref_xcorr_all']=x_pac['xcorrelation']
            chn[chp.cr_xcorrelations]=xcorrelation

    def phase_plus(self,phase1,phase2,phase_max = 255):
        phase = phase1+phase2
        if phase>phase_max:
            return phase-phase_max
        elif phase<0:
            return phase+phase_max
        return phase

    def get_gaussian_fit(self,phase_lst,chi_lst,mu,iteration = 5000):
        half_width = int(len(phase_lst)/2)
        def gaussian(x, A, mu, sigma, C):
            return A * np.exp(-0.5 * ((x - mu) / sigma)**2) + C
        amp0    = np.max(chi_lst)-np.min(chi_lst)
        mu0     = half_width
        sigma0  = half_width/3
        C0      = np.min(chi_lst)
        p0      = [amp0,mu0,sigma0,C0]
        popt, pcov = curve_fit(
            gaussian,phase_lst,chi_lst,
            bounds=([0      , mu0-0.5,   0.5       , -np.inf   ],
                    [np.inf , mu0+0.5,   half_width, np.inf    ]),
            maxfev = iteration,
            p0=p0
        )
        A_fit, mu_fit, sigma_fit, C_fit = popt
        errors = np.sqrt(np.diag(pcov)) 
        y_pred = gaussian(phase_lst, *popt)
        ss_res = np.sum((chi_lst - y_pred)**2)
        ss_tot = np.sum((chi_lst - chi_lst.mean())**2)
        r2     = 1 - ss_res / ss_tot
        return [y_pred, np.max(y_pred), r2, errors, popt, mu_fit, mu]

    def get_window_arr(self,arr,center,half_width=25):
        shift = -(center - half_width)   # shift so window starts at left edge
        window = np.roll(arr, shift)[:2*half_width]
        return window

    def adjust_255_0(self,evt:NuRadioReco.framework.event.Event):
        def find_largest_gap_start(mus, period=256):
            angles = sorted((mu / period) * 2 * np.pi for mu in mus)
            gaps = np.diff(angles, append=angles[0] + 2 * np.pi)
            return angles[np.argmax(gaps)]  # angle just BEFORE the largest gap

        def fix_wrap(mus, period=256):
            """
            Rotate all values so the largest gap straddles 0.
            Now no signal sits near the 0/255 boundary → safe to subtract directly.
            """
            shift_angle = find_largest_gap_start(mus)
            shift_mu    = shift_angle * period / (2 * np.pi)

            return [round(shift_mu-mu,8) % period for mu in mus]
        stn = evt.get_station(51)
        mus = []
        for chn in [4,5,6]:
            ch = stn.get_channel(chn)
            mus.append(ch[chp.cr_xcorrelations]['cr_ref_xcorr_time_raw'])
        mus = fix_wrap(mus)
        for chn in [4,5,6]:
            ch = stn.get_channel(chn)
            times = ch.get_times()
            dt=times[1]-times[0]
            ch[chp.cr_xcorrelations]['cr_ref_xcorr_time'] = (mus[chn-4]+128)*dt

        

    def get_fit_with_window(self,evt:NuRadioReco.framework.event.Event,slide_range=10,fig_info=[False,'Nothing']):
        stn = evt.get_station(51)
        iden = ToolsPac.get_id_info(evt)
        fig_check = fig_info[0]
        fig_path = fig_info[1]
        if fig_check:
            fig,axes = plt.subplots(figsize=(10,8),constrained_layout=True,nrows=3, sharex='col', sharey='col')
            fig.suptitle(f'{iden}')
        for chn in [4,5,6]:  
            channel = stn.get_channel(chn)
            chi = channel[chp.cr_xcorrelations]['cr_ref_xcorr_all']
            # chi = gaussian_filter1d(chi, sigma=0.5)
            bin = range(0,len(chi))
            chi_max_index = np.argmax(chi)
            fit_lst = []
            for phase in np.linspace(chi_max_index-slide_range,chi_max_index+slide_range,slide_range+1):
                win_chi = self.get_window_arr(chi,phase)
                win_bin = self.get_window_arr(bin,phase)
                length = len(win_bin)
                fit_component = self.get_gaussian_fit(np.linspace(0,length-1,length),win_chi,phase)
                fit_component.append(win_bin)
                fit_lst.append(fit_component)
            
            best = max(fit_lst, key=lambda x: x[1])
            half_width = int(len(best[0])/2)
            mu = self.phase_plus(self.phase_plus(best[5],-half_width),best[6])
            best[5] = mu
            sig = best[4][2]
            times = channel.get_times()
            dt=times[1]-times[0]
            channel[chp.cr_xcorrelations]['cr_ref_xcorr_time_raw'] = mu
            channel[chp.cr_xcorrelations]['cr_ref_xcorr_time_sig'] = sig*dt
            channel[chp.cr_xcorrelations]['cr_ref_xcorr_gaussian_fit']          = {}
            channel[chp.cr_xcorrelations]['cr_ref_xcorr_gaussian_fit']['phase'] = best[7]
            channel[chp.cr_xcorrelations]['cr_ref_xcorr_gaussian_fit']['chi']   = best[0]
            channel[chp.cr_xcorrelations]['cr_ref_xcorr_gaussian_fit']['details']   = best

            if fig_check:
                ax = axes[chn-4]
                ax.plot(best[7],best[0],alpha = 0.8,label=f'$\sigma$:{sig:.2f}')
                ax.axvline(x=mu, color='red', linestyle='--', linewidth=1)
                ax.axvline(x=self.phase_plus(mu,+sig), color='blue', linestyle='--', linewidth=1)
                ax.axvline(x=self.phase_plus(mu,-sig), color='blue', linestyle='--', linewidth=1)
                ax.plot(bin,chi,zorder = -1)
                ax.set_title(f'chn:{chn}')
                ax.legend()
        self.adjust_255_0(evt)
        if fig_check:
            plt.savefig(os.path.join(fig_path,f'{iden}.png'))
        


                

            

        




            

        
