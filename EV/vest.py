# 02-04-2023
  
# self.home_charge_prop = 0.7    #propensity to charge at home station


# 31-03-2023

# make multiple list attributes for each CS, depending on cp count per CS

# Focus 
# Assign charge rates to CS as list of values from config file.
# for cs in self.chargestations:
#     cs.cp_rates = worker.remove_list_item_seq(worker.get_dict_values(worker.get_power_values_for_route(self.params, cs.route)))
#     # Display Charge stations and their routes  
#     print(f"CS {cs.unique_id}, Route: {cs.route}, CheckpointID: {cs.checkpoint_id} kilometres on route {cs.route}. Number of charge points: {cs.no_cps}. CP rates: {cs.cp_rates} ") 
#     # dynamically create chargepoints per charge station lists vars. Each element is charge rate for each cp.
#     for i in range(cs.no_cps):
#         setattr(cs, f"cp_{i}", [])

# section 5 
# # dynamically create chargepoints per charge station lists vars. Each element is charge rate for each cp.
# for cs in self.chargestations:
#     for i in range(cs.no_cps):
#         setattr(cs, f"cp_{i}", [])


# def nest_charging_stations(csv_file):
#     nested_dict = {}
    
#     with open(csv_file, newline='') as csvfile:
#         reader = csv.DictReader(csvfile)
        
#         for row in reader:
#             route = row['Route']
#             station = row['Station']
#             cpid = row['CPID']
#             power = int(row['Power'])
#             distance = int(row['Distance'])
#             price = float(row['Price'])
#             green = bool(int(row['Green']))
#             booking = bool(int(row['Booking']))
            
#             if route not in nested_dict:
#                 nested_dict[route] = {}
                
#             if station not in nested_dict[route]:
#                 nested_dict[route][station] = {}
                
#             nested_dict[route][station]['CPID'] = cpid
#             nested_dict[route][station]['Power'] = power
#             nested_dict[route][station]['Distance'] = distance
#             nested_dict[route][station]['Price'] = price
#             nested_dict[route][station]['Green'] = green
#             nested_dict[route][station]['Booking'] = booking
            
#     return nested_dict 



# test ???
    # if hasattr(self, f"checkpoint_id"):
    #     print("attr set")

# old architecture

# # self.cpspcs = worker.get_cs_cp_count() #list
# self.cpspcs_AB = worker.get_dict_values(worker.count_charge_points_by_station(self.params, 'A-B'))  
# self.cpspcs_AC = worker.get_dict_values(worker.count_charge_points_by_station(self.params, 'A-C')) 
# # self.chargepoints = []
# print(f"Number of CPs per CS, Route A-B: {self.cpspcs_AB}")
# print(f"Number of CPs per CS, Route A-C: {self.cpspcs_AC}")





# CS 
# loop to set up chargepoints for chargestations from input dictionary
# loop to set up route_id, route_name, distance, total_route_length = distance goal



# ############################################################################################################


# class EVModel(Model):
#     """Simulation Model with EV agents and Charging Points agents.
    
#     Args:
#         no_evs (int): Number of EV agents to create.
#         no_css (int): Number of Charging Point agents to create.
#         ticks (int): Number of ticks to run the simulation for.
        
#     Attributes: 
#         ticks (int): Number of ticks to run the simulation for.
#         _current_tick (int): Current tick of the simulation.
#         no_evs (int): Number of EV agents to create.
#         no_css (int): Number of Charging Point agents to create.
#         schedule (RandomActivation): Schedule for the model.
#         evs (list): List of EV agents.
#         chargestations (list): List of Charging Point agents.
            
#     """
  
#     def __init__(self, no_evs, no_css, ticks, cp_count) -> None:
#         """
#         Initialise the model.
        
#         Args:
#             no_evs (int): Number of EV agents to create.
#             no_css (int): Number of Charging Point agents to create.
#             ticks (int): Number of ticks to run the simulation for.

#         """
#         super().__init__()
#         # init with input args
#         self.running = True
#         self.random = True
#         self.ticks = ticks
#         self._current_tick = 1
#         self.no_evs = no_evs
#         self.no_css = no_css
#         # self.checkpoints = [40, 80, 120, 160, 200, 240, 280]
#         self.checkpoints = self.compute_checkpoints(self.no_css+1) #+1 to ensure no overruns.
#         self.current_day_count = 0
#         self.max_days = 0
#         self.set_max_days()
#         # other key model attr 
#         # self.schedule = mesa.time.RandomActivation(self)
#         self.schedule = mesa.time.StagedActivation(self, shuffle=False, shuffle_between_stages=False, stage_list=['stage_1','stage_2'])
#         # self.schedule = SimultaneousActivation(self)
#         # self.schedule = RandomActivationByType(self) #requires addional args in model.step()
#         # Populate model with agents
#         self.evs = []
#         self.chargestations = []
        
