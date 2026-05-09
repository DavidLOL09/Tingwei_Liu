from NuRadioReco.utilities import units
# import NuRadioReco.modules.io.coreas.readCoREAS
import sys
from icecream import ic
import readCoREASStationGrid
ic(readCoREASStationGrid.__file__)
import NuRadioReco.modules.io.coreas.simulationSelector
import NuRadioReco.modules.efieldToVoltageConverter
import NuRadioReco.modules.channelGenericNoiseAdder
import NuRadioReco.modules.channelBandPassFilter
import NuRadioReco.modules.electricFieldBandPassFilter
import NuRadioReco.modules.eventTypeIdentifier
import NuRadioReco.modules.channelStopFilter
import NuRadioReco.modules.channelResampler
import NuRadioReco.modules.trigger.highLowThreshold
import NuRadioReco.modules.trigger.simpleThreshold
import NuRadioReco.modules.ARIANNA.hardwareResponseIncorporator
import NuRadioReco.modules.channelAddCableDelay
import NuRadioReco.modules.channelLengthAdjuster
ic(NuRadioReco.__file__)
import NuRadioReco.modules.triggerTimeAdjuster as tTimeAdjuster
import astropy
import argparse
import NuRadioReco.modules.io.eventWriter
import numpy as np
import os
import datetime
from scipy import constants
import ToolsPac
from NuRadioReco.detector import antennapattern
import pandas as pd
import matplotlib.pyplot as plt

from NuRadioReco.detector import detector
from NuRadioReco.detector import generic_detector

# from modifyEfieldForSurfaceReflection import modifyEfieldForSurfaceReflection
from NuRadioReco.framework.parameters import showerParameters as shp

import logging
logger=logging.getLogger("module")
logger.setLevel(logging.WARNING)

det = detector.Detector(json_filename=f'/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation/station51_InfAir.json', assume_inf=False, antenna_by_depth=False)
det.update(astropy.time.Time('2018-1-1'))

from NuRadioReco.modules.io import NuRadioRecoio


input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/CR_BL_2backlope_Template_final'
reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))

