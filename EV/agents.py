import numpy as np
import math
import os
import random
from random import choice
import warnings
warnings.simplefilter("ignore")
import pandas as pd
import numpy as np
import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation, RandomActivationByType, SimultaneousActivation
from mesa.datacollection import DataCollector
from matplotlib import pyplot as plt, patches
import scipy.stats as ss
import cufflinks as cf
cf.go_offline()
from plotly.offline import iplot
# from statemachine import StateMachine, State
from transitions import Machine
import random

from transitions import Machine
from transitions.extensions import GraphMachine
from functools import partial

class Model:
    def clear_state(self, deep=False, force=False):
        print("Clearing State ... ")
        return True

model = Model()
machine = GraphMachine(model=model, states=['Idle', 'Travel', 'In_queue', 'Charge', 'Travel_low'],
                        transitions= [
                        {'trigger': 'start_travel', 'source': 'Idle', 'dest': 'Travel'},
                        {'trigger': 'get_low', 'source': 'Travel', 'dest': 'Travel_low'},
                        {'trigger': 'seek_charge_queue', 'source': 'Travel_low', 'dest': 'Seek_queue'},
                        {'trigger': 'join_charge_queue', 'source': 'Seek_queue', 'dest': 'In_queue'},
                        {'trigger': 'start_charge', 'source': 'In_queue', 'dest': 'Charge'},
                        {'trigger': 'continue_charge', 'source': 'Charge', 'dest': 'Charge'},
                        {'trigger': 'end_charge', 'source': 'Charge', 'dest': 'Travel'},
                        {'trigger': 'continue_travel', 'source': 'Travel', 'dest': 'Travel'},
                        {'trigger': 'end_travel', 'source': 'Travel', 'dest': 'Idle'},
                        ], 
                        initial = 'Idle', show_conditions=True)

class EVSM(Machine):
    """A state machine for managing status of EV agent in AB model.
    Can be deployed as EvState object.

States:
    Idle, Travel, Travel_low, Seek_queue, In_queue, Charge
Transitions:
    start_travel: Idle -> Travel
    get_low: Travel -> Travel_low
    seek_charge_queue: Travel_low -> Seek_queue
    join_charge_queue: Seek_queue -> In_queue
    start_charge: In Queue -> Charge
    end_charge: Charge -> Travel
    continue_travel: Travel -> Travel
    continue_charge: Charge -> Charge
    end_travel: Travel -> Idle
    """

