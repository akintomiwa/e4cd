from random import choice
import warnings
from transitions import Machine
from transitions.extensions import GraphMachine

"""State machines for managing status and city-level location of EV agent in AB model."""


class EVSM(Machine):
    """A state machine for managing status of EV agent in AB model.
    Can be deployed as EvState object.

    States:
    Idle, Travel, Seek_queue, Travel_low, In_queue, Charge, Travel_low, Battery_dead, Home_Charge
    Transitions:
    start_travel: Idle -> Travel
    get_low: Travel -> Travel_low
    seek_charge_queue: Travel_low -> Seek_queue
    deplete_battery: Travel_low -> Battery_dead
    join_charge_queue: Seek_queue -> In_queue
    wait_in_queue: In_queue -> In_queue
    start_charge: In Queue -> Charge
    end_charge: Charge -> Travel
    continue_travel: Travel -> Travel
    continue_charge: Charge -> Charge
    end_travel: Travel -> Idle
    end_travel_low: Travel_low -> Idle
    end_charge_abrupt: Charge -> Idle
    end_queue_abrupt: In_queue -> Idle
    end_seek_abrupt: Seek_queue -> Idle

    """

states = ['Idle', 'Travel', 'Seek_queue', 'In_queue', 'Charge', 'Travel_low', 'Battery_dead', 'Home_Charge']
transitions = [
    {'trigger': 'start_home_charge', 'source': 'Idle', 'dest': 'Home_Charge'},
    {'trigger': 'end_home_charge', 'source': 'Home_Charge', 'dest': 'Idle'},
    {'trigger': 'start_travel', 'source': 'Idle', 'dest': 'Travel'},
    {'trigger': 'get_low', 'source': 'Travel', 'dest': 'Travel_low'},
    {'trigger': 'seek_charge_queue', 'source': 'Travel_low', 'dest': 'Seek_queue'},
    {'trigger': 'deplete_battery', 'source': 'Travel_low', 'dest': 'Battery_dead'},
    {'trigger': 'join_charge_queue', 'source': 'Seek_queue', 'dest': 'In_queue'},
    {'trigger': 'wait_in_queue', 'source': 'In_queue', 'dest': 'In_queue'},
    {'trigger': 'start_charge', 'source': 'In_queue', 'dest': 'Charge'},
    {'trigger': 'continue_charge', 'source': 'Charge', 'dest': 'Charge'},
    {'trigger': 'end_charge', 'source': 'Charge', 'dest': 'Travel'},
    {'trigger': 'continue_travel', 'source': 'Travel', 'dest': 'Travel'},
    {'trigger': 'end_travel', 'source': 'Travel', 'dest': 'Idle'},
    {'trigger': 'end_travel_low', 'source': 'Travel_low', 'dest': 'Idle'},
    {'trigger': 'emergency_intervention', 'source': 'Battery_dead', 'dest': 'Idle'},
    {'trigger': 'end_charge_abrupt', 'source': 'Charge', 'dest': 'Idle'},
    {'trigger': 'end_queue_abrupt', 'source': 'In_queue', 'dest': 'Idle'},
    {'trigger': 'end_seek_abrupt', 'source': 'Seek_queue', 'dest': 'Idle'},
    ]


class LSM(Machine):
    """A state machine for managing location status of EV agent in AB model.
    
    States: City_A, City_B, City_C, City_D
    Transitions:
    city_d_2_a: City_D -> City_A
    city_d_2_b: City_D -> City_B
    city_d_2_c: City_D -> City_C
    
    """

lstates = ['City_A', 'City_B', 'City_C', 'City_D']
ltransitions = [
    {'trigger': 'city_d_2_a', 'source': 'City_D', 'dest': 'City_A'},
    {'trigger': 'city_d_2_b', 'source': 'City_D', 'dest': 'City_B'},
    {'trigger': 'city_d_2_c', 'source': 'City_D', 'dest': 'City_C'},
    {'trigger': 'city_d_2_d', 'source': 'City_D', 'dest': 'City_D'},  
    ]

# Visualizing the state machines

# EVSM

class TModel():
    def clear_state(self, deep=False, force=False):
        print("Clearing State ... ")
        return True

model = TModel()
machine = GraphMachine(model=model, states=['Idle', 'Travel', 'Seek_queue', 'In_queue', 'Charge', 'Travel_low', 'Battery_dead', 'Home_Charge'],
                        transitions= [
                        {'trigger': 'start_home_charge', 'source': 'Idle', 'dest': 'Home_Charge'},
                        {'trigger': 'end_home_charge', 'source': 'Home_Charge', 'dest': 'Idle'},
                        {'trigger': 'start_travel', 'source': 'Idle', 'dest': 'Travel'},
                        {'trigger': 'get_low', 'source': 'Travel', 'dest': 'Travel_low'},
                        {'trigger': 'seek_charge_queue', 'source': 'Travel_low', 'dest': 'Seek_queue'},
                        {'trigger': 'deplete_battery', 'source': 'Travel_low', 'dest': 'Battery_dead'},
                        {'trigger': 'join_charge_queue', 'source': 'Seek_queue', 'dest': 'In_queue'},
                        {'trigger': 'start_charge', 'source': 'In_queue', 'dest': 'Charge'},
                        {'trigger': 'wait_in_queue', 'source': 'In_queue', 'dest': 'In_queue'},
                        {'trigger': 'continue_charge', 'source': 'Charge', 'dest': 'Charge'},
                        {'trigger': 'end_charge', 'source': 'Charge', 'dest': 'Travel'},
                        {'trigger': 'continue_travel', 'source': 'Travel', 'dest': 'Travel'},
                        {'trigger': 'end_travel', 'source': 'Travel', 'dest': 'Idle'},
                        {'trigger': 'end_travel_low', 'source': 'Travel_low', 'dest': 'Idle'},
                        {'trigger': 'emergency_intervention', 'source': 'Battery_dead', 'dest': 'Idle'},
                        {'trigger': 'end_charge_abrupt', 'source': 'Charge', 'dest': 'Idle'},
                        {'trigger': 'end_queue_abrupt', 'source': 'In_queue', 'dest': 'Idle'},
                        {'trigger': 'end_seek_abrupt', 'source': 'Seek_queue', 'dest': 'Idle'},
                        ], 
                        initial = 'Idle', show_conditions=True)

# Render the state machine as a graph. Requires pygraphviz and graphviz to be installed.
# model.get_graph().draw('EV_state_diagram_v2.png', prog = 'dot')

class LModel():
    def clear_state(self, deep=False, force=False):
        print("Clearing State ... ")
        return True

model2 = LModel()

machine2 = GraphMachine(model=model2, 
               states=['City_A', 'City_B', 'City_C', 'City_D'], 
               transitions=[
                           {'trigger': 'city_d_2_a', 'source': 'City_D', 'dest': 'City_A'},
                            {'trigger': 'city_d_2_b', 'source': 'City_D', 'dest': 'City_B'},
                            {'trigger': 'city_d_2_c', 'source': 'City_D', 'dest': 'City_C'},
                            {'trigger': 'city_d_2_d', 'source': 'City_D', 'dest': 'City_D'},

               ], 
               initial='City_D', 
               show_conditions=True)

# Render the state machine as a graph. Requires pygraphviz and graphviz to be installed.
# model2.get_graph().draw('EV_location_state_diagram_v2.png', prog = 'dot')