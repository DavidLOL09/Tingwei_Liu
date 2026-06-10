import sys
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/')
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation')
from NuRadioReco.modules.io import NuRadioRecoio
from icecream import ic
import pandas as pd
import polynomial_regression
import matplotlib.pyplot as plt
poly_reger = polynomial_regression.polynomial_regression()
from NuRadioReco.modules.channelLengthAdjuster import channelLengthAdjuster
import numpy as np
from NuRadioReco.framework.parameters import showerParameters as shp
from NuRadioReco.utilities import units
from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.utilities.fft as fft
import NuRadioReco.modules.channelBandPassFilter
from NuRadioReco.framework.parameters import stationParameters as stnp
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()
from NuRadioReco.framework.parameters import channelParameters as chp
import matplotlib
import datetime
import send2trash
import os
import ToolsPac
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter1d
import NuRadioReco.modules.templateDirectionFitter
templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()
from NuRadioReco.detector import detector
det = detector.Detector(json_filename=f'/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation/station51_InfAir.json', assume_inf=False, antenna_by_depth=False)
import custimizedTemplateCorrelation
ic(custimizedTemplateCorrelation.__file__)
Correlation = custimizedTemplateCorrelation.custimizedTemplateCorrelation()
template_path_no_backlope='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_Template_final'
template_path_1_backlope='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_1backL_Template_final'
template_path_2_backlope='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_2backlope_Template_final'
template_path_4_backlope='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/template_4_backlope'
template_path_elder_2='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/template2backlope_bandpass_stopfilter'
Correlation.begin(template_path_2_backlope)

def get_Chi_spectrum(input_path,vip_id=[],if_zen=False):
    reader=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
    for evt in reader.get_events():
        fig,axes = plt.subplots(figsize=(10,8),constrained_layout=True,nrows=3, sharex='col', sharey='col')
        stn = evt.get_station(51)
        iden=f'R{evt.get_run_number()}E{evt.get_id()}'
        if if_zen:
            zenith=stn.get_parameter(stnp.zenith)/units.deg
            suptitle = f'{iden} zen:{zenith:.2f}deg'
        else:
            suptitle = iden
        if vip_id !=[]:
            suptitle = f'{suptitle} candidate: {iden in vip_id}'
        for chn in [4,5,6]:  
            channel = stn.get_channel(chn)
            # Xcorr.append(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])
            Xcorr=channel[chp.cr_xcorrelations]['cr_ref_xcorr_all']
            xcorrelation = channel[chp.cr_xcorrelations]
            ic(xcorrelation.keys())
            bin = range(0,len(Xcorr))
            ax=axes[chn-4]
            ax.plot(bin,Xcorr)
        fig.suptitle(suptitle)
        plt.savefig(f'{os.path.join(input_path,iden)}.png')

def phase_plus(phase1,phase2,phase_max = 255):
    phase = phase1+phase2
    if phase>phase_max:
        return phase-phase_max
    elif phase<0:
        return phase+phase_max
    return phase

def get_gaussian_fit(phase_lst,chi_lst,mu,iteration = 5000):
    half_width = int(len(phase_lst)/2)
    def gaussian(x, A, mu, sigma, C):
        return A * np.exp(-0.5 * ((x - mu) / sigma)**2) + C
    amp0    = np.max(chi_lst)-np.min(chi_lst)
    mu0     = mu
    sigma0  = half_width/3
    C0      = np.min(chi_lst)
    p0      = [amp0,mu0,sigma0,C0]
    popt, pcov = curve_fit(
        gaussian,phase_lst,chi_lst,
        bounds  = ( [0      , mu-0.5,   0.5       , -np.inf   ],
                    [np.inf , mu+0.5,   half_width, np.inf    ]),
        maxfev  = iteration,
        p0      = p0
    )
    A_fit, mu_fit, sigma_fit, C_fit = popt
    errors = np.sqrt(np.diag(pcov)) 
    y_pred = gaussian(phase_lst, *popt)
    ss_res = np.sum((chi_lst - y_pred)**2)
    ss_tot = np.sum((chi_lst - chi_lst.mean())**2)
    r2     = 1 - ss_res / ss_tot
    return [y_pred, np.max(y_pred), r2, errors, popt, mu_fit, phase_lst]

def get_window_arr(arr,center,half_width=25):
    shift = -(center - half_width)   # shift so window starts at left edge
    window = np.roll(arr, shift)[:2*half_width]
    return window

def get_fit_with_window(evt:NuRadioReco.framework.event.Event,slide_range=10,fig_check = False):
    stn = evt.get_station(51)
    if fig_check:
        fig,axes = plt.subplots(figsize=(10,8),constrained_layout=True,nrows=3, sharex='col', sharey='col')
        fig.suptitle(ToolsPac.get_id_info(evt))
    for chn in [4,5,6]:  
        channel = stn.get_channel(chn)
        chi = channel[chp.cr_xcorrelations]['cr_ref_xcorr_all']
        # chi = gaussian_filter1d(chi, sigma=0.5)
        bin = range(0,len(chi))
        chi_max_index = np.argmax(chi)
        fit_lst = []
        for phase in np.linspace(chi_max_index-slide_range,chi_max_index+slide_range,slide_range+1):
            win_chi = get_window_arr(chi,phase)
            win_bin = get_window_arr(bin,phase)
            fit_component = get_gaussian_fit(win_bin,win_chi,phase)
            fit_lst.append(fit_component)
        best = max(fit_lst, key=lambda x: x[1])
        mu = best[5]
        sig = best[4][2]
        if fig_check:
            ax = axes[chn-4]
            ax.plot(best[6],best[0],alpha = 0.8)
            ax.axvline(x=mu, color='red', linestyle='--', linewidth=1, label='peak phase')
            ax.axvline(x=mu-sig, color='blue', linestyle='--', linewidth=1, label='peak phase')
            ax.axvline(x=mu+sig, color='blue', linestyle='--', linewidth=1, label='peak phase')
            ax.plot(bin,chi,zorder = -1)
            ax.set_title(f'chn:{chn}')
    if fig_check:
        plt.show() 
    
    
