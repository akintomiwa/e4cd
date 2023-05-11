# imports 
# from random import choice
# import warnings
# warnings.simplefilter("ignore")
# import cufflinks as cf
# cf.go_offline()

from mesa.datacollection import DataCollector
from EV.statemachines import EVSM, LSM

from datetime import datetime
import EV.model_config as cfg
import EV.model as model

"""
This is the main file for the EV ABM simulator.
It is used to run the model and collect the data.

"""

# today's date as string
date_str = str(datetime.today())

def run() -> object:
    """
    Runs the model. Parameterisation - imported from model_config file

    Returns:
        model_run: The model object.

    """
    model_run = model.EVModel(
        ticks=cfg.ticks, 
        no_evs=cfg.no_evs, 
        station_params=cfg.station_config, 
        location_params=cfg.location_config, 
        station_location_param=cfg.station_location_config, 
        overnight_charging=cfg.overnight_charging,
        grid_height=cfg.grid_height,
        grid_width=cfg.grid_width)
    for i in range(cfg.ticks):
        model_run.step()
    return model_run

def export_data(model, format) -> None:
    run_stats = model.datacollector.get_model_vars_dataframe()
    if format == 'csv':
        run_stats.to_csv(cfg.DATA_PATH + 'data_' + date_str[0:10] + '_' + str(cfg.no_evs) + '_EV_agent_model_output.csv')
        print('Model data exported to csv')
    elif format == 'xlsx' or 'xls':
        run_stats.to_excel(cfg.DATA_PATH + 'data_' + date_str[0:10] + '_' + str(cfg.no_evs) + '_EV_agent_model_output.xlsx', index=False)
        print('Model data exported to xlsx')

if __name__ == '__main__':
    run()
    if cfg.export_data == True:
        export_data(run(),format=cfg.output_format)


# def plot_data(model) -> None:
#     run_stats = model.datacollector.get_model_vars_dataframe()
#     run_stats.plot()
#     plt.show()