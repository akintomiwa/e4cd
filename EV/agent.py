"""This module contains the agent classes for the EV model."""

import numpy as np
import pandas as pd
# import math
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
from transitions.extensions import GraphMachine
from functools import partial
from EV.statemachine import EVSM, LSM, states, transitions, lstates, ltransitions
import config.worker as worker


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
        self.cprates = []  #kW
        self._charge_rate = 0
        
        self.prelim_report()
        
        # self.init_report()

        # End initialisation
    


    # def assign_cp_id(self):
    #     for i in range((self.no_cps)):
    #         setattr(self, f'cp_id_{i}', None)
    
    def prelim_report(self):
        print(f"CS {(self.unique_id)}, initialized.")

    def init_report(self):
        print(f"\nCS info: ID: {(self.unique_id)}, initialized. Charge rates for charge points: {self.cprates} kW.")
        print(f"It has {self.no_cps} charging points.")
        for i in range(self.no_cps):
            print(f"CP_{i} is {(getattr(self, f'cp_id_{i}'))}")

    def retrieve_charge_point_rate(self,cp_id) -> int:
        """Return the charge rate of the charge point with id cp_id."""
        cr = self.cprates[self.cp_id]
        return cr
        

    def __str__(self) -> str:
        """Return the agent's unique id."""
        return str(self.unique_id + 1)
    
    # modify to run through all charge points in the station. Multiple lists.
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
                elif attr_value is not None:
                    self.occupied_cps.add(attr_name)
                    active.machine.wait_in_queue()
                    # reinsert active into queue
                    self.queue.insert(0, active)
                    print(f"EV {active.unique_id} remains in queue at CS {self.unique_id} at CP {attr_name} and is in state: {active.machine.state}.")
                    # print(f"CP: {attr_name} at ChargeStation {self.unique_id} is currently occupied by EV {attr_value} {attr_value.unique_id}")
                    print(f"CP: {attr_name} at ChargeStation {self.unique_id} is currently occupied by an EV")
            return False  
        except IndexError:
            print(f"The queue at ChargeStation {self.unique_id} is empty.")
            return False
        except Exception as e:
            print(f"Error assigning EV to charge point: {e}")
            return False



    # def dequeue(self) -> None:
    #     """Remove the first EV from queue."""
    #     try:
    #         active = self.queue.pop(0) #pick first EV in queue
    #         for attr_name in dir(self):
    #             if attr_name.startswith("cp_id_"):
    #                 attr_value = getattr(self, attr_name)
    #                 if attr_value is None:
    #                     setattr(self, attr_name, active)
    #                     active.machine.start_charge()
    #                     print(f"EV {active.unique_id} dequeued at CS {self.unique_id} at CP {attr_name} and is in state: {active.machine.state}")
    #                     print("EV started charging.")
    #                     # print(f"{attr_name} at CP {self.unique_id} is None")
    #                 else:
    #                     print(f"CP: {attr_name} at ChargeStation {self.unique_id} is currently occupied by EV {attr_value}")
    #     except:
    #         IndexError
    #         print(f"The queue at ChargeStation {self.unique_id} is empty.")
        # elif len(self.queue) > self.max_queue_size:
        #     print("Queue is full.")
    
    # March rewrite 1
    def finish_charge(self) -> None:
        try:
            for attr_name in dir(self):
                if attr_name.startswith("cp_id_"):
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
        print(f"Queue Length at ChargeStation {self.unique_id} is {len(self.queue)}")  # testing
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
        self.loc_machine = LSM(initial='City_D', states=lstates, transitions=ltransitions)
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
     
        # set EV speed
        self.set_speed()
        # set energy consumption rate
        self.set_ev_consumption_rate()
        # Home Station 
        self.home_cs_rate = 10 #kW

        # old flow  
        # choose journey type
        self.journey_type = self.choose_journey_type()
        # # choose actual destination and set distance goal based on journey type
        # self.choose_destination(self.journey_type)

        
        # set EV start time moved to model as not at init
        # self.set_start_time()


        # Initialisation Report
        self.prelim_report()
        # self.initalization_report()
        # self.checkpoint_list_reverse = reversed(self.checkpoint_list)
    
    # def travel_reverse(self)-> None:
    #     if self.to_fro == True:

    # def select_route(self, de):

    def __str__(self) -> str:
        """Return the agent's unique id as a string, not zero indexed."""
        return str(self.unique_id + 1)
    
    def prelim_report(self):
        print(f"EV {(self.unique_id)}, initialized.")

    def initalization_report(self) -> None:
        """Prints the EV's initialisation report."""
        print(f"\nEV info: ID: {self.unique_id}, route: {self.route}, destination name: {self.destination}, journey type: {self.journey_type}, max_battery: {self.max_battery}, energy consumption rate: {self.ev_consumption_rate}, speed: {self._speed}, State: {self.machine.state}.")
        print(f"EV info (Cont'd): Start time: {self.start_time}, distance goal: {self._distance_goal}, soc usage threshold: {self._soc_usage_thresh}, range anxiety {self.range_anxiety}, location: {self.loc_machine.state}.")
        print(f"EV {self.unique_id} Checkpoint list: {self.checkpoint_list}")

    # Internal functions
    
    # Remove as part of redesign: 
    # works
    def choose_journey_type(self) -> str:
        """Chooses a journey type for the EV driver.
        Returns:
            journey_type: Choice of journey the EV driver makes.
        """
        self._journey_choice = choice([True, False]) #True = Urban, False = Highway
        if self._journey_choice == True:
            # self._distance_goal = 100 #miles
            self.journey_type = "Urban"
        else:
            # self._distance_goal = 200 #miles
            self.journey_type = "InterUrban"
        return self.journey_type
    

    
    # # experimental 
    # def choose_journey_type(self) -> str:
    #     """Chooses a journey type for the EV driver.
    #     Returns:
    #         journey_type: Choice of journey the EV driver makes.
    #     """
    #     if self.current_day_count == 1:
    #         self._journey_choice = choice([True, False]) #True = Urban, False = Highway
    #         if self._journey_choice == True:
    #             self.journey_type = "Urban"
    #         else:
    #             self.journey_type = "InterUrban"
    #             self.to_fro = "To"

    #     elif self.current_day_count > 1:
    #         if self.to_fro == "To" and self.journey_type == "InterUrban":
    #             self.journey_type = "InterUrban"
    #             self.to_fro = "Fro"
            
    #         # partially problematic. fix soon. make recursive?
    #         elif self.to_fro == "Fro":
    #             self._journey_choice = choice([True, False])
    #             if self._journey_choice == True:
    #                 self.journey_type = "Urban"
    #             else:
    #                 self.journey_type = "InterUrban"
    #                 self.to_fro = "To"
    #     return self.journey_type
    
    # Key. Old set speed function
    def set_speed(self) -> None:
        """Sets the speed of the EV driver."""
        base_speed = 10 #urban speed (mph). Interurban speed is scaled by 2.
        if self.journey_type == "Urban":
            self._speed = base_speed
        else:
            self._speed = (base_speed * 2) #interurban speed (mph). 

        
    def set_ev_consumption_rate(self) -> None:
        # baselines
        mu_urban, mu_interurban = 0.2, 0.5 # means
        sigma = 0.1 # standard deviation
        # set vehicle energy consumption rate
        if self.journey_type == "Urban":
            # self.ev_consumption_rate = 0.2 # 200 Wh/mile OR 20 kWh/100 miles OR 0.2 kWh/mile
            # self.ev_consumption_rate = np.random.normal(mu_urban, sigma) # opt: size = 1
            self.ev_consumption_rate = np.random.default_rng().normal(mu_urban, sigma) # opt: size = 1
        else:
            # self.ev_consumption_rate = 0.5 # 500 Wh/mile OR 50 kWh/100 miles
            # self.ev_consumption_rate = np.random.normal(mu_interurban, sigma) # opt: size = 1
            self.ev_consumption_rate = np.random.default_rng().normal(mu_interurban, sigma) # opt: size = 1
    
    # def choose_dest_from_route(self) -> None:
    #     """Chooses a destination for the EV driver.
    #     Args:
    #         route: Choice of route the EV driver makes.
    #     Returns:
    #         destination: Choice of destination for the EV driver.
    #     """
    #     if self.route == "A-B":
    #         # Option 1: use keys to determine destination
    #         destinations = {'work': 50, 'store': 80, 'friend_1': 45}
    #         self.destination = choice(list(destinations.keys()))
    #         self._distance_goal = destinations[self.destination]
    #         # return self.destination
    #     elif self.route == "A-C":
    #         # Option 1: use keys to determine destination
    #         destinations = {'friend_2': 25, 'auto_shop': 35, 'gym': 40}
    #         self.destination = choice(list(destinations.keys()))
    #         self._distance_goal = destinations[self.destination]
    #         # return self.destination
    
    def choose_destination(self, journey_type:str) -> str:
        """Chooses a destination for the EV driver.
        Args:
            journey_type: Choice of journey type the EV driver makes.
        Returns:
            destination: Choice of destination for the EV driver.
        """
        if journey_type == "Urban":
            self.choose_destination_urban()
        else:
            self.choose_destination_interurban()
        return self.destination # type: ignore

    def choose_destination_urban(self) -> None:
        """Chooses a destination for the EV driver. Urban destination from destinations distances dictionary.
        Returns:     
            destination: Choice of destination for the EV driver. (implicit)
            distance_goal: Distance goal for the EV driver. (implicit)
        """

        # Option 2: use values directly to determine destination
        # destinations_distances = {'work': 50, 'market': 80, 'friend_1': 45, 'friend_2': 135, 'autoshop': 70} #miles. Initial
        if self.route == "A-B":
            destinations_distances = {'work': 60, 'market': 90, 'friend_1': 55} #miles. Updated
            destination = random.choice(list(destinations_distances))
            self.destination = destination
            self._distance_goal = destinations_distances.get(destination)
        elif self.route == "A-C":
            destinations_distances = {'work': 50, 'autoshop': 85, 'gym': 70}
            destination = random.choice(list(destinations_distances))
            self.destination = destination
            self._distance_goal = destinations_distances.get(destination)

    def choose_destination_interurban(self) -> None:
        """
        Chooses a destination for the EV driver. InterUrban destination from destinations distances dictionary.
        Returns:
            destination: Choice of destination for the EV driver.
            distance_goal: Distance goal for the EV driver.
        """
        # choices = {'City A': 210, 'City B': 140, 'City C': 245}
        # destination = random.choices(list(choices.keys()), weights=list(choices.values()), k=1)
        # return destination
        # destinations_distances = {'City A': 210, 'City B': 140, 'City C': 245} # miles . Initial
        if self.route == "A-B":
            destinations_distances = {'City B': 120, 'City E': 100} # miles. Updated
            destination = random.choice(list(destinations_distances))
            self.destination = destination
            self._distance_goal = destinations_distances.get(destination)
        elif self.route == "A-C":
            destinations_distances = {'City C': 160, 'City D': 130}
            destination = random.choice(list(destinations_distances))
            self.destination = destination
            self._distance_goal = destinations_distances.get(destination)
 
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
    
    # Dynamic propensity for charging behavior
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
    def travel(self) -> None:
        """
        Travel function. Moves EV along the road. Updates odometer and battery level.
        
        Returns:
            odometer: Odometer reading for the EV.
            battery: Battery level for the EV.
        """
        
        self.odometer += self._speed
        self.battery -= self.energy_usage_tick()
        print(f"EV {self.unique_id} is travelling. Odometer: {self.odometer}, Battery: {self.battery}")

        # if self.to_fro == "To":
        #     self.odometer += self._speed
        #     self.battery -= self.energy_usage_tick()
        #     # print(f"EV {self.unique_id} is travelling. Odometer: {self.odometer}, Battery: {self.battery}")

        # elif self.to_fro == "":
        #     self.odometer += self._speed
        #     self.battery -= self.energy_usage_tick()
        #     # print(f"EV {self.unique_id} is travelling. Odometer: {self.odometer}, Battery: {self.battery}")

        # elif self.to_fro == "Fro":
        #     self.odometer -= self._speed
        #     self.battery -= self.energy_usage_tick()
        #     # print(f"EV {self.unique_id} is travelling. Odometer: {self.odometer}, Battery: {self.battery}")
       
        # # redundancy condition
        # elif self.to_fro == "":
        #     self.odometer += self._speed
        #     self.battery -= self.energy_usage_tick()


       

        # use station selection process instead
    
    def charge(self):
        """Charge the EV at the Charge Station. The EV is charged at the Charge Station's charge rate.
        
        Returns:
            battery: Battery level for the EV.
        """
        # self.battery += self._chosen_cs._charge_rate
        # maybe use function from CS to charge
        self.battery += self._chosen_cs._charge_rate()
        # print(f"EV {self.unique_id} at CS {self._chosen_cs.unique_id} is in state: {self.machine.state}, Battery: {self.battery}")

    def charge_overnight(self):
        """
        Charge the EV at the Home Charge Station, at the Home Charge Station's charge rate.
        
        Returns:
            battery: Battery level for the EV.
        """
        self.battery += self.home_cs_rate
        print(f"EV {self.unique_id} at Home CS. state: {self.machine.state}, Battery: {self.battery}")
        # self.machine.start_home_charge()
        # #  used to be self._soc_charging_thresh
        # if self.battery < self._soc_usage_thresh:
        #     self.battery += self.home_cs_rate
        #     print(f"EV {self.unique_id} at Home CS. state: {self.machine.state}, Battery: {self.battery}")
        # else:
        #     self.machine.end_home_charge()
        #     print(f"EV {self.unique_id} at Home CS. state: {self.machine.state}, Battery: {self.battery}")
    
   # 16 Feb charge flow redo - new methods
    def choose_charge_station(self):
        """
        Chooses a charge station to charge at. Selects the charge station with the correct checkpoint id.
        Returns:
            _chosen_cs: Charge Station chosen for charging.

        """
        # choose station
        for cs in self.model.chargestations:
            if (cs.checkpoint_id == self.odometer) and (cs.route == self.route):
                self._chosen_cs = cs
                self._chosen_cs._is_active = True
        print(f"EV {(self.unique_id)} selected Charge Station: {(self._chosen_cs.unique_id)} for charging.")
        
        # # choose station 2 way
        # if self.direction == 1:
        #     for cs in self.model.chargestations:
        #         if cs._checkpoint_id == self.odometer:
        #             self._chosen_cs = cs
        #             self._chosen_cs._is_active = True
        #     print(f"EV {(self.unique_id)} selected Charge Station: {(self._chosen_cs.unique_id)} for charging.")
        # elif self.direction == 2:
        #     rev_list = self.model.chargestations[::-1]
        #     for cs in rev_list:
        #         if cs._checkpoint_id == self.odometer:
        #             self._chosen_cs = cs
        #             self._chosen_cs._is_active = True


    # # new select queue for charging
    # def choose_cs_queue(self) -> None:
    #     """Chooses a queue at the charge station to charge at. Chooses the queue with the shortest queue."""
    #     print(f"Length of q1: {(len(self._chosen_cs.queue_1))}. Length of q2: {(len(self._chosen_cs.queue_2))}")
    #     if len(self._chosen_cs.queue_1) > len(self._chosen_cs.queue_2):
    #         self._chosen_cs.queue_2.append(self)
    #         print(f"EV {(self.unique_id)} selected queue 2 at Charge Station {(self._chosen_cs.unique_id)}")
    #     elif len(self._chosen_cs.queue_1) < len(self._chosen_cs.queue_2):
    #         self._chosen_cs.queue_1.append(self)
    #         print(f"EV {(self.unique_id)} selected queue 1 at Charge Station {(self._chosen_cs.unique_id)}")
    #     elif len(self._chosen_cs.queue_1) == len(self._chosen_cs.queue_2):
    #         self._chosen_cs.queue_1.append(self)
    #         print(f"EV {(self.unique_id)} selected queue 1 at Charge Station {(self._chosen_cs.unique_id)}")
    
    def join_cs_queue(self) -> None:
        self._chosen_cs.queue.append(self)
        print(f"EV {(self.unique_id)} joined queue at Charge Station {(self._chosen_cs.unique_id)}")
  
    # Model env functions
    def add_soc_eod(self) -> None:
        """Adds the battery level at the end of the day to a list."""
        self.battery_eod.append(self.battery)
        print(f"EV {self.unique_id} Battery level at end of day: {self.battery_eod[-1]}")
    
    
    def finish_day(self) -> None:
        """
        Finishes the day for the EV. Increments current_day_count by 1 and resets the EV odometer to 0.
        """
        # self.battery = self.battery_eod[-1]
        self.current_day_count += 1
        self.odometer = 0
    
    def relaunch_base(self,n) -> None:
        """
        Relaunches the EV at the end of the day. Sets the start time to the next day, and chooses a new journey type and destination. Finally, generates an initialization report.

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
        self.choose_journey_type()
        self.choose_destination(self.journey_type)
        print(f"\nEV {self.unique_id} relaunch prep successful. New start time: {self.start_time}")
        self.initalization_report()
        # if self.start_time > marker:
        #     print(f"EV {self.unique_id} restart successful. New start time: {self.start_time}")
        #     self.initalization_report()
        # else:
        #     print(f"EV {self.unique_id} restart unsuccessful. New start time: {self.start_time}")
    
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
        self.relaunch_base(n = self.model.current_day_count)

    def start_travel(self) -> None:
        """
        Starts the EV travelling at the assigned start time.
        """
        if self.model.schedule.time == self.start_time:
            self.machine.start_travel()
            # print(f"EV {self.unique_id} has started travelling at {self.model.schedule.time}")
            print(f"EV {self.unique_id} started travelling at {self.start_time} and is in state: {self.machine.state}")
    
    # TO-DO: Fix this, reflect routing variable.
    def update_lsm(self) -> None:
        if self.journey_type == 'Urban':
            self.loc_machine.city_d_2_d()
        elif self.journey_type == 'InterUrban':
            if self.destination == 'City A':
                self.loc_machine.city_d_2_a()
            elif self.destination == 'City B':
                self.loc_machine.city_d_2_b()
            elif self.destination == 'City C':
                self.loc_machine.city_d_2_c()
        print(f"EV {self.unique_id} is at location: {self.loc_machine.state}")

    # def ev_overrun(self) -> None:
    #     """
    #     Handles the case where the EV is still travelling by the relaunch time.
    #     """
    #     if self.model.schedule.time == 
        # if self.machine.state == "Travel":
        #     if self.battery <= 0:
        #         self.machine.battery_dead()
        #         print(f"EV {self.unique_id} has run out of battery at {self.model.schedule.time}")
        #         print(f"EV {self.unique_id} is in state: {self.machine.state}")
        #         print(f"EV {self.unique_id} is at location: {self.loc_machine.state}")
        #         self.relaunch_dead()
        #     else:
        #         pass
    
    # def update_home_charge_prop(self, new_prop):
    #     self.home_charge_prop = new_prop

    

    # def update_soc_usage_thresh(self):
    #     new_thresh = self.max_battery * self.rannge_anxiety
    #     self._soc_usage_thresh = new_thresh

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
                self.travel()
                self.machine.continue_travel()
                print(f"EV {self.unique_id}  has travelled: {self.odometer} miles. State: {self.machine.state}. Battery: {self.battery} kWh")
            elif self.machine.state == 'Travel_low':
                if self.battery > 0:
                    print(f"EV {self.unique_id} is low on charge and is seeking a charge station. Current charge: {self.battery} kWh")
                    self.travel()
                elif self.battery <= 0:
                    self.machine.deplete_battery()
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
            self._in_garage = True
            self._journey_complete = False
            self.decrease_range_anxiety()
            print(f"EV {self.unique_id} has completed its journey. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh. Range anxiety: {self.range_anxiety}")
            # self.update_lsm()

        # Transition Case 8: Journey complete, battery low. travel_low -> idle
        if self.machine.state == 'Travel_low' and self.odometer >= self._distance_goal:
            self.machine.end_travel_low()
            # decrease range anxiety?
            print(f"EV {self.unique_id} has completed its journey. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh. Range anxiety: {self.range_anxiety}")
        
        # if self.machine.state == 'In_Queue':


        # 27 Feb
        # if (self.machine.state == 'Idle' and self._in_garage == True) and model.schedule.time 
        #     if self.battery < self.max_battery:
        #         # self.machine.return_to_garage()
        #         self.charge_overnight()
                # print(f"EV {self.unique_id} is in state: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
        
   


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