def apply_direction_reconstruct(evt:NuRadioReco.framework.event.Event,fig_info = [False,'Nothing']):
    stn = evt.get_station(51)
    time = stn.get_station_time()
    det.update(time)
    Correlation.get_fit_with_window(evt,fig_info=fig_info)
    templateDirectionFitter.run(evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)
    zen=stn.get_parameter(stnp.zenith)/units.deg
    azi=stn.get_parameter(stnp.azimuth)/units.rad
    return zen,azi


              

    

candi_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_SNR'
# get_Chi_spectrum(candi_path)
output_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_direct/new_phase_algorithm'
reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(candi_path))
writer = ToolsPac.set_writer(output_path,'new_phase.nur',False)
def apply_precise_phase(reader,writer):
    dir_lst = []
    for evt in reader.get_events():
        # zen,azi = apply_direction_reconstruct(evt,fig_info=[True,'/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR'])
        zen,azi = apply_direction_reconstruct(evt)
        dir_lst.append([zen,azi])
        writer.run(evt)
        
    fig,ax = plt.subplots(1,1,figsize=(10,8),layout='constrained',subplot_kw={'projection': 'polar'})
    ax.set_rlim(0,90)
    direct=np.array(dir_lst)
    zen=direct[:,0]
    azi=direct[:,1]
    # if len(zen)<10000:
    #     al=0.5
    # else:
    #     al=0.1
    # annotate_scatter(ax,azi,zen,Iden)
    ax.scatter(azi,zen,s=40,color='red',label=f'direct:{len(direct)}')
    ax.legend(fontsize=20)
    ic(np.sum(zen>85)/len(zen))
    plt.savefig(os.path.join(output_path,'direct.png'))
apply_precise_phase(reader,writer)
# [y_pred, np.max(y_pred), r2, errors, popt, mu_fit, mu, window_bins]
# popt[A_fit, mu_fit, sigma_fit, C_fit]
def chi_spectrum_with_fit_curve(reader:NuRadioReco.modules.io.NuRadioRecoio.NuRadioRecoio,output_path):
    for evt in reader.get_events():
        iden = ToolsPac.get_id_info(evt)
        fig,axes = plt.subplots(figsize=(10,8),constrained_layout=True,nrows=3, sharex='col', sharey='col')
        stn = evt.get_station(51)
        zen = stn.get_parameter(stnp.zenith)/units.deg
        azi = stn.get_parameter(stnp.azimuth)/units.deg
        fig.suptitle(f'{iden} zen:{zen:.2f} azi:{azi:.2f}')
        for ch in [4,5,6]:
            chn = stn.get_channel(ch)
            chi= chn[chp.cr_xcorrelations]['cr_ref_xcorr_all']
            bin = np.linspace(0,len(chi)-1,len(chi))
            win_phase = chn[chp.cr_xcorrelations]['cr_ref_xcorr_gaussian_fit']['phase']
            win_chi   = chn[chp.cr_xcorrelations]['cr_ref_xcorr_gaussian_fit']['chi']
            fit_info  = chn[chp.cr_xcorrelations]['cr_ref_xcorr_gaussian_fit']['details']
            # mu  = fit_info[5]
            mu = chn[chp.cr_xcorrelations]['cr_ref_xcorr_time_raw']
            sig = fit_info[4][2]
            ax  = axes[ch-4]
            ax.plot(win_phase,win_chi,alpha = 0.8,label=f'$\sigma$:{sig:.2f} $\mu$:{mu:.4f}')
            ax.axvline(x=mu, color='red', linestyle='--', linewidth=1)
            ax.axvline(x=phase_plus(mu,+sig), color='blue', linestyle='--', linewidth=1)
            ax.axvline(x=phase_plus(mu,-sig), color='blue', linestyle='--', linewidth=1)
            ax.plot(bin,chi,zorder = -1)
            ax.set_title(f'chn:{ch}')
            ax.legend()

        def savefig(output_dir,filename):
            try:
                plt.savefig(os.path.join(output_dir,filename))
            except(FileNotFoundError):
                os.makedirs(output_dir)
                plt.savefig(os.path.join(output_dir,filename))

        if zen>30 and zen<40:
            if azi>45 and azi<90:
                savefig(os.path.join(output_path,'sus_dir/chi_spec'),f'{iden}.png')
                continue
        if zen<85:
            savefig(os.path.join(output_path,'good_dir/chi_spec'),f'{iden}.png')
        else:
            savefig(os.path.join(output_path,'fail_dir/chi_spec'),f'{iden}.png')
        # plt.savefig(os.path.join(output_path,f'{zen<85}_{iden}.png'))
# output_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_direct/new_phase_algorithm'
# reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(output_path))
# chi_spectrum_with_fit_curve(reader,output_path)






# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_direct/'
# # ic(ToolsPac.get_input(input_path))
# # reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
# ic(reader.get_n_events())
# get_Chi_spectrum(input_path,if_zen=True)

# ic| np.sum(a>2): np.int64(2)
# ic| fail_num: np.int64(7806)
#     total: 16363
#     fail_num/total: np.float64(0.477051885351097)