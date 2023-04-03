import numpy as np
from mesa.datacollection import DataCollector
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

def get_evs_dead(model):
    evs_dead = [ev.machine.state == 'Battery_dead' for ev in model.evs]
    no_evs_dead = np.sum(evs_dead)
    return no_evs_dead

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
    eod_soc = [ev.battery_eod for ev in model.evs]
    return eod_soc

def get_state_evs(model):
    eod_soc = [ev.machine.state for ev in model.evs]
    return eod_soc

def get_evs_destinations(model):
    evs_destinations = [ev.destination for ev in model.evs]
    return evs_destinations

def get_evs_range_anxiety(model):
    ev_cprop = [ev.range_anxiety for ev in model.evs]
    return ev_cprop

# Attribute based functions for Charging station agents
# def get_queue_1_length(model):
#     cpoint_len = [len(cs.queue_1) for cs in model.chargestations]
#     # no_evs_active = np.sum(evs_active)
#     return cpoint_len

# def get_queue_2_length(model):  
#     cpoint_len = [len(cs.queue_2) for cs in model.chargestations]
#     # no_evs_active = np.sum(evs_active)
#     return cpoint_len
def get_queue_length(model):  
    cpoint_len = [len(cs.queue) for cs in model.chargestations]
    # no_evs_active = np.sum(evs_active)
    return cpoint_len

# 28/02 Request: Get number of EVs at each charging station
# def get_evs_at_cstation(model):
#     evs_at_cstation = [len(cs.queue) for cs in model.chargestations]
#     for attr_name in dir(cs):
#         if attr_name.startswith("cp_id_") and attr_v:
#     pass

# Approach 2
def get_agent_info(self, agent_id):
        """Return a dictionary of information about a specific agent"""
        agent = self.schedule._agents[agent_id]
        return {
            "id": agent.unique_id,
            "state": agent.machine.state,
            # "type": agent.type,
            # "x": agent.pos[0],
            # "y": agent.pos[1],
            # Add more attributes as desired
        }

def data_collector(self):
    """Return a DataCollector object that collects agent data"""
    return DataCollector(
        model_reporters={"agent_data": lambda m: [
            m.get_agent_info(agent_id) for agent_id in m.schedule.agent_buffer
        ]}
    )





# def get_evs_active(model):
#     evs_active = [ev._is_active for ev in model.evs]
#     no_evs_active = np.sum(evs_active)
#     return no_evs_active

# def get_evs_charging(model):
#     evs_charging = [ev._is_charging is True for ev in model.evs]
#     no_evs_charging = np.sum(evs_charging)
#     return no_evs_charging