# from mesa import Agent, Model
# from mesa.time import RandomActivation
# import random

# class ChargingStation(Agent):
#     def __init__(self, unique_id, model, num_chargepoints):
#         super().__init__(unique_id, model)
#         self.queue = []
#         self.num_chargepoints = num_chargepoints
        
#     def step(self):
#         # Check for available chargepoints
#         while len(self.queue) > 0 and self.num_chargepoints > 0:
#             # Remove EV from queue
#             ev = self.queue.pop(0)
            
#             # Decrement number of available chargepoints
#             self.num_chargepoints -= 1
            
#             # Schedule charging completion
#             self.model.schedule_once(ev, "charging_complete")
            
#         # Randomly add EV to queue
#         if random.random() < 0.5:
#             ev = EV(self.model.next_id(), self.model)
#             self.queue.append(ev)
#             self.model.schedule_once(ev, "start_charging")
            
# class EV(Agent):
#     def __init__(self, unique_id, model):
#         super().__init__(unique_id, model)
        
#     def step(self):
#         pass
        
#     def start_charging(self):
#         # Start charging
#         self.model.schedule_once(self, "stop_charging", 10)
        
#     def stop_charging(self):
#         # Increment available chargepoints
#         charging_station = self.model.schedule.agents_by_type[ChargingStation][0]
#         charging_station.num_chargepoints += 1
        
# model = Model()
# model.schedule = RandomActivation(model)

# charging_station = ChargingStation(1, model, 2)
# model.schedule.add(charging_station)

# model.run_steps(100)