#         # Setup
#         # evs
#         for i in range(self.no_evs):
#             ev = EV(i,self)
#             self.schedule.add(ev)
#             self.evs.append(ev)
#         # charging points
#         for i in range(self.no_css):
#             # cs = ChargeStation(i + no_evs, self)
#             cs = ChargeStation(i + no_evs, self, cp_count)
#             # for i in range(self.cp_count):
#                 # cs.cp(i) = None
#             self.schedule.add(cs)
#             self.chargestations.append(cs)
#         # assign checkpoints to charging points
#         for  i, cs in enumerate(self.chargestations):
#             cs._checkpoint_id = self.checkpoints[i]        
#         # display Charge stations and their checkpoints
#         print(f"\nNumber of Charging Stations: {len(self.chargestations)}")
#         for cs in self.chargestations:
#             print(f"Charging Station: {cs.unique_id} is at checkpoint: {cs._checkpoint_id} kilometers.")
#         # data collector
#         self.datacollector = DataCollector(
#             model_reporters={'EVs Charging': get_evs_charge,
#                              'EVs Activated': get_evs_active,
#                              'EVs Travelling': get_evs_travel,
#                              'EVs Queued': get_evs_queue,
#                              'EVs Dead': get_evs_dead,
#                              'EVs Charge Level': get_evs_charge_level,
#                              'EVs Range Anxiety': get_evs_range_anxiety,
#                              'EVs Not Idle': get_evs_not_idle,
#                              'EVs EOD Battery SOC': get_eod_evs_socs,
#                              'EVs Destinations': get_evs_destinations,
#                              'EVs at Charging Station - S': get_evs_at_station_state,
#                             #  'Length of Queue 1 at Charging Stations': get_queue_1_length,
#                             #  'Length of Queue 2 at Charging Stations': get_queue_2_length,
#                              'Length of Queue at Charging Stations': get_queue_length,
#                              'EVs at Charging Stations': get_evs_at_cstation,
#                              },
#             # agent_reporters={'Battery': 'battery',
#             #                 'Battery EOD': 'battery_eod',
#             #                 'Destination': 'destination',
#             #                 'State': 'state',
#             #                 }
#                              )
#         print(f"\nModel initialised. {self.no_evs} EVs and {self.no_css} Charging Points. Simulation will run for {self.ticks} ticks or {self.max_days} days.\n")
#         # print(f"Charging station checkpoints: {self.checkpoints}")
    
#     # def compute_ev_start_time(self, ev) -> int:
#     #     """Compute the start time for the EV agent."""
#     #     start_time = np.random.randint(5, 7)
#     #     return start_time
        

#     def compute_checkpoints(self,n) -> list:
#         """Compute the checkpoints for the simulation.
#         Args:
#             n (int): Number of charging points.
        
#         Returns:
#             checkpoints (list): List of checkpoints.
#         """
#         start = 40
#         # steps = n
#         interval = 40
#         checkpoints = np.arange(start, interval * n , interval)
#         return checkpoints
    
#     def model_finish_day(self) -> None: 
#         """
#         Reset the EVs at the end of the day. Calls the EV.add_soc_eod() and EV.finish_day() methods.
#         """
#         for ev in self.evs:
#             ev.add_soc_eod()
#             ev.finish_day()

#     def update_day_count(self) -> None:
#         """Increments the day count of the simulation. Called at the end of each day."""
#         self.current_day_count += 1
#         print(f"\nCurrent day: {self.current_day_count}.")

#     def set_max_days(self) -> None:
#         """Set the max number of days for the simulation."""
#         self.max_days = self.ticks / 24
#         # print(f"Max days: {self.max_days}")

#     def ev_relaunch(self) -> None:
#         """
#         Relaunches EVs that are dead or idle at the end of the day. Ignores EVs that are charging or travelling.
#         """
#         for ev in self.evs:
#             if ev.machine.state == 'Battery_dead':
#                 ev.relaunch_dead()
#             elif ev.machine.state == 'Idle':
#                 ev.relaunch_idle()
#             elif ev.machine.state == 'Travel':
#                 ev.relaunch_travel()
#             elif ev.machine.state == 'Charging':
#                 ev.relaunch_charge()
#                 pass
#             # ev.update_home_charge_prop()
    
#     def overnight_charge_evs(self) -> None:
#         """Calls the EV.charge_overnight() method for all EVs in the model."""
#         for ev in self.evs:
#             ev.charge_overnight()

#     # def step(self, shuffle_types = True, shuffle_agents = True) -> None:
#     def step(self) -> None:
#         """Advance model one step in time"""
#         print(f"\nCurrent timestep (tick): {self._current_tick}.")
#         # print("Active Css: " + str(get_active_css(self)))
#         # print(self.get_agent_count(self))
#         self.schedule.step()
        
#         # old code
#         # if self.schedule.steps % 24 == 0:
#         #     # print(f"This is the end of day:{(self.schedule.steps + 1) / 24} ")
#         #     print(f"This is the end of day: {self.schedule.steps / 24}. ")
#         #     for ev in self.evs:
#         #         ev.add_soc_eod()
#         #         ev.choose_journey_type()
#         #         ev.choose_destination(ev.journey_type)
#         #         ev.set_new_day()
#         self.datacollector.collect(self)

#         # if self.schedule.steps % 24 == 0:
#         if self._current_tick % 24 == 0:
#             # print(f"This is the end of day:{(self.schedule.steps + 1) / 24} ")
#             self.model_finish_day()
#             self.update_day_count()
#             # print(f"This is the end of day: {self.schedule.steps / 24}. Or {self.current_day_count} ")
#             print(f"This is the end of day: {self.current_day_count} ")
#         self._current_tick += 1

#         # soft reset at beginning of day
#         if self._current_tick > 24 and self._current_tick % 24 == 1:
#             try: 
#                 self.ev_relaunch() #current no of days
#             except MachineError:
#                 print("Error in relaunching EVs. EV is in a state other than Idle or Battery_Dead.")
#             # else:
#             #     print("Some other error.")
        
#         # overnight charging. integraition with relaunch??
#         # # overnight charging. Every day at 02:00
#         # if self._current_tick > 24 and self._current_tick % 24 == 2:
#         #     self.overnight_charge_evs()

# class ChargeStation(Agent):
#     """A charging station (CS) agent.
#     Attributes:
#         unique_id: Unique identifier for the agent.
#         model: The model the agent is running in.
#         queue_1: A list of EVs waiting to charge at the CS.
#         queue_2: A list of EVs waiting to charge at the CS.
#         _active_ev_1: The first EV currently charging at the CS.
#         _active_ev_2: The second EV currently charging at the CS.
#         _charge_rate: The rate at which the CS charges an EV.
#         _checkpoint_id: The ID of the checkpoint the CS is associated with. Initialised to 0.
#         max_queue_size: The maximum number of EVs that can be queued at the CS.

