import numpy as np
# import matplotlib.pyplot as plt
# import random
import mesa
from mesa import Model
# from mesa.time import RandomActivation, SimultaneousActivation, RandomActivationByType
from mesa.datacollection import DataCollector
from EV.agent import EV, ChargeStation


# Model Data Extraction Methods

# Attribute and Flag based functions for EV agents
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

def get_evs_at_station_flag(model):
    evs_charging = [ev._at_station is True for ev in model.evs]
    no_evs_charging = np.sum(evs_charging)
    return no_evs_charging

def get_ev_distance_covered(model):
    eod_socs = [ev.battery_eod for ev in model.evs]
    total_distance = np.sum(eod_socs)
    return total_distance


# State machine based functions for EV agents
def get_evs_travel(model):
    evs_travel = [ev.machine.state == 'Travel' or ev.machine.state == 'Travel_low' for ev in model.evs]
    no_evs_travel = np.sum(evs_travel)
    return no_evs_travel

def get_evs_charge(model):
    evs_charged = [ev.machine.state == 'Charge' for ev in model.evs]
    no_evs_charged = np.sum(evs_charged)
    return no_evs_charged

def get_evs_at_station_state(model):
    evs_at_station = [(ev.machine.state == 'Seek_queue' or ev.machine.state == 'In_queue') or (ev.machine.state == 'Charge') for ev in model.evs]
    no_evs_at_station = np.sum(evs_at_station)
    return no_evs_at_station

def get_evs_queue(model):
    evs_queued = [ev.machine.state == 'In_queue' for ev in model.evs]
    no_evs_queued = np.sum(evs_queued)
    return no_evs_queued

def get_evs_not_idle(model):
    evs_not_idle = [ev.machine.state != 'Idle' for ev in model.evs]
    no_evs_not_idle = np.sum(evs_not_idle)
    return no_evs_not_idle

def get_active_chargestations(model):
    active_Chargestations = [cs._is_active for cs in model.Chargestations]
    no_active_Chargestations = np.sum(active_Chargestations)
    return no_active_Chargestations

def get_eod_evs_socs(model):
    # eod_soc = [ev.battery_eod for ev in model.evs]
    eod_soc = [ev.battery_eod for ev in model.evs]
    return eod_soc
def get_evs_destinations(model):
    evs_destinations = [ev.destination for ev in model.evs]
    return evs_destinations

# Attribute and Flag based functions for Charging station agents
def get_queue_1_length(model):
    cpoint_len = [len(cs.queue_1) for cs in model.chargestations]
    # no_evs_active = np.sum(evs_active)
    return cpoint_len

def get_queue_2_length(model):  
    cpoint_len = [len(cs.queue_2) for cs in model.chargestations]
    # no_evs_active = np.sum(evs_active)
    return cpoint_len

# def get_evs_active(model):
#     evs_active = [ev._is_active for ev in model.evs]
#     no_evs_active = np.sum(evs_active)
#     return no_evs_active

# def get_evs_charging(model):
#     evs_charging = [ev._is_charging is True for ev in model.evs]
#     no_evs_charging = np.sum(evs_charging)
#     return no_evs_charging



############################################################################################################