for evt in reader.get_events():
    station = evt.get_station(51)
    station.set_station_time(datetime.datetime(2018, 10, 1))
    det.update(station.get_station_time())
    sim_shower = evt.get_sim_shower(0)
    zenith = sim_shower[shp.zenith]/units.rad
    azimuth = sim_shower[shp.azimuth]/units.rad
    efields=station.get_electric_fields()


    zenith_antenna_after_reflection = np.pi - zenith/units.rad

    antenna_model = det.get_antenna_model(station.get_id(), 4, zenith_antenna_after_reflection)
    __antenna_provider=antennapattern.AntennaPatternProvider()
    antenna_pattern = __antenna_provider.load_antenna_pattern(antenna_model)
    antenna_orientation = det.get_antenna_orientation(station.get_id(), 4)
    efield = efields[0]
    ff1 = efields[0].get_frequency_spectrum()
    ff = efields[0].get_frequencies()
    spectrum = np.linspace(0,len(ff)-1,len(ff))
    zen = 50
    azi = 0
    zenith = np.deg2rad(zen)
    azimuth= np.deg2rad(azi+51.35)
    vel = antenna_pattern.get_antenna_response_vectorized(ff,zenith,azimuth,*antenna_orientation)
    vel_bl = antenna_pattern.get_antenna_response_vectorized(ff,(np.pi-zenith),azimuth,*antenna_orientation)
    eff_h = {}
    eff_h_b = {}
    eff_h['theta']=np.abs(vel['theta'])
    eff_h['phi']=np.abs(vel['phi'])
    eff_h_b['theta']=np.abs(vel_bl['theta'])
    eff_h_b['phi']=np.abs(vel_bl['phi'])


    fig,axes = plt.subplots(2,1,sharex = True, figsize = (10,5))
    fig.suptitle(f'azi:{azi}deg zen:{zen}deg')
    ax = axes[0]
    ax.plot(spectrum,eff_h['theta'],label = f'frontlobe theta')
    ax.plot(spectrum,eff_h_b['theta'],label = f'backlobe theta')
    ax.set_ylabel('effective height')
    ax.set_xlabel('frequency(mHz)')
    ax.legend()

    ax = axes[1]
    ax.plot(spectrum,eff_h['phi'],label = f'frontlobe phi')
    ax.plot(spectrum,eff_h_b['phi'],label = f'backlobe phi')
    ax.set_ylabel('effective height')
    ax.set_xlabel('frequency(mHz)')
    ax.set_xlim(0,800)
    ax.legend()
    plt.show()
    exit()


    for zen in [0,10,20,30,45,60,70,80,90]:
        zenith = np.deg2rad(zen)
        azimuth = np.deg2rad(0)
        gain_theta = []
        gain_phi   = []
        azi_bin = np.linspace(0,360,361)
        for azimuth in np.deg2rad(azi_bin+51.35):
            vel = antenna_pattern.get_antenna_response_vectorized(ff, zenith, azimuth, *antenna_orientation)
            vel_bl = antenna_pattern.get_antenna_response_vectorized(ff, (np.pi-zenith), azimuth, *antenna_orientation)

            # fig,axes = plt.subplots(2,3,sharex=True,figsize=(15,5))
            # fig.suptitle(f'azi:{np.rad2deg(azimuth)}deg')
            # ax = axes[0][0]
            # ax.plot(spectrum,np.abs(vel['theta']))
            # ax.set_title(f'{np.rad2deg(zenith)}-theta')
            # ax = axes[1][0]
            # ax.plot(spectrum,np.abs(vel['phi']))
            # ax.set_title(f'{np.rad2deg(zenith)}-phi')
            # ic(vel['theta'])
            # ax = axes[0][1]
            # ax.plot(spectrum,np.abs(vel_bl['theta']))
            # ax.set_title(f'{np.rad2deg(np.pi-zenith)}-theta')
            # ax = axes[1][1]
            # ax.plot(spectrum,np.abs(vel_bl['phi']))
            # ax.set_title(f'{np.rad2deg(np.pi-zenith)}-phi')
            # ax = axes[0][2]
            # ax.plot(spectrum,np.abs(ff1[1]))
            # ax.set_title('Efield-theta')
            # ax = axes[1][2]
            # ax.plot(spectrum,np.abs(ff1[2]))
            # ax.set_title('Efield-phi')
            # ax.set_xlim(0,512)
            # ic(np.shape(vel['theta']))
            gain_theta.append(np.abs([vel['theta'][150],vel_bl['theta'][150]]))
            gain_phi.append(np.abs([vel['phi'][150],vel_bl['phi'][150]]))
        gain_theta=np.array(gain_theta)
        gain_phi = np.array(gain_phi)
        bin_30 = np.linspace(0,360,13)
        bin_45 = np.linspace(0,360,9)


        fig,axes = plt.subplots(3,2,sharex=True,figsize=(8,8),layout = 'constrained')

        fig.suptitle(f'zen:{np.rad2deg(zenith)}')
        ax = axes[0][0]
        ax.set_title('Frontlobe (theta)')
        ax.plot(azi_bin,gain_theta[:,0])
        ax.set_xlabel('azimuth')
        ax.set_ylabel('eff-height')

        ax = axes[0][1]
        ax.set_title('Frontlobe (phi)')
        ax.plot(azi_bin,gain_phi[:,0])
        ax.set_xlabel('azimuth')
        ax.set_ylabel('eff-height')

        ax = axes[1][0]
        ax.set_title('backlobe (theta)')
        ax.plot(azi_bin,gain_theta[:,1])
        ax.set_xlabel('azimuth')
        ax.set_ylabel('eff-height')

        ax = axes[1][1]
        ax.set_title('backlobe (phi)')
        ax.plot(azi_bin,gain_phi[:,1])
        ax.set_xlabel('azimuth')
        ax.set_ylabel('eff-height')

        ax = axes[2][0]
        ax.set_title('Frontlobe/backlobe ratio (theta)')
        ax.plot(azi_bin,gain_theta[:,0]/gain_theta[:,1])
        ax.set_xlabel('azimuth')
        ax.set_ylabel('ratio')

        ax = axes[2][1]
        ax.set_title('Frontlobe/backlobe ratio (phi)')
        ax.plot(azi_bin,gain_phi[:,0]/gain_phi[:,1])
        ax.set_xlabel('azimuth')
        ax.set_ylabel('ratio')

        ax.set_xticks(np.linspace(0,360,9))

        for axx in axes:
            for ax in axx:
                for b_30 in bin_30:
                    ax.axvline(x = b_30,linestyle = '--',color = 'red',alpha = 0.5,zorder = 0)
                for b_45 in bin_45:
                    ax.axvline(x = b_45,linestyle = '--',color = 'blue',alpha = 0.5,zorder = 0)

            # fig,axes = plt.subplots(2,1,sharex=True,sharey=True,figsize=(10,5),layout = 'constrained')
            # ax = axes[0]
            # ax.plot(spectrum,np.abs(vel['theta']))
            # ax.set_title(f'Frontlobe zen: {np.rad2deg(zenith)}deg theta')
            # ax.set_xlabel('Frequency(MHz)')
            # ax.set_ylabel('Antenna Response')
            # ax = axes[1]
            # ax.plot(spectrum,np.abs(vel_bl['theta']))
            # ax.set_title(f'Backlobe zen: {np.rad2deg(np.pi-zenith)}deg theta')
            # ax.set_xlabel('Frequency(MHz)')
            # ax.set_ylabel('Antenna Response')
            # ax.set_xlim(0,512)
        plt.savefig(os.path.join('/Users/david/Desktop/antenna_model',f'eff_H_zen_{zen}.png'))
        plt.show()
    exit()
        

