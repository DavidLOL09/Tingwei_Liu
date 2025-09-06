import os
import numpy as np
import astrotools.auger as auger
from icecream import ic
import sys
# sys.path.insert(0,'/Users/david/PycharmProjects/Demo1/Research/Repository/NuRadioMC')
sys.path.insert(0,'/pub/tingwel4/Tingwei_Liu/NuRadioMC')
import NuRadioReco
ic(f'line11{NuRadioReco.__file__}')
from NuRadioReco.modules.io import NuRadioRecoio
import matplotlib.pyplot as plt
from NuRadioReco.utilities import units
from pathlib import Path
from NuRadioReco.framework.parameters import showerParameters as shp
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.modules.io.eventWriter
evt_writer = NuRadioReco.modules.io.eventWriter.eventWriter()

def getTriggerRatePerBin(simulation_files_folder, e_bins, zen_bins, trigger_names):
    # simulation_files_folder   : path/to/simulation/files --NOTE!: The simulation needs to be configured to save non-triggering events too
    # e_bins                    : list of energy bin edges, in log10
    # zen_bins                  : list of zenith bin edges, in whatever format files are saved in (sin2val for IceTop)
    # trigger_names             : list of strings of trigger names
    ###
    # returns
    # trig_rate_per_bin         : dictionary of a 2D numpy array of trigger rate per bin in energy/zenith per trigger name

    trig_rate_per_bin = {}
    n_trig_per_bin = {}
    for trigger in trigger_names:
        trig_rate_per_bin[trigger] = np.zeros((len(zen_bins)-1,len(e_bins)-1))
        n_trig_per_bin[trigger] = np.zeros((len(zen_bins)-1,len(e_bins)-1))

    for iE in range(len(e_bins)-1):
        for iS in range(len(zen_bins)-1):
            # Load files for given bin only
            nurFiles= []

            for file in os.listdir(simulation_files_folder):
                if file.endswith('.nur') and (f'{e_bins[iE]:.1f}-{e_bins[iE+1]:.1f}eV_{zen_bins[iS]:.1f}sin2' in file):
                    nurFiles.append(os.path.join(simulation_files_folder, file))
            if nurFiles == []:
                continue



            eventReader = NuRadioRecoio.NuRadioRecoio(nurFiles)
            n_trig_2of3_3_5sig = 0
            n_trig_3of3_3_5sig = 0
            n_trig_3of3_5sig = 0
            n_throw = 0
            for i, evt in enumerate(eventReader.get_events()):
                n_throw += 1
                station_ids = evt.get_station_ids()
                for stn_id in station_ids:
                    station = evt.get_station(stn_id)
                    if not station.has_triggered():
                        continue
                    for trigger in trigger_names:
                        if station.has_triggered(trigger_name=trigger):
                            n_trig_per_bin[trigger][iS][iE] += 1
        
            for trigger in trigger_names:
                trig_rate_per_bin[trigger][iS][iE] = n_trig_per_bin[trigger][iS][iE] / n_throw

    return n_trig_per_bin, trig_rate_per_bin

def getAeffRatePerBin(trig_rate_per_bin,trigger_names, max_distance):
    # Returns the effective area per bin in energy/zenith assuming a circular simulation area with maximum distance max_distance

    aeff_per_bin = {}
    for trigger in trigger_names:
        aeff_per_bin[trigger] = trig_rate_per_bin[trigger] * (max_distance)**2 / np.pi
    return aeff_per_bin

