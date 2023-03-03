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
from EV.statemachine import EVSM, LSM, states, transitions, lstates, ltransitions
# from EV.statemachine import EVSM, LSM

class ChargeStation(Agent):
    """A charging point agent.
    Attributes:
        unique_id: Unique identifier for the agent.
        model: The model the agent is running in.
        queue: A list of EVs waiting to charge at the CS.
        _is_charging: A boolean value indicating whether the CS is currently charging an EV.
        _active_ev: The EV currently charging at the CS.
        _charge_rate: The rate at which the CS charges an EV.
        _checkpoint_id: The ID of the checkpoint the CS is associated with. Initialised to 0.
        max_queue_size: The maximum number of EVs that can be queued at the CS.

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


        print(f"\nCP info: ID: {(self.unique_id)}, initialized. Charge rate: {self._charge_rate} kW.")

        # End initialisation

    def __str__(self) -> str:
        """Return the agent's unique id."""
        return str(self.unique_id + 1)
    
    
    def dequeue_1(self) -> None:
        """Remove the first EV from each queue. FIFO fom queue.
        If the queue is empty, do nothing. 
        If the queue is not empty, remove the first EV from the queue and set as active ev.
        Transition the EV to the charging state.

        """
        try:
            self.active_ev_1 = self.queue_1.pop(0)
            self.active_ev_1.machine.start_charge()
            print(f"EV {(self.active_ev_1.unique_id)} dequeued at CS {self.unique_id} at Queue 1 and is in state: {self.active_ev_1.machine.state}")
            print(f"Queue 1 size after dequeuing: {len(self.queue_1)}")
        except:
            pass
    
    def dequeue_2(self) -> None:
        """Remove the first EV from each queue. FIFO fom queue. 
        This is the same as dequeue_1, but for queue 2."""
        try:
            self.active_ev_2 = self.queue_2.pop(0)
            self.active_ev_2.machine.start_charge()
            print(f"EV {(self.active_ev_2.unique_id)} dequeued at CP {self.unique_id} at Queue 2 and is in state: {self.active_ev_2.machine.state}")
            print(f"Queue 2 size after dequeuing: {len(self.queue_2)}")
        except:
            pass
    
    def finish_charge_ev_1(self):
        """Finish charging the EV at CP1 at the Charge Station."""
        if self.active_ev_1 is not None:
            # self.active_ev_1.machine.end_charge() # this is a toggle
            self.active_ev_1 = None
            print(f"EV at Charge Station {self.unique_id}, CP 1 has exited.")

    def finish_charge_ev_2(self):
        """Finish charging the EV at CP2 at the Charge Station."""
        if self.active_ev_2 is not None:
            # self.active_ev_2.machine.end_charge() # this is another toggle
            self.active_ev_2 = None
            print(f"EV at Charge Station {self.unique_id}, CP 2 has exited.")

    def stage_1(self):
        """Stage 1 of the charge station's step function."""
        if self.active_ev_1 is None:
            self.dequeue_1()
        if self.active_ev_2 is None:
            self.dequeue_2()

    def stage_2(self):
        """Stage 2 of the charge station's step function."""
        if self.active_ev_1 is not None:
            if self.active_ev_1.battery < self.active_ev_1._soc_charging_thresh:
                self.active_ev_1.charge()
                self.active_ev_1.machine.continue_charge()
            else:    
                # print(f"EV {self.active_ev_2}, Pre-trans: {self.active_ev_1.machine.state}.")                                       #testing
                self.active_ev_1.machine.end_charge()
                self.finish_charge_ev_1()
        if self.active_ev_2 is not None:
            if self.active_ev_2.battery < self.active_ev_2._soc_charging_thresh:
                self.active_ev_2.charge()
                self.active_ev_2.machine.continue_charge()
            else:
                # print(f"EV {self.active_ev_2}, Pre-trans: {self.active_ev_2.machine.state}.")                                       #testing
                self.active_ev_2.machine.end_charge()
                self.finish_charge_ev_2()
                

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

    Methods:
        __init__: Initialise the EV agent.
        __str__: Return the agent's unique id.
        initialization_report: Print the agent's initial state.
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
        stage_1: Stage 1 of the EV's step function. Handles the EV's journey.
        stage_2: Stage 2 of the EV's step function. Handles the EV's charging.

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
        self.loc_machine = LSM(initial='City_D', states=lstates, transitions=ltransitions)
        self._is_active = True
        self.odometer = 0
        self._distance_goal = 0
        self.journey_type = None
        self.destination = None
        self.battery = random.randint(40, 70) #kWh
        self.max_battery = self.battery
        # EV Driver Behaviour
        self._speed = 0
        self.charge_prop = 0.4    #propensity to charge at main station 
        # battery soc level at which EV driver feels compelled to start charging at station.
        # self._soc_usage_thresh = (0.4 * self.max_battery) 
        self._soc_usage_thresh = (self.charge_prop * self.max_battery) 
        # battery soc level at which EV driver is comfortable with stopping charging at station.
        self._soc_charging_thresh = (0.8 * self.max_battery) 
        # Newest
        self.ev_consumption_rate = 0
        self.tick_energy_usage = 0
        self.battery_eod = []
        self.current_day_count = 1
        self.start_time = 0
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
        
        # set EV start time
        self.set_start_time()

        # Home Station 
        self.home_cs_rate = 20 #kW
        # self.home_charge_prop = 0.7    #propensity to charge at home

        # self._home_cs = ChargeStation(0, model)

        # Initialisation Report
        self.initalization_report()
    

    def __str__(self) -> str:
        """Return the agent's unique id as a string, not zero indexed."""
        return str(self.unique_id + 1)
    
    def initalization_report(self) -> None:
        """Prints the EV's initialisation report."""
        print(f"\nEV info: ID: {self.unique_id}, destination name: {self.destination}, journey type: {self.journey_type}, max_battery: {self.max_battery}, speed: {self._speed}, State: {self.machine.state}.")
        print(f"EV info (Cont'd): Start time: {self.start_time}, distance goal: {self._distance_goal}, energy consumption rate: {self.ev_consumption_rate}, charge prop {self.charge_prop}, location: {self.loc_machine.state}.")

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
        return self.destination

    def choose_destination_urban(self) -> None:
        """Chooses a destination for the EV driver. Urban destination from destinations distances dictionary.
        Returns:     
            destination: Choice of destination for the EV driver. (implicit)
            distance_goal: Distance goal for the EV driver. (implicit)
            
        """

        # Option 2: use values directly to determine destination
        # destinations_distances = {'work': 50, 'market': 80, 'friend_1': 45, 'friend_2': 135, 'autoshop': 70} #miles. Initial
        destinations_distances = {'work': 50, 'market': 40, 'friend_1': 30, 'friend_2': 90, 'autoshop': 60} #miles. Updated
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
        destinations_distances = {'City A': 120, 'City B': 80, 'City C': 150} # miles. Updated
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
    
    def dead_intervention(self) -> None:
        """
        Intervention for when the EV runs out of battery. 
        The EV will be recharged to maximum by emergency services and will be transported to its destination.
        """
        self.battery = self.max_battery
        # self.odometer = self._distance_goal
        self.increase_charge_prop()
        self.machine.emergency_intervention()
        # self.locationmachine.set_state("At_destination")
        print(f"\nEV {self.unique_id} has been recharged to {self.battery} by emergency services and is now in state: {self.machine.state}. Charge prop: {self.charge_prop}")

    
    def set_start_time(self) -> None:
        """Sets the start time for the EV to travel. 
        Sets start time based on distance goal - if distance goal is greater than or equal to 90 miles, start time is earlier
        """
        # self.start_time = random.randint(6, 12)

        if self._distance_goal < 90:
            self.start_time = random.randint(10, 14)

        elif self._distance_goal >= 90:
            self.start_time = random.randint(6, 9)
    
    # Dynamic propensity for charging behavior
    def increase_charge_prop(self) -> None:
        margin = 0.1
        self.charge_prop += margin

    def decrease_charge_prop(self) -> None:
        margin = 0.1
        self.charge_prop -= margin
  
    # Core EV Functions
    def travel(self) -> None:
        """Travel function. Moves EV along the road. Updates odometer and battery level."""
        self.odometer += self._speed
        self.battery -= self.energy_usage_tick()
        print(f"EV {self.unique_id} is travelling. Odometer: {self.odometer}, Battery: {self.battery}")
    
    def charge(self):
        """Charge the EV at the Charge Station. The EV is charged at the Charge Station's charge rate."""
        self.battery += self._chosen_cs._charge_rate
        print(f"EV {self.unique_id} at CS {self._chosen_cs.unique_id} is in state: {self.machine.state}, Battery: {self.battery}")

    def charge_overnight(self):
        """Charge the EV at the Home Charge Station, at the Home Charge Station's charge rate."""
        # self.machine.set_state("Charging")
        self.machine.start_home_charge()
        if self.battery < self._soc_charging_thresh:
            self.battery += self.home_cs_rate
            print(f"EV {self.unique_id} at Home CS. state: {self.machine.state}, Battery: {self.battery}")
        else:
            self.machine.end_home_charge()
            print(f"EV {self.unique_id} at Home CS. state: {self.machine.state}, Battery: {self.battery}")
    
   # 16 Feb charge flow redo - new methods
    def choose_charge_station(self):
        """
        Chooses a charge station to charge at. 
        Selects the charge station with the correct checkpoint id.
        """
        # choose station
        for cs in self.model.chargestations:
            if cs._checkpoint_id == self.odometer:
                self._chosen_cs = cs
                self._chosen_cs._is_active = True
        print(f"EV {(self.unique_id)} selected Charge Station: {(self._chosen_cs.unique_id)} for charging.")

    # new select queue for charging
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
        
  
    # Model env functions
    def add_soc_eod(self) -> None:
        """Adds the battery level at the end of the day to a list."""
        self.battery_eod.append(self.battery)
        print(f"EV {self.unique_id} Battery level at end of day: {self.battery_eod[-1]}")
    
    
    def finish_day(self) -> None:
        """Finishes the day. Sets the battery level to the end of day level from previous day, for the new day.
        Increments day_count and resets the odometer to 0.
        """
        # self.battery = self.battery_eod[-1]
        self.current_day_count += 1
        self.odometer = 0
    
    def relaunch_base(self,n) -> None:
        """
        Relaunches the EV at the end of the day.
        Choose a new journey type and destination.
        """
        self.set_start_time() #???
        # self.start_time = self.model._current_tick - (n * 24) # use model.schedule.time?
        # self.start_time += self.model._current_tick - (n * 24)
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

    def relaunch_dead(self) -> None:
        self.dead_intervention()
        self.relaunch_base(n = self.model.current_day_count)

    def relaunch_idle(self) -> None:
        # if self.machine.state == "Idle":
        #     self.relaunch_base(self,n)
        # elif self.machine.state != "Idle":
        #     print(f"EV {self.unique_id} is not in Idle state. Cannot relaunch for new day.")
        self.relaunch_base(n = self.model.current_day_count)
    def start_travel(self) -> None:
        if self.model.schedule.time == self.start_time:
            self.machine.start_travel()
            # print(f"EV {self.unique_id} has started travelling at {self.model.schedule.time}")
            print(f"EV {self.unique_id} started travelling at {self.start_time} and is in state: {self.machine.state}")
    
    
    # def update_home_charge_prop(self, new_prop):
    #     self.home_charge_prop = new_prop

    

    # def update_soc_usage_thresh(self):
    #     new_thresh = self.max_battery * self.charge_prop
    #     self._soc_usage_thresh = new_thresh

    # staged step functions
    def stage_1(self):
        """Stage 1: EV travels until it reaches the distance goal or runs out of battery. 
        If it needs to charge during the journey, it will transition to Stage 2.
        """

        # Transition Case 1: Start travelling. idle -> travel
        # Depending on start time, EV will start travelling, transitioning from Idle to Travel.
        if self.machine.state == 'Battery_dead':
            pass
        else:
            self.start_travel() 

        # # approach 2
        # try:
        #     self.start_travel()
        # except:
        #     MachineError
    
        # Transition Case 2: Still travelling, battery low. Travel -> travel_low  
        if self.machine.state == 'Travel' and self.battery <= self._soc_usage_thresh:
            self.machine.get_low()
            # print(f"EV: {self.unique_id} has travelled: {str(self.odometer)} miles and is now {self.machine.state}. Current charge level is: {self.battery} kwh")

        # 21/02/23 - new flow for locating a station. Combo of 1b and 4
        # Locating a Charge Station #

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

        
        # 21/02/23 - new flow for recognising a charge station (CS). Also, choosing a CS and charge queue.
        # Recognising a Charge Station #
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
                # Here, EV has arrived at CS, joined one of the two queues and is waiting to become the active ev, and get charged.
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
            self._in_garage = True
            self._journey_complete = False
            print(f"EV {self.unique_id} has completed its journey. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")

        # Transition Case 8: Journey complete, battery low. travel_low -> idle
        if self.machine.state == 'Travel_low' and self.odometer >= self._distance_goal:
            self.machine.end_travel_low()
            print(f"EV {self.unique_id} has completed its journey. State: {self.machine.state}. This EV has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
    
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

        