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

    def __init__(self, no_evs, station_params, location_params, station_location_param, ticks) -> None:
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
        
        # print(f"location params {self.location_params}")                          #OK
        self.no_css = len(self.station_locations) # number of charging stations
        self._current_tick = 1
        self.current_day_count = 0
        self.max_days = 0
        self.set_max_days()
        
        # other key model attr 
        self.schedule = mesa.time.StagedActivation(self, shuffle=False, shuffle_between_stages=False, stage_list=['stage_1','stage_2'])
        self.grid = mesa.space.MultiGrid(100, 100, torus=True) # torus=True means the grid wraps around. TO-DO: remove hardcoding of grid size.
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
            # Make duplicates of the above for later assignment to EVs.
            setattr(self,f"ev_distances_{route}", worker.cumulative_cs_distances(worker.get_dict_values(worker.get_charging_stations_along_route(self.station_params, route))))
          

        # create cs.routes list to assign routes to CSs from.
        for route in worker.select_route_as_key(self.cs_route_choices):
            self.csroutes.append(route)
        
       

        print(f"\nRoute choice space for ChargeStation agents: {self.csroutes}")

        print(f"\nRoute choice space for EV agents: {self.routes}")

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
       
        # show CS routes and associated distances. not chkpts per se, but the cummulative distances between CSs along the route, relative to start.
        for route in self.routes:
            setattr(self, f"checkpoint_{route}", [])
            # make another list of checkpoints for each route, and assign to CSs
            print(f"\nCheckpoint lists for Route: {route}: {getattr(self, f'distances_{route}')}") # test
        
        # Set name, inital locations coordinates for Locations
        for i, loc in enumerate(self.locations):
            loc.name = list(location_params.keys())[i]
            loc.pos = list(location_params.values())[i]

        # Set inital locations and coordinates for Charging Stations
        for i, cs in enumerate(self.chargestations):
            cs.name = list(station_location_param.keys())[i]
            cs.pos = list(station_location_param.values())[i]
        print(f"ChargeStation coordinates set.\n")
         # Summarize ChargeStation information

        print("\nCharge stations, positions and associated routes:")
        # Assign checkpoint_id, no_cps and cp_rates attributes to CSs from config file. Also, assign charge point count and create cps.
        for cs in self.chargestations:
            # cs.checkpoint_list = getattr(self, f"distances_{cs.route}")
            cs.checkpoint_id = worker.remove_list_item_seq(getattr(self, f"distances_{cs.route}"))
            cs.no_cps = worker.remove_list_item_seq(worker.get_dict_values(worker.count_charge_points_by_station(self.station_params, cs.route)))
            cs.cprates = worker.remove_list_item_seq(worker.get_dict_values(worker.get_power_values_for_route(self.station_params, cs.route)))
            # Display Charge stations and their routes  
            print(f"CS {cs.unique_id}, Route: {cs.route}, Position: {cs.pos}, CheckpointID: {cs.checkpoint_id} kilometres on route {cs.route}. Number of charge points: {cs.no_cps}. CP rates: {cs.cprates} ") 
            # dynamically create chargepoints per charge station lists vars. Each element is charge rate for each cp.
            for i in range(cs.no_cps):
                setattr(cs, f"cp_{i}", [])
            # place ev agent on grid
            self.grid.place_agent(cs, cs.pos)
        
        # loop to update distance goal, route_name, total_route_length
        # amend charge function to use the charge rate of the charge point.

        # Route assignment for EVs as in CSs above. improve to spead evenly amongst routes.
        # Perform every day at relaunch?
        
        print("\n")
        for ev in self.evs:
            ev.set_start_time()
            ev.route = choice(self.routes)
            ev.select_initial_coord(self)
            ev.select_destination_coord(self)
            ev.set_destination()
            ev.get_distance_goal_from_dest()
            ev.initialization_report(self)
            # # place ev agent on grid
            self.grid.place_agent(ev, ev.pos)
            print(f"EV {ev.unique_id}, Grid position: {ev.pos}, Destination Position: {ev.dest_pos}")
            
            # print(f"EV {ev.unique_id}, EV Checkpoint list: {ev.checkpoint_list}")
            # print(f"EV Location: {ev.location}, Position: {ev.pos}, Direction: {ev.direction}")
      
        # same done for EVs in earlier loop above

        print("\n")
        print("The location agents in this model are: \n")
        for loc in self.locations:
            print(f"Location {loc.name}, Position: {loc.pos}")
            self.grid.place_agent(loc, loc.pos)

        # end of update section
        print("\nAgents Updated")
        

        # print(f"\nNumber of Charging Stations: {len(self.chargestations)}, Number of EVs: {len(self.evs)}")
     
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
    
    # TO-DO: Add a method to redo set up of the EVs and their routes. 
    # under ev.finish_day; make EV methods for:
    # set new route 
    # update location machine to new location
    # update new destination
    # update distance goal
    # update checkpoint list
    # update route information from model attributes
    
    def model_finish_day_evs(self) -> None: 
        """
        Reset the EVs at the end of the day. Calls the EV.add_soc_eod() and EV.finish_day() methods.
        """
        for ev in self.evs:
            print(f"At end of day {self.current_day_count}...")
            ev.add_soc_eod()
            
            ev.reset_odometer()
            ev.increment_day_count()
            # print out ev locations
            
            print(f"EV {ev.unique_id}, Route: {ev.route}, Destination: {ev.destination}, Distance Goal: {ev._distance_goal}, Checkpoint List: {ev.checkpoint_list}")
    
    def model_start_day_evs(self) -> None: 
        """
        Sets up the EVs at the start of the day.
        """
        print("EVs reset for new day. Assigning new routes, destinations and distance goals... \n")
        for ev in self.evs:
            # new
            ev.route = choice(self.routes)
            # set location machine to start of route
            ev.get_destination_from_route(ev.route)
            # set destination from possible choices
            ev.set_initial_loc_mac_from_route(ev.route) 
            # set distance goalc
            ev.set_distance_goal()
            # read route information from model attributes

            ev.initialization_report(ev.model)
            

    def update_day_count(self) -> None:
        """Increments the day count of the simulation. Called at the end of each day."""
        self.current_day_count += 1
        print(f"\nCurrent day: {self.current_day_count}.")

    def set_max_days(self) -> None:
        """Set the max number of days for the simulation."""
        self.max_days = self.ticks / 24
        # print(f"Max days: {self.max_days}")

    def evs_relaunch(self) -> None:
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
            self.model_finish_day_evs()
            self.update_day_count()
            # print(f"This is the end of day: {self.schedule.steps / 24}. Or {self.current_day_count} ")
            print(f"This is the end of day: {self.current_day_count} ")
        self._current_tick += 1

        # relaunch at beginning of day
        if self._current_tick > 24 and self._current_tick % 24 == 1:
            try: 
                self.evs_relaunch() #current no of days
                self.model_start_day_evs()
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
                