states = ['Idle', 'Travel', 'Seek_queue', 'In_queue', 'Charge', 'Travel_low']
transitions = [
    {'trigger': 'start_travel', 'source': 'Idle', 'dest': 'Travel'},
    {'trigger': 'get_low', 'source': 'Travel', 'dest': 'Travel_low'},
    {'trigger': 'seek_charge_queue', 'source': 'Travel_low', 'dest': 'Seek_queue'},
    {'trigger': 'join_charge_queue', 'source': 'Seek_queue', 'dest': 'In_queue'},
    {'trigger': 'start_charge', 'source': 'In_queue', 'dest': 'Charge'},
    {'trigger': 'continue_charge', 'source': 'Charge', 'dest': 'Charge'},
    {'trigger': 'end_charge', 'source': 'Charge', 'dest': 'Travel'},
    {'trigger': 'continue_travel', 'source': 'Travel', 'dest': 'Travel'},
    {'trigger': 'end_travel', 'source': 'Travel', 'dest': 'Idle'},
]


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
        machine: EV State Machine.
        _pos_init: Initial position of the EV.
        _is_active: Boolean value indicating whether the EV is active.
        odometer: Odometer of the EV.
        _distance_goal: Distance goal of the EV.
        journey_type: Type of journey the EV is undertaking.
        _soc_usage_thresh: State of charge at which EV driver feels compelled to start charging at station.
        _soc_charging_thresh: State of charge at which EV driver is comfortable with stopping charging at station.
        _journey_choice: Choice of journey the EV driver makes.
        battery: State of charge of the EV.
        max_battery: Maximum state of charge of the EV.

        unused:
        _pos_init: Initial position of the EV.
        _chosen_cp: Charging point chosen by the EV driver.
        _chosen_cp_id: ID of Charging point  chosen by the EV driver.
        tick_energy_usage: Energy usage of the EV in a tick.
        battery_eod: State of charge of the EV at the end of the day.
        day_count: Number of days the EV has been active.

        
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self._charge_rate = 7.5# kW 7200W
        self._in_queue = False
        self._in_garage = False
        self._is_charging = False
        self._was_charged = False
        self._is_travelling = False
        self._journey_complete = False
        self.machine = EVSM(initial='Idle', states=states, transitions=transitions)
        self._pos_init = None #unused Fix in v.0.2
        self._is_active = True
        self.odometer = 0
        self._distance_goal = 0
        self.journey_type = None
        self.destination = None
        self.battery = random.randint(40, 70) #kWh
        self.max_battery = self.battery
        # EV Driver Behaviour
        self._speed = 0
        # battery soc level at which EV driver feels compelled to start charging at station.
        self._soc_usage_thresh = (0.3 * self.max_battery) 
        # battery soc level at which EV driver is comfortable with stopping charging at station.
        self._soc_charging_thresh = (0.8 * self.max_battery) 
        self._chosen_cpoint = None # unused Fix in v.0.2
        # Newest
        self.ev_consumption_rate = 0
        self.tick_energy_usage = 0
        self.battery_eod = []
        self.day_count = 0
        # choose journey type
        self.journey_type = self.choose_journey_type()
        # set speed
        self.set_speed()
        # set energy consumption rate
        self.set_ev_consumption_rate()
        # choose actual destination and set distance goal based on journey type
        self.choose_destination(self.journey_type)
        # TO-DO
        self._chosen_cp_idx = 0 #in selected_cp
        self._chosen_cp = 0 #in selected_cp correct

        # Initialisation Report

        print("EV No " + str(self.unique_id + 1) + " initialized. Journey type: " + str(self.journey_type) +
        ". Vehicle State: " + str(self.machine.state))

        print(f"EV info: ID: {self.unique_id}, destination name: {self.destination} , distance goal: {self._distance_goal}, max_battery: {self.max_battery}, speed: {self._speed}, energy consumption rate {self.ev_consumption_rate}")
        # End initialisation

        # set tick distance
        # 15/01: For now, tick = 1 hour. Consider changing to 30 miles per tick. 
        # Change to self._speed for dynamic tick distance.
        # self.tick_distance = 10 # 10 mile per tick. ??
        # speed == distance per tick
        # if EV active over multiple days, use learnt value from prev day. If overnight charge, set to 100. write methods to handle cases later.
        # dynamic tick distance uses _speed = tick_distance
        # self._chosen_cpoint_idx = 0
    
    # Internal functions
    def choose_journey_type(self):
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
    
    def set_speed(self) -> None:
        """Sets the speed of the EV driver."""
        base_speed = 10 #urban speed (mph). Interurban speed is scaled by 2.
        if self.journey_type == "Urban":
            self._speed = base_speed
        else:
            self._speed = (base_speed * 2) #interurban speed (mph). 
        
    def set_ev_consumption_rate(self) -> None:
        # set vehicle energy consumption rate
        if self.journey_type == "Urban":
            self.ev_consumption_rate = 0.2 # 200 Wh/mile OR 20 kWh/100 miles OR 0.2 kWh/mile
        else:
            self.ev_consumption_rate = 0.5 # 500 Wh/mile OR 50 kWh/100 miles
    
    def choose_destination(self, journey_type):
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
        return self.destination

    def choose_destination_urban(self) -> None:
        """Chooses a destination for the EV driver. Urban destination from destinations distances dictionary.
        
        Returns:     
            destination: Choice of destination for the EV driver. (imp)
            distance_goal: Distance goal for the EV driver. (imp)
            
        """
        # Option 1: use weights to determine destination
        # define weights used
        # destinations_weights = {'work': 40, 'market': 10, 'friend_1': 15, 'friend_2': 20, 'autoshop': 15} #probability
        # assign distances to each destination
        # destination = random.choices(list(destinations_weights.keys()), weights=list(destinations_weights.values()), k=1)


        # Option 2: use values directly to determine destination
        destinations_distances = {'work': 50, 'market': 80, 'friend_1': 45, 'friend_2': 135, 'autoshop': 70} #miles
        destination = random.choice(list(destinations_distances))
        self.destination = destination
        # print(f"Destination name: {self.destination}.")
        # set distance goal based on destination
        # if self.journey_type == "Urban":
        self._distance_goal = destinations_distances.get(destination)
        # print(f"Destination goal: {self._distance_goal}.")
        # return destination

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
        destinations_distances = {'City A': 210, 'City B': 140, 'City C': 245} # miles
        destination = random.choice(list(destinations_distances))
        self.destination = destination
        # print(f"Destination name: {self.destination}.")
        # set distance goal based on destination
        # if self.journey_type == "Interurban":
        self._distance_goal = destinations_distances.get(destination)
        # print(f"Destination goal: {self._distance_goal}.")

    def energy_usage_trip(self):
        """Energy consumption (EC) for the entire trip. EC from distance covered"""
        usage = (self.ev_consumption_rate * self.odometer)
        return usage

    def energy_usage_tick(self):
        """Energy consumption (EC) for each tick. EC from distance covered"""
        usage = (self.ev_consumption_rate * self._speed)
        # self.tick_energy_usage = usage
        return usage

    def delta_battery_neg(self):
        """ Marginal negative change in battery level per tick."""
        # delta = ((self.battery - self.tick_energy_usage)/self._max_battery)
        delta = (self.tick_energy_usage / self.max_battery)
        return delta
  
    # Core EV Functions
    def travel(self):
        """Travel function. Moves EV along the road. Updates odometer and battery level."""
        self.odometer += self._speed # old: self.tick_distance
        # self._distance_goal - self.tick_distance
        self.battery -= self.energy_usage_tick()
        print("Vehicle " + str(self.unique_id + 1 ) + " is travelling")
  
    # unused function
    def select_cp(self):
        """Selects a CP to charge at. Chooses the CP with the shortest queue."""
        self._in_queue = True
        # queue at shortest cp
        self._chosen_cp_idx = np.argmin([len(cpoint.queue) for cpoint in self.model.cpoints])
        # 
        # self._chosen_counter_idx = np.argmin([len(counter.queue) for counter in self.model.counters])
        # self._chosen_counter = self.model.counters[self._chosen_counter_idx]
        # print("No of active Cpoints: " + str(self.model.cpoints.count(self)))
        self._chosen_cp = self.model.cpoints[self._chosen_cp_idx]
        self._chosen_cp.queue.append(self)
        print(f"Vehicle {self.unique_id + 1} selected: {self._chosen_cp.unique_id} for charging.")


    def add_soc_eod(self):
        """Adds the battery level at the end of the day to a list."""
        self.battery_eod.append(self.battery)
        print("Battery level at end of day: " + str(self.battery_eod[-1]))
        # print("Length of B3EOD: " + str(len(self.battery_eod))) # sanity check
    
    def set_new_day(self):
        """
        Sets the battery level to the end of day level from previous day, for the new day.
        Increments day_count and resets the odometer to 0.
        """
        self.battery = self.battery_eod[-1]
        self.day_count += 1
        self.odometer = 0
    
    def charge_simple(self):
        """Simple charging function. Charges the EV according to the charge rate."""
        # flags
        self._is_charging = True
        self.battery += self._charge_rate
        print("Vehicle " + str(self.unique_id + 1 ) + " charged status: " + str(self._was_charged)+ ". CLevel: " + str(self.battery))
        # self._was_charged = True
                
    # def charge_main(self):                                                                                            # For V 0.2
    #     # self._chosen_cp.active_car = None
    #     self.check_for_cp()
    #     if CP.free_cp:
    #         self.takeCP()
    #     else:
    #         # wait_time = 0
    #         self.wait_time += 1
    #         self.waitInQueue()
    #         # self._in_queue = True
    #         # self._chosen_cp.queue.append(self)

        
    #     print("Vehicle " + str(self.unique_id + 1 ) + " charging status: " + str(self._was_charged)+ ". CLevel: " + str(self.soc))

    # def charge_overnight(self):                                                                                        # For V 0.3
    #     if self._in_garage == True & self.soc < self._max_battery:
    #         # self.soc = self._max_battery
    #         self.soc += self._charge_rate
    #     self._is_charging = True
    #     self._was_charged = True
            

    def step(self):
        # Block A - Transitions SM:
        # Transition Case 1: Start travelling. idle -> travel
        if self.machine.state == 'Idle' and self.odometer < self._distance_goal:
            self.machine.start_travel()
            print("Current EV state: " + str(self.machine.state))
        if self.machine.state == 'Travel':
            self.machine.continue_travel()
            self.travel()
            print("Current EV state: " + str(self.machine.state))
            print("Vehicle id: " + str(self.unique_id + 1) + ". This vehicle has travelled: " + str(self.odometer) + " distance units")
            print("Vehicle id: " + str(self.unique_id + 1) + ". This vehicle's current charge level is: " + str(self.battery) + " kWh")
        # Transition Case 2: Still travelling, battery low. Travel -> travel_low
        if self.machine.state == 'Travel' and self.battery <= self._soc_usage_thresh:
            self.machine.get_low()
            print("Current EV state: " + str(self.machine.state))
            print("Vehicle id: " + str(self.unique_id + 1) + ". This vehicle has travelled: " + str(self.odometer) + " distance units")
            print("Vehicle id: " + str(self.unique_id + 1) + ". This vehicle's current charge level is: " + str(self.battery) + " wh")
        # Transition Case 3: Stopped travelling, Join queue, select cp. Travel_low -> in_queue
        if self.machine.state == 'Travel_low' and self.odometer < self._distance_goal:
            # self.select_cp()     check and pick cp
            self.machine.seek_charge_queue() #travel_low -> seek_queue

            # self.machine.join_charge_queue()
            # self._chosen_cp.join_queue(self)
            # self._chosen_cp.queue.append(self)
            print("Current EV state: " + str(self.machine.state))
            # print("Vehicle " + str(self.unique_id) + " is at CP with id: " + str(self._chosen_cpoint.unique_id) + " . CLevel: " + str(self.battery))
        
        # Transition Case 4: Looking for CP. Travel_low -> seek_queue
        if self.machine.state == 'Seek_queue':


        # Transition Case 5: Start charging. In_queue -> charge
        if self.machine.state == 'In_queue':
            if self.battery < self._soc_charging_thresh:
                self.machine.start_charge()
                self.charge_simple()
                # instead, join queue, select cp, then start charge
            else:
                self.machine.end_charge()
        # Transition Case 6: Continue charging. Charge -> charge
        if self.machine.state == 'Charge':
            if self.battery >= self._soc_charging_thresh:
                print("Charge complete. Vehicle " + str(self.unique_id + 1) + " is now " + str(self.machine.state) + "d.")
                self.machine.end_charge()
            else:
                self.machine.continue_charge()
                self.charge_simple()
        # # Transition Case 7: Journey Complete. travel -> idle
        if self.machine.state == 'Travel' and self.odometer >= self._distance_goal:
            self.machine.end_travel()
            print("Current EV state: " + str(self.machine.state))
            print("Vehicle " + str(self.unique_id + 1) + " has completed its journey and is now " + str(self.machine.state))
        # Transition Case 8: Jouney Complete. travel_low -> idle. JIT                                                       # For V 0.2
        
        # Record EV battery soc at the end of every 23 steps
        # Reinitialise agent variables for next day
        if (model.schedule.steps + 1) % 24 == 0:
            print("This is the end of day: " + str((model.schedule.steps + 1) / 24))
            self.add_soc_eod()
            self.set_new_day()



