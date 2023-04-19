"""This module contains the agent classes for the EV model."""

import numpy as np
import pandas as pd
import math
# import os
import random
from random import choice
import warnings
warnings.simplefilter("ignore")
import numpy as np
from mesa import Agent
from mesa.datacollection import DataCollector
from matplotlib import pyplot as plt, patches
import scipy.stats as ss
import cufflinks as cf
cf.go_offline()
# from plotly.offline import iplot
from transitions import Machine, MachineError
# from transitions.extensions.diagrams import GraphMachine
from functools import partial
from EV.statemachines import EVSM, LSM, states, transitions, lstates, ltransitions
import EV.worker as worker


class ChargeStation(Agent):
    """A charging station (CS) agent.
    Attributes:
        unique_id: Unique identifier for the agent.
        model: The model the agent is running in.
        queue_1: A list of EVs waiting to charge at the CS.
        queue_2: A list of EVs waiting to charge at the CS.
        _active_ev_1: The first EV currently charging at the CS.
        _active_ev_2: The second EV currently charging at the CS.
        _charge_rate: The rate at which the CS charges an EV.
        checkpoint_id: The ID of the checkpoint the CS is associated with, on its route. Initialised to 0. Subsequently updated by model.
    Post initialisation attributes:
        route: The route the CS is associated with.
        checkpoint_id: Updated by model.
        no_cps: The number of charging points at the CS.
        cp_rates: The charging rates of the charging points at the CS.
        cp_{i}: The i-th charging point at the CS.
        



    Methods:
        __init__: Initialises the agent.
        __str__: Returns the agent's unique id.
        dequeue_ev: Removes the first EV from queue_1.
        finish_charge_ev: Finish charging the EV at CP1 at the Charge Station.
        stage_1: Stage 1 of the agent's step function.
        stage_2: Stage 2 of the agent's step function.

    """
    def __init__(self, unique_id, model): #rem: no_cps,
        super().__init__(unique_id, model)
        # Start initialisation
        self.queue = []
        self.occupied_cps = set()
        self.no_cps = 0
        self._is_active = False
        # self._charge_rate = choice([7, 15, 100, 300]) #different charge rates
        # self.base_cp_count = 0
        self.checkpoint_id = 0 # was 0 

        # new
        self.route = None
        self.cplist = None

        self.name = None
        self.pos = None

        self.cprates = []  #kW
        self._charge_rate = 0
        
        self.prelim_report()
        
        # self.init_report()

        # End initialisation
    
    def prelim_report(self):
        print(f"CS {(self.unique_id)}, initialized.")

    def init_report(self):
        print(f"\nCS info: ID: {(self.unique_id)}, initialized. Charge rates for charge points: {self.cprates} kW.")
        print(f"It has {self.no_cps} charging points.")
        for i in range(self.no_cps):
            print(f"CP_{i} is {(getattr(self, f'cp_id_{i}'))}")
    
    
    def get_cp_rating_by_index(self, index):
        cp_attrs = sorted([key for key in vars(self) if key.startswith('cp_')], key=lambda x: int(x.split('_')[1]))
        cp_key = cp_attrs[index]
        # cp_value = getattr(self, cp_key) #EV itself?
        rate_value = self.cprates[index]
        # return cp_value * rate_value
        return rate_value

    # def _charge_rate(self):
    #     charge_rate = 0
    #     for i in range(self.no_cps):
    #         rate = self.get_cp_rating_by_index(i)
    #         print(f"CP_{i} is {(getattr(self, f'cp_id_{i}'))} and has a charge rate of {rate} kW.")
    #         rate.append(charge_rate)
    #     print(f"Charge rate vector is {charge_rate} kW.")
    #     return charge_rate
            

    def __str__(self) -> str:
        """Return the agent's unique id."""
        return str(self.unique_id + 1)
 

    def dequeue(self) -> bool:
        """Remove the first EV from queue."""
        try:
            active = self.queue.pop(0)  # pick first EV in queue
            if active is None:
                return False
            # go through all charge points and assign the first one that is free
            for attr_name in [a for a in dir(self) if a.startswith("cp_")]:
                attr_value = getattr(self, attr_name)
                if attr_value is None and attr_name not in self.occupied_cps:
                    setattr(self, attr_name, active)
                    active.machine.start_charge()
                    self.occupied_cps.add(attr_name)
                    print(f"EV {active.unique_id} dequeued at CS {self.unique_id} at CP {attr_name} and is in state: {active.machine.state}. Charging started")
                    return True
            # if all charge points are occupied, reinsert active into queue
            self.queue.insert(0, active)
            print(f"EV {active.unique_id} remains in queue at CS {self.unique_id} and is in state: {active.machine.state}.")
            return False
        except IndexError:
            print(f"The queue at ChargeStation {self.unique_id} is empty.")
            return False
        except Exception as e:
            print(f"Error assigning EV to charge point: {e}")
            return False

    
    # March rewrite 1
    def finish_charge(self) -> None:
        try:
            for attr_name in dir(self):
                if attr_name.startswith("cp_"):
                    attr_value = getattr(self, attr_name)
                    if attr_value is None:
                        print(f"This CP, {attr_name} at ChargeStation {self.unique_id} is empty.")
                    else:
                        if attr_value.battery < attr_value._soc_charging_thresh:
                            # attr_value.charge()
                            attr_value.machine.continue_charge()
                            print(f"EV {(attr_value.unique_id)} at CS {self.unique_id} at CP {attr_name} is in state: {attr_value.machine.state}. Charging continues.")
                        elif attr_value.battery >= attr_value._soc_charging_thresh:
                            attr_value.machine.end_charge()
                            setattr(self, attr_name, None)
                            # new change
                            self.occupied_cps.remove(attr_name)
                            print(f"EV at CS {self.unique_id} at CP {attr_name} has finished charging. CP is now empty.")
        except:
            pass


    def stage_1(self):
        """Stage 1 of the charge station's step function."""
        # if self.active_ev_1 is None:
        #     self.dequeue_1()
        # if self.active_ev_2 is None:
        #     self.dequeue_2()
        self.dequeue()
        if self.dequeue == True:
            print(f"Dequeue successful. Length at ChargeStation {self.unique_id} is now {len(self.queue)}")  # testing
        elif self.dequeue == False:
            print(f"Dequeue unsuccessful. Length at ChargeStation {self.unique_id} is still {len(self.queue)}")
        # self.announce()

    def stage_2(self):
        """Stage 2 of the charge station's step function."""
        self.finish_charge()
        # if self.active_ev_1 is not None:
        #     if self.active_ev_1.battery < self.active_ev_1._soc_charging_thresh:
        #         self.active_ev_1.charge()
        #         self.active_ev_1.machine.continue_charge()
        #     else:    
        #         # print(f"EV {self.active_ev_2}, Pre-trans: {self.active_ev_1.machine.state}.")                                       #testing
        #         self.active_ev_1.machine.end_charge()
        #         self.finish_charge_ev_1()
        # if self.active_ev_2 is not None:
        #     if self.active_ev_2.battery < self.active_ev_2._soc_charging_thresh:
        #         self.active_ev_2.charge()
        #         self.active_ev_2.machine.continue_charge()
        #     else:
        #         # print(f"EV {self.active_ev_2}, Pre-trans: {self.active_ev_2.machine.state}.")                                       #testing
        #         self.active_ev_2.machine.end_charge()
        #         self.finish_charge_ev_2()
        # pass      