#     Methods:
#         __init__: Initialises the agent.
#         __str__: Returns the agent's unique id.
#         dequeue_1: Removes the first EV from queue_1.
#         dequeue_2: Removes the first EV from queue_2.
#         finish_charge_ev_1: Finish charging the EV at CP1 at the Charge Station.
#         finish_charge_ev_2: Finish charging the EV at CP2 at the Charge Station.
#         stage_1: Stage 1 of the agent's step function.
#         stage_2: Stage 2 of the agent's step function.

#     """
#     def __init__(self, unique_id, model):
#         super().__init__(unique_id, model)
#         self.queue_1 = []
#         self.queue_2 = []
#         self._is_active = False
#         self.active_ev_1 = None
#         self.active_ev_2 = None
#         # can replace with array of 2
#         # self.active_evs = []
#         # self._charge_rate = choice([7, 15, 100, 300]) #different charge rates

#         self._charge_rate = 7.5 #kW
#         self._checkpoint_id = 0

#         # new
#         self.max_queue_size = 10


#         print(f"\nCP info: ID: {(self.unique_id)}, initialized. Charge rate: {self._charge_rate} kW.")

#         # End initialisation

#     def __str__(self) -> str:
#         """Return the agent's unique id."""
#         return str(self.unique_id + 1)
    
    
#     def dequeue_1(self) -> None:
#         """Remove the first EV from each queue. FIFO fom queue.
#         If the queue is empty, do nothing. 
#         If the queue is not empty, remove the first EV from the queue and set as active ev.
#         Transition the EV to the charging state.

#         """
#         try:
#             self.active_ev_1 = self.queue_1.pop(0)
#             self.active_ev_1.machine.start_charge()
#             print(f"EV {(self.active_ev_1.unique_id)} dequeued at CS {self.unique_id} at Queue 1 and is in state: {self.active_ev_1.machine.state}")
#             print(f"Queue 1 size after dequeuing: {len(self.queue_1)}")
#         except:
#             pass
    
#     def dequeue_2(self) -> None:
#         """Remove the first EV from each queue. FIFO fom queue. 
#         This is the same as dequeue_1, but for queue 2."""
#         try:
#             self.active_ev_2 = self.queue_2.pop(0)
#             self.active_ev_2.machine.start_charge()
#             print(f"EV {(self.active_ev_2.unique_id)} dequeued at CP {self.unique_id} at Queue 2 and is in state: {self.active_ev_2.machine.state}")
#             print(f"Queue 2 size after dequeuing: {len(self.queue_2)}")
#         except:
#             pass
    
#     def finish_charge_ev_1(self):
#         """Finish charging the EV at CP1 at the Charge Station."""
#         if self.active_ev_1 is not None:
#             # self.active_ev_1.machine.end_charge() # this is a toggle
#             self.active_ev_1 = None
#             print(f"EV at Charge Station {self.unique_id}, CP 1 has exited.")

#     def finish_charge_ev_2(self):
#         """Finish charging the EV at CP2 at the Charge Station."""
#         if self.active_ev_2 is not None:
#             # self.active_ev_2.machine.end_charge() # this is another toggle
#             self.active_ev_2 = None
#             print(f"EV at Charge Station {self.unique_id}, CP 2 has exited.")

#     def stage_1(self):
#         """Stage 1 of the charge station's step function."""
#         if self.active_ev_1 is None:
#             self.dequeue_1()
#         if self.active_ev_2 is None:
#             self.dequeue_2()

#     def stage_2(self):
#         """Stage 2 of the charge station's step function."""
#         if self.active_ev_1 is not None:
#             if self.active_ev_1.battery < self.active_ev_1._soc_charging_thresh:
#                 self.active_ev_1.charge()
#                 self.active_ev_1.machine.continue_charge()
#             else:    
#                 # print(f"EV {self.active_ev_2}, Pre-trans: {self.active_ev_1.machine.state}.")                                       #testing
#                 self.active_ev_1.machine.end_charge()
#                 self.finish_charge_ev_1()
#         if self.active_ev_2 is not None:
#             if self.active_ev_2.battery < self.active_ev_2._soc_charging_thresh:
#                 self.active_ev_2.charge()
#                 self.active_ev_2.machine.continue_charge()
#             else:
#                 # print(f"EV {self.active_ev_2}, Pre-trans: {self.active_ev_2.machine.state}.")                                       #testing
#                 self.active_ev_2.machine.end_charge()
#                 self.finish_charge_ev_2()
            


# def compute_checkpoints(self,n) -> list:
#     """Compute the checkpoints for the simulation.
#     Args:
#         n (int): Number of charging points.
    
#     Returns:
#         checkpoints (list): List of checkpoints.
#     """
#     start = 40
#     # steps = n
#     interval = 40
#     checkpoints = np.arange(start, interval * n , interval)
#     return checkpoints


# for attr_name in dir(cs):
# if attr_name.startswith("cpspcs_"):

    # old architecture
# for cs in self.chargestations:
#     if cs.route == "A-B":
#         for  i, cs in enumerate(self.checkpoints_AB):
#             cs.checkpoint_id = self.checkpoints_AB[i]  

# for cs in self.chargestations:
#     if cs.route == "A-C":
#         for i,cs in enumerate(self.checkpoints_AC):
#             cs.checkpoint_id = self.checkpoints_AC[i]      


# for i,cs in enumerate(self.chargestations):
#     for route in self.routes:
#         if cs.route == route:
#             cs._checkpoint_id = self.checkpoints[i]
#             print(f"CS {cs.unique_id}, Route: {cs.route}, Checkpoint: {cs._checkpoint_id}")
#     # cs._checkpoint_id = self.checkpoints[i]
#     # print(f"CS {cs.unique_id}, Route: {cs.route}, Checkpoint: {cs._checkpoint_id}")