# class EV(Agent):
#     """An agent used to model an electric vehicle (EV).
#     Attributes:
#         unique_id: Unique identifier for the agent.
#         model: Model object that the agent is a part of.
#         _charge_rate: Charge rate of the EV in kW.
#         _in_queue: Boolean value indicating whether the EV is in queue.
#         _in_garage: Boolean value indicating whether the EV is in garage.
#         _is_charging: Boolean value indicating whether the EV is charging.
#         _was_charged: Boolean value indicating whether the EV was charged.
#         _is_travelling: Boolean value indicating whether the EV is travelling.
#         _journey_complete: Boolean value indicating whether the EV's journey is complete.
#         machine: EV State Machine.
#         _pos_init: Initial position of the EV.
#         _is_active: Boolean value indicating whether the EV is active.
#         odometer: Odometer of the EV.
#         _distance_goal: Distance goal of the EV.
#         journey_type: Type of journey the EV is undertaking.
#         _soc_usage_thresh: State of charge at which EV driver feels compelled to start charging at station.
#         _soc_charging_thresh: State of charge at which EV driver is comfortable with stopping charging at station.
#         _journey_choice: Choice of journey the EV driver makes.
#         battery: State of charge of the EV.
#         max_battery: Maximum state of charge of the EV.

#         unused:
#         _pos_init: Initial position of the EV.
#         _chosen_cp: Charging point chosen by the EV driver.
#         _chosen_cp_id: ID of Charging point  chosen by the EV driver.
#         tick_energy_usage: Energy usage of the EV in a tick.
#         battery_eod: State of charge of the EV at the end of the day.
#         day_count: Number of days the EV has been active.

        
#     """
#     def __init__(self, unique_id, model):
#         super().__init__(unique_id, model)
#         self._charge_rate = 7.5# kW 7200W
#         self._in_queue = False
#         self._in_garage = False
#         self._is_charging = False
#         self._was_charged = False
#         self._is_travelling = False
#         self._journey_complete = False
#         self.machine = EVSM(initial='Idle', states=states, transitions=transitions)
#         self._pos_init = None #unused Fix in v.0.2
#         self._is_active = True
#         self.odometer = 0
#         self._distance_goal = 0
#         self.journey_type = None
#         self.destination = None
#         self.battery = random.randint(40, 70) #kWh
#         self.max_battery = self.battery
#         # EV Driver Behaviour
#         self._speed = 0
#         # battery soc level at which EV driver feels compelled to start charging at station.
#         self._soc_usage_thresh = (0.3 * self.max_battery) 
#         # battery soc level at which EV driver is comfortable with stopping charging at station.
#         self._soc_charging_thresh = (0.8 * self.max_battery) 
#         self._chosen_cpoint = None # unused Fix in v.0.2
#         # Newest
#         self.ev_consumption_rate = 0
#         self.tick_energy_usage = 0
#         self.battery_eod = []
#         self.day_count = 0
#         # choose journey type
#         self.journey_type = self.choose_journey_type()
#         # set speed
#         self.set_speed()
#         # set energy consumption rate
#         self.set_ev_consumption_rate()
#         # choose actual destination and set distance goal based on journey type
#         self.choose_destination(self.journey_type)
#         # TO-DO
#         self._chosen_cp_idx = 0 #in selected_cp
#         self._chosen_cp = 0 #in selected_cp correct

