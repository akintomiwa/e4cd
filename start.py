# imports
import os
import seaborn as sns
from random import choice
import warnings
warnings.simplefilter("ignore")
import pandas as pd
import numpy as np
import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation, RandomActivationByType, SimultaneousActivation
from mesa.datacollection import DataCollector
from matplotlib import pyplot as plt, patches
import scipy.stats as ss
import cufflinks as cf
cf.go_offline()
from plotly.offline import iplot
from transitions import Machine
import random
from transitions.extensions import GraphMachine
import graphviz
import timeit
from datetime import datetime
import logging
from collections import Counter


import config.model_config as cfg
import config.worker as worker
from EV.agent import EV, ChargeStation
import EV.model as model
from EV.statemachine import EVSM, LSM
from EV.modelquery import get_evs_charge, get_evs_charge_level, get_evs_active, get_evs_queue, get_evs_travel, get_evs_not_idle, get_active_chargestations, get_eod_evs_socs, get_evs_destinations, get_ev_distance_covered
"""
This is the main file for the EV ABM simulator.
It is used to run the model and collect the data.

"""

def run():
    station_config = worker.read_csv(cfg.STATION_PATH +'stations.csv')
    ticks = 48
    no_evs = 2
    model_run = model.EVModel(ticks=ticks, no_evs=no_evs, params=station_config)
    for i in range(ticks):
        model_run.step()


if __name__ == '__main__':
    run()
 