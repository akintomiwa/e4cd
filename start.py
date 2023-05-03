# imports 
from random import choice
import warnings
warnings.simplefilter("ignore")

from mesa.datacollection import DataCollector
# from matplotlib import pyplot as plt, patches
# import scipy.stats as ss
import cufflinks as cf
cf.go_offline()
from datetime import datetime



import EV.model_config as cfg
# import config.worker as worker
# from EV.agent import EV, ChargeStation
import EV.model as model
from EV.statemachines import EVSM, LSM
from EV.modelquery import get_evs_charge, get_evs_charge_level, get_evs_active, get_evs_queue, get_evs_travel, get_evs_not_idle, get_active_chargestations, get_eod_evs_socs, get_evs_destinations, get_ev_distance_covered
"""
This is the main file for the EV ABM simulator.
It is used to run the model and collect the data.

"""
# Parameterisation
# from config file

# today's date as string
date_str = str(datetime.today())


def run() -> object:
    model_run = model.EVModel(ticks=cfg.ticks, no_evs=cfg.no_evs, station_params=cfg.station_config, location_params=cfg.location_config, station_location_param=cfg.station_location_config, overnight_charging=cfg.overnight_charging)
    for i in range(cfg.ticks):
        model_run.step()
    return model_run

def extract_data(model) -> None:
    run_stats = model.datacollector.get_model_vars_dataframe()
    print(run_stats)

def export_data(model, format) -> None:
    run_stats = model.datacollector.get_model_vars_dataframe()
    # run_stats.to_csv(cfg.DATA_PATH + 'run_stats.csv', index=False)
    if format == 'csv':
        run_stats.to_csv(cfg.DATA_PATH + 'data_' + date_str[0:10] + '_' + str(cfg.no_evs) + '_EV_agent_model_output.csv')
        print('Model data exported to csv')
    elif format == 'xlsx' or 'xls':
        run_stats.to_excel(cfg.DATA_PATH + 'data_' + date_str[0:10] + '_' + str(cfg.no_evs) + '_EV_agent_model_output.xlsx', index=False)
        print('Model data exported to xlsx')

    # run_stats.to_excel(cfg.DATA_PATH + 'run_stats.xlsx', index=False)
    # print('Data exported to csv and xlsx')



if __name__ == '__main__':
    run()
    if cfg.export_data == True:
        export_data(run(),format=cfg.output_format)

    # if cfg.overnight_charging == True:
    #     model_run = model.EVModel(ticks=cfg.ticks, no_evs=cfg.no_evs, station_params=cfg.station_config, location_params=cfg.location_config, station_location_param=cfg.station_location_config, overnight_charging = cfg.overnight_charging)
    #     for i in range(cfg.ticks):
    #         model_run.step()
    #     # return model_run
 

#    if cfg.export_data:
#         export_data(model_run)

# def plot_data(model) -> None:
#     run_stats = model.datacollector.get_model_vars_dataframe()
#     run_stats.plot()
#     plt.show()