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
from mesa.time import RandomActivation, RandomActivationByType ,SimultaneousActivation
from mesa.datacollection import DataCollector
from matplotlib import pyplot as plt, patches
import scipy.stats as ss
import cufflinks as cf
cf.go_offline()
from plotly.offline import iplot
from statemachine import StateMachine, State
from transitions import Machine
import random


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
        self._distance_goal = None
        self.journey_type = None
        # External 
        self._journey_choice = choice([True, False]) #True = Urban, False = Highway
        self.battery = random.randint(40, 70) #kWh
        self.max_battery = self.battery
        self._soc_usage_thresh = (0.3 * self.max_battery) # battery soc level at which EV driver is comfortable with starting charging at station.
        self._soc_charging_thresh = (0.8 * self.max_battery) # battery soc level at which EV driver is comfortable with stopping charging at station.
        self._chosen_cpoint = None # unused Fix in v.0.2
        # Newest
        self.tick_energy_usage = 0
        self.battery_eod = []
        self.day_count = 0

        # set distance_goal #Hardcoded for now
        if self._journey_choice == True:
            self._distance_goal = 100 #miles
            self.journey_type = "Urban"
        else:
            self._distance_goal = 200 #miles
            self.journey_type = "InterUrban"
        # set speed
        self._speed = 0
        self.base_speed = 10 #urban speed (mph). Interurban speed is scaled by 2.
        if self.journey_type == "Urban":
            self._speed = self.base_speed
        else:
            self._speed = (self.base_speed * 2) #interurban speed (mph). 
        # set vehicle energy consumption rate
        if self.journey_type == "Urban":
            self.ev_consumption_rate = 0.2 # 200 Wh/mile OR 20 kWh/100 miles OR 0.2 kWh/mile
        else:
            self.ev_consumption_rate = 0.5 # 500 Wh/mile OR 50 kWh/100 miles
        
        self._chosen_cp_idx = 0 #in selected_cp
        self._chosen_cp = 0 #in selected_cp correct

        #

        print("EV No " + str(self.unique_id + 1) + " initialized. Journey type: " + str(self.journey_type) +
        ". Vehicle State: " + str(self.machine.state) )

        print(f"EV info: ID: {self.unique_id}, distance goal: {self._distance_goal}, max_battery: {self.max_battery}, speed: {self._speed}, energy consumption rate {self.ev_consumption_rate}")
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
    def energy_usage_trip(self):
        """Energy consumption for the entire trip (EC). EC from distance covered"""
        usage = (self.ev_consumption_rate * self.odometer)
        return usage

    def energy_usage_tick(self):
        """Energy consumption for each tick (EC). EC from distance covered"""
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
    def check_for_cp(self):
        """Checks for a free CP in the vicinity. If found, calls select_cp."""
        for agent in self.model.schedule.agents:
            if type(Agent) == Cpoint:
                return agent.free_cp
    # unused function
    def takeCP(self):
        """Signifies that CP is taken and charging begins."""
        for agent in self.model.schedule.agents:
            if type(agent) == Cpoint:
                agent.free_cp = False
                print("Vehicle " + str(self.unique_id + 1 ) + " is charging at " + str(agent))
                return agent.free_cp
    # unused function
    def select_cp(self):
        """Selects a CP to charge at. Chooses the CP with the shortest queue."""
        self._in_queue = True
        # queue at shortest cp
        self._chosen_cp_idx = np.argmin([len(cpoint.queue) for cpoint in self.model.cpoints])
        print("No of active Cpoints: " + str(self.model.cpoints.count(self)))
        self._chosen_cp = self.model.cpoints[self._chosen_cp_idx]
        print("Vehicle " + str(self.unique_id + 1 ) + " selected: " + str(self._chosen_cp) + " for charging.")


    def add_soc_eod(self):
        """Adds the battery level at the end of the day to a list."""
        # eod_battery = self.battery
        self.battery_eod.append(self.battery)
        # return
    
    def set_new_day(self):
        """Resets the battery level to the end of day level from previous day, for the new day."""
        self.battery = self.battery_eod.pop()
        self.day_count += 1
        self.odometer = 0
    
    def charge_simple(self):
        """Simple charging function. Charges the EV according to the charge rate."""
        # flags
        self._is_charging = True
        self.battery += self._charge_rate
        print("Vehicle " + str(self.unique_id + 1 ) + " charged status: " + str(self._was_charged)+ ". CLevel: " + str(self.battery))
        self._was_charged = True
                
    # def charge_main(self):                                                                                            # For V 0.2
    #     self._is_charging = True
    #     self._was_charged = True
    #     self._chosen_cp.active_car = None
    #     self.soc += self._charge_rate
    #     # self._is_charging = False
    #     
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
            self.machine.join_charge_queue() #travel_low -> in_queue
            # self.checkForCP()
            # self.select_cp()
            print("Current EV state: " + str(self.machine.state))
            # print("Vehicle " + str(self.unique_id) + " is at CP with id: " + str(self._chosen_cpoint.unique_id) + " . CLevel: " + str(self.battery))

        # Transition Case 4: Start charging. In_queue -> charge
        if self.machine.state == 'In_queue':
            if self.battery < self._soc_charging_thresh:
                self.machine.start_charge()
                self.charge_simple()
                # instead, join queue, select cp, then start charge
            else:
                self.machine.end_charge()
        # Transition Case 5: Continue charging. Charge -> charge
        if self.machine.state == 'Charge':
            if self.battery >= self._soc_charging_thresh:
                print("Charge complete. Vehicle " + str(self.unique_id + 1) + " is now " + str(self.machine.state) + "d.")
                self.machine.end_charge()
            else:
                self.machine.continue_charge()
                self.charge_simple()
        # # Transition Case 6: Journey Complete. travel -> idle
        if self.machine.state == 'Travel' and self.odometer >= self._distance_goal:
            self.machine.end_travel()
            print("Current EV state: " + str(self.machine.state))
            print("Vehicle " + str(self.unique_id + 1) + " has completed its journey and is now " + str(self.machine.state))
        # Transition Case 7: Jouney Complete. travel_low -> idle. JIT                                                       # For V 0.2
        
        # Record EV battery soc at the end of every 23 steps
        # Reinitialise agent variables for next day
        if (model.schedule.steps + 1) % 24 == 0:
            print("This is the end of day: " + str((model.schedule.steps + 1) / 24))
            self.add_soc_eod()
            self.set_new_day()


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
        self.queue = []
        self._is_charging = True
        self.active_ev = None
        # self._charge_rate = choice([7, 15, 100, 300]) #different charge rates
        self._charge_rate = 7
        print("CP No " + str(self.unique_id) + " initialized. Charge rate: " + str(self._charge_rate) + "kW" +
        ". Charge State: " + str(self._is_charging))
    def __str__(self):
        """Return the agent's unique id."""
        return ("CP No: " + str(self.unique_id))
    
    def join_queue(self, ev):
        """Add an EV to the CP's queue."""
        self.queue.append(ev)
        print("EV " + str(ev.unique_id + 1) + " joined queue at CP " + str(self.unique_id))

    def dequeue(self):
        """Remove the first EV from the queue. FIFO fom queue."""
        try:
            self.active_ev = self.queue.pop(0)
            print("Current EV " + str(self.active_ev) + " dequeued")
            # self.active_ev = model.queue.pop(0)
            # self.active_ev.machine.state == 'Charge'
            # print("Current EV at CP is in state: " + str(self.active_ev.machine.state))
        except:
            pass
    def charge_ev(self):
        """Charge the EV at the CP.
        The EV is charged at the CP's charge rate.
        """
        # EV.battery += self._charge_rate
        if self.active_ev is not None:
            self.active_ev.battery += self._charge_rate
            self.active_ev.machine.state == 'Charge'
            print("Current EV at CP is in state: " + str(self.active_ev.machine.state))
            # print("Vehicle " + str(self.active_ev.unique_id + 1 ) + " was charged status: " + str(self._was_charged)+ ". CLevel: " + str(self.active_ev.battery))

    def step(self):
        for ev in model.evs:
            if ev.machine.state == 'In_queue':
                self.join_queue(ev)
        # Transition Case 4: Start charging. In_queue -> charge
        if self.active_ev is None:
            self.dequeue()
        else:
            self.charge_ev()