import numpy as np
from random import choice, randint, random, sample
import mesa
from mesa import Model
from mesa.datacollection import DataCollector
from EV.agent import EV, ChargeStation, Location
from transitions import MachineError
import EV.worker as worker
import EV.modelquery as mq
from datetime import datetime
from collections import OrderedDict
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

    def __init__(self, no_evs, station_params, location_params, station_location_param, overnight_charging, ticks, grid_height, grid_width) -> None:
        """
        Initialise the model.
        
        Args:
            no_evs (int): Number of EV agents to create.
            station_params (dict): Dictionary of model parameters.
            location_params (dict): Dictionary of model parameters.
            ticks (int): Number of ticks to run the simulation for.
        
        TO-DO:    

        """
        super().__init__()
        # init with input args
        self.running = True
        self.random = True
        self.ticks = ticks

        # section 1 - user station_params 
        self.no_evs = no_evs
        self.no_locations = len(location_params)
        self.station_params = station_params
        self.location_params = OrderedDict(location_params)
        self.station_locations = OrderedDict(station_location_param)
        self.overnight_charging = overnight_charging
        
        # print(f"location params {self.location_params}")                          #OK
        self.no_css = len(self.station_locations) # number of charging stations
        self._current_tick = 1
        self.current_day_count = 0
        self.max_days = 0
        self.set_max_days()
        
        # other key model attr 
        self.schedule = mesa.time.StagedActivation(self, shuffle=False, shuffle_between_stages=False, stage_list=['stage_1','stage_2'])
        self.grid = mesa.space.MultiGrid(height=grid_height, width=grid_width, torus=True) # torus=True means the grid wraps around. TO-DO: remove hardcoding of grid size.
        # create core model structures
        self.evs = []
        self.chargestations = []
        self.locations = []
        self.csroutes = []
        self.evroutes = []
        
        # set up routes
        # section 2 - create routes iterable
        self.routes = worker.get_routes(self.station_params)
        self.all_routes = set(worker.get_combinations(self.location_params)) #/locations .csv param file
        print(f"\nAvailable routes: {self.routes}")
        print("\n")
    
        self.cs_route_choices = {route: len(self.station_params[route]) for route in self.station_params}
        self.checkpoints = 0
        
        # Building environment 
        print("\nWelcome to the ec4d EV ABM Simulator v 0.3.5-beta.")
        print(f"\nToday's date is: {str(datetime.today())}.")
        print("\nBuilding model environment from input parameters...")
        print(f"\nAvailable routes: {self.routes}")
        
        # Dynamically create checkpoint_route list, distance list, and route checkpoint variables
        for route in self.routes:
            # Create checkpoint_route list variables for model. Depends on number of routes.
            setattr(self,f"checkpoints_{route}", [])
            # Set distance lists from checkpoints lists for each available route. lists contain i.e CS distances - from start to end of route.
            # last nest level is the total distance for the route. Converts individual distances to cumulative sum, relative to start of route.
            setattr(self,f"distances_{route}", worker.cumulative_cs_distances(worker.get_dict_values(worker.get_charging_stations_along_route(self.station_params, route))))
            # Assign route checkpoints to model attributes
            setattr(self,f"checkpoints_{route}", list(worker.get_route_from_config(route, self.station_params)))
            # Make duplicate of 'distances_{route}' the above for later assignment to EVs.
            setattr(self,f"ev_distances_{route}", worker.cumulative_cs_distances(worker.get_dict_values(worker.get_charging_stations_along_route(self.station_params, route))))

        # create cs.routes list to assign routes to CSs from.
        for route in worker.select_route_as_key(self.cs_route_choices):
            self.csroutes.append(route)
        
        # print(f"\nRoute choice space for ChargeStation agents: {self.csroutes}")
        # print(f"\nRoute choice space for EV agents: {self.routes}")

        print("\nCreating agents...")
    
        # Populate model with agents
        
        # ChargingStations 
        for i in range(self.no_css):
            cs = ChargeStation(i, self)
            self.schedule.add(cs)
            self.chargestations.append(cs)
        print("\n")

        # EVs
        for i in range(self.no_evs):
            ev = EV(i + self.no_css, self)
            self.schedule.add(ev)
            self.evs.append(ev)
        print("\n")

        # Locations 
        for i in range(self.no_locations):
            location = Location(i + self.no_evs + self.no_css,self)
            self.schedule.add(location)
            self.locations.append(location)
      
        print("\nAgents Created")
        
        print("\nUpdating agents with particulars - route (EV and CS), destination (EV), charge point count (CS), grid locations ...")

        # assign routes to chargestations using model chargestations and csroutes lists.
        for  i, cs in enumerate(self.chargestations):
            cs.route = self.csroutes[i]        
        
        # Set name, inital locations coordinates for Locations
        for i, loc in enumerate(self.locations):
            loc.name = list(location_params.keys())[i]
            loc.pos = list(location_params.values())[i]

        # Set inital locations and coordinates for Charging Stations
        for i, cs in enumerate(self.chargestations):
            cs.name = list(station_location_param.keys())[i]
            cs.pos = list(station_location_param.values())[i]

        print(f"\nChargeStation coordinates set.")
         # Summarize ChargeStation information

        print("\nCharge stations, positions and associated routes:")
        # Assign checkpoint_id, no_cps and cp_rates attributes to CSs from config file. Also, assign charge point count and create cps.
        for cs in self.chargestations:
            # cs.checkpoint_list = getattr(self, f"distances_{cs.route}")
            cs.checkpoint_id = worker.remove_list_item_seq(getattr(self, f"distances_{cs.route}"))
            cs.no_cps = worker.remove_list_item_seq(worker.get_dict_values(worker.count_charge_points_by_station(self.station_params, cs.route)))
            cs.cprates = worker.remove_list_item_seq(worker.get_dict_values(worker.get_power_values_for_route(self.station_params, cs.route)))
            # Display Charge stations and their routes  
            print(f"CS {cs.unique_id}, Route: {cs.route}, Position: {cs.pos}. Number of charge points: {cs.no_cps}. CP rates: {cs.cprates} ")  #CheckpointID: {cs.checkpoint_id} kilometres on route {cs.route}
            # dynamically create chargepoints per charge station lists vars. Not zero indexed. Each element is charge rate for each cp.
            for i in range(1,cs.no_cps+1):
                # setattr(cs, f"cp_{i}", [])
                setattr(cs, f"cp_{i}", None)
                
            # place CS agent on grid
            self.grid.place_agent(cs, cs.pos)
        
        # loop to update distance goal, route_name, total_route_length

        # Route assignment for EVs as in CSs above. improve to spead evenly amongst routes.
        # Perform every day at relaunch? Currently in evs_relaunch() method.
      
        self.ev_launch_sequence()

        # same done for EVs in earlier loop above

        print("\n")
        print("The location agents in this model are: \n")
        for loc in self.locations:
            print(f"Location {loc.name}, Position: {loc.pos}")
            self.grid.place_agent(loc, loc.pos)

        # end of update section
        print("\nAgents Updated")
         
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
        print(f"\nModel initialised. {self.no_evs} EVs and {self.no_css} Charging Points. Simulation will run for {self.ticks} ticks or {self.max_days} day(s).\n")



    def _set_up_routes(self) -> None:
        for route in self.routes:
            setattr(self, route, str(route))
    
    def _set_up_checkpoints(self, route, station_config)-> list:
        a = worker.get_route_from_config(route, station_config)
        b = (list(a.keys()))
        c = worker.cumulative_cs_distances(b)
        print(c)
        return c
    
    def model_finish_day_evs_css(self) -> None: 
        """
        Reset the EVs at the end of the day. Calls the EV.add_soc_eod() and EV.finish_day() methods.
        """
        for ev in self.evs:
            print("\n")
            ev.add_soc_eod()
            ev.reset_odometer()
            # print out ev locations
            print(f"EV {ev.unique_id}, State: {ev.machine.state}, Route: {ev.route}, Current Location (LSM): {ev.loc_machine.state}")
            # print(f"EV {ev.unique_id}, Route: {ev.route}, Destination: {ev.destination}, Distance Goal: {ev._distance_goal}, Checkpoint List: {ev.checkpoint_list}")
        
        for cs in self.chargestations:
            print(f"\nCS ID {cs.unique_id}, Name {cs.name},Route: {cs.route}, Position: {cs.pos}, CheckpointID: {cs.checkpoint_id} kilometres on route {cs.route}. Occupancy: {cs.location_occupancy}, Length of Occupied CPs {len(cs.occupied_cps)} , Length of Queue: {len(cs.queue)}")
    
    def model_start_day_evs(self) -> None: 
        """
        Sets up the EVs at the start of the day.
        """
        print("\nEVs reset for new day. Assigning new routes, destinations and distance goals... \n")

        self.ev_launch_sequence()


    def ev_launch_sequence(self) -> None:
        """
        Launches the EVs at the start of the simulation. Called at the start of the simulation.
        """
        for ev in self.evs:
            if self.current_day_count == 0:
                ev.route = choice(self.routes)
                
            elif self.current_day_count >= 1:
                possibilities = worker.get_possible_journeys_long(ev.loc_machine.state)
                ev.route = choice(possibilities)
                print(f"\nEV {ev.unique_id}, Location: {ev.loc_machine.state}, Route possibilities: {possibilities}")
                print(f"EV {ev.unique_id}, New Route: {ev.route}")

            # ev.route = choice(self.routes)
            ev.set_start_time()
           
            # set source attribute from route.
            ev.get_initial_location_from_route(ev.route) 
            # extract destination from route. Set destination attribute from route.
            ev.get_destination_from_route(ev.route)
            # set LSM source location from route  
            ev.set_source_loc_mac_from_source(ev.source)
            # coords 
            ev.select_initial_coord(self)
            ev.select_destination_coord(self)
            ev.get_distance_goal_and_coord_from_dest()
            # place ev agent on grid
            self.grid.place_agent(ev, ev.pos)
            ev.initialization_report(self)
        

    def update_day_count(self) -> None:
        """Increments the day count of the simulation. Called at the end of each day."""
        self.current_day_count += 1
        print(f"\nCurrent day: {self.current_day_count}.")

    def set_max_days(self) -> None:
        """Set the max number of days for the simulation."""
        self.max_days = self.ticks / 24

    def evs_relaunch(self) -> None:
        """
        Relaunches EVs that are dead or idle at the end of the day. Ignores EVs that are charging or travelling.
        """
        for ev in self.evs:
            if ev.machine.state == 'Battery_dead':
                ev.relaunch_dead(ev.model)
            elif ev.machine.state == 'Idle':
                ev.relaunch_idle()
            elif ev.machine.state == 'Travel':
                ev.relaunch_travel()
            elif ev.machine.state == 'Charge':
                ev.relaunch_charge()
                pass
    
    def start_overnight_charge_evs(self) -> None:
        """Calls the EV.charge_overnight() method for all EVs in the model."""
        for ev in self.evs:
            try:
                ev.machine.start_home_charge()
                ev.charge_overnight()
            except MachineError:
                print(f"Error in charging EVs overnight. EV {ev.unique_id} is in a state other than Idle.")
    
    def start_overnight_charge_ev(self) -> None:
        """
        """
        for ev in self.evs:
            try:
                ev.machine.start_home_charge()
                ev.charge_overnight()
            except MachineError:
                print(f"Error in charging EVs overnight. EV {ev.unique_id} is in a state other than Idle.")

    def end_overnight_charge_evs(self) -> None:
        """Calls the EV.end_home_charge() method for all EVs in the model."""
        for ev in self.evs:
            try:
                ev.machine.end_home_charge()
                # ev.end_overnight_charge()
                print(f"EV {ev.unique_id} has ended overnight charging and is now in State: {ev.machine.state}.")
            except MachineError:
                print(f"Error in ending overnight charging. EV {ev.unique_id} is in a state other than Home_charge.")
    
    # def end_overnight_charge_ev(self) -> None:
    #     for ev in self.evs:
    #         if (ev.start_time - 1) == self._current_tick:
    #             try:
    #                 ev.machine.end_home_charge()
    #             except MachineError:
    #                 print(f"Error in ending overnight charging. EV {ev.unique_id} is in a state other than Home_charge.")

    def step(self) -> None:
        """Advance model one step in time"""
        print(f"\nCurrent timestep (tick): {self._current_tick}.")
        self.schedule.step()
        self.datacollector.collect(self)

        # if self.schedule.steps % 24 == 0:
        if self._current_tick % 24 == 0:
            self.model_finish_day_evs_css()
            self.update_day_count()
            print(f"This is the end of day: {self.current_day_count} ")

        # relaunch at beginning of day
        if self._current_tick > 24 and self._current_tick % 24 == 1:
            try: 
                self.evs_relaunch() #current no of days
                self.model_start_day_evs()
            except MachineError:
                print("Error in relaunching EVs. EV is in a state other than Idle or Battery_Dead.")
            else:
                print("Some other error.")
        
        # start overnight charging. Every day at 02:00
        # overnight charging integration with relaunch?
        
        if self.overnight_charging == True:
            if self._current_tick > 24 and self._current_tick % 24 == 2:
                try:
                    self.start_overnight_charge_evs()
                except MachineError:
                    print("Error in charging EVs overnight. EV is in a state other than Idle or Battery_Dead.")
                except Exception:
                    print("Some other error occurred when attempting to charge EVs overnight.")
            # elif self._current_tick > 24 and self._current_tick % 24 == 8:
            #     self.end_overnight_charge_evs()

        # end overnight charging. Every day at 05:00
        # rewrite overnight charging stop to be individual for EVs.
        # Also, dependent on model time and start time of EV.

        # if self._current_tick > 24 and self._current_tick % 24 == 5:
        # if self._current_tick > 24 and self._current_tick % 24 == 5:
        #     if self.overnight_charging == True:
        #         self.end_overnight_charge_evs()

        # Last step of the day
        self._current_tick += 1
                


