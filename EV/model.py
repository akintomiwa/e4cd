import numpy as np
import mesa
from mesa import Model
# from mesa.time import RandomActivation, SimultaneousActivation, RandomActivationByType
from mesa.datacollection import DataCollector
from EV.agent import EV, ChargeStation
from transitions import MachineError


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
  
    def __init__(self, no_evs, params, ticks) -> None:
        """
        Initialise the model.
        
        Args:
            no_evs (int): Number of EV agents to create.
            params (dict): Dictionary of model parameters including 'no_css' (int): Number of Charging Point 
                            agents to create and 'no_cps_per_cs' (dict): dictionary containing the number of charge 
                            points per charging station with the key as the charging station id and the value as 
                            the number of charge points.
            ticks (int): Number of ticks to run the simulation for.

        """
        super().__init__()
        # init with input args
        self.running = True
        self.random = True
        self.ticks = ticks
        self._current_tick = 1
        self.no_evs = no_evs
        self.no_css = params['no_css']
        # self.no_cps = no_cps
        self.default_cppcs = params['default_cppcs']
        self.no_cps_per_cs = params['no_cps_per_cs']
        # self.checkpoints = [40, 80, 120, 160, 200, 240, 280]
        self.checkpoints = self.compute_checkpoints(self.no_css+1) #+1 to ensure no overruns.
        self.current_day_count = 0
        self.max_days = 0
        self.set_max_days()
        # other key model attr 
        self.schedule = mesa.time.StagedActivation(self, shuffle=False, shuffle_between_stages=False, stage_list=['stage_1','stage_2'])
        # Populate model with agents
        self.evs = []
        self.chargestations = []
        # self.chargepoints = []
        print('Creating agents...')
        # print(self.no_cps_per_cs.get('4'))
        # print(self.no_evs, self.no_css, self.no_cps_per_cs)
        # Setup
        # charging stations
        for i in range(self.no_css):
            # dynamically create charge station with number of charge points
            cs = ChargeStation(i, self, self.no_cps_per_cs.get('i', self.default_cppcs))
            # add checkpoint id as a propery of cs
            cs.__setattr__('checkpoint_id', self.checkpoints[i])    
            self.schedule.add(cs)
            self.chargestations.append(cs)
        # EVs
        for i in range(self.no_evs):
            ev = EV(i + self.no_css, self)
            self.schedule.add(ev)
            self.evs.append(ev)
            # # chargepoints
        # for i in range(self.no_cps):
        #     cp = Chargepoint(i * 100, self)
        #     self.schedule.add(cp)
        #     self.chargepoints.append(cp)
        # assign checkpoints to charging points
        # for  i, cs in enumerate(self.chargestations):
            # cs._checkpoint_id = self.checkpoints[i]        
        # display Charge stations and their checkpoints
       
        print(f"\nNumber of Charging Stations: {len(self.chargestations)}")
        for cs in self.chargestations:
            # print(f"Charging Station: {cs.unique_id} is at checkpoint: {cs._checkpoint_id} kilometers.")
            print(f"Charging Station: {cs.unique_id} is at checkpoint: {cs.checkpoint_id} kilometers.")
        # data collector
        self.datacollector = DataCollector(
            model_reporters={'EVs Charging': get_evs_charge,
                             'EVs Activated': get_evs_active,
                             'EVs Travelling': get_evs_travel,
                             'EVs Queued': get_evs_queue,
                             'EVs Dead': get_evs_dead,
                             'EVs Charge Level': get_evs_charge_level,
                             'EVs Range Anxiety': get_evs_range_anxiety,
                             'EVs Not Idle': get_evs_not_idle,
                             'EVs EOD Battery SOC': get_eod_evs_socs,
                             'EVs Destinations': get_evs_destinations,
                             'EVs at Charging Station - S': get_evs_at_station_state,
                             'Length of Queue at Charging Stations': get_queue_length,
                            #  'EVs at Charging Stations': get_evs_at_cstation,
                             'EV State': get_state_evs,

                             },
            # agent_reporters={'Battery': 'battery',
            #                 'Battery EOD': 'battery_eod',
            #                 'Destination': 'destination',
            #                 'State': 'state',
            #                 }
                             )
        print(f"\nModel initialised. {self.no_evs} EVs and {self.no_css} Charging Points. Simulation will run for {self.ticks} ticks or {self.max_days} days.\n")
        # print(f"Charging station checkpoints: {self.checkpoints}")
    
    # def compute_ev_start_time(self, ev) -> int:
    #     """Compute the start time for the EV agent."""
    #     start_time = np.random.randint(5, 7)
    #     return start_time
        

    def compute_checkpoints(self,n) -> list:
        """Compute the checkpoints for the simulation.
        Args:
            n (int): Number of charging points.
        
        Returns:
            checkpoints (list): List of checkpoints.
        """
        start = 40
        # steps = n
        interval = 40
        checkpoints = np.arange(start, interval * n , interval)
        return checkpoints
    
    def model_finish_day(self) -> None: 
        """
        Reset the EVs at the end of the day. Calls the EV.add_soc_eod() and EV.finish_day() methods.
        """
        for ev in self.evs:
            ev.add_soc_eod()
            ev.finish_day()

    def update_day_count(self) -> None:
        """Increments the day count of the simulation. Called at the end of each day."""
        self.current_day_count += 1
        print(f"\nCurrent day: {self.current_day_count}.")

    def set_max_days(self) -> None:
        """Set the max number of days for the simulation."""
        self.max_days = self.ticks / 24
        # print(f"Max days: {self.max_days}")

    def ev_relaunch(self) -> None:
        """
        Relaunches EVs that are dead or idle at the end of the day. Ignores EVs that are charging or travelling.
        """
        for ev in self.evs:
            if ev.machine.state == 'Battery_dead':
                ev.relaunch_dead()
            elif ev.machine.state == 'Idle':
                ev.relaunch_idle()
            elif ev.machine.state == 'Travel':
                ev.relaunch_travel()
            elif ev.machine.state == 'Charge':
                ev.relaunch_charge()
                pass
            # ev.update_home_charge_prop()
    
    def start_overnight_charge_evs(self) -> None:
        """Calls the EV.charge_overnight() method for all EVs in the model."""
        for ev in self.evs:
            try:
                ev.machine.start_home_charge()
                # ev.charge_overnight()
            except MachineError:
                print(f"Error in charging EVs overnight. EV {ev.unique_id} is in a state other than Idle or Battery_Dead.")
    
    def end_overnight_charge_evs(self) -> None:
        """Calls the EV.end_home_charge() method for all EVs in the model."""
        for ev in self.evs:
            try:
                ev.machine.end_home_charge()
                # ev.end_overnight_charge()
            except MachineError:
                print(f"Error in ending overnight charging. EV {ev.unique_id} is in a state other than Idle or Battery_Dead.")

    # def step(self, shuffle_types = True, shuffle_agents = True) -> None:
    def step(self) -> None:
        """Advance model one step in time"""
        print(f"\nCurrent timestep (tick): {self._current_tick}.")
        # print("Active Css: " + str(get_active_css(self)))
        # print(self.get_agent_count(self))
        self.schedule.step()
        self.datacollector.collect(self)

        # if self.schedule.steps % 24 == 0:
        if self._current_tick % 24 == 0:
            # print(f"This is the end of day:{(self.schedule.steps + 1) / 24} ")
            self.model_finish_day()
            self.update_day_count()
            # print(f"This is the end of day: {self.schedule.steps / 24}. Or {self.current_day_count} ")
            print(f"This is the end of day: {self.current_day_count} ")
        self._current_tick += 1

        # relaunch at beginning of day
        if self._current_tick > 24 and self._current_tick % 24 == 1:
            try: 
                self.ev_relaunch() #current no of days
            except MachineError:
                print("Error in relaunching EVs. EV is in a state other than Idle or Battery_Dead.")
            # else:
            #     print("Some other error.")
        
        # overnight charging. integration with relaunch??
        # start overnight charging. Every day at 02:00
        if self._current_tick > 24 and self._current_tick % 24 == 2:
                try:
                    self.start_overnight_charge_evs()
                except MachineError:
                    print("Error in charging EVs overnight. EV is in a state other than Idle or Battery_Dead.")
                except Exception:
                    print("Some other error occurred when attempting to charge EVs overnight.")
        
        # # end overnight charging. Every day at 05:00
        # if self._current_tick > 24 and self._current_tick % 24 == 5:
        #     self.end_overnight_charge_evs()
                





