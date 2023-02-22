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
from transitions import Machine, MachineError
from transitions.extensions import GraphMachine
from functools import partial
# import EV.model as model
from EV.statemachine import EVSM, states, transitions

class ChargeStation(Agent):
    """A charging point agent.
    Attributes:
        unique_id: Unique identifier for the agent.
        model: The model the agent is running in.
        queue: A list of EVs waiting to charge at the CP.
        _is_charging: A boolean value indicating whether the CP is currently charging an EV.
        _active_ev: The EV currently charging at the CP.
        _charge_rate: The rate at which the CP charges an EV.

    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.queue_1 = []
        self.queue_2 = []
        self._is_active = False
        self.active_ev_1 = None
        self.active_ev_2 = None
        # can replace with array of 2
        # self.active_evs = []
        # self._charge_rate = choice([7, 15, 100, 300]) #different charge rates

        self._charge_rate = 7.5 #kW
        self._checkpoint_id = 0

        # new
        self.max_queue_size = 10


        print(f"CP info: ID: {(self.unique_id)}, initialized. Charge rate: {self._charge_rate} kW.")

        # End initialisation

    def __str__(self) -> str:
        """Return the agent's unique id."""
        return str(self.unique_id + 1)
    
    # def dequeue(self) -> None:
    #     """Remove the first EV from each queue. FIFO fom queue."""
    #     try:
    #         self.active_ev_1 = self.queue_1.pop(0)
    #         self.active_ev_2 = self.queue_2.pop(0)
    #         print(f"EV {(self.active_ev_1.unique_id)} dequeued at CP {self.unique_id} at Queue 1 and is in state: {self.active_ev_1.machine.state}")
    #         print(f"EV {(self.active_ev_2.unique_id)} dequeued at CP {self.unique_id} at Queue 2 and is in state: {self.active_ev_2.machine.state}")
    #         print(f"Queue 1 size: {len(self.queue_1)}, Queue 2 size: {len(self.queue_2)}")
    #     except:
    #         pass
    
    def dequeue_1(self) -> None:
        """Remove the first EV from each queue. FIFO fom queue."""
        try:
            self.active_ev_1 = self.queue_1.pop(0)
            self.active_ev_1.machine.start_charge()
            print(f"EV {(self.active_ev_1.unique_id)} dequeued at CS {self.unique_id} at Queue 1 and is in state: {self.active_ev_1.machine.state}")
            print(f"Queue 1 size after dequeuing: {len(self.queue_1)}")
        except:
            pass
    
    def dequeue_2(self) -> None:
        """Remove the first EV from each queue. FIFO fom queue."""
        try:
            self.active_ev_2 = self.queue_2.pop(0)
            print(f"EV {(self.active_ev_2.unique_id)} dequeued at CP {self.unique_id} at Queue 2 and is in state: {self.active_ev_2.machine.state}")
            print(f"Queue 2 size after dequeuing: {len(self.queue_2)}")
        except:
            pass

    # def charge_ev_1(self):
    #     """Charge the EV at the Charge Station.
    #     The EV is charged at the Chargepoint's charge rate.
    #     """
    #     # Transition Case: EV is charging at CP.
    #     if self.active_ev_1 is not None:
    #         print(f"EV {self.unique_id} is in state; {self.active_ev_1.machine.state}")
    #         self.active_ev_1.battery += self._charge_rate
    #         print(f"EV {self.active_ev_1.unique_id} at CP {self.unique_id} is in state: {self.active_ev_1.machine.state}, Battery: {self.active_ev_1.battery}")
    
    # def charge_ev_2(self):
    #     """Charge the EV at the Charge Station.
    #     The EV is charged at the Chargepoint's charge rate.
    #     """
    #     # Transition Case: EV is charging at CP.
    #     if self.active_ev_2 is not None:
    #         print(f"EV {self.unique_id} is in state; {self.active_ev_2.machine.state}")
    #         self.active_ev_2.battery += self._charge_rate
    #         print(f"EV {self.active_ev_2.unique_id} at CP {self.unique_id} is in state: {self.active_ev_2.machine.state}, Battery: {self.active_ev_2.battery}")
    
    # def charge_evs(self):
    #     self.charge_ev_1()
    #     self.charge_ev_2()

    # def charge_ev(self):
    #     """Charge the EV at the Charge Station.
    #     The EV is charged at the Chargepoint's charge rate.
    #     """
    #     # Transition Case: EV is charging at CP.
    #     if self.active_ev_1:
    #         print(f"EV {self.unique_id} is in state; {self.active_ev_1.machine.state}")
    #         self.active_ev_1.battery += self._charge_rate
    #         print(f"EV {self.active_ev_1.unique_id} at CP {self.unique_id} is in state: {self.active_ev_1.machine.state}, Battery: {self.active_ev_1.battery}")

    #     if self.active_ev_2:
    #         self.active_ev_2.battery += self._charge_rate
    #         print(f"EV {str(self.active_ev_2.unique_id)} at CP {(self.unique_id)} is in state: {self.active_ev_2.machine.state}, Battery: {self.active_ev_2.battery}")
       
    #     # # problem zone
    #     # if self.active_ev_1 is not None:
    #     #     print(f"EV {self.unique_id} is in state; {self.active_ev_1.machine.state}")
    #     #     self.active_ev_1.battery += self._charge_rate
    #     #     print(f"EV {self.active_ev_1.unique_id} at CP {self.unique_id} is in state: {self.active_ev_1.machine.state}, Battery: {self.active_ev_1.battery}")
    #     #     # print(f"The length of the queue 1 is now: {len(self.queue_1)}")
    #     # if self.active_ev_2 is not None:
    #     #     self.active_ev_2.battery += self._charge_rate
    #     #     print(f"EV {str(self.active_ev_2.unique_id)} at CP {(self.unique_id)} is in state: {self.active_ev_2.machine.state}, Battery: {self.active_ev_2.battery}")
    #     #     # print(f"The length of the queue 2 is now: {len(self.queue_2)}")
    
    def finish_charge_ev_1(self):
        """Finish charging the EV at CP1 at the Charge Station."""
        if self.active_ev_1 is not None:
            # self.active_ev_1.machine.end_charge()
            self.active_ev_1 = None
            print(f"EV at Charge Station {self.unique_id}, CP 1 has exited.")

    def finish_charge_ev_2(self):
        """Finish charging the EV at CP2 at the Charge Station."""
        if self.active_ev_2 is not None:
            # self.active_ev_2.machine.end_charge()
            self.active_ev_2 = None
            print(f"EV at Charge Station {self.unique_id}, CP 2 has exited.")

    def stage_1(self):
        if self.active_ev_1 is None:
            self.dequeue_1()
        if self.active_ev_2 is None:
            self.dequeue_2()

    def stage_2(self):
        if self.active_ev_1 is not None:
            if self.active_ev_1.battery < self.active_ev_1._soc_charging_thresh:
                self.active_ev_1.charge()
                self.active_ev_1.machine.continue_charge()
            else:
                self.active_ev_1.machine.end_charge()
                self.finish_charge_ev_1()
        if self.active_ev_2 is not None:
            if self.active_ev_2.battery < self.active_ev_2._soc_charging_thresh:
                self.active_ev_2.charge()
                self.active_ev_1.machine.continue_charge()
            else:
                # self.active_ev_1.machine.end_charge()
                self.finish_charge_ev_2()

    # def step(self):
    #     # if self.active_ev_1 or self.active_ev_2 is None:
    #     #     self.dequeue()
    #     # # else:
    #     #     self.charge_ev()
    #     # step_1
    #     if self.active_ev_1 is None:
    #         self.dequeue_1()
    #     if self.active_ev_2 is None:
    #         self.dequeue_2()
    #     # pass

    #     # step2
    #     # for CS in self.model.chargestations:
    #     # active_ev 2
    #     if self.active_ev_1.battery < self.active_ev_1._soc_usage_thresh:
    #         self.active_ev_1.charge_ev_1()
    #     else:
    #         self.active_ev_1.finish_charge_ev_1()
    #     # active_ev 2
    #     if self.active_ev_2.battery < self.active_ev_2._soc_usage_thresh:
    #         self.active_ev_2.charge_ev_2()
    #     else:
    #         self.active_ev_2.finish_charge_ev_2()
                

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
        self._at_station = False
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
        # Newest
        self.ev_consumption_rate = 0
        self.tick_energy_usage = 0
        self.battery_eod = []
        self.day_count = 0

        # choose journey type
        self.journey_type = self.choose_journey_type()
        # set EV speed
        self.set_speed()
        # set energy consumption rate
        self.set_ev_consumption_rate()
        # choose actual destination and set distance goal based on journey type
        self.choose_destination(self.journey_type)
        # CPoint Intractions
        # self._chosen_cp_idx = 0 #in selected_cp
        self._chosen_cs = 0 #in selected_cp correct
        self.checkpoint_list = model.checkpoints

        # Initialisation Report

        print(f"EV info: ID: {self.unique_id}, destination name: {self.destination}, journey type: {self.journey_type}, distance goal: {self._distance_goal}, max_battery: {self.max_battery}, speed: {self._speed}, energy consumption rate {self.ev_consumption_rate}. State: {self.machine.state}")

        # End initialisation report
    
    def __str__(self) -> str:
        """Return the agent's unique id as a string, not zero indexed."""
        return str(self.unique_id + 1)

    # Internal functions
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
        print(f"EV {self.unique_id} is travelling. Odometer: {self.odometer}, Battery: {self.battery}")
    
    def charge(self):
        """Charge the EV at the Charge Station.
        The EV is charged at the Chargepoint's charge rate.
        """
    
        print(f"EV {self.unique_id} is in state; {self.machine.state}")
        self.battery += self._charge_rate
        print(f"EV {self.unique_id} at CP {self._chosen_cs.unique_id} is in state: {self.machine.state}, Battery: {self.battery}")
    
    # 16 Feb charge flow redo - new methods
    def choose_charge_station(self):
        # choose station
        for cs in self.model.chargestations:
            if cs._checkpoint_id == self.odometer:
                self._chosen_cs = cs
                self._chosen_cs._is_active = True

        # print(f"Charge Station selected: {(self._chosen_cs.unique_id)}")
        print(f"EV {(self.unique_id)} selected Charge Station: {(self._chosen_cs.unique_id)} for charging.")

    # new select cp
    def choose_cs_queue(self) -> None:
        """Chooses a queue at the charge station to charge at. Chooses the queue with the shortest queue."""
        print(f"Length of q1: {(len(self._chosen_cs.queue_1))}. Length of q2: {(len(self._chosen_cs.queue_2))}")
        if len(self._chosen_cs.queue_1) > len(self._chosen_cs.queue_2):
            self._chosen_cs.queue_2.append(self)
            print(f"EV {(self.unique_id)} selected queue 2 at Charge Station {(self._chosen_cs.unique_id)}")
        elif len(self._chosen_cs.queue_1) < len(self._chosen_cs.queue_2):
            self._chosen_cs.queue_1.append(self)
            print(f"EV {(self.unique_id)} selected queue 1 at Charge Station {(self._chosen_cs.unique_id)}")
        elif len(self._chosen_cs.queue_1) == len(self._chosen_cs.queue_2):
            self._chosen_cs.queue_1.append(self)
            print(f"EV {(self.unique_id)} selected queue 1 at Charge Station {(self._chosen_cs.unique_id)}")
    
    # def exit_charge_station(self) -> None:
    #     """EV exits the charge station. Removes EV from queue and sets charge station to inactive."""
    #     if self._chosen_cs.active_ev_1 == self:
    #         self._chosen_cs = None
    #     elif self._chosen_cs.active_ev_2 == self:
    #         self._chosen_cs = None
    #     print(f"EV {(self.unique_id)} exited charge point at Charge Station {(self._chosen_cs.unique_id)}")
        
  
    # Model env functions
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

    # # Approach 1: use a link, index calculated by journey goal/by distance tick
    # def _set_checkpoint(self, factor) -> float:
    #     distance = self._distance_goal * factor
    #     return distance
    # # next step, do checkpointing using a link, index calculated by journey goal/by distance tick
    
 

    # staged step 
    def stage_1(self):
        """Stage 1: EV selects a charge station to charge at."""
        # Transition Case 1: Start travelling. idle -> travel
        if self.machine.state == 'Idle' and self.odometer < self._distance_goal:
            self.machine.start_travel()

        
        # Transition Case 2: Still travelling, battery low. Travel -> travel_low  
        if self.machine.state == 'Travel' and self.battery <= self._soc_usage_thresh:
            self.machine.get_low()
            # print(f"EV: {self.unique_id} has travelled: {str(self.odometer)} miles and is now {self.machine.state}. Current charge level is: {self.battery} kwh")


        ######################
        # Locating a Station #
        ######################
        # 21/02/23 - new flow for locating a station
        # Combo of 1b and 4

        if (self.machine.state == 'Travel' or self.machine.state == 'Travel_low') and self.odometer < self._distance_goal:
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

        
        # 21/02/23 - new flow for recognising a charge station (CS), choosing a CS and charge queue.
        # combine both below for stopping at charge station:
        if self.odometer in self.checkpoint_list:
            if self.machine.state == 'Travel':
                print(f"EV {self.unique_id} has arrived at Charge Station but is in state: {self.machine.state}. Not travelling low.")
            elif self.machine.state == 'Travel_low':
                self._at_station = True
                print(f"EV {self.unique_id} is low on battery and is at a station. Seeking charge queue. Current EV state: {self.machine.state}")
                # self.select_cp()
                self.choose_charge_station()
                self.machine.seek_charge_queue()
                self.choose_cs_queue()
                # at this point EV has arrived at CS, joined one of the two queues and is waiting to become the active ev, and get charged.
                self.machine.join_charge_queue()
                self._in_queue = True

       
    
    def stage_2(self):
        """Stage 2: EV waits in queue until it is the active EV."""
         # Transition Case 3: EV with low battery does not arrive at charge station. Travel_low -> Battery_dead
        # condition self.battery < 10 because 10 is the minimum expenditure of energy to move the vehicle in one timestep
        if self.machine.state == 'Travel_low' and self.battery < 10:
            self.machine.deplete_battery()
            print(f"EV {self.unique_id} is now in state: {self.machine.state} and is out of charge.")
        # Transition Case 7: Journey Complete. travel -> idle
        if self.machine.state == 'Travel' and self.odometer >= self._distance_goal:
            self.machine.end_travel()
            print(f"EV {self.unique_id} has completed its journey. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")

        # Transition Case 8: Journey complete, battery low. travel_low -> idle
        if self.machine.state == 'Travel_low' and self.odometer >= self._distance_goal:
            self.machine.end_travel_low()
            print(f"EV {self.unique_id} has completed its journey. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
    



    # Working with issues
    # def step(self):

    #     ############
    #     # Travelling #
    #     ############

    #     # Block A - Transitions SM:

    #     # Transition Case 1: Start travelling. idle -> travel
    #     if self.machine.state == 'Idle' and self.odometer < self._distance_goal:
    #         self.machine.start_travel()

    #     # # 1b    
    #     # if self.machine.state == 'Travel' and self.odometer < self._distance_goal:
    #     #     self.machine.continue_travel()
    #     #     self.travel()
    #     #     print(f"Vehicle id: {self.unique_id} is {self.machine.state}. This vehicle has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
        
    #     # Transition Case 2: Still travelling, battery low. Travel -> travel_low  
    #     if self.machine.state == 'Travel' and self.battery <= self._soc_usage_thresh:
    #         self.machine.get_low()
    #         # print(f"EV: {self.unique_id} has travelled: {str(self.odometer)} miles and is now {self.machine.state}. Current charge level is: {self.battery} kwh")


    #     ######################
    #     # Locating a Station #
    #     ######################
    #     # 21/02/23 - new flow for locating a station
    #     # Combo of 1b and 4

    #     if (self.machine.state == 'Travel' or self.machine.state == 'Travel_low') and self.odometer < self._distance_goal:
    #         if self.machine.state == 'Travel':
    #             self.travel()
    #             self.machine.continue_travel()
    #             print(f"EV {self.unique_id}  has travelled: {self.odometer} miles. State: {self.machine.state}. Battery: {self.battery} kWh")
    #         elif self.machine.state == 'Travel_low':
    #             if self.battery > 0:
    #                 print(f"EV {self.unique_id} is low on charge and is seeking a charge station. Current charge: {self.battery} kWh")
    #                 self.travel()
    #             elif self.battery <= 0:
    #                 self.machine.deplete_battery()
    #                 print(f"EV {self.unique_id} is out of charge and can no longer travel. State: {self.machine.state}. Current charge: {self.battery} kWh")

        

    #     # # Transition Case 4: EV with low battery is on lookout for Charge station. Notification.
    #     # if self.machine.state == 'Travel_low' and self.odometer < self._distance_goal:
    #     #     if self.battery > 0:
    #     #         print(f"EV {self.unique_id} is low on charge and is seeking a charge station. Current charge: {self.battery} kWh")
    #     #         self.travel()
    #     #     elif self.battery <= 0:
    #     #         self.machine.deplete_battery()
    #     #         print(f"EV {self.unique_id} is out of charge and can no longer travel. State: {self.machine.state}. Current charge: {self.battery} kWh")
        
    #     # 21/02/23 - new flow for recognising a charge station (CS), choosing a CS and charge queue.
    #     # combine both below for stopping at charge station:
    #     if self.odometer in self.checkpoint_list:
    #         if self.machine.state == 'Travel':
    #             print(f"EV {self.unique_id} has arrived at Charge Station but is in state: {self.machine.state}. Not travelling low.")
    #         elif self.machine.state == 'Travel_low':
    #             self._at_station = True
    #             print(f"EV {self.unique_id} is low on battery and is at a station. Seeking charge queue. Current EV state: {self.machine.state}")
    #             # self.select_cp()
    #             self.choose_charge_station()
    #             self.machine.seek_charge_queue()
    #             self.choose_cs_queue()
    #             # at this point EV has arrived at CS, joined one of the two queues and is waiting to become the active ev, and get charged.
    #             self.machine.join_charge_queue()
    #             self._in_queue = True

    #             # # experimental - limit queue size to limit defined in charge station
    #             # if (len(self._chosen_cs.queue_1) + len(self._chosen_cs.queue_2)) >= self._chosen_cs.queue_limit:
    #             #     print(f"EV {self.unique_id} has arrived at Charge Station but the queue is full. EV is not in queue.")
    #             #     self._in_queue = False
    #             # else:
    #             #     self.choose_cs_queue()
    #             #     self.machine.join_charge_queue()
    #             #     self._in_queue = True

    #     # Transition Case 3: EV with low battery does not arrive at charge station. Travel_low -> Battery_dead
    #     # condition self.battery < 10 because 10 is the minimum expenditure of energy to move the vehicle in one timestep
    #     if self.machine.state == 'Travel_low' and self.battery < 10:
    #         self.machine.deplete_battery()
    #         print(f"EV {self.unique_id} is now in state: {self.machine.state} and is out of charge.")

    #     # # old flow for recognising a charge station (CS), choosing a CS and charge queue.
    #     # # EV travelling or travelling low, checking for Charge Station at each checkpoint
    #     # if self.machine.state == 'Travel' and self.odometer in self.checkpoint_list:
    #     #     print(f"EV {self.unique_id} has arrived at Charge Station but is in state: {self.machine.state}. Not travelling low.")

    #     # if self.machine.state == 'Travel_low' and self.odometer in self.checkpoint_list:
    #     #     self._at_station = True
    #     #     print(f"EV {self.unique_id} is low on battery and is at a station. Seeking charge queue. Current EV state: {self.machine.state}")
    #     #     # self.select_cp()
    #     #     self.choose_charge_station()
    #     #     self.machine.seek_charge_queue()
    #     #     self.choose_cs_queue()
    #     #     self.machine.join_charge_queue()
    #     #     self._in_queue = True

    #     #     # # experimental - limit queue size to limit defined in charge station
    #     #     # if (len(self._chosen_cs.queue_1) == self._chosen_cs._max_queue_size) and (len(self._chosen_cs.queue_2) == self._chosen_cs._max_queue_size):
    #     #     #     print("Queue 1 and 2 are full. EV travelling under stress.")
    #     #     # self.machine.join_charge_queue()
    #     #     # # notification handled in charge station step method

        

        
        

    #     ############
    #     # Charging #
    #     ############

    #     # # Transition Case 6: Continue charging. Charge -> charge
    #     # if self.machine.state == 'Charge':
    #     #     self._at_station = True
    #     #     if self.battery >= self._soc_charging_thresh:
    #     #         print(f"Charge complete. EV {self.unique_id} is {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
    #     #         self.machine.end_charge()
    #     #         self._is_charging = False
    #     #         self._at_station = False
    #     #         self._chosen_cs.finish_charge_ev() #??? untested, may break things
    #     #     if self.battery < self._soc_charging_thresh:
    #     #         # self.machine.continue_charge() # this is a redundant state, but it's here for completeness. may be responsible for some of the re-charging in same timestep issues
    #     #         self._chosen_cs.charge_evs()
    #     #         # self._chosen_cs.charge_ev_1()
    #     #         self._is_charging = True
    #     #         print(f"Charging. EV {self.unique_id} is {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
        

    #     for ev in self.model.evs:
    #         if ev.machine.state == 'In_queue' and (ev == ev._chosen_cs.active_ev_1 or ev == ev._chosen_cs.active_ev_2):
    #             if ev.battery < ev._soc_charging_thresh:
    #                 try:
    #                     self.machine.start_charge()
    #                     self._chosen_cs.charge_evs()
    #                 except MachineError:
    #                     print(f"EV {self.unique_id} is in state: {self.machine.state}. Cannot start charging.")
    #         if ev.machine.state == 'Charge' and (ev == ev._chosen_cs.active_ev_1 or ev == ev._chosen_cs.active_ev_2):
    #             if ev.battery < ev._soc_charging_thresh:
    #                 self.machine.continue_charge()
    #                 self._chosen_cs.charge_evs()

    #                 # if this causes multiple charges in Timestep, move to separate elif block.
    #         if ev.machine.state == 'In_queue' and (ev != ev._chosen_cs.active_ev_1 or ev != ev._chosen_cs.active_ev_2):
    #             self.machine.wait_in_queue()
    #             print(f"EV {self.unique_id} is in state: {self.machine.state}. Waiting in queue.")

        

        
    #     # under work

    #     # # For chosen CS, if EV is active_ev at CS, start charging. If EV is not active_ev, wait in queue.
    #     # # Transition Case 5: Start charging. in_queue -> charge
    #     # if self.machine.state == 'In_queue' and self.ev == self._chosen_cs.active_ev:
    #     #     if self._chosen_cs.active_ev_1.battery >= self._chosen_cs.active_ev_1._soc_charging_thresh:
    #     #         print(f"Charge complete. EV {self.unique_id} is {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
    #     #         self._chosen_cs.active_ev_1.machine.end_charge()
    #     #         self._is_charging = False
    #     #         self._at_station = False
    #     #         self._chosen_cs.finish_charge_ev() #??? untested, may break things
    #     #     if self.battery < self._soc_charging_thresh:
    #     #         # self.machine.continue_charge() # this is a redundant state, but it's here for completeness. may be responsible for some of the re-charging in same timestep issues
    #     #         self._chosen_cs.charge_evs()
    #     #         # self._chosen_cs.charge_ev_1()
    #     #         self._is_charging = True
    #     #         print(f"Charging. EV {self.unique_id} is {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
    #     #     self.machine.start_charge()
    #     #     self._chosen_cs.charge_evs()
    #     #     # self._in_queue = False

    #     # # Transition Case 6: Continue charging. Charge -> charge
    #     # if self.machine.state == 'Charge':
    #     #     self._at_station = True
    #     #     if self.battery >= self._soc_charging_thresh:
    #     #         print(f"Charge complete. EV {self.unique_id} is {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
    #     #         self.machine.end_charge()
    #     #         self._is_charging = False
    #     #         self._at_station = False
    #     #         self._chosen_cs.finish_charge_ev() #??? untested, may break things
    #     #     if self.battery < self._soc_charging_thresh:
    #     #         # self.machine.continue_charge() # this is a redundant state, but it's here for completeness. may be responsible for some of the re-charging in same timestep issues
    #     #         self._chosen_cs.charge_evs()
    #     #         # self._chosen_cs.charge_ev_1()
    #     #         self._is_charging = True
    #     #         print(f"Charging. EV {self.unique_id} is {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
                
    #     # Transition Case 7: Journey Complete. travel -> idle
    #     if self.machine.state == 'Travel' and self.odometer >= self._distance_goal:
    #         self.machine.end_travel()
    #         print(f"EV {self.unique_id} has completed its journey. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")

    #     # Transition Case 8: Journey complete, battery low. travel_low -> idle
    #     if self.machine.state == 'Travel_low' and self.odometer >= self._distance_goal:
    #         self.machine.end_travel_low()
    #         print(f"EV {self.unique_id} has completed its journey. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
    





    #     # # Transition Case 5: Start charging. in_queue -> charge
    #     # if self.machine.state == 'In_queue':
    #     #     self.machine.start_charge()
    #     #     # self._in_queue = False

    #     # # Transition Case 6: Continue charging. Charge -> charge
    #     # if self.machine.state == 'Charge':
    #     #     self._at_station = True
    #     #     if self.battery >= self._soc_charging_thresh:
    #     #         print(f"Charge complete. EV {self.unique_id} is {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
    #     #         self.machine.end_charge()
    #     #         self._is_charging = False
    #     #         self._at_station = False
    #     #         self._chosen_cs.finish_charge_ev() #??? untested, may break things
    #     #     if self.battery < self._soc_charging_thresh:
    #     #         # self.machine.continue_charge() # this is a redundant state, but it's here for completeness. may be responsible for some of the re-charging in same timestep issues
    #     #         self._chosen_cs.charge_evs()
    #     #         # self._chosen_cs.charge_ev_1()
    #     #         self._is_charging = True
    #     #         print(f"Charging. EV {self.unique_id} is {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
                
    #     # # Transition Case 7: Journey Complete. travel -> idle
    #     # if self.machine.state == 'Travel' and self.odometer >= self._distance_goal:
    #     #     self.machine.end_travel()
    #     #     print(f"EV {self.unique_id} has completed its journey. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")

    #     # # Transition Case 8: Journey complete, battery low. travel_low -> idle
    #     # if self.machine.state == 'Travel_low' and self.odometer >= self._distance_goal:
    #     #     self.machine.end_travel_low()
    #     #     print(f"EV {self.unique_id} has completed its journey. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
    


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
        

        