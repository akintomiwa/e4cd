"""This module contains the agent classes for the EV model."""

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
from transitions import Machine
from transitions.extensions import GraphMachine
from functools import partial
# import EV.model as model
from EV.statemachine import EVSM, states, transitions

class Cpoint(Agent):
    """A charging point agent.
    Attributes:
        unique_id: Unique identifier for the agent.
        model: The model the agent is running in.
        queue: A list of EVs waiting to charge at the CP.
        _is_charging: A boolean value indicating whether the CP is currently charging an EV.
        active_ev: The EV currently charging at the CP.
        _charge_rate: The rate at which the CP charges an EV.

    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.queue_1 = []
        self.queue_2 = []
        self._is_charging = True
        self.active_ev_1 = None
        self.active_ev_2 = None
        # can replace wit h array of 2
        # self.active_evs = []
        # self._charge_rate = choice([7, 15, 100, 300]) #different charge rates
        self._charge_rate = 7.5 #kW
        self._checkpoint_id = 0

        print(f"CP info: ID: {(self.unique_id)}, initialized. Charge rate: {self._charge_rate} kW.")

        # End initialisation

    def __str__(self) -> str:
        """Return the agent's unique id."""
        return str(self.unique_id + 1)
    
    def dequeue(self) -> None:
        """Remove the first EV from each queue. FIFO fom queue."""
        try:
            self.active_ev_1 = self.queue_1.pop(0)
            self.active_ev_2 = self.queue_2.pop(0)
            print(f"EV {(self.active_ev_1.unique_id)} dequeued at CP {self.unique_id} at Queue 1 and is in state: {self.active_ev_1.machine.state}")
            print(f"EV {(self.active_ev_2.unique_id)} dequeued at CP {self.unique_id} at Queue 2 and is in state: {self.active_ev_2.machine.state}")
        except:
            pass
    
    # def set_checkpoint_id(self, checkpoint_id) -> None:
    #     """Set the checkpoint id of the EV."""
    #     self._checkpoint_id = checkpoint_id
    #     pass
    
    def charge_ev(self):
        """Charge the EV at the Charge Station.
        The EV is charged at the Chargepoint's charge rate.
        """
        # Transition Case 6: EV is charging at CP.
        # self.active_ev_1.machine.start_charge()
        # self.active_ev_2.machine.start_charge()

        if self.active_ev_1 is not None:
            # self.active_ev.machine.start_charge()
            # if self.active_ev_1.machine.state == 'Charge':
            print(f"EV {self.unique_id} is in state; {self.active_ev_1.machine.state}")
            self.active_ev_1.battery += self._charge_rate
            # self.active_ev.machine.start_charge()
            print(f"EV {str(self.active_ev_1.unique_id)} at CP {(self.unique_id)} is in state: {self.active_ev_1.machine.state}, CLevel {self.active_ev_1.battery}")
        # if self.active_ev_2 is not None:
        #     # self.active_ev.machine.start_charge()
        #     if self.active_ev_2.machine.state == 'Charge':
        #         self.active_ev_2.battery += self._charge_rate
        #         # self.active_ev.machine.start_charge()
        #         print(f"EV {str(self.active_ev_2.unique_id)} at CP {(self.unique_id)} is in state: {self.active_ev_2.machine.state}, CLevel {self.active_ev_2.battery}")


    def step(self):
        if self.active_ev_1 or self.active_ev_2 is None:
            self.dequeue()
        else:
            self.charge_ev()

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
        self._soc_usage_thresh = (0.4 * self.max_battery) 
        # battery soc level at which EV driver is comfortable with stopping charging at station.
        self._soc_charging_thresh = (0.8 * self.max_battery) 
        self._chosen_cpoint = None # unused Fix in v.0.2
        # Newest
        self.ev_consumption_rate = 0
        self.tick_energy_usage = 0
        self.battery_eod = []
        self.day_count = 0
        self.checkp_1 = 0
        self.checkp_2 = 0
        # choose journey type
        self.journey_type = self.choose_journey_type()
        # set speed
        self.set_speed()
        # set energy consumption rate
        self.set_ev_consumption_rate()
        # choose actual destination and set distance goal based on journey type
        self.choose_destination(self.journey_type)
        # CPoint Intractions
        self._chosen_cp_idx = 0 #in selected_cp
        self._chosen_cp = 0 #in selected_cp correct

        # self.checkp_1 = self._set_checkpoint(0.3)
        # self.checkp_2 = self._set_checkpoint(0.6)

        # self.checkpoint_list = [40,80,120,160,200,240]
        self.checkpoint_list = model.checkpoints

        # Initialisation Report

        print("EV No " + str(self.unique_id + 1) + " initialized. Journey type: " + str(self.journey_type) +
        ". Vehicle State: " + str(self.machine.state))
        # print("EV No " + str(self.__str__) + " initialized. Journey type: " + str(self.journey_type) + ". Vehicle State: " + str(self.machine.state))

        print(f"EV info: ID: {self.unique_id}, destination name: {self.destination} , distance goal: {self._distance_goal}, max_battery: {self.max_battery}, speed: {self._speed}, energy consumption rate {self.ev_consumption_rate}")
        
        # print(f"CheckP1: {self.checkp_1}, CheckP2: {self.checkp_2}")

        # End initialisation report
    
    def __str__(self):
        """Return the agent's unique id."""
        return str(self.unique_id + 1)

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
    
    def choose_destination(self, journey_type) -> str:
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

        # Option 2: use values directly to determine destination
        destinations_distances = {'work': 50, 'market': 80, 'friend_1': 45, 'friend_2': 135, 'autoshop': 70} #miles
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
        destinations_distances = {'City A': 210, 'City B': 140, 'City C': 245} # miles
        destination = random.choice(list(destinations_distances))
        self.destination = destination
        self._distance_goal = destinations_distances.get(destination)

    def energy_usage_trip(self) -> float:
        """Energy consumption (EC) for the entire trip. EC from distance covered"""
        usage = (self.ev_consumption_rate * self.odometer)
        return usage

    def energy_usage_tick(self) -> float:
        """Energy consumption (EC) for each tick. EC from distance covered"""
        usage = (self.ev_consumption_rate * self._speed)
        return usage

    def delta_battery_neg(self) -> float:
        """ Marginal negative change in battery level per tick."""
        delta = (self.tick_energy_usage / self.max_battery)
        return delta
  
    # Core EV Functions
    def travel(self) -> None:
        """Travel function. Moves EV along the road. Updates odometer and battery level."""
        self.odometer += self._speed
        self.battery -= self.energy_usage_tick()
        print(f"Vehicle {self.unique_id} is travelling. Odometer: {self.odometer}, Battery: {self.battery}")
    
    # new select cp
    def select_cp(self) -> None:
        """Selects a CP to charge at. Chooses the CP at the scheckpoint"""
        # self._chosen_cp_idx = np.argmin((cpoint.unique_id) for cpoint in self.model.cpoints)
        # self._chosen_cp = self.model.cpoints[self._chosen_cp_idx]

        # self._chosen_cp = self.model.cpoints[self.model.cpoints._checkpoint_id == self.odometer]

        for cp in self.model.cpoints:
            if cp._checkpoint_id == self.odometer:
                self._chosen_cp = cp

        print(f"Charge Station selected: {(self._chosen_cp.unique_id)}")
        print(f"Length of queue 1: {(len(self._chosen_cp.queue_1))}")
        print(f"Length of queue 2: {(len(self._chosen_cp.queue_2))}")
        self.choose_cp_queue()
        print(f"Vehicle {(self.unique_id)} selected Charge Station: {(self._chosen_cp.unique_id)} for charging.")

    def choose_cp_queue(self) -> None:
        """Chooses a queue at the CP to charge at. Chooses the queue with the shortest queue."""
        if len(self._chosen_cp.queue_1) > len(self._chosen_cp.queue_2):
            self._chosen_cp.queue_2.append(self)
            print(f"EV {(self.unique_id)} selected queue 2 at Charge Station {(self._chosen_cp.unique_id)}")
        elif len(self._chosen_cp.queue_1) < len(self._chosen_cp.queue_2):
            self._chosen_cp.queue_1.append(self)
            print(f"EV {(self.unique_id)} selected queue 1 at Charge Station {(self._chosen_cp.unique_id)}")
        # elif len(self._chosen_cp.queue_1) < len(self._chosen_cp.queue_2):
        #     self.queue_choice = random.choice(["1","2"])
        #     if choice == "1":
        #         self._chosen_cp.queue_1.append(self)
        #     else:
        #         self._chosen_cp.queue_2.append(self)
        #     print(f"The selected queue is {self.queue_choice}")
        elif len(self._chosen_cp.queue_1) == len(self._chosen_cp.queue_2):
            self._chosen_cp.queue_1.append(self)
            print(f"EV {(self.unique_id)} selected queue 1 at Charge Station {(self._chosen_cp.unique_id)}")


    def add_soc_eod(self) -> None:
        """Adds the battery level at the end of the day to a list."""
        self.battery_eod.append(self.battery)
        print(f"Battery level at end of day: {self.battery_eod[-1]}")

    
    def set_new_day(self) -> None:
        """
        Sets the battery level to the end of day level from previous day, for the new day.
        Increments day_count and resets the odometer to 0.
        """
        self.battery = self.battery_eod[-1]
        self.day_count += 1
        self.odometer = 0

    # Approach 1: use a link, index calculated by journey goal/by distance tick
    def _set_checkpoint(self, factor) -> float:
        distance = self._distance_goal * factor
        return distance
    
    # next step, do checkpointing using a link, index calculated by journey goal/by distance tick
    
    # Approach 2: use a list of checkpoints stored as a list of checkpoints



    def step(self):
        # Block A - Transitions SM:
        # Transition Case 1: Start travelling. idle -> travel
        if self.machine.state == 'Idle' and self.odometer < self._distance_goal:
            self.machine.start_travel()
            # print("Current EV state: " + str(self.machine.state))
        if self.machine.state == 'Travel':
            self.machine.continue_travel()
            self.travel()
            print(f"Vehicle id: {self.unique_id} is {self.machine.state}. This vehicle has travelled: {self.odometer} miles. Battery: {self.battery} kWh")

        # Transition Case 2: Still travelling, battery low. Travel -> travel_low
        # if self.machine.state == 'Travel' and self.battery <= self._soc_usage_thresh:
        #     self.machine.get_low()
        #     print("Current EV state: " + str(self.machine.state))
        #     print("Vehicle id: " + str(self.unique_id + 1) + ". This vehicle has travelled: " + str(self.odometer) + " distance units")
        #     print("Vehicle id: " + str(self.unique_id + 1) + ". This vehicle's current charge level is: " + str(self.battery) + " wh")
        # Transition Case 3, 4 and 5: Stopped travelling, Join queue, select cp. Travel_low -> in_queue
        # if self.machine.state == 'Travel_low' and self.odometer < self._distance_goal:
        #     self.machine.seek_charge_queue() #travel_low -> seek_queue
        #     self.select_cp()     # check and pick cp. appends ev to cp queue
        #     self.machine.join_charge_queue() #seek_queue -> in_queue 
        #     print("Current EV state: " + str(self.machine.state))
        #     # print("Vehicle " + str(self.unique_id) + " is at CP with id: " + str(self._chosen_cpoint.unique_id) + " . CLevel: " + str(self.battery))
        
        ########
        # focus
        ########

        if self.machine.state == 'Travel_low' and self.battery == 0:
            self.machine.deplete_battery()
            print(f"EV {self.unique_id} is now in state: {self.machine.state} and is out of charge.")

        if self.machine.state == 'Travel_low' and self.odometer < self._distance_goal:
            if self.battery > 0:
                print(f"EV {self.unique_id} is low on charge and is seeking a charge station. Current charge: {self.battery} kWh")
                self.travel()
            elif self.battery == 0:
                print(f"EV {self.unique_id} is out of charge and is seeking a charge station.")
                self.machine.deplete_battery()

                
        if self.machine.state == 'Travel' and self.battery <= self._soc_usage_thresh:
            self.machine.get_low()
            print("Current EV state: " + str(self.machine.state))
            print(f"EV: {self.unique_id}. This vehicle has travelled: {str(self.odometer)} miles and is low on battery. This vehicle's current charge level is: {str(self.battery)} kwh")


        # Approach 2: use a list of checkpoints stored as a list of checkpoints
        if self.machine.state == 'Travel' and self.odometer in self.checkpoint_list:
            print("EV has arrived at Charge Station but is not yet low on battery")

        if self.machine.state == 'Travel_low' and self.odometer in self.checkpoint_list:
            self.machine.seek_charge_queue()
            print(f"EV {self.unique_id} is low on battery and is at a station. Seeking charge queue. Current EV state: {self.machine.state}")
            self.select_cp()
            self.machine.join_charge_queue()
        
        #######
        
        # Transition Case 7: Continue charging. Charge -> charge
        if self.machine.state == 'Charge':
            if self.battery >= self._soc_charging_thresh:
                print("Charge complete. Vehicle " + str(self.unique_id + 1) + " is now " + str(self.machine.state) + "d.")
                self.machine.end_charge()
            if self.battery < self._soc_charging_thresh:
                self.machine.continue_charge()
                self.charge()
                print(f"Vehicle {self.unique_id} is {self.machine.state}. This vehicle has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
                
        # # Transition Case 8: Journey Complete. travel -> idle
        if self.machine.state == 'Travel' and self.odometer >= self._distance_goal:
            self.machine.end_travel()
            print("Current EV state: " + str(self.machine.state))
            print("Vehicle " + str(self.unique_id) + " has completed its journey and is now " + str(self.machine.state))
        # Transition Case 8: Journey Complete. travel_low -> idle. JIT                                                       # For V 0.2
        
    
        # Transition Case 4: Looking for CP. Travel_low -> seek_queue
        # Handled in Cpoint step function
        
        # Transition Case 5: Find best queue and take spot. Seek_queue -> In_queue
        # Handled in Cpoint step function





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
        

        