class EV(Agent):
    """An agent used to model an electric vehicle (EV).
    Attributes:
        unique_id: Unique identifier for the agent.
        model: Model object that the agent is a part of.
        _charge_rate: Charge rate of the EV in kW.
        _in_queue: Boolean value indicating whether the EV is in queue.
        _in_garage: Boolean value indicating whether the EV is in garage.
        _is_charging: Boolean value indicating whether the EV is charging.
        _was_charged: Boolean value indicating whether the EV was charged.
        _is_travelling: Boolean value indicating whether the EV is travelling.
        _journey_complete: Boolean value indicating whether the EV's journey is complete.
        machine: Primary EV State Machine.
        loc_machine: Secondary EV State Machine.
        _is_active: Boolean value indicating whether the EV is active.
        odometer: Odometer of the EV.
        _distance_goal: Distance goal of the EV.
        journey_type: Type of journey the EV is undertaking.
        _soc_usage_thresh: State of charge at which EV driver feels compelled to start charging at station.
        _soc_charging_thresh: State of charge at which EV driver is comfortable with stopping charging at station.
        _journey_choice: Choice of journey the EV driver makes.
        battery: State of charge of the EV battery.
        max_battery: Maximum state of charge of the EV.

    Methods:
        __init__: Initialise the EV agent.
        __str__: Return the agent's unique id.
        initialization_report: Print the details of the agent's initial state.
        choose_journey_type: Choose the type of journey the EV will undertake.
        set_speed: Set the speed of the EV.
        set_ev_consumption_rate: Set the energy consumption of the EV.
        choose_destination: Choose the destination of the EV.
        choose_destintion_urban: Choose the destination of the EV in an urban area.
        choose_destination_interurban: Choose the destination of the EV in an interurban area.
        energy_usage_trip: Energy usage of the EV in a trip.
        energy_usage_tick: Energy usage of the EV in a tick.
        delta_battery_neg: Calculate the change in state of charge of the EV.
        dead_intervention: Intervene if the EV is dead. Recharge the EV to max.
        set_start_time: Set the start time of the EV.
        increase_charge_prop: Increase the propensity-to-charge of the EV.
        decrease_charge_prop: Decrease the propensity-to-charge of the EV.
        travel: Travel function for the EV agent.
        charge: Charge the EV.
        charge_overnight: Charge the EV overnight.
        choose_charge_station: Choose the associated Chargestation to charge the EV.
        choose_cs_queue: Choose the queue to join at the charge station.
        add_soc_eod: Add the state of charge of the EV at the end of the day to a list.
        finish_day: Finish the day for the EV. Increment the day count. Reset the odometer.
        relaunch_base: Base EV relaunch process.
        relaunch_dead: Relaunch process for dead EVs.
        relaunch_idle: Relaunch process for idle EVs.
        start_travel: Start the travel process for the EV at the allocated start time.

        step functions:
        stage_1: Stage 1 of the agent step function. Handles the EV's journey.
        stage_2: Stage 2 of the agent step function. Handles the EV's charging.

        unused:

        tick_energy_usage: Energy usage of the EV in a tick.
        battery_eod: State of charge of the EV at the end of the day.
        day_count: Number of days the EV has been active.

        TO-DO
        pull from params:
        charge rate, distance, price, green


        
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self._charge_rate = 7.5# kW 7200W
        self._in_queue = False
        self._in_garage = False
        self._is_charging = False
        self._was_charged = False
        self._at_station = False
        self._is_travelling = False
        self._journey_complete = False
        self.route = None
        self.machine = EVSM(initial='Idle', states=states, transitions=transitions)
        self.loc_machine = LSM(initial='City_A', states=lstates, transitions=ltransitions)
        self._is_active = True
        self.odometer = 0
        self._distance_goal = 0
        self.journey_type = None
        self.destination = None
        self.battery = random.randint(30, 60) #kWh (40, 70) 
        self.max_battery = self.battery
        # To/ Fro handling
        self.to_fro = ""
        # EV Driver Behaviour
        self._speed = 0
        self.range_anxiety = 0.5    #likelihood to charge at charge station 
        # battery soc level at which EV driver feels compelled to start charging at station.
        # self._soc_usage_thresh = (0.4 * self.max_battery) 
        self._soc_usage_thresh = (self.range_anxiety * self.max_battery) 
        # battery soc level at which EV driver is comfortable with stopping charging at station.
        self._soc_charging_thresh = (0.8 * self.max_battery) 
        # Newest
        self.ev_consumption_rate = 0
        self.tick_energy_usage = 0
        self.battery_eod = []
        self.current_day_count = 1
        self.start_time = 0
        self._chosen_cs = 0 #in selected_cp correct
        self.checkpoint_list = []
        
        self.pos = None
        self.direction = None
        self.locations = []
        self.dest_pos = None

        # set EV speed
        self.set_speed()
        # set energy consumption rate
        self.set_ev_consumption_rate()
        # Home Station 
        self.home_cs_rate = 10 #kW
    
        # Initialisation Report
        self.prelim_report()
        # self.initalization_report()
    
    # Reporting functions
    def __str__(self) -> str:
        """Return the agent's unique id as a string, not zero indexed."""
        return str(self.unique_id + 1)
    
    def prelim_report(self):
        print(f"EV {(self.unique_id)}, initialized.")
    # old report 
    # def initialization_report(self) -> None:
    #     """Prints the EV's initialisation report."""
    #     print(f"\nEV info: ID: {self.unique_id}, route: {self.route}, destination name: City {self.destination}, max_battery: {self.max_battery}, energy consumption rate: {self.ev_consumption_rate}, speed: {self._speed}, State: {self.machine.state}.")
    #     print(f"EV info (Cont'd): Start time: {self.start_time}, distance goal: {self._distance_goal}, soc usage threshold: {self._soc_usage_thresh}, range anxiety {self.range_anxiety}, location: {self.loc_machine.state}.")
    #     print(f"EV {self.unique_id} Checkpoint list: {self.checkpoint_list}, direction: {self.direction}")
    def initialization_report(self, model) -> None:
        """Prints the EV's initialisation report."""
        print(f"\nEV info: ID: {self.unique_id}, max_battery: {self.max_battery:.2f}, energy consumption rate: {self.ev_consumption_rate}, speed: {self._speed}, State: {self.machine.state}.")
        print(f"EV info (Cont'd): Start time: {self.start_time},  soc usage threshold: {self._soc_usage_thresh}, range anxiety {self.range_anxiety}.")
        print(f"EV Grid info: current position: {self.pos}, destination position: {self.dest_pos}, Distance goal: {self._distance_goal}.")
        # print(f"EV {self.unique_id}, distance goal: {self._distance_goal}, location state: {self.loc_machine.state}")
        



    # Internal functions
    def set_initial_loc_mac_from_route(self, route:str):
        self.loc_machine.set_state(self.get_location_from_route(route))

    def update_loc_mac_from_destination(self, destination:str):
        """Updates the EV's location machine state to the destination on arrival.
        Args:
            destination (str): The destination of the EV's journey.
        """
        self.loc_machine.set_state(destination)
    
    def get_location_from_route(self, route:str):
        location = worker.get_string_before_hyphen(route)                        # separate get and set
        return location

    def get_destination_from_route(self, route:str):
        destination = worker.get_string_after_hyphen(route)
        self.destination = destination                          # separate get and set
        return destination
    
    def update_destination_for_new_trip(self, location:str):
        options = worker.get_possible_journeys_long(location)
        return random.choice(options)
    
    def set_speed(self) -> None:
        """Sets the speed of the EV driver."""
        base_speed = 10
        self._speed = base_speed
    
    def set_ev_consumption_rate(self) -> None:
        # baselines
        mu =  0.5 # means
        sigma = 0.1 # standard deviation
        # set vehicle energy consumption rate
        self.ev_consumption_rate = np.random.default_rng().normal(mu, sigma) # opt: size = 1
    
    def set_distance_goal(self) -> None:
        # self._distance_goal = self.checkpoint_list[-1]
        print("distance goal not set")

 
    def energy_usage_trip(self) -> float:
        """Energy consumption (EC) for the entire trip. EC is the product of distance covered and energy consumption rate.
        
        Returns:
            usage: Energy consumption for the entire trip.
        """
        usage = (self.ev_consumption_rate * self.odometer)
        return usage

    def energy_usage_tick(self) -> float:
        """Energy consumption (EC) for each tick. EC is the product of distance covered and energy consumption rate per timestep.
        
        Returns:
            usage: Energy consumption for each tick.
        """
        usage = (self.ev_consumption_rate * self._speed)
        return usage

    def delta_battery_neg(self) -> float:
        """ Marginal negative change in battery level per tick.
        
        Returns:
            delta: Marginal negative change in battery level per tick.
        """
        delta = (self.tick_energy_usage / self.max_battery)
        return delta
    
    # interventions 
    def dead_intervention(self) -> None:
        """
        Intervention for when the EV runs out of battery. The EV is recharged to the maximum by emergency services and will be transported to its destination.
        """
        self.battery = self.max_battery
        # self.odometer = self._distance_goal
        self.increase_range_anxiety()
        self.machine.emergency_intervention()
        print(f"\nEV {self.unique_id} has been recharged to {self.battery} by emergency services and is now in state: {self.machine.state}. Range anxiety: {self.range_anxiety}")

    def travel_intervention(self) -> None:
        """Intervention for when the EV is traveling. The EV is set to Idle and will be transported to its destination.
        """
        self.machine.end_travel()
        print(f"EV {self.unique_id} was forced to end its stip due to overrun. It is now in state: {self.machine.state}. ")
        # assumes EV overruning is doing interuban trip
        # self.loc_machine.set_state(f"{self.destination}")
    def charge_intervention(self) -> None:
        """Intervention for when the EV is charging. The EV is set to Idle and will be transported to its destination.
        """
        if self.machine.state == "Charge":
            self.machine.end_charge_abrupt()
        elif self.machine.state == "In_queue":
            self.machine.end_queue_abrupt()
        elif self.machine.state == "Seek_queue":
            self.machine.end_seek_queue_abrupt()

        # self.machine.end_charge_abrupt()
        print(f"EV {self.unique_id} was forced to end its charge due to time overrun. It is now in state: {self.machine.state}. ")
        # assumes EV overruning is doing interuban trip
        # self.loc_machine.set_state(f"{self.destination}")


    def set_start_time(self) -> None:
        """Sets the start time for the EV to travel. Sets start time based on distance goal - if distance goal is greater than or equal to 90 miles, start time is earlier.
        """
        # self.start_time = random.randint(6, 12)

        if self._distance_goal < 90:
            self.start_time = random.randint(10, 14)

        elif self._distance_goal >= 90:
            self.start_time = random.randint(6, 9)
    
    # Range Anxiety charging behavior
    def increase_range_anxiety(self) -> None:
        """Increases the propensity for charging. Higher propensity for charging means that the EV is more likely to charge at a Charge Station, due to having a higher soc_usage threshold.
        
        Returns:
            charge_prop: Propensity for charging behavior.
        """
        mu, sigma = 0.1, 0.01 # mean and standard deviation
        margin = np.random.default_rng().normal(mu, sigma)
        # margin = 0.1
        self.range_anxiety += abs(margin)

    def decrease_range_anxiety(self) -> None:
        """
        Decreases the propensity for charging. Lower propensity for charging means that the EV is less likely to charge at a Charge Station, due to having a lower soc_usage threshold.
        
        Returns:/
            charge_prop: Propensity for charging behavior.
        """
        mu, sigma = 0.05, 0.01 # mean and standard deviation
        margin = np.random.default_rng().normal(mu, sigma)
        # margin = 0.1
        self.range_anxiety -= abs(margin)
  
    # Core EV Functions

    def select_initial_coord(self, model) -> None:
        """Selects the initial coordinate for the EV.
        
        Returns:
            coord: Initial coordinate for the EV.
        """
        coord = random.choice(model.locations).pos
        self.pos = coord

    def select_destination_coord(self,model) -> None:
        """Gets the destination of the EV.
        
        Returns:
            destination: Destination of the EV.
        """
        # If the EV has not set a destination yet, randomly choose one of the other locations
        if self.dest_pos is None:
            locations = [l.pos for l in model.locations if l.pos != self.pos]
            self.dest_pos = random.choice(locations)
    
    def set_destination(self) -> None:
        """Sets the destination of the EV.
        
        Args:
            destination: Destination of the EV.
        """
        self.destination = worker.find_key(self.dest_pos, self.model.location_params)
        
    def get_distance_goal_from_dest(self) -> None:
        # Calculate the unit vector towards the destination
        dx = self.dest_pos[0] - self.pos[0]
        dy = self.dest_pos[1] - self.pos[1]
        self._distance_goal = math.sqrt(dx*dx + dy*dy)


    def move(self, model):
        scaling_factor= 2
        distance = self._distance_goal
 
        if distance == 0:
            # The EV has reached its destination
            self.dest_pos = None
            print(f"EV {self.unique_id} has reached its destination. IN MOVE")
            return
        
        # Calculate the unit vector towards the destination
        dx = self.dest_pos[0] - self.pos[0]
        dy = self.dest_pos[1] - self.pos[1]
        
        # Normalize the vector to get a unit vector
        dx /= distance
        dy /= distance

        scaled_x = dx * self._speed*scaling_factor
        scaled_y = dy * self._speed*scaling_factor
        
        # Calculate the next position of the EV by moving along the unit vector
        
        # next_pos = (int((self.pos[0] + dx)*self._speed), int((self.pos[1] + dy)*self._speed))
        # next_pos = (int((self.pos[0] + dx)), int((self.pos[1] + dy)))
        next_pos = (int((self.pos[0] + scaled_x)), int((self.pos[1] + scaled_y)))
        
        # Check if the next position is inside the grid boundaries
        if (0 <= next_pos[0] < model.grid.width) and (0 <= next_pos[1] < model.grid.height):
            # Move the EV to the next position
            model.grid.move_agent(self, next_pos)
            
            # # Check if the EV has encountered a ChargeStation agent
            # cellmates = model.grid.get_cell_list_contents([next_pos])
            # for cellmate in cellmates:
            #     if isinstance(cellmate, ChargeStation):
            #         cellmate.queue.append(self)
            #         # self._chosen_station = cellmate
        # else:
        #     # The next position is outside the grid, the EV has reached the edge of the grid
        #     self.dest_pos = None

    # old flow 
    # def set_initial_grid_location(self, route) -> None:
    #     """
    #     Sets the initial grid location of the EV based on the route.

    #     """
    #     self.location = worker.get_string_before_hyphen(route)
    #     self.pos = worker.get_location_coordinates_by_name(self.model.location_params, self.location)
    #     print(f"This is EV position {self.pos}")

    # def get_direction(self, route: str) -> int:
    #     """Gets the direction of the EV based on the route.
    #     """
    #     s = route
    #     # Extract the source and destination points from the input string
    #     src, dest_pos = s.split('-')
    #     # Define a dictionary to map each point to its row and column in the grid
    #     point_map = {'A': (0, 0), 'B': (0, 1), 'C': (1, 0), 'D': (1, 1)}
    #     # Get the row and column numbers for the source and destination points
    #     src_row, src_col = point_map[src]
    #     dest_row, dest_col = point_map[dest_pos]
    #     # Calculate the row and column differences between the source and destination points
    #     row_diff = dest_row - src_row
    #     col_diff = dest_col - src_col
    #     # Determine the direction based on the row and column differences
    #     if row_diff == -1 and col_diff == 0:
    #         return 1  # up
    #     elif row_diff == 0 and col_diff == 1:
    #         return 2  # right
    #     elif row_diff == 1 and col_diff == 0:
    #         return 3  # down
    #     elif row_diff == 0 and col_diff == -1:
    #         return 4  # left
    #     elif row_diff == -1 and col_diff == 1:
    #         return 5  # diagonal - right and up
    #     elif row_diff == -1 and col_diff == -1:
    #         return 6  # diagonal - left and up
    #     elif row_diff == 1 and col_diff == 1:
    #         return 7  # diagonal - right and down
    #     elif row_diff == 1 and col_diff == -1:
    #         return 8  # diagonal - left and down
    #     else:
    #         raise ValueError('Invalid input: {}'.format(s))
    
    # TO-DO: Fix this, reflect routing variable.
    def update_lsm(self) -> None:
        if self.destination == 'City A':
            self.loc_machine.city_d_2_a()
        elif self.destination == 'City B':
            self.loc_machine.city_d_2_b()
        elif self.destination == 'City C':
            self.loc_machine.city_d_2_c()
        print(f"EV {self.unique_id} is at location: {self.loc_machine.state}")



    def travel(self) -> None:
        """
        Travel function. Moves EV along the road. Updates odometer and battery level.
        
        Returns:
            odometer: Odometer reading for the EV.
            battery: Battery level for the EV.
        """
        self.move(self.model)
        # self.move(direction=direction)
        # self.move_new()
        self.odometer += self._speed
        self.battery -= self.energy_usage_tick()
        print(f"EV {self.unique_id} is travelling. State: {self.machine.state}, Odometer: {self.odometer}, Battery: {self.battery:.2f}, Location: {self.pos}, Destination: {self.destination}.")

        # use station selection process instead
    
    def charge(self):
        """Charge the EV at the Charge Station. The EV is charged at the Charge Station's charge rate.
        
        Returns:
            battery: Battery level for the EV.
        """
        # self.battery += self._chosen_cs._charge_rate
        # maybe use function from CS to charge
        self.battery += self._chosen_cs._charge_rate() #with right rate
        # print(f"EV {self.unique_id} at CS {self._chosen_cs.unique_id} is in state: {self.machine.state}, Battery: {self.battery}")

    def charge_overnight(self):
        """
        Charge the EV at the Home Charge Station, at the Home Charge Station's charge rate.
        
        Returns:
            battery: Battery level for the EV.
        """
        self.battery += self.home_cs_rate
        print(f"EV {self.unique_id} at Home CS. state: {self.machine.state}, Battery: {self.battery}")
    