# ############################################################################################################


# class EVModel(Model):
#     """Simulation Model with EV agents and Charging Points agents.
    
#     Args:
#         no_evs (int): Number of EV agents to create.
#         no_css (int): Number of Charging Point agents to create.
#         ticks (int): Number of ticks to run the simulation for.
        
#     Attributes: 
#         ticks (int): Number of ticks to run the simulation for.
#         _current_tick (int): Current tick of the simulation.
#         no_evs (int): Number of EV agents to create.
#         no_css (int): Number of Charging Point agents to create.
#         schedule (RandomActivation): Schedule for the model.
#         evs (list): List of EV agents.
#         chargestations (list): List of Charging Point agents.
            
#     """
  
#     def __init__(self, no_evs, no_css, ticks, cp_count) -> None:
#         """
#         Initialise the model.
        
#         Args:
#             no_evs (int): Number of EV agents to create.
#             no_css (int): Number of Charging Point agents to create.
#             ticks (int): Number of ticks to run the simulation for.

#         """
#         super().__init__()
#         # init with input args
#         self.running = True
#         self.random = True
#         self.ticks = ticks
#         self._current_tick = 1
#         self.no_evs = no_evs
#         self.no_css = no_css
#         # self.checkpoints = [40, 80, 120, 160, 200, 240, 280]
#         self.checkpoints = self.compute_checkpoints(self.no_css+1) #+1 to ensure no overruns.
#         self.current_day_count = 0
#         self.max_days = 0
#         self.set_max_days()
#         # other key model attr 
#         # self.schedule = mesa.time.RandomActivation(self)
#         self.schedule = mesa.time.StagedActivation(self, shuffle=False, shuffle_between_stages=False, stage_list=['stage_1','stage_2'])
#         # self.schedule = SimultaneousActivation(self)
#         # self.schedule = RandomActivationByType(self) #requires addional args in model.step()
#         # Populate model with agents
#         self.evs = []
#         self.chargestations = []
        