# for cs in  self.chargestations:
#     for i in self.csroutes:
#         if cs.route == i:
#             cs._checkpoint_id = self.checkpoints[i]
#             print(f"CS {cs.unique_id}, Route: {cs.route}, Checkpoint: {cs._checkpoint_id}")


 
# # check for existence of checkpoint and distance lists
# for attr_name in dir(self):
#     if attr_name.startswith("checkpoints_"):
#         print(attr_name)
# for attr_name in dir(self):
#     if attr_name.startswith("distances_"):
#         print(attr_name)

# if hasattr(self, f"checkpoint_id"):
#         print("attr set")


# 29-03-23

# for route in self.routes:
#     setattr(self,f"distances_{route}", worker.get_dict_values(worker.get_charging_stations_along_route(self.params, route)))

# show initial distance values, non cumulative
 # # use existing checkpoint_AB, checkpoint_AC lists and append to them..
        # for route in self.routes:
        #     setattr(self, f"checkpoint_{route}", [])
        #     print(f"\nIndividual distance measures for Route: {route}: {getattr(self, f'checkpoints_{route}')}") # test

# # use existing checkpoint_AB, checkpoint_AC lists and append to them
# for route in self.routes:
#     setattr(self, f"checkpoint_{route}", [])
#     for i in range(len(self.routes)):
#         getattr(self, f"checkpoints_{route}").append(None) #this added None to list 2 extra times
#     print(f"Checkpoint lists for Route: {route}: {getattr(self, f'checkpoints_{route}')}") # test

# for cs in self.chargestations:
    #     for attr_name in dir(cs):
    #             if attr_name.startswith("checkpoint_"):
    #                 print(attr_name)


    # for cs in self.chargestations:
    #     for route in self.routes:
    #         if cs.route == route:
    #             for i, j in enumerate(getattr(self, f"checkpoints_{route}")):
    #                 cs.checkpoint_id = j
    #                 print(f"CS {cs.unique_id}, Checkpoint {i}: {j}")
    
    
    # # CS, route, checkpoint ID print check
    # for cs in self.chargestations:
    #     for attr_name in dir(cs):
    #         if attr_name.startswith("checkpoint_"):
    #             print(f"CS {cs.unique_id}, Route: {cs.route}, Checkpoint: {getattr(cs, attr_name)}")


# 27-03-2023

# # route checkpoint attrib print test                        OK
    # for attr_name in dir(self):
    #     if attr_name.startswith("checkpoints_"):
    #         print(f"Checkpoints: {attr_name} is {getattr(self, attr_name)}")

#     # chargepoints
# for i in range(self.no_cps):
#     cp = Chargepoint(i * 100, self)
#     self.schedule.add(cp)
#     self.chargepoints.append(cp)
## assign checkpoints to charging points

# a = worker.get_route('A-B', self.params)
    # b = (list(a.keys()))
    # self.checkpoints_route_ab = worker.cumulative_sum(b)

    ###

# works but not sure if it's the best way
# def charging_stations_on_route_reverse_2(route_dict, route_name):
#     charging_stations = []
#     if route_name in route_dict:
#         for charging_station in route_dict[route_name].values():
#             charging_stations.extend(charging_station)
#         charging_stations = list(reversed(charging_stations))
#     return charging_stations

# # route checkpoint list attrib print test     OK
# for attr_name in dir(self):
#     if attr_name.startswith("checkpoints_"):
#         print(attr_name)

# for attr_name in dir(self):
#     if attr_name.startswith("route_"):
#         attr_value = getattr(self, attr_name)
#         if attr_value is None:
#             print(f"{attr_name} is None")
#         else:
#             # setattr(self, f"route_{route}", str(route))
#             setattr(self, f"route_{route}", self._set_up_checkpoints(route=route))
#             print(f"{attr_name} is {attr_value}")


# model.routes source of route data for CS agents
# model. 


# make checkpoints
# self.checkpoints = self.compute_checkpoints(self.no_css+1) #+1 to ensure no overruns.

# for route in self.routes:
#     # self.checkpoints = worker.get_checkpoint_list(self.routes, route) # ??
#     # setattr(self, f"route_checkpoints_{route}", worker.get_checkpoint_list(params, route))
#     a = worker.remove_random_item(self.routes)

# for route in self.routes:
#     print('Route: ', route)
#     print('Checkpoints: ', self.checkpoints)


# old parameterisation

# self.no_css = params['no_css']
# self.no_cps = no_cps
# self.default_cppcs = params['default_cppcs']
# self.no_cps_per_cs = params['no_cps_per_cs']
# self.checkpoints = [40, 80, 120, 160, 200, 240, 280]


# route names
# self.set_up_routes()
# route ids
# self.set_up_route_ids()
# self.chosen_route = worker.get_charging_stations_on_route(params, 'A-C')

# # check choices
# for choice in self.route_choices:
#     print(choice)



# for attr_name in dir(self):
#     if attr_name.startswith("checkpoints_"):
#         attr_value = getattr(self, attr_name)

# what does ab look like? get analog

# aa = worker.get_route_from_config('A-B', self.params)
# ab = (list(aa.keys()))
# print(ab)
# self.checkpointsAB = worker.cumulative_cs_distances(ab)

# aac = worker.get_route_from_config('A-C', self.params)
# abc = (list(aac.keys()))
# print(abc)
# self.checkpointsAC = worker.cumulative_cs_distances(abc)

# print(f"Checkpoints AB: {self.checkpointsAB}")
# print(f"Checkpoints AC: {self.checkpointsAC}")

# two list link template
# for cs in self.chargestations:
#     cs.update_checkpoint_id()
#     cs.update_cp_ratings()

# for  i, cs in enumerate(self.chargestations):
#     cs._checkpoint_id = self.checkpoints[i]        
        