#    # 16 Feb charge flow redo - new methods
#     def choose_charge_station(self):
#         """
#         Chooses a charge station to charge at. Selects the charge station with the correct checkpoint id.
#         Returns:
#             _chosen_cs: Charge Station chosen for charging.

#         """
#         # choose station
#         # neighbours = self.model.grid.get_neighbors(self.pos, include_center=True, moore = True) radius = 1
#         neighbours = self.model.grid.get_neighborhood(self.pos, moore = True, include_center = True)
#         for neighbour in neighbours:
#             if isinstance(neighbour, ChargeStation):
#                 # if neighbour.checkpoint_id == self.checkpoint_id:
#                 self._chosen_cs = neighbour
#         print(f"Chosen CS object is of type: {type(self._chosen_cs)}. Value: {self._chosen_cs}")
#         # print(f"EV {self.unique_id} chose CS {self._chosen_cs.unique_id} to charge at.")
#         return self._chosen_cs
    
    def choose_charge_station(self):
        """
        Chooses a charge station to charge at. Selects the charge station with the correct checkpoint id.
        Returns:
            _chosen_cs: Charge Station chosen for charging, or None if no suitable neighbor was found.

        """
        # choose station
        neighbours = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=True)
        for neighbour in neighbours:
            if isinstance(neighbour, ChargeStation) and neighbour.checkpoint_id == self.checkpoint_id:
                self._chosen_cs = neighbour
                print(f"Chosen CS object is of type: {type(self._chosen_cs)}. Value: {self._chosen_cs}")
                return self._chosen_cs
        print("No suitable neighbor was found.")
        return None

    
    def join_cs_queue(self) -> None:
        self._chosen_cs.queue.append(self)
        print(f"EV {(self.unique_id)} joined queue at Charge Station {(self._chosen_cs.unique_id)}")
  
    # Model env functions
    def add_soc_eod(self) -> None:
        """Adds the battery level at the end of the day to a list."""
        self.battery_eod.append(self.battery)
        print(f"EV {self.unique_id} Battery level at end of day: {self.battery_eod[-1]}")
    
    
    def increment_day_count(self) -> None:
        """
        Increments current_day_count by 1.
        """
        self.current_day_count += 1

    def reset_odometer(self) -> None:
        """Resets the EV odometer to 0."""
        # self.battery = self.battery_eod[-1]
        self.odometer = 0
    
    def relaunch_base(self,n) -> None:
        """
        Relaunches the EV at the end of the day. Sets the start time to the next day, and chooses a new journey type and destination. Finally, generates an initialization report.
        Also sets the _journey_complete flag to 'False'.
        Args:
            n (int): Day number.

        Returns:
            start_time: Start time for the EV.
            journey_type: Journey type for the EV.
            destination: Destination for the EV.
        """
        self.set_start_time() 
        marker = (n * 24)
        self.start_time += marker
        # self.choose_journey_type()
        # self.choose_destination(self.journey_type)
        print(f"\nEV {self.unique_id} relaunch prep successful. New start time: {self.start_time}")
        self.initialization_report(self.model)
        self._journey_complete = False

    
    def relaunch_travel(self)-> None:
        self.travel_intervention()
        self.relaunch_base(n = self.model.current_day_count)

    def relaunch_charge(self) -> None:
        """
        Relaunches charging EVs by calling the charge_intervention method, followed by the relaunch_base method.
        """
        self.charge_intervention()
        self.relaunch_base(n = self.model.current_day_count)

    def relaunch_dead(self) -> None:
        """
        Relaunches dead EVs by calling the dead_intervention method, followed by the relaunch_base method.
        """
        self.dead_intervention()
        self.relaunch_base(n = self.model.current_day_count)

    def relaunch_idle(self) -> None:
        """
        Relaunches idle EVs by calling the relaunch_base method.
        """
        # if self.machine.state == "Idle":
        #     self.relaunch_base(self,n)
        # elif self.machine.state != "Idle":
        #     print(f"EV {self.unique_id} is not in Idle state. Cannot relaunch for new day.")
        self.relaunch_base(n = self.model.current_day_count, )

    def start_travel(self) -> None:
        """
        Starts the EV travelling at the assigned start time.
        """
        if self.model.schedule.time == self.start_time:
            self.machine.start_travel()
            # print(f"EV {self.unique_id} has started travelling at {self.model.schedule.time}")
            print(f"EV {self.unique_id} started travelling at {self.start_time} and is in state: {self.machine.state}")
    
    
   

    # staged step functions
    def stage_1(self):
        """Stage 1: EV travels until it reaches the distance goal or runs out of battery. 
        If it needs to charge during the journey, it will transition to Stage 2.
        """

        # Transition Case 1: Start travelling. idle -> travel
        # Depending on start time, EV will start travelling, transitioning from Idle to Travel.

        # # This is the reason for charging stopping at the change into the new day. Need to fix this.
        if self.machine.state == 'Battery_dead':
            pass
        else:
            self.start_travel() 
    
        # Transition Case 2: Still travelling, battery low. Travel -> travel_low  
        if self.machine.state == 'Travel' and self.battery <= self._soc_usage_thresh:
            self.machine.get_low()
            # print(f"EV: {self.unique_id} has travelled: {str(self.odometer)} miles and is now {self.machine.state}. Current charge level is: {self.battery} kwh")

        # 21/02/23 - new flow for locating a station. Combo of 1b and 4
        # Locating a Charge Station #

        if (self.machine.state == 'Travel' or self.machine.state == 'Travel_low') and (self.odometer < self._distance_goal):
            if self.machine.state == 'Travel':
                # self.travel(direction=self.direction)
                self.travel()
                self.machine.continue_travel()
                print(f"EV {self.unique_id} has travelled: {self.odometer} miles. State: {self.machine.state}. Battery: {self.battery:.2f} kWh")
            elif self.machine.state == 'Travel_low':
                if self.battery > 0:
                    print(f"EV {self.unique_id} is low on charge and is seeking a charge station. Current charge: {self.battery} kWh")
                    # self.travel(direction=self.direction)
                    self.travel()
                elif self.battery <= 0:
                    self.machine.deplete_battery()
                    self._journey_complete = True
                    print(f"EV {self.unique_id} is out of charge and can no longer travel. State: {self.machine.state}. Current charge: {self.battery} kWh")

        
        # 21/02/23 - new flow for recognising a charge station (CS). Also, choosing a CS and charge queue.
        # Recognising a Charge Station #
        if (self.odometer in self.checkpoint_list):
            if self.machine.state == 'Travel':
                print(f"EV {self.unique_id} has arrived at Charge Station but is in state: {self.machine.state}. Not travelling low.")
            elif self.machine.state == 'Travel_low':
                self._at_station = True
                print(f"EV {self.unique_id} is low on battery and is at a station. Seeking charge queue. Current EV state: {self.machine.state}")
                # self.select_cp()
                self.choose_charge_station()
                self.machine.seek_charge_queue()
                self.machine.join_charge_queue()
                # self.choose_cs_queue()
                self.join_cs_queue()
                # Here, EV has arrived at CS, joined one of the two queues and is waiting to become the active ev, and get charged.
                # self.machine.start_charge()
                self._in_queue = True
        if self.machine.state == 'Travel' or self.machine.state == 'Travel_low': 
            if self.machine.state == 'Travel': 
                # Check if the EV has encountered a ChargeStation agent
                # cellmates = self.model.grid.get_cell_list_contents([next_pos])
                cellmates = self.model.grid.get_neighbors(self.pos, moore = True, include_center=False, radius=2)
                for cellmate in cellmates:
                    if isinstance(cellmate, ChargeStation):
                        print(f"EV {self.unique_id} has encountered a Charge Station, but is not low on battery. State: {self.machine.state}.")
            if self.machine.state == 'Travel_low': 
                # Check if the EV has encountered a ChargeStation agent
                # cellmates = self.model.grid.get_cell_list_contents([next_pos])
                cellmates = self.model.grid.get_neighbors(self.pos, moore = True, include_center=False, radius=2)
                for cellmate in cellmates:
                    if isinstance(cellmate, ChargeStation):
                        cellmate.queue.append(self)
                        # self._chosen_station = cellmate
                        self.machine.seek_charge_queue()
                        self.machine.join_charge_queue()
                        print(f"EV {self.unique_id} has encountered a Charge Station and is low on battery. State: {self.machine.state}.")


       
    
    def stage_2(self):
        """Stage 2: EV waits in queue until it is the active EV."""
        
        if self.machine.state == 'Charge':
            self._in_queue = False
            self.charge()
            # print(f"EV {self.unique_id} is charging. EV State: {self.machine.state}. Current charge: {self.battery} kWh")
            if self.battery >= self._soc_charging_thresh:
                self.machine.end_charge()
                print(f"EV {self.unique_id} has finished charging. EV State: {self.machine.state}. Current charge: {self.battery} kWh")
                self._at_station = False
            elif self.battery < self._soc_charging_thresh:
                self.machine.continue_charge()
                print(f"EV {self.unique_id} is still charging. EV State: {self.machine.state}. Current charge: {self.battery} kWh")
        
        if self.machine.state == 'Home_Charge':
            self._is_charging = True
            self.charge_overnight()
            if self.battery >= self._soc_usage_thresh:
                self.machine.end_home_charge()
                print(f"EV {self.unique_id} has finished Home charging. EV State: {self.machine.state}. Current charge: {self.battery} kWh")
                self._is_charging = False
            elif self.battery < self._soc_usage_thresh:
                self.machine.continue_home_charge()
                print(f"EV {self.unique_id} is still charging at home. EV State: {self.machine.state}. Current charge: {self.battery} kWh")
        
        # Transition Case 3: EV with low battery does not arrive at charge station. Travel_low -> Battery_dead
        # condition self.battery < 10 because 10 is the minimum expenditure of energy to move the vehicle in one timestep
        # if self.machine.state == 'Travel_low' and self.battery < 10:
        #     self.machine.deplete_battery()
        #     print(f"EV {self.unique_id} is now in state: {self.machine.state} and is out of charge.")
        # removed 07/03
        
        # Transition Case 7: Journey Complete. travel -> idle
        if self.machine.state == 'Travel' and self.odometer >= self._distance_goal:
            self.machine.end_travel()
            # self._in_garage = True
            self._journey_complete = True
            self.decrease_range_anxiety()
            print(f"EV {self.unique_id} has completed its journey to Location {self.destination}. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh. Range anxiety: {self.range_anxiety}")
            # self.update_lsm()

        # Transition Case 8: Journey complete, battery low. travel_low -> idle
        if self.machine.state == 'Travel_low' and self.odometer >= self._distance_goal:
            self.machine.end_travel_low()
            self._journey_complete = True
            # decrease range anxiety?
            print(f"EV {self.unique_id} narrowly completed its journey. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh. Range anxiety: {self.range_anxiety}")
        
        # if self.machine.state == 'In_Queue':


        # 27 Feb
        # if (self.machine.state == 'Idle' and self._in_garage == True) and model.schedule.time 
        #     if self.battery < self.max_battery:
        #         # self.machine.return_to_garage()
        #         self.charge_overnight()
                # print(f"EV {self.unique_id} is in state: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
        
   