#         # Setup
#         # evs
#         for i in range(self.no_evs):
#             ev = EV(i,self)
#             self.schedule.add(ev)
#             self.evs.append(ev)
#         # charging points
#         for i in range(self.no_css):
#             # cs = ChargeStation(i + no_evs, self)
#             cs = ChargeStation(i + no_evs, self, cp_count)
#             # for i in range(self.cp_count):
#                 # cs.cp(i) = None
#             self.schedule.add(cs)
#             self.chargestations.append(cs)
#         # assign checkpoints to charging points
#         for  i, cs in enumerate(self.chargestations):
#             cs._checkpoint_id = self.checkpoints[i]        
#         # display Charge stations and their checkpoints
#         print(f"\nNumber of Charging Stations: {len(self.chargestations)}")
#         for cs in self.chargestations:
#             print(f"Charging Station: {cs.unique_id} is at checkpoint: {cs._checkpoint_id} kilometers.")
#         # data collector
#         self.datacollector = DataCollector(
#             model_reporters={'EVs Charging': get_evs_charge,
#                              'EVs Activated': get_evs_active,
#                              'EVs Travelling': get_evs_travel,
#                              'EVs Queued': get_evs_queue,
#                              'EVs Dead': get_evs_dead,
#                              'EVs Charge Level': get_evs_charge_level,
#                              'EVs Range Anxiety': get_evs_range_anxiety,
#                              'EVs Not Idle': get_evs_not_idle,
#                              'EVs EOD Battery SOC': get_eod_evs_socs,
#                              'EVs Destinations': get_evs_destinations,
#                              'EVs at Charging Station - S': get_evs_at_station_state,
#                             #  'Length of Queue 1 at Charging Stations': get_queue_1_length,
#                             #  'Length of Queue 2 at Charging Stations': get_queue_2_length,
#                              'Length of Queue at Charging Stations': get_queue_length,
#                              'EVs at Charging Stations': get_evs_at_cstation,
#                              },
#             # agent_reporters={'Battery': 'battery',
#             #                 'Battery EOD': 'battery_eod',
#             #                 'Destination': 'destination',
#             #                 'State': 'state',
#             #                 }
#                              )
#         print(f"\nModel initialised. {self.no_evs} EVs and {self.no_css} Charging Points. Simulation will run for {self.ticks} ticks or {self.max_days} days.\n")
#         # print(f"Charging station checkpoints: {self.checkpoints}")
    