#         # Initialisation Report

#         print("EV No " + str(self.unique_id + 1) + " initialized. Journey type: " + str(self.journey_type) +
#         ". Vehicle State: " + str(self.machine.state))

#         print(f"EV info: ID: {self.unique_id}, destination name: {self.destination} , distance goal: {self._distance_goal}, max_battery: {self.max_battery}, speed: {self._speed}, energy consumption rate {self.ev_consumption_rate}")
#         # End initialisation

#         # set tick distance
#         # 15/01: For now, tick = 1 hour. Consider changing to 30 miles per tick. 
#         # Change to self._speed for dynamic tick distance.
#         # self.tick_distance = 10 # 10 mile per tick. ??
#         # speed == distance per tick
#         # if EV active over multiple days, use learnt value from prev day. If overnight charge, set to 100. write methods to handle cases later.
#         # dynamic tick distance uses _speed = tick_distance
#         # self._chosen_cpoint_idx = 0
    
#     # Internal functions
#     def choose_journey_type(self):
#         """Chooses a journey type for the EV driver.
#         Returns:
#             journey_type: Choice of journey the EV driver makes.
#         """
#         self._journey_choice = choice([True, False]) #True = Urban, False = Highway
#         if self._journey_choice == True:
#             # self._distance_goal = 100 #miles
#             self.journey_type = "Urban"
#         else:
#             # self._distance_goal = 200 #miles
#             self.journey_type = "InterUrban"
#         return self.journey_type
    