class Location(Agent):
    """A location agent. This agent represents a location in the model, and is used to store information about the location."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.location_type = None
        self.name = None
        self.location_capacity = 0
        self.x = None
        self.y = None
        self.pos = None
        self.location_occupancy = 0
        self.location_occupancy_list = []

    # def set_location_name(self, locations_dict)->None:
    #     """set name for Location Agent"""
    #     self.name = ""
    #     pass

    def check_location_for_arrivals(self, model):
        """Checks the location for arrivals."""
        neighbours = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True)
        for neighbour in neighbours:
            if isinstance(neighbour, EV):
                if neighbour.machine.state == 'Idle' and neighbour._journey_complete == True:  
                    self.location_occupancy += 1
                    self.location_occupancy_list.append(neighbour.unique_id)
                    print(f"EV {neighbour.unique_id} has arrived at {self.name}. Current occupancy: {self.location_occupancy}")
                    model.grid.remove_agent(neighbour)
                    print(f"EV {neighbour.unique_id} has been removed from grid on arrival at {self.name}. Current state: {neighbour.machine.state}")
                    break
    
        #  # Check the neighborhood for the presence of a Location agent
        # for nx, ny in self.model.grid.get_neighborhood(self.pos, moore=True, radius=1):
        #     cell = self.model.grid.get_cell_list_contents([(nx, ny)])
        #     for agent in cell:
        #         if isinstance(agent, Location):
        #             self.model.remove_agent(self)
        #             break

    # def remove_arrived_ev(self, ev_id):
    #     """Removes an EV from the location's occupancy list."""
    #     self.location_occupancy -= 1
    #     self.location_occupancy_list.remove(ev_id)
    #     print(f"EV {ev_id} has left {self.name}. Current occupancy: {self.location_occupancy}")

    def stage_1(self):
        """Stage 1 of the charge station's step function."""
        self.check_location_for_arrivals(self.model)

    def stage_2(self):
        """Stage 2 of the charge station's step function."""
        if self.location_occupancy_list != []:
            for ev_id in self.location_occupancy_list:
                ev = self.model.schedule.agents[ev_id]
                if (ev.machine.state == 'Travel' or ev.machine.state == 'Travel_low') and ev._journey_complete == False:
                    self.location_occupancy -= 1
                    self.location_occupancy_list.remove(ev_id)
                    print(f"EV {ev_id} has left {self.name}. Current occupancy: {self.location_occupancy}")
                    break 
        

# # Check the neighborhood for the presence of a Location agent
#         for nx, ny in self.model.grid.get_neighborhood(self.pos, moore=True, radius=1):
#             cell = self.model.grid.get_cell_list_contents([(nx, ny)])
#             for agent in cell:
#                 if isinstance(agent, Location):
#                     self.model.remove_agent(self)
#                     break


#########
# Logging
#########


# logging.basicConfig(level=logging.DEBUG)
# logging.debug('This is a debug message')
# logging.info('This is an info message')
# logging.warning('This is a warning message')
# logging.error('This is an error message')
# logging.critical('This is a critical message')

# To-D0
# CPs at initialization - 2

# check for CP at 0.3 and 0.6 of length
# Charge point w/ two queues
# EV initialisation time drawn from probability distribution
# State Machine for managing CP charging status. Charging/NCharging

# import logging
# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('transitions').setLevel(logging.INFO)