# cs = ChargeStation(i, self, self.no_cps_per_cs.get('i', self.default_cppcs))
# add checkpoint id as a propery of cs
# cs.__setattr__('checkpoint_id', self.checkpoints[i])  

# no_evs = 3
# no_css = 5
# no_cps = 2
# check points = [40, 80, 120, 160, 200, 240, 280]
# params = {'no_css': 5, 
#           'no_cps_per_cs':{
#                 '1':2, '2':3, '3':4, '4':2, '5':2
#                 },
#             'default_cppcs': 3,
#             }


# 24-02-2023

# New structure

# def read_charging_data(filename):
#     charging_data = {}

#     with open(filename, 'r') as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=',')
#         next(csv_reader)  # skip the header row

#         for row in csv_reader:
#             route = row[0]
#             station = row[1]
#             cpid = row[2]
#             power = int(row[3])
#             distance = int(row[4])
#             price = int(row[5])
#             green = bool(int(row[6]))
#             booking = bool(int(row[7]))

#             if route not in charging_data:
#                 charging_data[route] = {}

#             if station not in charging_data[route]:
#                 charging_data[route][station] = {'cpids': [], 'power': {}, 'total_power': 0, 'total_price': 0, 'green': 0, 'booking': 0}

#             charging_data[route][station]['cpids'].append(cpid)

#             if power not in charging_data[route][station]['power']:
#                 charging_data[route][station]['power'][power] = 0

#             charging_data[route][station]['power'][power] += 1
#             charging_data[route][station]['total_power'] += power
#             charging_data[route][station]['total_price'] += price
#             charging_data[route][station]['green'] |= green
#             charging_data[route][station]['booking'] |= booking

#     return charging_data

# def return_strings(num_calls, string_list):
#     """
#     Returns one of the strings from the given list each time the function is called up to the
#     number of times specified in the num_calls argument.
    
#     Parameters:
#     num_calls (int): The maximum number of times the function can be called.
#     string_list (list): The list of strings to return from.
    
#     Returns:
#     A string from the list of strings.
#     """
#     if not string_list:
#         raise ValueError("The string list cannot be empty.")
        
#     def counter_wrapper():
#         if counter_wrapper.counter < num_calls:
#             counter_wrapper.counter += 1
#             return random.choice(string_list)
#         else:
#             return None
        
#     counter_wrapper.counter = 0
#     return counter_wrapper


# def count_charging_stations(param_dict, target_route):
#     station_counts = {}
#     for route, stations in param_dict.items():
#         num_stations = len(stations)
#         station_counts[route] = num_stations
#     return station_counts



# def get_station_distances(route_name, station_config):
#     route_stations = station_config['routes'][route_name]['charging_stations']
#     station_distances = []
#     for i, station_id in enumerate(route_stations):
#         if i == 0:
#             station_distances.append(station_config['charging_stations'][station_id]['distance'])
#         else:
#             prev_station_id = route_stations[i-1]
#             prev_station_distance = station_config['charging_stations'][prev_station_id]['distance']
#             curr_station_distance = station_config['charging_stations'][station_id]['distance']
#             station_distances.append(curr_station_distance - prev_station_distance)
#     return station_distances

# def get_cumulative_distances(route, station_config):
#     distances = []
#     current_station = f"CS_{route}_1"
#     distance_to_current = station_config[current_station]['distance_to_next']
#     distances.append(distance_to_current)
    
#     while True:
#         next_station = station_config[current_station]['next_station']
#         if next_station is None:
#             break
#         distance_to_next = station_config[next_station]['distance_to_next']
#         distances.append(distance_to_current + distance_to_next)
#         current_station = next_station
#         distance_to_current += distance_to_next
    
#     return distances


# def cumulative_distances(route_name, station_config):
#     route = station_config["routes"][route_name]
#     distances = [route["distance"]]

#     for i in range(1, len(route["stations"])):
#         station_id = route["stations"][i]
#         distance = station_config["charging_stations"][station_id]["distance"]
#         distances.append(distance)

#     return [sum(distances[:i]) for i in range(1, len(distances) + 1)]

# def get_station_distances(nested_dict, route_name):
#     # Find the stations for the given route
#     route_stations = [key for key in nested_dict.keys() if key.startswith(route_name)]

#     # Get the distance values for each station
#     distances = []
#     for i, station in enumerate(route_stations):
#         distance_key = f"{station}_distance"
#         distance = nested_dict[station].get(distance_key)
#         if distance is None:
#             raise ValueError(f"No distance value found for station {station}")
#         if i == 0:
#             distances.append(distance)
#         else:
#             prev_station = route_stations[i-1]
#             prev_distance_key = f"{prev_station}_distance"
#             prev_distance = nested_dict[prev_station].get(prev_distance_key)
#             if prev_distance is None:
#                 raise ValueError(f"No distance value found for station {prev_station}")
#             distances.append(distance - prev_distance)

#     return distances


# def get_cumulative_distances(route_name, charging_stations):
#     route_data = charging_stations.get(route_name)
#     if not route_data:
#         return None
    
#     cumul_distances = []
#     curr_distance = 0
#     for station_id, station_data in route_data.items():
#         station_distance = station_data.get('distance')
#         curr_distance += station_distance
#         cumul_distances.append(curr_distance)
        
#     if cumul_distances:
#         cumul_distances[0] = charging_stations[route_name]['CS'][0]['distance']
    
#     return cumul_distances

# def get_cumulative_distances(route_name, charging_stations_dict):
#     # Find the route with the given name
#     route = None
#     for r in charging_stations_dict['routes']:
#         if r['name'] == route_name:
#             route = r
#             break
#     if route is None:
#         raise ValueError(f"No route found with name '{route_name}'")
    
#     # Initialize the list of distances with the distance to the first charging station
#     distances = [route['distanceToFirstCS']]
    
