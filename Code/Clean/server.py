from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from mesa.visualization.TextVisualization import (
    TextData, TextGrid, TextVisualization
)

from model import GentrificationModel

class DataElement(TextElement):
    '''
    Display data in text element.
    '''

    def __init__(self):
        pass

    def render(self, model):
        return ("<b>Neighborhood Status: " + 
                str(round(model.status,2))+ "<br/>" +
                "<div style='color: blue'>Average Income: " + 
                str(round(model.mean_income,2))+ "</div><br/>" +
                "<div style='color: green'>Average Property Condition: " + 
                str(round(model.mean_condition,2)) + "</div>" +
                "Time (years): " + str(int(model.schedule.steps/12)) + 
                "<br/></b>")


def canvas_draw(agent):
    '''
    Portrayal Method for canvas
    '''
  
    portrayal = {"Shape": "rect", "h": 1.0, "w": 1.0 ,"Filled": "true", "Layer": 0}
    
    if agent.income < 0.33:
        portrayal["Color"] = "Red"
    elif agent.income >= 0.33 and agent.income < 0.67:
        portrayal["Color"] = "Yellow"
    else:
        portrayal["Color"] = "Green"

    if agent.empty == True:
        portrayal["Color"] = "White"

    return portrayal

grid_size = 25
data_element = DataElement()
canvas_element = CanvasGrid(canvas_draw, grid_size, grid_size, 500, 500)
plot_chart = ChartModule([{"Label": "status", "Color": "Black"},
        {"Label": "income", "Color": "Blue"},
        {"Label": "condition", "Color": "Green"}])
        

model_params = {
    "height": grid_size,
    "width": grid_size,
    "depreciation_rate": UserSettableParameter(
                    "slider", "Depreciation Rate", 0.0015, 0.00, 0.01, 0.0005),
    "mobility": UserSettableParameter(
                    "slider", "Agent mobility", 0.025, 0.00, 0.10, 0.005),
    "status": UserSettableParameter(
                    "slider", "Initial Neighborhood Status", 0.50, 0.00, 1.00, 0.01),
    "stat_var": UserSettableParameter(
                    "slider", "Status Variability (Noise)", 0.025, 0.00, 0.10, 0.005),
    "d_factor": UserSettableParameter(
                    "slider", "d - Dependency", 0.5, 0.00, 1.0, 0.1)
}

server = ModularServer(GentrificationModel,
    [canvas_element, data_element, plot_chart],
    "Schelling", model_params)
server.launch()