class EVModel(Model):
    """Simulation Model with EV agents and Charging Points agents.
    
    Args:
        no_evs (int): Number of EV agents to create.
        no_css (int): Number of Charging Point agents to create.
        ticks (int): Number of ticks to run the simulation for.
        
    Attributes: 
        ticks (int): Number of ticks to run the simulation for.
        _current_tick (int): Current tick of the simulation.
        no_evs (int): Number of EV agents to create.
        no_css (int): Number of Charging Point agents to create.
        schedule (RandomActivation): Schedule for the model.
        evs (list): List of EV agents.
        chargestations (list): List of Charging Point agents.
            
    """
  
    def __init__(self, no_evs, no_css, ticks) -> None:
        super().__init__()
        # init with input args
        self.running = True
        self.random = True
        self.ticks = ticks
        self._current_tick = 1
        self.no_evs = no_evs
        self.no_css = no_css
        # self.checkpoints = [40, 80, 120, 160, 200, 240, 280]
        self.checkpoints = self.compute_checkpoints(self.no_css+1) #+1 to ensure no overruns.
        # other key model attr 
        # self.schedule = mesa.time.RandomActivation(self)
        self.schedule = mesa.time.StagedActivation(self, shuffle=False, shuffle_between_stages=False, stage_list=['stage_1','stage_2'])
        # self.schedule = SimultaneousActivation(self)
        # self.schedule = RandomActivationByType(self) #requires addional args in model.step()
        # Populate model with agents
        self.evs = []
        self.chargestations = []
        
        # Setup
        # evs
        for i in range(self.no_evs):
            ev = EV(i,self)
            self.schedule.add(ev)
            self.evs.append(ev)
        # charging points
        for i in range(self.no_css):
            cs = ChargeStation(i + no_evs, self)
            self.schedule.add(cs)
            self.chargestations.append(cs)
        # assign checkpoints to charging points
        for  i, cs in enumerate(self.chargestations):
            cs._checkpoint_id = self.checkpoints[i]        
        # display Charge stations and their checkpoints
        for cs in self.chargestations:
            print(f"Charging Station: {cs.unique_id} is at checkpoint: {cs._checkpoint_id} miles.")
        
        # define method for computing EV start time
        # self.

        self.datacollector = DataCollector(
            model_reporters={'EVs Charging': get_evs_charge,
                             'EVs Activated': get_evs_active,
                             'EVs Travelling': get_evs_travel,
                             'EVs Queued': get_evs_queue,
                             'EVs Charge Level': get_evs_charge_level,
                             'EVs Currently charging': get_evs_charging,
                             'EVs Not Idle': get_evs_not_idle,
                             'EOD Battery SOC': get_eod_evs_socs,
                             'EVs Destinations': get_evs_destinations,
                             'EVs at Charging Station - F': get_evs_at_station_flag,
                             'EVs at Charging Station - S': get_evs_at_station_state,
                             'Length of Queue 1 at Charging Stations': get_queue_1_length,
                             'Length of Queue 2 at Charging Stations': get_queue_2_length,

                             },
            # agent_reporters={'Battery': 'battery',
            #                 'Battery EOD': 'battery_eod',
            #                 'Destination': 'destination',
            #                 'State': 'state',
            #                 }
                             )
        print(f"\nModel initialised. {self.no_evs} EVs and {self.no_css} Charging Points. Simulation will run for {self.ticks} ticks.")
        # print(f"Charging station checkpoints: {self.checkpoints}")
    
    def compute_ev_start_time(self, ev) -> int:
        """Compute the start time for the EV agent."""
        start_time = np.random.randint(5, 7)
        return start_time
        

    def compute_checkpoints(self,n) -> list:
        """Compute the checkpoints for the simulation."""
        start = 40
        # steps = n
        interval = 40
        checkpoints = np.arange(start, interval * n , interval)
        return checkpoints

    # def step(self, shuffle_types = True, shuffle_agents = True) -> None:
    def step(self) -> None:
        """Advance model one step in time"""
        print(f"\nCurrent timestep (tick): {self._current_tick}.")
        # print("Active Css: " + str(get_active_css(self)))
        # print(self.get_agent_count(self))
        self.schedule.step()
        # if self.schedule.steps % 24 == 0:
        #     # print(f"This is the end of day:{(self.schedule.steps + 1) / 24} ")
        #     print(f"This is the end of day: {self.schedule.steps / 24}. ")
        #     for ev in self.evs:
        #         ev.add_soc_eod()
        #         ev.choose_journey_type()
        #         ev.choose_destination(ev.journey_type)
        #         ev.set_new_day()
        self.datacollector.collect(self)
        self._current_tick += 1
        if self.schedule.steps % 24 == 0:
            # print(f"This is the end of day:{(self.schedule.steps + 1) / 24} ")
            print(f"This is the end of day: {self.schedule.steps / 24}. ")
            for ev in self.evs:
                ev.add_soc_eod()
                ev.choose_journey_type()
                ev.choose_destination(ev.journey_type)
                ev.set_new_day()