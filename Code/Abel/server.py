from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from mesa.visualization.TextVisualization import (
    TextData, TextGrid, TextVisualization
)

from model import SchellingModel


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
        status_viz = TextData(self.model, 'status')
        self.elements = [grid_viz, status_viz]

##    @staticmethod
##    def ascii_agent(a):
##        '''
##        Minority agents are X, Majority are O.
##        '''
##        if a.type == 0:
##            return 'O'
##        if a.type == 1:
##            return 'X'
    @staticmethod
    def ascii_agent(a):
        '''
        Minority agents are X, Majority are O.
        '''
        if a.wealth < -0.2:
            return 'L'
        elif a.wealth < 0.2:
            return 'M'
        else:
            return 'H'


class StatusElement(TextElement):
    '''
    Display a text count of how many happy agents there are.
    '''

    def __init__(self):
        pass

    def render(self, model):
        return "Status: " + str(model.status)

def schelling_draw(agent):
    '''
    Portrayal Method for canvas
    '''
    portrayal = {"Shape": "rect", "h": 1.0, "w": 1.0 ,"Filled": "true", "Layer": 0}
    if agent.wealth < 0.4:
        portrayal["Color"] = "Red"
    elif agent.wealth < 0.6:
        portrayal["Color"] = "Purple"
    else:
        portrayal["Color"] = "Blue"
    return portrayal


status_element = StatusElement()
canvas_element = CanvasGrid(schelling_draw, 50, 50, 500, 500)
status_chart = ChartModule([{"Label": "status", "Color": "Black"}])

model_params = {
    "height": 50,
    "width": 50,
    "density": UserSettableParameter("slider", "Agent density", 0.9, 0.1, 1.0, 0.05),
    "minority_pc": UserSettableParameter("slider", "Fraction minority", 0.5, 0.00, 1.0, 0.05),
    "homophily": UserSettableParameter("slider", "Homophily", 5, 0, 8, 1)
}

server = ModularServer(SchellingModel,
                       [canvas_element, status_element, status_chart],
                       "Schelling", model_params)
server.launch()
