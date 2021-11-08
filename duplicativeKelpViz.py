from duplicativeKelp import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

canvasDims = 1000
width = 100
height = 100
kelpAmnt = 600
seaCowAmnt = 100

#makes the agents visualize
def agent_portrayal(agent):
    #if its a kelp
    if agent.type == "kelp":
        #and has food, set the portrayal to be normal

        portrayal = {"Shape": "rect",
                    "Filled": "true",
                    "Layer": 1,
                    "Color": "#194711", #green
                    "w": 1,
                    "h": 1,
                    "text": agent.unique_id,
                    "text_color": "3d3d3d"
                    }

    #if its a sea cow, make a portrayal
    elif agent.type == "seaCow":
        portrayal = {"Shape": "circle",
                    "Filled": "true",
                    "Layer": 1,
                    "Color": "#3d3d3d", #grey
                    "r": .5}
    return portrayal

#makes the visual grid
grid = CanvasGrid(agent_portrayal, width, height, canvasDims, canvasDims)

#makes the chart. IDK how, basically magic
kelpChart = ChartModule([{"Label": "Total Kelp Available",
                     "Color": "#194711"}],
                    data_collector_name = "kelpCollector")

seaCowChart = ChartModule([{"Label": "Total Sea Cows",
                     "Color": "#3d3d3d"}],
                    data_collector_name = "seaCowCollector")

#makes a web server for it all. This is wizardry
server = ModularServer(MoneyModel,
                       [grid, kelpChart, seaCowChart],
                       "Extinction Model",
                       {"kelpAmnt":kelpAmnt, "seaCowAmnt":seaCowAmnt, "width":width, "height":height})

#starts the web server
server.port = 8521 # The default
server.launch()