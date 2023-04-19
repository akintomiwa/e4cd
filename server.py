# import mesa
from EV.model import EVModel
from EV.agent import EV, ChargeStation, Location
# from EV.model_config import model_config
import EV.model_config as model_config
from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid, ChartModule, BarChartModule, TextElement


def agent_portrayal(agent):
    if type(agent) is EV:
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 0,
                     "Color": "green",
                     "r": 1}
        # Add a label with the agent's unique id
        portrayal["text"] = f"EV: {agent.unique_id}, State: {agent.machine.state}, SOC: {agent.battery:.2f}"
        portrayal["text_color"] = "white"
        portrayal["text_size"] = 12
        if agent.machine.state == 'Travel':
            portrayal["Color"] = "green"
            portrayal["Layer"] = 1
        elif agent.machine.state == 'Travel_low':
            portrayal["Color"] = "orange"
            portrayal["Layer"] = 1
            portrayal["r"] = 1
        elif agent.machine.state == 'Battery_dead':
            portrayal["Color"] = "red"
            portrayal["Layer"] = 1
            portrayal["r"] = 1
        elif agent.machine.state == 'Charge':
            portrayal["Color"] = "blue"
            portrayal["Layer"] = 1
            portrayal["r"] = 1
        
    elif type(agent) is ChargeStation:
        portrayal = {"Shape": "rect",
                     "Filled": "true",
                     "Layer": 0,
                     "Color": "blue",
                     "w": 1,
                     "h": 1}
        # Add a label with the agent's unique id
        portrayal["text"] = f"Location: {agent.name}, Queue Length: {len(agent.queue)}"
        portrayal["text_color"] = "white"
        portrayal["text_size"] = 12
    elif type(agent) is Location:
        portrayal = {"Shape": "rect",
                     "Filled": "true",
                     "Layer": 0,
                     "Color": "black",
                     "w": 2,
                     "h": 2}
        # Add a label with the agent's unique id
        portrayal["text"] = f"Location: {agent.name}, Count: {agent.location_occupancy}."
        portrayal["text_color"] = "white"
        portrayal["text_size"] = 12
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


grid = CanvasGrid(agent_portrayal, 100, 100,600, 500)

# Define other visualization elements such as charts or text
# text = TextElement(text="My Model")
chart = ChartModule([{"Label": "EV status", "Color": "green"}, 
                     {"Label": "ChargeStation occupancy", "Color": "red"}])

bar_chart = BarChartModule([{"Label": "Count", "Color": "black"}])

# Define user parameters if necessary
user_param = UserSettableParameter('slider', "My Parameter", 5, 1, 10, 1)

server = ModularServer(EVModel,
                    [grid, chart, bar_chart, EVLegend(), StationLegend(), LocationLegend()],
                    "ec4d EV Model",
                    {'no_evs': 10, 
                     'station_params':model_config.station_config, 
                     'location_params':model_config.location_config,
                     'station_location_param':model_config.station_location_config, 
                     'ticks': 27})

server.port = 8521
server.launch()