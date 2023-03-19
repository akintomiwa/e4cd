import mesa
def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                "Filled": "true",
                "Layer": 0,
                "Color": "red",
                "r": 0.5}
    return portrayal
grid = mesa.visualization.CanvasGrid(agent_portrayal, 10, 10, 500, 500)
server = mesa.visualization.ModularServer(MyModel,
                    [grid],
                    "My Model",
                    {'n_agents': 10})
server.launch()