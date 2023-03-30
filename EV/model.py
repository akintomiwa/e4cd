import numpy as np
from random import choice, randint, random, sample
import mesa
from mesa import Model
from mesa.datacollection import DataCollector
from EV.agent import EV, ChargeStation
from transitions import MachineError
import config.worker as worker
import EV.modelquery as mq
# from mesa.time import RandomActivation, SimultaneousActivation, RandomActivationByType



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
            params (dict): Dictionary of model parameters.
            ticks (int): Number of ticks to run the simulation for.
        
        TO-DO:    

        """
        super().__init__()
        # init with input args
        self.running = True
        self.random = True
        self.ticks = ticks

        # section 1 - user params 
        self.no_evs = no_evs
        self.params = params
        # total number of CSs for all routes
        self.no_css = worker.sum_total_charging_stations(self.params)                            #OK
        self._current_tick = 1
        self.current_day_count = 0
        self.max_days = 0
        self.set_max_days()
        
        # other key model attr 
        self.schedule = mesa.time.StagedActivation(self, shuffle=False, shuffle_between_stages=False, stage_list=['stage_1','stage_2'])
        
        # create core model structures
        self.evs = []
        self.chargestations = []
        self.csroutes = []
        self.evroutes = []
        
        # set up routes
        # section 2 - create routes iterable
        self.routes = worker.get_routes(self.params)
        self.cs_route_choices = {route: len(self.params[route]) for route in self.params}
        self.checkpoints = 0
        
        # Building environment 
        print("\nBuilding model environment from input parameters...")
        print(f"\nAvailable routes: {self.routes}")
        
        # section 3

        # dynamically create checkpoint_route list variables for model. Depends on number of routes.
        for route in self.routes:
            setattr(self,f"checkpoints_{route}", [])
        
        # dynamically set distance lists from checkpoints lists for each available route. lists contain i.e CS distances - from start to end of route.
        # last nest level is the total distance for the route. Converts individual distances to cumulative sum, relative to start of route.
        for route in self.routes:
            setattr(self,f"distances_{route}", worker.cumulative_cs_distances(worker.get_dict_values(worker.get_charging_stations_along_route(self.params, route))))

        # section 4 -  update model attributes with route checkpoints, chargestation checkpoint assignments

        # Dynamically go through list of routes and assign route checkpoints to model attributes
        for route in self.cs_route_choices:
            setattr(self,f"checkpoints_{route}", list(worker.get_route_from_config(route, self.params)))
    

        # create cs.routes list to assign routes to CSs from 
        for route in worker.select_route_as_key(self.cs_route_choices):
            self.csroutes.append(route)

        
        # TO-DO: create EV routes list as for CS above
        # repetition of above for EVs. May remmove this and use a single list for both CS and EVs.
        # for route in worker.select_route_as_key(self.routes):
        #     self.evroutes.append(route)


        print(f"\nRoute choice space for ChargeStation agents: {self.csroutes}")

        print(f"\nRoute choice space for EV agents: {self.routes}")

        print("\nCreating agents...")
    
        # Populate model with agents

        # ChargingStations 
        for i in range(self.no_css):
            cs = ChargeStation(i, self)
            self.schedule.add(cs)
            self.chargestations.append(cs)
        # EVs
        for i in range(self.no_evs):
            ev = EV(i + self.no_css, self)
            self.schedule.add(ev)
            self.evs.append(ev)
      
        print("\nAgents Created")
        
        print("\nUpdating agents with particulars - route (EV and CS), destination (EV), charge point count (CS)")


        # assign routes to chargestations using model chargestations and csroutes lists.
        for  i, cs in enumerate(self.chargestations):
            cs.route = self.csroutes[i]        
        # display Charge stations and their checkpoints
        
       
                                  
        # TO-DO : write dynamic version for checkpoint_route lists vars          OK
        # use cumulative sum to get total number of checkpoints for each route
       
        # convert checkpoint lists to cumulative distance lists
        for route in self.routes:
            setattr(self, f"checkpoint_{route}", [])
            print(f"\nCheckpoint lists for Route: {route}: {getattr(self, f'distances_{route}')}") # test

        # Summarize ChargeStation information

        print("\nCharge stations, routes and associated checkpoints:")

        # Focus
        for cs in self.chargestations:
            i = worker.remove_list_item_seq(getattr(self, f"distances_{cs.route}"))
            # setattr(self, f"checkpoint_id", i)
            cs.checkpoint_id = i

            # test ???
            # if hasattr(self, f"checkpoint_id"):
            #     print("attr set")



        # display Charge stations and their routes
        for cs in self.chargestations:
            print(f"CS {cs.unique_id}, Route: {cs.route}, CheckpointID: {cs.checkpoint_id} kilometres on route {cs.route}")


        # CG 

        
        # TO-DO : Do route assignment for EVs as in CSs above.
        for ev in self.evs:
            i = choice(self.routes)
            setattr(self, f"route", i)
            print(f"EV {ev.unique_id}, Route: {ev.route}")

        
        # TO-DO: CP per CS assignment

        # section 5 - Focus
        # dynamically create chargepoints per charge station lists vars 
        for cs in self.chargestations:
            setattr(self,f"cpspcs_{cs}", [])
            # for i in range(len(self.chargestations)):
            #     getattr(self, f"cpspcs_{cs}").append(None)

        # Dynamically go through list of routes and assign cp counts to chargestation model attributes
        for cs in self.chargestations:
            setattr(self,f"cpspcs_{cs}", list(worker.get_dict_values(worker.count_charge_points_by_station(self.params, cs))))
        
        # # route CS cpcount attrib print test                        OK
        # for attr_name in dir(self):
        #     if attr_name.startswith("cpspcs_"):
        #         print(f"Charge point per cs: {attr_name} is {getattr(self, attr_name)}")


        
        for cs in self.chargestations:
            for attr_name in dir(cs):
                if attr_name.startswith("cpspcs_"):
                    print(f"CS {cs.unique_id}, Route: {cs.route}, CPCount: {getattr(cs, attr_name)}")


        # # self.cpspcs = worker.get_cs_cp_count() #list
        # self.cpspcs_AB = worker.get_dict_values(worker.count_charge_points_by_station(self.params, 'A-B'))  
        # self.cpspcs_AC = worker.get_dict_values(worker.count_charge_points_by_station(self.params, 'A-C')) 
        # # self.chargepoints = []
        # print(f"Number of CPs per CS, Route A-B: {self.cpspcs_AB}")
        # print(f"Number of CPs per CS, Route A-C: {self.cpspcs_AC}")
        


        

        # CS 
        # loop to set up chargepoints for chargestations from input dictionary
        # loop to set up route_id, route_name, distance, total_route_length = distance goal


        # EV 
        # loop to set up routes
        # loop to update distance goal, route_name, total_route_length.
        # amend chargefunction to use the charge rate of the charge point.
       
        print(f"\nNumber of Charging Stations: {len(self.chargestations)}")
     
        # data collector
        self.datacollector = DataCollector(
            model_reporters={'EVs Charging': mq.get_evs_charge,
                             'EVs Activated': mq.get_evs_active,
                             'EVs Travelling': mq.get_evs_travel,
                             'EVs Queued': mq.get_evs_queue,
                             'EVs Dead': mq.get_evs_dead,
                             'EVs Charge Level': mq.get_evs_charge_level,
                             'EVs Range Anxiety': mq.get_evs_range_anxiety,
                             'EVs Not Idle': mq.get_evs_not_idle,
                             'EVs EOD Battery SOC': mq.get_eod_evs_socs,
                             'EVs Destinations': mq.get_evs_destinations,
                             'EVs at Charging Station - S': mq.get_evs_at_station_state,
                             'Length of Queue at Charging Stations': mq.get_queue_length,
                             'EV State': mq.get_state_evs,
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

    # def route_assignment(self) -> None:
    #     """Assign routes to EV agents."""
    #     print('Assigning routes...')
    #     # for ev in self.evs:
    #     #     ev.assign_route()

    def _set_up_routes(self) -> None:
        for route in self.routes:
            setattr(self, route, str(route))
    
    def _set_up_checkpoints(self, route, station_config)-> list:
        a = worker.get_route_from_config(route, station_config)
        b = (list(a.keys()))
        c = worker.cumulative_cs_distances(b)
        print(c)
        return c

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