import numpy as np
import matplotlib.pyplot as plt
import random
from mesa import Agent, Model
from mesa.time import RandomActivation, SimultaneousActivation, RandomActivationByType
from mesa.datacollection import DataCollector
from EV.agent import EV, Cpoint


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

def get_eod_evs_socs(model):
    # eod_soc = [ev.battery_eod for ev in model.evs]
    eod_soc = [ev.battery_eod for ev in model.evs]
    return eod_soc
def get_evs_destinations(model):
    evs_destinations = [ev.destination for ev in model.evs]
    return evs_destinations

# Agent Data Extraction Methods
def get_ev_distance_covered(ev):
    eod_socs = [ev.battery_eod for ev in model.evs]
    total_distance = np.sum(eod_socs)


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
  
    def __init__(self, no_evs, no_cps, ticks) -> None:
        super().__init__()
        # init with input args
        self.running = True
        self.random = True
        self.ticks = ticks
        self._current_tick = 1
        self.no_evs = no_evs
        self.no_cps = no_cps
        # self.checkpoints = [40, 80, 120, 160, 200, 240, 280]
        self.checkpoints = self.compute_checkpoints(self.no_cps+1)
        # other key model attr 
        # self.schedule = RandomActivation(self)
        self.schedule = SimultaneousActivation(self)
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
            self.schedule.add(cp)
            self.cpoints.append(cp)

        # assign checkpoints to charging points
        for  i, cp in enumerate(self.cpoints):
            cp._checkpoint_id = self.checkpoints[i]
            
        # display Charge stations and their checkpoints
        for cp in self.cpoints:
            print(f"CP: {cp.unique_id} is at checkpoint: {cp._checkpoint_id} miles")


        self.datacollector = DataCollector(
            model_reporters={'EVs Charged': get_evs_charged,
                             'EVs Activated': get_evs_active,
                             'EVs Travelling': get_evs_travel,
                             'EVs Charge Level': get_evs_charge_level,
                             'EVs Currently charging': get_evs_charging,
                             'EVs Not Idle': get_evs_not_idle,
                             'EOD Battery SOC': get_eod_evs_socs,
                             'EVs Destinations': get_evs_destinations,
                             },
            # agent_reporters={'Battery': 'battery',
            #                 'Battery EOD': 'battery_eod',
            #                 'Destination': 'destination',
            #                 'State': 'state',
            #                 }
                             )
        print(f"Model initialised. {self.no_evs} EVs and {self.no_cps} Charging Points. Simulation will run for {self.ticks} ticks.")
        # print(f"Charging station checkpoints: {self.checkpoints}")
    
    def compute_checkpoints(self,n) -> list:
        """Compute the checkpoints for the simulation."""
        start = 40
        # steps = n
        interval = 40
        checkpoints = np.arange(start, interval * n , interval)
        # print(checkpoints)
        return checkpoints

    def step(self) -> None:
        """Advance model one step in time"""
        print(f"\nCurrent timestep (tick): {self._current_tick}.")
        # print("Active CPs: " + str(get_active_cps(self)))
        # print(self.get_agent_count(self))
        self.schedule.step()
        if (self.schedule.steps + 1) % 24 == 0:
            print("This is the end of day: " + str((self.schedule.steps + 1) / 24))
            for ev in self.evs:
                # ev.
                ev.add_soc_eod()
                ev.choose_journey_type()
                ev.choose_destination(ev.journey_type)
                ev.set_new_day()
        self.datacollector.collect(self)
        self._current_tick += 1