#     # def compute_ev_start_time(self, ev) -> int:
#     #     """Compute the start time for the EV agent."""
#     #     start_time = np.random.randint(5, 7)
#     #     return start_time
        

#     def compute_checkpoints(self,n) -> list:
#         """Compute the checkpoints for the simulation.
#         Args:
#             n (int): Number of charging points.
        
#         Returns:
#             checkpoints (list): List of checkpoints.
#         """
#         start = 40
#         # steps = n
#         interval = 40
#         checkpoints = np.arange(start, interval * n , interval)
#         return checkpoints
    
#     def model_finish_day(self) -> None: 
#         """
#         Reset the EVs at the end of the day. Calls the EV.add_soc_eod() and EV.finish_day() methods.
#         """
#         for ev in self.evs:
#             ev.add_soc_eod()
#             ev.finish_day()

#     def update_day_count(self) -> None:
#         """Increments the day count of the simulation. Called at the end of each day."""
#         self.current_day_count += 1
#         print(f"\nCurrent day: {self.current_day_count}.")

#     def set_max_days(self) -> None:
#         """Set the max number of days for the simulation."""
#         self.max_days = self.ticks / 24
#         # print(f"Max days: {self.max_days}")

#     def ev_relaunch(self) -> None:
#         """
#         Relaunches EVs that are dead or idle at the end of the day. Ignores EVs that are charging or travelling.
#         """
#         for ev in self.evs:
#             if ev.machine.state == 'Battery_dead':
#                 ev.relaunch_dead()
#             elif ev.machine.state == 'Idle':
#                 ev.relaunch_idle()
#             elif ev.machine.state == 'Travel':
#                 ev.relaunch_travel()
#             elif ev.machine.state == 'Charging':
#                 ev.relaunch_charge()
#                 pass
#             # ev.update_home_charge_prop()
    
#     def overnight_charge_evs(self) -> None:
#         """Calls the EV.charge_overnight() method for all EVs in the model."""
#         for ev in self.evs:
#             ev.charge_overnight()

#     # def step(self, shuffle_types = True, shuffle_agents = True) -> None:
#     def step(self) -> None:
#         """Advance model one step in time"""
#         print(f"\nCurrent timestep (tick): {self._current_tick}.")
#         # print("Active Css: " + str(get_active_css(self)))
#         # print(self.get_agent_count(self))
#         self.schedule.step()
        
#         # old code
#         # if self.schedule.steps % 24 == 0:
#         #     # print(f"This is the end of day:{(self.schedule.steps + 1) / 24} ")
#         #     print(f"This is the end of day: {self.schedule.steps / 24}. ")
#         #     for ev in self.evs:
#         #         ev.add_soc_eod()
#         #         ev.choose_journey_type()
#         #         ev.choose_destination(ev.journey_type)
#         #         ev.set_new_day()
#         self.datacollector.collect(self)

#         # if self.schedule.steps % 24 == 0:
#         if self._current_tick % 24 == 0:
#             # print(f"This is the end of day:{(self.schedule.steps + 1) / 24} ")
#             self.model_finish_day()
#             self.update_day_count()
#             # print(f"This is the end of day: {self.schedule.steps / 24}. Or {self.current_day_count} ")
#             print(f"This is the end of day: {self.current_day_count} ")
#         self._current_tick += 1

#         # soft reset at beginning of day
#         if self._current_tick > 24 and self._current_tick % 24 == 1:
#             try: 
#                 self.ev_relaunch() #current no of days
#             except MachineError:
#                 print("Error in relaunching EVs. EV is in a state other than Idle or Battery_Dead.")
#             # else:
#             #     print("Some other error.")
        
#         # overnight charging. integraition with relaunch??
#         # # overnight charging. Every day at 02:00
#         # if self._current_tick > 24 and self._current_tick % 24 == 2:
#         #     self.overnight_charge_evs()