#     def set_speed(self) -> None:
#         """Sets the speed of the EV driver."""
#         base_speed = 10 #urban speed (mph). Interurban speed is scaled by 2.
#         if self.journey_type == "Urban":
#             self._speed = base_speed
#         else:
#             self._speed = (base_speed * 2) #interurban speed (mph). 
        
#     def set_ev_consumption_rate(self) -> None:
#         # set vehicle energy consumption rate
#         if self.journey_type == "Urban":
#             self.ev_consumption_rate = 0.2 # 200 Wh/mile OR 20 kWh/100 miles OR 0.2 kWh/mile
#         else:
#             self.ev_consumption_rate = 0.5 # 500 Wh/mile OR 50 kWh/100 miles
    
#     def choose_destination(self, journey_type):
#         """Chooses a destination for the EV driver.
#         Args:
#             journey_type: Choice of journey type the EV driver makes.
#         Returns:
#             destination: Choice of destination for the EV driver.
#         """
#         if journey_type == "Urban":
#             self.choose_destination_urban()
#         else:
#             self.choose_destination_interurban()
#         return self.destination

#     def choose_destination_urban(self) -> None:
#         """Chooses a destination for the EV driver. Urban destination from destinations distances dictionary.
        
#         Returns:     
#             destination: Choice of destination for the EV driver. (imp)
#             distance_goal: Distance goal for the EV driver. (imp)
            
