               
class EVModel(Model):
    """Simulation Model with EV agents."""

    def __init__(self, no_evs, ticks):
        # super().__init__()
        # init with input args
        self.ticks = ticks
        self._current_tick = 1
        self.no_evs = no_evs
        # other key model attr 
        self.schedule = RandomActivation(self)
        # Populate model with agents
        self.evs = []
        for i in range(self.no_evs):
            ev = EV(i,self)
            self.schedule.add(ev)
            self.evs.append(ev)
        self.datacollector = DataCollector(
            model_reporters={'EVs Charged': get_evs_charged,
                             'EVs Activated': get_evs_active,
                             'EVs Charge Level': get_evs_charge_level,
                             'EVs Currently charging': get_evs_charging,}
            )
    
    def step(self):
        """Advance model one step in time"""
        self.datacollector.collect(self)
        self.schedule.step()
        self._current_tick += 1