def getEventRatePerBin(aeff_per_bin, e_bins, zen_bins, trigger_names):
    # Returns the event rate per bin in energy/zenith

    # NOTE! zen_bins needs to be in degrees

    # rate_per_bin  : dictionary of a 2D numpy array of event rate per bin in energy/zenith per trigger name
    # rate_sin_sum  : dictionary of a 1D numpy array of event rate per bin in energy per trigger name (summed over all zenith bins)

    rate_per_bin = {}
    rate_sin_sum = {}

    # rate per bin is Aeff * (flux_high - flux_low)
    # the function auger.event_rate returns the flux in events/year, as aeff is passed in
    for iT, trigger in enumerate(trigger_names):
        rate_per_bin[trigger] = np.zeros_like(aeff_per_bin[trigger])
        rate_sin_sum[trigger] = np.zeros(len(e_bins)-1)
        for iE in range(len(e_bins)-1):
            for iS in range(len(zen_bins)-1):
                # ic(aeff_per_bin[trigger][iS][iE] )
                high_flux = auger.event_rate(e_bins[iE], e_bins[iE+1], zmax=zen_bins[iS+1], area=aeff_per_bin[trigger][iS][iE])
                low_flux = auger.event_rate(e_bins[iE], e_bins[iE+1], zmax=zen_bins[iS], area=aeff_per_bin[trigger][iS][iE])
                rate_per_bin[trigger][iS][iE] = high_flux - low_flux

        for iS in range(len(zen_bins)-1):
            rate_sin_sum[trigger] += rate_per_bin[trigger][iS]

    return rate_per_bin, rate_sin_sum

def getParametersPerEvent(simulation_files_folder, trigger, output, filename, max_distance=2,sin2Val=np.arange(0, 1.01, 0.1),e_bins=None, zen_bins=None, rate_per_bin=None, n_trig_per_bin=None):
    # Trigger names should be a single string

    # Default e_bins and zen_bins
    if e_bins is None:
        # Range of IceTop energy simulations
        e_bins = np.arange(16, 18.6, 0.1)
    if zen_bins is None:
        # sin2Val = np.arange(0, 1.01, 0.1)   #Bin edges evenly spaces in sin^2(angle) in radians
        zen_bins = np.rad2deg(np.arcsin(np.sqrt(sin2Val)))    #Bin edges in degrees

    # If work has not already been done to get rate and trig per bin, do it here
    if rate_per_bin is None or n_trig_per_bin is None:
        n_trig_per_bin, trig_rate_per_bin = getTriggerRatePerBin(simulation_files_folder, e_bins, sin2Val, [trigger])
        aeff_per_bin = getAeffRatePerBin(trig_rate_per_bin,[trigger],max_distance)
        rate_per_bin, rate_sin_sum = getEventRatePerBin(aeff_per_bin, e_bins, zen_bins, [trigger])

    # Get the parameters per event

    nurFiles= []

    for file in os.listdir(simulation_files_folder):
        # ic(f'{e_bins[0]:.1f}-{e_bins[1]:.1f}eV_{zen_bins[0]:.1f}sin2')
        # ic(file)
        if file.endswith('.nur') and (f'{e_bins[0]:.1f}-{e_bins[1]:.1f}eV_{sin2Val[0]:.1f}sin2' in file):
            nurFiles.append(os.path.join(simulation_files_folder, file))
    if nurFiles == []:
        return [],[],[],[],[]
    
    trig_energy = []
    trig_zenith = []
    trig_azimuth= []
    trig_weight = []
    trig_id     = []

    eventReader = NuRadioRecoio.NuRadioRecoio(nurFiles)

    evt_writer.begin(os.path.join(output,f'{filename}.nur'))

    for i, evt in enumerate(eventReader.get_events()):
        station_ids = evt.get_station_ids()
        for stn_id in station_ids:
            station = evt.get_station(stn_id)
            if not station.has_triggered():
                continue
            if station.has_triggered(trigger_name=trigger):
                sim_shower = evt.get_sim_shower(0)

                # Need to know which bin this event falls into
                e_digit = np.digitize(np.log10(sim_shower[shp.energy]), e_bins)-1
                zen_digit = np.digitize(np.rad2deg(sim_shower[shp.zenith]), zen_bins)-1

                # This splits up the weight of evnts/yr for the bin into each individual event that triggered equally
                if n_trig_per_bin[trigger][zen_digit][e_digit]==0 and rate_per_bin[trigger][zen_digit][e_digit]==0:
                    evtrate=0
                else:
                    evtrate=rate_per_bin[trigger][zen_digit][e_digit] / n_trig_per_bin[trigger][zen_digit][e_digit]

                if evtrate==0:
                    continue
                else:
                    trig_energy.append(sim_shower[shp.energy])  # in eV
                    trig_zenith.append(sim_shower[shp.zenith])  # in radians
                    trig_azimuth.append(sim_shower[shp.azimuth])    # in radians
                    trig_weight.append(evtrate) 
                    trig_id.append(f'R{evt.get_run_number()}E{evt.get_id}')
                    evt.set_parameter(evtp.event_rate,evtrate)
                    evt_writer.run(evt)
    return trig_energy, trig_zenith, trig_azimuth, trig_weight, trig_id



