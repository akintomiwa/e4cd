
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