#         """
#         # Option 1: use weights to determine destination
#         # define weights used
#         # destinations_weights = {'work': 40, 'market': 10, 'friend_1': 15, 'friend_2': 20, 'autoshop': 15} #probability
#         # assign distances to each destination
#         # destination = random.choices(list(destinations_weights.keys()), weights=list(destinations_weights.values()), k=1)


#         # Option 2: use values directly to determine destination
#         destinations_distances = {'work': 50, 'market': 80, 'friend_1': 45, 'friend_2': 135, 'autoshop': 70} #miles
#         destination = random.choice(list(destinations_distances))
#         self.destination = destination
#         # print(f"Destination name: {self.destination}.")
#         # set distance goal based on destination
#         # if self.journey_type == "Urban":
#         self._distance_goal = destinations_distances.get(destination)
#         # print(f"Destination goal: {self._distance_goal}.")
#         # return destination

#     def choose_destination_interurban(self) -> None:
#         """
#         Chooses a destination for the EV driver. InterUrban destination from destinations distances dictionary.
#         Returns:
#             destination: Choice of destination for the EV driver.
#             distance_goal: Distance goal for the EV driver.
#         """
#         # choices = {'City A': 210, 'City B': 140, 'City C': 245}
#         # destination = random.choices(list(choices.keys()), weights=list(choices.values()), k=1)
#         # return destination
#         destinations_distances = {'City A': 210, 'City B': 140, 'City C': 245} # miles
#         destination = random.choice(list(destinations_distances))
#         self.destination = destination
#         # print(f"Destination name: {self.destination}.")
#         # set distance goal based on destination
#         # if self.journey_type == "Interurban":
#         self._distance_goal = destinations_distances.get(destination)
#         # print(f"Destination goal: {self._distance_goal}.")

#     def energy_usage_trip(self):
#         """Energy consumption (EC) for the entire trip. EC from distance covered"""
#         usage = (self.ev_consumption_rate * self.odometer)
#         return usage

#     def energy_usage_tick(self):
#         """Energy consumption (EC) for each tick. EC from distance covered"""
#         usage = (self.ev_consumption_rate * self._speed)
#         # self.tick_energy_usage = usage
#         return usage

#     def delta_battery_neg(self):
#         """ Marginal negative change in battery level per tick."""
#         # delta = ((self.battery - self.tick_energy_usage)/self._max_battery)
#         delta = (self.tick_energy_usage / self.max_battery)
#         return delta
  