if __name__ == '__main__':


    date = '4.22.24'
    sim_folder = f'SimpleFootprintSimulation/output/{date}/'
    plot_folder = f'plots/SimpleFootprintSimulation/{date}/'
    Path(plot_folder).mkdir(parents=True, exist_ok=True)

    # Livetime of station data in years
    station_livetime = (46 + (10 + (57 + 27.6/60)/60)/24) / 364.25 # 46 days, 10 hours, 57 minutes, 27.6 seconds


    max_distance = 2
    n_cores = 100
    num_icetop = 30
    min_energy = 16.0
    max_energy = 18.6
    # sin2Val = -0.1
    e_bins = np.arange(min_energy, max_energy, 0.1)
    sin2Val = np.arange(0, 1.01, 0.1)                   # Current simulations are ran in bins of sin^2(angle) in radians
    angle_bins = np.rad2deg(np.arcsin(np.sqrt(sin2Val)))



    total_cores = n_cores * num_icetop
    trigger_names = ['direct_LPDA_2of3_3.5sigma', 'direct_LPDA_3of3_3.5sigma', 'direct_LPDA_3of3_5sigma']
    colors = ['b', 'g', 'r']

    n_trig_per_bin, trig_rate_per_bin = getTriggerRatePerBin(sim_folder, e_bins, sin2Val, trigger_names)
    aeff_per_bin = getAeffRatePerBin(trig_rate_per_bin, trigger_names, max_distance)
    rate_per_bin, rate_sin_sum = getEventRatePerBin(aeff_per_bin, e_bins, angle_bins, trigger_names)


    # Plot each trigger separately, showing different sin bins
    for iT, trigger in enumerate(trigger_names):
        for iS in range(len(sin2Val)-1):
            # plt.bar(e_bins[:-1], aeff_per_bin[trigger][iS], width=0.1, alpha=0.5, label=f'{angle_bins[iS]:.1f}-{angle_bins[iS+1]:.1f}sin2')
            plt.hist(e_bins[:-1], weights=aeff_per_bin[trigger][iS], bins=e_bins, histtype='step', label=f'{angle_bins[iS]:.1f}-{angle_bins[iS+1]:.1f} deg')
        plt.xlabel('Energy [eV]')
        plt.ylabel('Effective Area [km^2]')
        plt.yscale('log')
        plt.legend(loc='upper left', prop={'size': 8})
        plt.savefig(plot_folder+f'Stn51_Aeff_{trigger}.png')
        plt.clf()

    # Plot all triggers together, sum of all sin bins
    aeff_sin_sum = {}
    for iT, trigger in enumerate(trigger_names):
        aeff_sin_sum[trigger] =  np.zeros(len(e_bins)-1)
        for iS in range(len(sin2Val)-1):
            aeff_sin_sum[trigger] += aeff_per_bin[trigger][iS]
        # plt.bar(e_bins[:-1], aeff_sin_sum[trigger], width=0.1, alpha=0.5, label=f'{trigger}')
        plt.hist(e_bins[:-1], weights=aeff_sin_sum[trigger], bins=e_bins, histtype='step', label=f'{trigger}, {np.sum(aeff_sin_sum[trigger]):.0f} total Aeff', color=colors[iT])
    plt.xlabel('Energy [eV]')
    plt.ylabel('Effective Area [km^2]')
    plt.yscale('log')
    plt.legend(loc='upper left', prop={'size': 8})
    plt.savefig(plot_folder+f'Stn51_Aeff_AllTriggers.png')
    plt.clf()



    # Plot event rate showing different angle bins per trigger
    for iT, trigger in enumerate(trigger_names):
        for iS in range(len(sin2Val)-1):
            # plt.bar(e_bins[:-1], rate_per_bin[trigger][iS], width=0.1, alpha=0.5, label=f'{angle_bins[iS]:.1f}-{angle_bins[iS+1]:.1f}sin2')
            plt.hist(e_bins[:-1], weights=rate_per_bin[trigger][iS], bins=e_bins, histtype='step', label=f'{angle_bins[iS]:.1f}-{angle_bins[iS+1]:.1f} deg')
        plt.xlabel('Energy [eV]')
        plt.ylabel('Events / Year')
        plt.yscale('log')
        plt.legend(loc='upper left', prop={'size': 8})
        plt.savefig(plot_folder+f'Stn51_EventRate_{trigger}.png')
        plt.clf()

    for iT, trigger in enumerate(trigger_names):
        # plt.bar(e_bins[:-1], rate_sin_sum[trigger], width=0.1, alpha=0.5, label=trigger)
        evts_in_data = station_livetime * np.sum(rate_sin_sum[trigger])
        plt.hist(e_bins[:-1], weights=rate_sin_sum[trigger], bins=e_bins, histtype='step', label=f'{trigger}, {evts_in_data:.1f} events in data', color=colors[iT])
    plt.xlabel('Energy [eV]')
    plt.ylabel('Events / Year')
    plt.yscale('log')
    plt.legend(loc='upper left', prop={'size': 8})
    plt.savefig(plot_folder+f'Stn51_EventRate_AllTriggers.png')
    plt.clf()


    # Calc rate after cutting at ~40deg. Doing cut at 39.2deg since that's bin edge
    rate_sin_sum_cut = {}
    for trigger in trigger_names:
        rate_sin_sum_cut[trigger] = np.zeros(len(e_bins)-1)
        for iS in range(len(sin2Val)-1):
            if angle_bins[iS] > 39:
                rate_sin_sum_cut[trigger] += rate_per_bin[trigger][iS]

    for iT, trigger in enumerate(trigger_names):
        # plt.bar(e_bins[:-1], rate_sin_sum[trigger], width=0.1, alpha=0.5, label=trigger)
        evts_in_data = station_livetime * np.sum(rate_sin_sum[trigger])
        evts_in_data_cut = station_livetime * np.sum(rate_sin_sum_cut[trigger])
        plt.hist(e_bins[:-1], weights=rate_sin_sum[trigger], bins=e_bins, histtype='step', label=f'{trigger}, {evts_in_data:.1f} events in data', color=colors[iT])
        plt.hist(e_bins[:-1], weights=rate_sin_sum_cut[trigger], bins=e_bins, histtype='step', label=f'39deg cut, {evts_in_data_cut:.1f} events in data', color=colors[iT], linestyle='--')
    plt.xlabel('Energy [eV]')
    plt.ylabel('Events / Year')
    plt.yscale('log')
    plt.legend(loc='upper left', prop={'size': 8})
    plt.savefig(plot_folder+f'Stn51_EventRate_AllTriggers_40degCut.png')
    plt.clf()


    # Now can do plots of parameters
    trig_energy, trig_zenith, trig_azimuth, trig_weight = getParametersPerEvent(sim_folder, trigger_names[0], e_bins, sin2Val, rate_per_bin, n_trig_per_bin)
    # TODO