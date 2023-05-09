# Visualizing the state machines

# EVSM

class TModel():
    def clear_state(self, deep=False, force=False):
        print("Clearing State ... ")
        return True

model = TModel()
machine = GraphMachine(model=model, states=['Idle', 'Travel', 'Seek_queue', 'In_queue', 'Charge', 'Travel_low', 'Battery_dead', 'Home_charge'],
                        transitions= [
                        {'trigger': 'start_home_charge', 'source': 'Idle', 'dest': 'Home_charge'},
                        {'trigger': 'continue_home_charge', 'source': 'Home_charge', 'dest': 'Home_charge'},
                        {'trigger': 'end_home_charge', 'source': 'Home_charge', 'dest': 'Idle'},
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
               states=['A', 'B', 'C', 'D'], 
               transitions=[
                            {'trigger': 'city_a_2_b', 'source': 'A', 'dest': 'B'},
                            {'trigger': 'city_a_2_c', 'source': 'A', 'dest': 'C'},
                            {'trigger': 'city_a_2_d', 'source': 'A', 'dest': 'D'},
                            {'trigger': 'city_b_2_a', 'source': 'B', 'dest': 'A'},
                            {'trigger': 'city_b_2_c', 'source': 'B', 'dest': 'C'},
                            {'trigger': 'city_b_2_d', 'source': 'B', 'dest': 'D'},
                            {'trigger': 'city_c_2_a', 'source': 'C', 'dest': 'A'},
                            {'trigger': 'city_c_2_b', 'source': 'C', 'dest': 'B'},
                            {'trigger': 'city_c_2_d', 'source': 'C', 'dest': 'D'},
                            {'trigger': 'city_d_2_a', 'source': 'D', 'dest': 'A'},
                            {'trigger': 'city_d_2_b', 'source': 'D', 'dest': 'B'},
                            {'trigger': 'city_d_2_c', 'source': 'D', 'dest': 'C'},
               ], 
               initial='City_A', 
               show_conditions=True)

# Render the state machine as a graph. Requires pygraphviz and graphviz to be installed.
# model2.get_graph().draw('EV_location_state_diagram_v2.png', prog = 'dot')