#     # Core EV Functions
#     def travel(self):
#         """Travel function. Moves EV along the road. Updates odometer and battery level."""
#         self.odometer += self._speed # old: self.tick_distance
#         # self._distance_goal - self.tick_distance
#         self.battery -= self.energy_usage_tick()
#         print("Vehicle " + str(self.unique_id + 1 ) + " is travelling")
#     # unused function
#     def check_for_cp(self):
#         """Checks for a free CP in the vicinity. If found, calls select_cp."""
#         # self.define_vicinity() or 
#         for agent in self.model.schedule.agents:
#             if type(Agent) == Cpoint and (agent.free_cp == True):
#                 return agent
#     # unused function
#     def takeCP(self):
#         """Signifies that CP is taken and charging begins."""
#         for agent in self.model.schedule.agents:
#             if type(agent) == Cpoint:
#                 agent.free_cp = False
#                 print("Vehicle " + str(self.unique_id + 1 ) + " is charging at " + str(agent))
#                 return agent.free_cp
#     # unused function
#     def select_cp(self):
#         """Selects a CP to charge at. Chooses the CP with the shortest queue."""
#         self._in_queue = True
#         # queue at shortest cp
#         self._chosen_cp_idx = np.argmin([len(cpoint.queue) for cpoint in self.model.cpoints])
#         print("No of active Cpoints: " + str(self.model.cpoints.count(self)))
#         self._chosen_cp = self.model.cpoints[self._chosen_cp_idx]
#         print("Vehicle " + str(self.unique_id + 1 ) + " selected: " + str(self._chosen_cp) + " for charging.")


#     def add_soc_eod(self):
#         """Adds the battery level at the end of the day to a list."""
#         self.battery_eod.append(self.battery)
#         print("Battery level at end of day: " + str(self.battery_eod[-1]))
#         # print("Length of B3EOD: " + str(len(self.battery_eod))) # sanity check
    
#     def set_new_day(self):
#         """
#         Sets the battery level to the end of day level from previous day, for the new day.
#         Increments day_count and resets the odometer to 0.
#         """
#         self.battery = self.battery_eod[-1]
#         self.day_count += 1
#         self.odometer = 0
    
#     def charge_simple(self):
#         """Simple charging function. Charges the EV according to the charge rate."""
#         # flags
#         self._is_charging = True
#         self.battery += self._charge_rate
#         print("Vehicle " + str(self.unique_id + 1 ) + " charged status: " + str(self._was_charged)+ ". CLevel: " + str(self.battery))
#         self._was_charged = True
                
#     # def charge_main(self):                                                                                            # For V 0.2
#     #     # self._chosen_cp.active_car = None
#     #     self.check_for_cp()
#     #     if CP.free_cp:
#     #         self.takeCP()
#     #     else:
#     #         # wait_time = 0
#     #         self.wait_time += 1
#     #         self.waitInQueue()
#     #         # self._in_queue = True
#     #         # self._chosen_cp.queue.append(self)

        
#     #     print("Vehicle " + str(self.unique_id + 1 ) + " charging status: " + str(self._was_charged)+ ". CLevel: " + str(self.soc))

#     # def charge_overnight(self):                                                                                        # For V 0.3
#     #     if self._in_garage == True & self.soc < self._max_battery:
#     #         # self.soc = self._max_battery
#     #         self.soc += self._charge_rate
#     #     self._is_charging = True
#     #     self._was_charged = True
            

#     def step(self):
#         # Block A - Transitions SM:
#         # Transition Case 1: Start travelling. idle -> travel
#         if self.machine.state == 'Idle' and self.odometer < self._distance_goal:
#             self.machine.start_travel()
#             print("Current EV state: " + str(self.machine.state))
#         if self.machine.state == 'Travel':
#             self.machine.continue_travel()
#             self.travel()
#             print("Current EV state: " + str(self.machine.state))
#             print("Vehicle id: " + str(self.unique_id + 1) + ". This vehicle has travelled: " + str(self.odometer) + " distance units")
#             print("Vehicle id: " + str(self.unique_id + 1) + ". This vehicle's current charge level is: " + str(self.battery) + " kWh")
#         # Transition Case 2: Still travelling, battery low. Travel -> travel_low
#         if self.machine.state == 'Travel' and self.battery <= self._soc_usage_thresh:
#             self.machine.get_low()
#             print("Current EV state: " + str(self.machine.state))
#             print("Vehicle id: " + str(self.unique_id + 1) + ". This vehicle has travelled: " + str(self.odometer) + " distance units")
#             print("Vehicle id: " + str(self.unique_id + 1) + ". This vehicle's current charge level is: " + str(self.battery) + " wh")
#         # Transition Case 3: Stopped travelling, Join queue, select cp. Travel_low -> in_queue
#         if self.machine.state == 'Travel_low' and self.odometer < self._distance_goal:
#             self.machine.join_charge_queue() #travel_low -> in_queue
#             # self.checkForCP()
#             # self.select_cp()
#             print("Current EV state: " + str(self.machine.state))
#             # print("Vehicle " + str(self.unique_id) + " is at CP with id: " + str(self._chosen_cpoint.unique_id) + " . CLevel: " + str(self.battery))