#     # Iterate over the charging stations on the route, adding their distances to the list
#     for cs in route['chargingStations']:
#         distances.append(cs['distanceToNextCS'])
    
#     # Return the list of cumulative distances
#     for i in range(1, len(distances)):
#         distances[i] += distances[i-1]
#     return distances





# route_counts = Counter([station['Route'] for station in charging_stations])
# print(route_counts)


# points_per_station_per_route = {}
# for station in charging_stations:
#     key = f"{station['Route']}_{station['Station']}"
#     if key not in points_per_station_per_route:
#         points_per_station_per_route[key] = []
#     points_per_station_per_route[key].append(station['CPID'])
# print(points_per_station_per_route)

# routes = list(set([station['Route'] for station in charging_stations]))
# print(routes)

# num_routes = len(routes)
# print(num_routes)




# Route,Station,CPID,Power,Distance,Price,Green,Booking
# A-B,CS_A-B_1,CS_AB_1_1,7,40,6,0,0
# A-B,CS_A-B_1,CS_AB_1_2,7,40,6,0,0
# A-B,CS_A-B_1,CS_AB_1_3,60,40,10,0,0
# A-B,CS_A-B_2,CS_AB_2_1,7,20,6,0,0
# A-B,CS_A-B_2,CS_AB_2_2,7,20,6,0,0
# A-B,CS_A-B_3,CS_AB_3_1,7,50,6,0,0
# A-B,CS_A-B_3,CS_AB_3_2,7,50,6,0,0
# A-B,CS_A-B_3,CS_AB_3_3,60,50,10,0,0
# A-B,CS_A-B_4,CS_AB_4_1,7,10,6,0,0
# A-B,CS_A-B_4,CS_AB_4_2,7,10,6,0,0
# A-B,CS_A-B_4,CS_AB_4_3,60,10,10,0,0
# A-B,CS_A-B_5,CS_AB_5_1,7,30,6,0,0
# A-B,CS_A-B_5,CS_AB_5_2,7,30,6,0,0
# A-B,CS_A-B_5,CS_AB_5_3,7,30,6,0,0
# A-C,CS_A-C_1,CS_AC_1_1,7,40,6,0,0
# A-C,CS_A-C_1,CS_AC_1_2,7,40,6,0,0
# A-C,CS_A-C_2,CS_AC_2_1,7,40,6,0,0
# A-C,CS_A-C_2,CS_AC_2_2,7,40,6,0,0
# A-C,CS_A-C_3,CS_AC_3_1,7,40,6,0,0
# A-C,CS_A-C_3,CS_AC_3_2,7,40,6,0,0
# A-C,CS_A-C_4,CS_AC_4_1,7,40,6,0,0
# A-C,CS_A-C_4,CS_AC_4_2,7,40,6,0,0

# 23-02-2023




# class Chargepoint(Agent):
#     """Charging point for charging stations"""
    
#     def __init__(self, unique_id: int, model: Model) -> None:
#         super().__init__(unique_id, model)
#         self.active_ev = None
#         self._charge_rate = 7.5 #kW
    
#     def init_report(self):
#         print(f"\nCP info: ID: {(self.unique_id)}, initialized. Charge rate: {self._charge_rate} kW.")
    
#  def get_checkpoints(self, route) -> int:
#         """Compute the checkpoint for the charging station.
#         Args:
#             cs (ChargeStation): The charging station.
        
#         Returns:
#             checkpoint (int): The checkpoint.
#         """
#         checkpoints = []
#         for i in range(len(route)):
#             checkpoints.append(route[i][0])
#         # checkpoint = cs.unique_id * 40

# 20-03-2023

# def count_charging_stations(param_dict, target_route):
#     station_counts = {}
#     for route, stations in param_dict.items():
#         num_stations = len(stations)
#         station_counts[route] = num_stations
#     return station_counts


# alt 2
    # def dequeue(self) -> bool:
    #     """Remove the first EV from queue."""
    #     try:
    #         if not self.queue:
    #             print(f"The queue at ChargeStation {self.unique_id} is empty.")
    #             return False
            
    #         if len(self.occupied_cps) == self.no_cps:
    #             print(f"All charge points at ChargeStation {self.unique_id} are occupied.")
    #             return False
            
    #         active = self.queue[0]
    #         if active in self.occupied_ev:
    #             self.queue.append(active)
    #             self.queue.pop(0)
    #             print(f"EV {active.unique_id} is already in the process of charging at ChargeStation {self.unique_id}. Moving it to the back of the queue.")
    #             return False
            
    #         for attr_name in [a for a in dir(self) if a.startswith("cp_id_")]:
    #             attr_value = getattr(self, attr_name)
    #             if attr_value is None and attr_name not in self.occupied_cps:
    #                 setattr(self, attr_name, active)
    #                 active.machine.start_charge()
    #                 self.occupied_cps.add(attr_name)
    #                 self.occupied_ev.add(active)
    #                 print(f"EV {active.unique_id} dequeued at CS {self.unique_id} at CP {attr_name} and is in state: {active.machine.state}. Charging started")
    #                 self.queue.pop(0)
    #                 return True
        
    #         # If no free charge points are found, move the EV to the back of the queue
    #         self.queue.append(active)
    #         self.queue.pop(0)
    #         print(f"All charge points at ChargeStation {self.unique_id} are occupied. Moving EV {active.unique_id} to the back of the queue.")
    #         return False
        
    #     except Exception as e:
    #         print(f"Error assigning EV to charge point: {e}")
    #         return False




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
    



# 19-03-2023

