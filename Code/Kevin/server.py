from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from mesa.visualization.TextVisualization import (
    TextData, TextGrid, TextVisualization
)

from model import SchellingModel

import matplotlib
import matplotlib.pyplot as plt


class SchellingTextVisualization(TextVisualization):
    '''
    ASCII visualization for schelling model
    '''

    def __init__(self, model):
        '''
        Create new Schelling ASCII visualization.
        '''
        self.model = model

        grid_viz = TextGrid(self.model.grid, self.ascii_agent)
        happy_viz = TextData(self.model, 'status')
        self.elements = [grid_viz, happy_viz]

    @staticmethod
    def ascii_agent(a):
        '''
        Minority agents are X, Majority are O.
        '''
        if a.type == 0:
            return 'O'
        if a.type == 1:
            return 'X'


class HappyElement(TextElement):
    '''
    Display a text count of how many happy agents there are.
    '''

    def __init__(self):
        pass

    def render(self, model):
        return ("<b>Neighborhood Status: " + str(round(model.status,2))+ "<br/>" +
                "\n <div style='color: blue'>Average Income: " + str(round(model.mean_income,2))+ "</div><br/>" +
                "\n <div style='color: green'>Average Property Condition: " + str(round(model.mean_condition,2)) + "</div></b>")


class HouseElement(TextElement):
    '''
    Display a text count of how many low/middle/high income households
    there are. (For every 5/10 row)
    '''

    def __init__(self):
        pass

    def render(self, model):
            string = "<table><tr><th>Rows</th><th>Low</th><th>Middle</th><th>High</th>"
            print(type(string))
            for i in range(3):
                    string += "<tr><td>" + str(15*(i+1)) + "</td><td>" + str(model.house_numbers[i*3]) + "</td><td>" + str(model.house_numbers[i*3+1]) + "</td><td>" + str(model.house_numbers[i*3+2]) + "</td></tr>"
            string += "</table>"
            return string

##                return ("<table><tr><th>Rows</th></tr> <tr><td>%d</td></tr></table>" %model.house_numbers[0])
##                return ("<table><tr> <th>Rows</th><th>Low</th><th>Middle</th> <th>High</th></tr><tr><td>15</td><td>%d</td><td>%d</td><td>%d</td></tr><tr><td>30</td><td>%d</td><td>%d</td><td>%d</td></tr><tr><td>45</td><td>%d</td><td>%d</td><td>%d</td></tr></table>" %(model.house_numbers[0], model.house_numbers[1], model.house_numbers[2],model.house_numbers[3], model.house_numbers[4], model.house_numbers[5],model.house_numbers[6], model.house_numbers[7], model.house_numbers[8]))
                       



def schelling_draw(agent):
    '''
    Portrayal Method for canvas
    '''
    cmap = plt.cm.get_cmap('jet_r')
    
    portrayal = {"Shape": "rect", "h": 1.0, "w": 1.0 ,"Filled": "true", "Layer": 0}

    # continuous color scale
    #portrayal["Color"] = matplotlib.colors.to_hex((cmap(agent.income)))
    
    if agent.income < 0.33:
        portrayal["Color"] = "Red"
    elif agent.income >= 0.33 and agent.income < 0.67:
        portrayal["Color"] = "Yellow"
    else:
        portrayal["Color"] = "Green"
    
    if agent.empty == True:
        portrayal["Color"] = "White"
        #return
    return portrayal

grid_size = 45
happy_element = HappyElement()
house_element = HouseElement()
canvas_element = CanvasGrid(schelling_draw, grid_size, grid_size, 500, 500)
happy_chart = ChartModule([{"Label": "status", "Color": "Black"},
                            {"Label": "income", "Color": "Blue"},
                            {"Label": "condition", "Color": "Green"}])

house_chart_15 = ChartModule([{"Label": "low15", "Color": "Red"},
                            {"Label": "middle15", "Color": "Yellow"},
                            {"Label": "high15", "Color": "Green"}])

house_chart_45 = ChartModule([{"Label": "low45", "Color": "Red"},
                            {"Label": "middle45", "Color": "Yellow"},
                            {"Label": "high45", "Color": "Green"}])



model_params = {
    "height": grid_size,
    "width": grid_size,
    "depreciation_rate": UserSettableParameter("slider", "Depreciation Rate", 0.002, 0.00, 0.01, 0.001),
    "mobility": UserSettableParameter("slider", "Agent mobility", 0.02, 0.00, 0.10, 0.005),
    "status": UserSettableParameter("slider", "Initial Neighborhood Status", 0.25, 0.00, 1.00, 0.05),
    "stat_var": UserSettableParameter("slider", "Status Variability (Noise)", 0.025, 0.00, 0.10, 0.005),
    "gradient_param": UserSettableParameter("slider", "Influence of distance to city centre", 1., 0.00, 2., 0.05),


}

server = ModularServer(SchellingModel,
    [canvas_element, happy_element, happy_chart,
     house_element, house_chart_15, house_chart_45],
    "Schelling", model_params)
server.launch()