#         # Transition Case 4: Start charging. In_queue -> charge
#         if self.machine.state == 'In_queue':
#             if self.battery < self._soc_charging_thresh:
#                 self.machine.start_charge()
#                 self.charge_simple()
#                 # instead, join queue, select cp, then start charge
#             else:
#                 self.machine.end_charge()
#         # Transition Case 5: Continue charging. Charge -> charge
#         if self.machine.state == 'Charge':
#             if self.battery >= self._soc_charging_thresh:
#                 print("Charge complete. Vehicle " + str(self.unique_id + 1) + " is now " + str(self.machine.state) + "d.")
#                 self.machine.end_charge()
#             else:
#                 self.machine.continue_charge()
#                 self.charge_simple()
#         # # Transition Case 6: Journey Complete. travel -> idle
#         if self.machine.state == 'Travel' and self.odometer >= self._distance_goal:
#             self.machine.end_travel()
#             print("Current EV state: " + str(self.machine.state))
#             print("Vehicle " + str(self.unique_id + 1) + " has completed its journey and is now " + str(self.machine.state))
#         # Transition Case 7: Jouney Complete. travel_low -> idle. JIT                                                       # For V 0.2
        
#         # Record EV battery soc at the end of every 23 steps
#         # Reinitialise agent variables for next day
#         if (model.schedule.steps + 1) % 24 == 0:
#             print("This is the end of day: " + str((model.schedule.steps + 1) / 24))
#             self.add_soc_eod()
#             self.set_new_day()

# class Cpoint(Agent):
#     """
#         A charging point agent.
#         Attributes:
#         unique_id: Unique identifier for the agent.
#         model: The model the agent is running in.
#         queue: A list of EVs waiting to charge at the CP.
#         _is_charging: A boolean value indicating whether the CP is currently charging an EV.
#         active_ev: The EV currently charging at the CP.
#         _charge_rate: The rate at which the CP charges an EV.

#     """
#     def __init__(self, unique_id, model):
#         super().__init__(unique_id, model)
#         self.queue = []
#         self._is_charging = True
#         self.active_ev = None
#         # self._charge_rate = choice([7, 15, 100, 300]) #different charge rates
#         self._charge_rate = 7
#         print(f"CP No {self.unique_id} initialized. Charge rate: {self._charge_rate}kW. Charge State: {self._is_charging}")
#     def __str__(self):
#         """Return the agent's unique id."""
#         return ("CP No: " + str(self.unique_id))
    
#     def join_queue(self, ev):
#         """Add an EV to the CP's queue."""
#         self.queue.append(ev)
#         print("EV " + str(ev.unique_id + 1) + " joined queue at CP " + str(self.unique_id))

#     def dequeue(self):
#         """Remove the first EV from the queue. FIFO fom queue."""
#         try:
#             self.active_ev = self.queue.pop(0)
#             print("Current EV " + str(self.active_ev) + " dequeued")
#             # self.active_ev = model.queue.pop(0)
#             # self.active_ev.machine.state == 'Charge'
#             # print("Current EV at CP is in state: " + str(self.active_ev.machine.state))
#         except:
#             pass
#     def charge_ev(self):
#         """Charge the EV at the CP.
#         The EV is charged at the CP's charge rate.
#         """
#         # EV.battery += self._charge_rate
#         if self.active_ev is not None:
#             self.active_ev.battery += self._charge_rate
#             self.active_ev.machine.state == 'Charge'
#             print("Current EV at CP is in state: " + str(self.active_ev.machine.state))
#             # print("Vehicle " + str(self.active_ev.unique_id + 1 ) + " was charged status: " + str(self._was_charged)+ ". CLevel: " + str(self.active_ev.battery))

#     def step(self):
#         for ev in model.evs:
#             if ev.machine.state == 'In_queue':
#                 self.join_queue(ev)
#         # Transition Case 4: Start charging. In_queue -> charge
#         if self.active_ev is None:
#             self.dequeue()
#         else:
#             self.charge_ev()