# try:
        #     # for i in range(len(self.charge_points)):
        #     # for i in self.vars():
        #     #     print(i)
        #         if getattr(self, self.charge_points[i]) is None:
        #             setattr(self, self.charge_points[i], self.queue.pop(0))
        #             print(f"EV {(getattr(self, self.charge_points[i]).unique_id)} dequeued at CS {self.unique_id} at CP {i} and is in state: {getattr(self, self.charge_points[i]).machine.state}")
        #             setattr(self, self.charge_points[i]).machine.start_charge() #used to be getattr
        #             # print(f"EV {(getattr(self, self.charge_points[i]).unique_id)} dequeued at CS {self.unique_id} at CP {i} and is in state: {getattr(self, self.charge_points[i]).machine.state}")
        #             print(f"Queue size after dequeuing: {len(self.queue)}")
        #         # elif getattr(self, self.charge_points[i]) is not None:
        # except:
        #     pass

        # try:
        #     for attr_name in dir(self):
        #         attr_value = getattr(self, attr_name)
        #         if attr_value is None:
        #             print(f"{attr_name} is None")
        #         else:
        #             print(f"{attr_name} is {attr_value}")
        # except:
        #     pass   


# 15-03-2023 Attempt to dynamically create cps for css

 #    cs = ChargeStation(i,self, self.no_cps_per_cs.get(str(i)))


#  for i in range(self.no_evs):
#             ev = EV(i,self)
#             self.schedule.add(ev)
#             self.evs.append(ev)
#         # charging stations
#         for i in range(self.no_css):
#             cs = ChargeStation(i + no_evs, self, no_cps_per_cs)
#             self.schedule.add(cs)
#             self.chargestations.append(cs)
#         for  i, cs in enumerate(self.chargestations):
#             cs._checkpoint_id = self.checkpoints[i]  
#             for j in range(self.no_cps_per_cs):
#                 cp = ChargePoint(j + (i * self.no_cps_per_cs), self, cs)
#                 self.schedule.add(cp)
#                 self.chargepoints.append(cp)







# 15-02-2023 Attempt to nest EV agent step function

#  def step(self):
#         # Block A - Transitions SM:

#         # Transition Case 1: Start travelling. idle -> travel
#         if self.machine.state == 'Idle':
#             if self.odometer < self._distance_goal:
#                 self.machine.start_travel()
            
#         if self.machine.state == 'Travel':
#             self.travel()
#             self.machine.continue_travel()
#             print(f"Vehicle id: {self.unique_id} is {self.machine.state}. This vehicle has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
#             # EV travelling or travelling low, checking for Charge Station at each checkpoint
#             if self.odometer in self.checkpoint_list:
#                 print("EV has arrived at Charge Station but is not yet low on battery")
        
#         # Transition Case 2: Still travelling, battery low. Travel -> travel_low  
#             if self.battery <= self._soc_usage_thresh:
#                 self.machine.get_low()
#                 print("Current EV state: " + str(self.machine.state))
#                 print(f"EV: {self.unique_id}. This vehicle has travelled: {str(self.odometer)} miles and is low on battery. This vehicle's current charge level is: {self.battery} kwh")

#             # Transition Case 7: Journey Complete. travel -> idle
#             if self.odometer >= self._distance_goal:
#                 self.machine.end_travel()
#                 print(f"Vehicle {self.unique_id} has completed its journey. State: {self.machine.state}. This vehicle has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
            
        
#         # Transition Case 3: EV with low battery does not arrive at charge station. Travel_low -> Battery_dead
#         # condition self.battery < 10 because 10 is the minimum expenditure of energy to move the vehicle in one timestep
#         if self.machine.state == 'Travel_low':
        
#             # Transition Case 4: EV with low battery is on lookout for Charge station. Notification.
#             if self.odometer < self._distance_goal:
#                 if self.battery > 10:
#                     print(f"EV {self.unique_id} is low on charge and is seeking a charge station. Current charge: {self.battery} kWh")
#                     self.travel()

#                 if self.battery < 10:
#                     self.machine.deplete_battery()
#                     print(f"EV {self.unique_id} is now in state: {self.machine.state} and is out of charge.")

#                 # if self.battery <= 0:
#                 #     self.machine.deplete_battery()
#                 #     print(f"EV {self.unique_id} is out of charge and can no longer travel. State: {self.machine.state}. Current charge: {self.battery} kWh")
#                 if self.odometer in self.checkpoint_list:
#                     self.machine.seek_charge_queue()
#                     print(f"EV {self.unique_id} is low on battery and is at a station. Seeking charge queue. Current EV state: {self.machine.state}")
#                     self.select_cp()
#                     self.machine.join_charge_queue()


#             # Transition Case 8: Joutney complete, battery low. travel_low -> idle
#             if self.odometer >= self._distance_goal:
#                 self.machine.end_travel_low()
#                 print(f"Vehicle {self.unique_id} has completed its journey. State: {self.machine.state}. This vehicle has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
                
#             # # experimental - limit queue size to limit defined in charge station
#             # if (len(self._chosen_cp.queue_1) == self._chosen_cp._max_queue_size) and (len(self._chosen_cp.queue_2) == self._chosen_cp._max_queue_size):
#             #     print("Queue 1 and 2 are full. EV travelling under stress.")
#             # self.machine.join_charge_queue()
#             # # notification handled in charge station step method
       
#         # Transition Case 5: Start charging. in_queue -> charge
#         if self.machine.state == 'In_queue':
#             self.machine.start_charge()

#         # Transition Case 6: Continue charging. Charge -> charge
#         if self.machine.state == 'Charge':
#             if self.battery >= self._soc_charging_thresh:
#                 print(f"Charge complete. Vehicle {self.unique_id} is {self.machine.state}. This vehicle has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
#                 self.machine.end_charge()
#             if self.battery < self._soc_charging_thresh:
#                 self.machine.continue_charge()
#                 self._chosen_cp.charge_ev()
#                 print(f"Charging. Vehicle {self.unique_id} is {self.machine.state}. This vehicle has travelled: {self.odometer} miles. Battery: {self.battery} kWh")
        

