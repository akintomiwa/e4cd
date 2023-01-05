class Car(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self._max_battery = 100
        self._soc_thresh = 10
        self._charge_rate = 10
        self._in_queue = False
        self._in_garage = False
        self._is_charging = False
        self._was_charged = False
        self._is_travelling = False
        self._journey_complete = False

        # self._chargerate = None
        # self._loc_init = 
        # self._soc_init = 50 #initially 50 (+/- 10?). if over multiple days, use learnt value from prev day. If overnight charge, set to 100. write methods to handle cases later.
        # self.queue_time = self.chargerate * self. 
        self.soc = ss.poisson(45).rvs()
        self._pos_init = None #Urgent Fix soon
        self._is_active = False
        self.odometer = 0
        self._distance_goal = None
        self.journey_type = None
        # External 
        self.journey_choice = choice([True, False])
        self.start_time = ss.norm.rvs(size=1000,loc=12,scale=2, random_state = 42)
        # self._cp_entry = None
        # self._cp_exit = None
        # self._charge_start = None

    def select_journey_type(self):
        self._is_active == True
        if self.journey_choice == True:
            self._distance_goal = 50
            self.journey_type = "Urban"
        else:
             self._distance_goal = 100
             self.journey_type = "InterUrban"
        if self._is_travelling == True & self._is_active == True:
            print("This car's id is: " + str(self.unique_id) + " and it's going on an " + str(self.journey_type) + " journey" + " with a distance goal of " 
            + str(self._distance_goal))
        # print("Journey type selected: " + str(self._distance_goal))


    def travel(self):
        self._is_active
        self._is_travelling = True
        self.odometer += 10
        self.soc -= 5


    # def select_cp(self):
    #     # self._in_queue = True
    #     # # queue at shortest cp
    #     # self._chosen_cp_idx = np.argmin([
    #     #     len(cpoint.queue) for cpoint in self.model.cpoints])
    #     # self._chosen_cp = self.model.cpoint[self._chosen_cpoint_idx]
    #     self._in_queue = True

    
    def charge(self):
        self._is_charging = True
        # self._cp_exit = self.model._current_tick
        # self._chosen_cp.active_car = None
        # self.soc = self._max_battery
        # while self.soc < self._max_battery:
        #     self.soc += self._charge_rate
        #     if self.soc == self._max_battery:
        #         self._is_charging = False
        while self.soc < self._max_battery:
            self.soc += self._charge_rate
        print("Vehicle charged")
        self._is_charging = False
        self._was_charged = True
                

    def charge_overnight(self):
        if self._in_garage == True:
            self.soc = self._max_battery
    
    # def step(self):
    #     if (self._in_queue == False) & (self.model._current_tick >= self.entry_time):
    #         self.select_cp()
    #     elif isinstance(self.self._cp_entry, int):
    #         if self.model._current_tick - self._cp_entry == self.charge_time:
    #             self.travel()
    def step(self):
        # if self.model._current_tick >= self.start_time:
        # while (self.odometer < self._distance_goal) & self.soc > self._soc_thresh: # didnt work. 
        self.select_journey_type()
        while (self.odometer < self._distance_goal):
            self.travel()
            print("Vehicle id: " + str(self.unique_id) + ". This vehicle travelled: " + str(self.odometer) + " distance units")
            print("Vehicle id: " + str(self.unique_id) + ". This vehicle's current charge level is: " + str(self.soc) + " kwh")
            if self.odometer == self._distance_goal:
                self._journey_complete == True
                print("This vehicle has completed its journey")
                self._is_active == False
                self._is_travelling == False

            if self.soc < self._soc_thresh:
                self._is_travelling == False
                print("Vehicle has hit SOC threshold. Heading to charging station")
                self._is_charging == True
                self.charge() #charge
                self.travel()
            




class MainModel(Model):
    """Simulation Model with cars and charging points as two types of agents, interacting."""

    def __init__(self, no_cars, ticks):
        # super().__init__()
        # init with input args
        self.ticks = ticks
        self._current_tick = 1
        self.no_cars = no_cars
        # other key model attr 
        self.schedule = RandomActivation(self)
        # Populate model with agents
        self.cars = []
        for i in range(self.no_cars):
            car = Car(i,self)
            self.schedule.add(car)

        self.datacollector = DataCollector(
            model_reporters={'Cars Charged': get_cars_charged,
                             'Cars Activated': get_cars_active})
    
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self._current_tick += 1
