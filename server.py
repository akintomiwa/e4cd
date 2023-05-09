# import mesa
from EV.model import EVModel
from EV.agent import EV, ChargeStation, Location
# from EV.cfg import cfg
import EV.model_config as cfg
from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid, ChartModule, BarChartModule, TextElement


def agent_portrayal(agent):
    if type(agent) is EV:
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 0,
                     "Color": "green",
                     "r": 3}
        # Add a label with the agent's unique id
        # portrayal["text"] = f"EV: {agent.unique_id}, State: {agent.machine.state}, SOC: {agent.battery:.2f}"
        portrayal["text"] = f"{agent.unique_id}"
        portrayal["text_color"] = "white"
        # portrayal["text_size"] = 12
        if agent.machine.state == 'Travel':
            portrayal["Color"] = "green"
        elif agent.machine.state == 'Travel_low':
            portrayal["Color"] = "orange"
        elif agent.machine.state == 'Battery_dead':
            portrayal["Color"] = "red"
        elif agent.machine.state == 'Charge':
            portrayal["Color"] = "blue"
        
    elif type(agent) is ChargeStation:
        portrayal = {"Shape": "rect",
                     "Filled": "true",
                     "Layer": 0,
                     "Color": "blue",
                     "w": 2,
                     "h": 2}
        # Add a label with the agent's unique id
        # portrayal["text"] = f"N: {agent.name}, Q: {len(agent.queue)}"
        portrayal["text"] = f"{agent.name}"
        portrayal["text_color"] = "white"
        portrayal["text_size"] = 12

    elif type(agent) is Location:
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "black",
                     "r": 5}
        # Add a label with the agent's unique id
        # portrayal["text"] = f"Name {agent.name}, O: {agent.location_occupancy}."
        portrayal["text"] = f"{agent.name}, {agent.location_occupancy}."
        portrayal["text_color"] = "white"
        portrayal["text_size"] = 6
        if len(agent.location_occupancy_list) > 2 and len(agent.location_occupancy_list) < 5:
            portrayal["r"] = 6
        elif len(agent.location_occupancy_list) >= 5:
            portrayal["r"] = 8
    return portrayal


class EVLegend(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "EV: <span style='color:green;'>Available</span>, <span style='color:orange;'>Traveling (low battery)</span>"

class StationLegend(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "Charge Station: <span style='color:blue;'>Available</span>"

class LocationLegend(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "Location: <span style='color:black;'>N/A</span>"


grid = CanvasGrid(agent_portrayal, grid_width=cfg.grid_width, grid_height=cfg.grid_height, canvas_height=800, canvas_width=800)

# Define other visualization elements such as charts or text
# text = TextElement(text="My Model")
chart = ChartModule([{"Label": "EV status", "Color": "green"}, 
                     {"Label": "ChargeStation occupancy", "Color": "red"}])


bar_chart = BarChartModule([{"Label": "Count", "Color": "black"}])

# Define user parameters if necessary
user_ev_param = UserSettableParameter(param_type='slider', name ="cfg.no_evs", value= 2, min_value=1, max_value=10, step = 1)
# user_ticks_option = UserSettableParameter('number', 'My Number', value=123)
# static_text = UserSettableParameter('static_text', value="This is a descriptive textbox")

server = ModularServer(EVModel,
                    [grid, chart, bar_chart, EVLegend(), StationLegend(), LocationLegend()],
                    "ec4d EV Model",
                    {'no_evs': cfg.no_evs, 
                     'station_params':cfg.station_config, 
                     'location_params':cfg.location_config,
                     'station_location_param':cfg.station_location_config, 
                     'overnight_charging':cfg.overnight_charging, 
                     'ticks': cfg.ticks,
                     'grid_height':cfg.grid_height,
                     'grid_width':cfg.grid_width,
                     }
                    )

server.port = 8521
server.launch()

# in stage 1  Agemt step_1
# Todo: replace odometer and distance goal check with dist_pos and self pos comparisiona
# Fix charging flow 