# 21/02/23
# logic for 'Stay in queue'

# if self._in_queue == True:
#     if self._chosen_cs.active_ev_1 == self:
#         self.machine.charge()
#         self._charging = True
#         self._in_queue = False
#         print(f"EV {self.unique_id} is now charging at Charge Station {self._chosen_cs.unique_id}. Current charge: {self.battery} kWh")
#     elif self._chosen_cs.active_ev_2 == self:
#         self.machine.charge()
#         self._charging = True
#         self._in_queue = False
#         print(f"EV {self.unique_id} is now charging at Charge Station {self._chosen_cs.unique_id}. Current charge: {self.battery} kWh")
#     else:
#         print(f"EV {self.unique_id} is waiting in queue at Charge Station {self._chosen_cs.unique_id}. Current charge: {self.battery} kWh")
#         self.machine.wait_in_queue()
#         self._in_queue = True
#         self._charging = False


# 22/02/23
# post successful tests, clean up EV class and remove redundant code



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
    


# def exit_charge_station(self) -> None:
    #     """EV exits the charge station. Removes EV from queue and sets charge station to inactive."""
    #     if self._chosen_cs.active_ev_1 == self:
    #         self._chosen_cs = None
    #     elif self._chosen_cs.active_ev_2 == self:
    #         self._chosen_cs = None
    #     print(f"EV {(self.unique_id)} exited charge point at Charge Station {(self._chosen_cs.unique_id)}")


  # # Approach 1: use a link, index calculated by journey goal/by distance tick
    # def _set_checkpoint(self, factor) -> float:
    #     distance = self._distance_goal * factor
    #     return distance
    # # next step, do checkpointing using a link, index calculated by journey goal/by distance tick
    

# From ChargeStation class 
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


# Explore for model
    #  if self.schedule.steps >= self.ticks:
            # self.running = False
            # print("Simulation finished.")
            # print(self.datacollector.get_agent_vars_dataframe())
            # print(self.datacollector.get_model_vars_dataframe())
            # print(self.datacollector.get_agent_vars_dataframe().columns)
            # print(self.datacollector.get_model_vars_dataframe().columns)
            # print(self.datacollector.get_agent_vars_dataframe().index)
            # print(self.datacollector.get_model_vars_dataframe().index)
            # print(self.datacollector.get_agent_vars_dataframe().index.names)
            # print(self.datacollector.get_model_vars_dataframe().index.names)
            # print(self.datacollector.get_agent_vars_dataframe().index.levels)
            # print(self.datacollector.get_model_vars_dataframe().index.levels)
            # print(self.datacollector.get_agent_vars_dataframe().index.levels[0])
            # print(self.datacollector.get_model_vars_dataframe().index.levels[0])
            # print(self.datacollector.get_agent_vars_dataframe().index.levels[1])
            # print(self.datacollector.get_model_vars_dataframe().index.levels[1])
            # print(self.datacollector.get_agent_vars_dataframe().index.levels[2])
            # print(self.datacollector.get_model_vars_dataframe().index.levels[2])
            # print(self.datacollector.get_agent_vars_dataframe().index.levels[3])
            # print(self.datacollector.get_model_vars_dataframe().index.levels[3])
            # print(self.datacollector.get_agent_vars_dataframe().index.levels[4])
            # print(self.datacollector.get_model_vars_dataframe().index.levels[4])
            # print(self.datacollector.get_agent_vars_dataframe().index.levels[5])
            # print(self.datacollector.get_model_vars_dataframe().index.levels[5])
            # print(self.datacollector.get_agent_vars_dataframe().index.levels[6])
            # print(self.datacollector.get_model_vars_dataframe().index.levels[6])
            # print(self.datacollector.get_agent_vars_dataframe().index.levels[7])
            # print(self.datacollector.get_model_vars_dataframe().index.levels[7])
            # print(self.datacollector.get_agent_vars_dataframe().index.levels[8])
            # print(self.datacollector.get_model_vars_dataframe().index.levels[8])
            # print(self.datacollector.get_agent_vars_dataframe().index.levels[9])
            # print(self.datacollector.get_model_vars_dataframe().index.levels[9])
            # print(self.datacollector.get_agent_vars_dataframe().index.levels[10])
            # print(self.datacollector.get_model_vars_dataframe().index.levels[10])


# def unpack_and_join(df, column_name):
#     # Get the column values as a list of strings
#     column_values = df[column_name].tolist()

#     # Strip the square brackets from the strings
#     column_values = [s.strip("[]") for s in column_values]

#     # Split the strings on commas and create a list of lists
#     split_values = [s.split(",") for s in column_values]

#     # Get the number of columns needed
#     num_cols = max([len(row) for row in split_values])

#     # Create the new columns in the output dataframe
#     column_names = [column_name+"_unpacked_"+str(i) for i in range(num_cols)]
#     new_df = pd.DataFrame(columns=column_names)

#     # Loop over the original column values and add the unpacked values to the new dataframe
#     for vals in split_values:
#         row_data = {}
#         for i in range(num_cols):
#             if i < len(vals):
#                 row_data[column_name+"_unpacked_"+str(i)] = vals[i].strip()
#             else:
#                 row_data[column_name+"_unpacked_"+str(i)] = ""
#         new_df = new_df.append(row_data, ignore_index=True)

#     # Join all values in the same position per row
#     new_df = new_df.apply(lambda x: ','.join(x.astype(str)), axis=1)

#     # Replace the original column with the unpacked and joined values
#     df[column_name] = new_df

#     return df



# 06/03/2023

# # imports
# import seaborn as sns
# from random import choice
# import warnings
# warnings.simplefilter("ignore")
# from plotly.offline import iplot
# # from statemachine import StateMachine, State
# from transitions import Machine
# import random
# from transitions.extensions import GraphMachine

# import EV.agent as agent
