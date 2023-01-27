import numpy as np
import matplotlib.pyplot as plt
import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from EV.agents import EV, Cpoint


# Model Data Extraction Methods
def get_evs_charged(model):
    evs_charged = [ev._was_charged for ev in model.evs]
    no_evs_charged = np.sum(evs_charged)
    return no_evs_charged

def get_evs_charge_level(model):
    evs_levels = [ev.battery for ev in model.evs]
    # no_evs_active = np.sum(evs_active)
    return evs_levels

def get_evs_active(model):
    evs_active = [ev._is_active for ev in model.evs]
    no_evs_active = np.sum(evs_active)
    return no_evs_active

def get_evs_charging(model):
    evs_charging = [ev._is_charging is True for ev in model.evs]
    no_evs_charging = np.sum(evs_charging)
    return no_evs_charging

# State machine based functions
def get_evs_travel(model):
    evs_travel = [ev.machine.state == 'Travel' for ev in model.evs]
    no_evs_travel = np.sum(evs_travel)
    return no_evs_travel

def get_evs_not_idle(model):
    evs_not_idle = [ev.machine.state != 'Idle' for ev in model.evs]
    no_evs_not_idle = np.sum(evs_not_idle)
    return no_evs_not_idle

def get_active_cpoints(model):
    active_cpoints = [cp._is_active for cp in model.cpoints]
    no_active_cpoints = np.sum(active_cpoints)
    return no_active_cpoints

def get_eod_soc(model):
    # eod_soc = [ev.battery_eod for ev in model.evs]
    eod_soc = [ev.battery_eod for ev in model.evs]
    return eod_soc

# Incomplete
# def get_evs_charged(model):
#     evs_charged = [ev._was_charged for ev in model.evs]
#     no_evs_charged = np.sum(evs_charged)
#     return no_evs_charged

class EVModel(Model):
    """Simulation Model with EV agents and Charging Points agents.
    
    Args:
        no_evs (int): Number of EV agents to create.
        no_cps (int): Number of Charging Point agents to create.
        ticks (int): Number of ticks to run the simulation for.
        
    Attributes: 
        ticks (int): Number of ticks to run the simulation for.
        _current_tick (int): Current tick of the simulation.
        no_evs (int): Number of EV agents to create.
        no_cps (int): Number of Charging Point agents to create.
        schedule (RandomActivation): Schedule for the model.
        evs (list): List of EV agents.
        cpoints (list): List of Charging Point agents.
            
    """
  
    def __init__(self, no_evs, no_cps, ticks):
        super().__init__()
        # init with input args
        self.ticks = ticks
        self._current_tick = 1
        self.no_evs = no_evs
        self.no_cps = no_cps
        # other key model attr 
        self.schedule = RandomActivation(self)
        # self.schedule = SimultaneousActivation(self)
        # self.schedule = RandomActivationByType(self)
        # Populate model with agents
        self.evs = []
        self.cpoints = []
        # evs
        for i in range(self.no_evs):
            ev = EV(i,self)
            self.schedule.add(ev)
            self.evs.append(ev)
        # charging points
        for i in range(self.no_cps):
            cp = Cpoint(i + no_evs, self)
            # cp = Cpoint(i, self)
            self.schedule.add(cp)
            self.cpoints.append(cp)
        self.datacollector = DataCollector(
            model_reporters={'EVs Charged': get_evs_charged,
                             'EVs Activated': get_evs_active,
                             'EVs Travelling': get_evs_travel,
                             'EVs Charge Level': get_evs_charge_level,
                             'EVs Currently charging': get_evs_charging,
                             'EVs Not Idle': get_evs_not_idle,
                             'EOD Battery SOC': get_eod_soc,
                             })
    
    def step(self):
        """Advance model one step in time"""
        print("Current tick: "+ str(self._current_tick) + ".")
        # print("Active CPs: " + str(get_active_cps(self)))
        # print(self.get_agent_count(self))
        self.schedule.step()
        self._current_tick += 1
        self.datacollector.collect(self)