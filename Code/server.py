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
        happy_viz = TextData(self.model, 'happy')
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
        return "Happy agents: " + str(model.happy)


def schelling_draw(agent):
    '''
    Portrayal Method for canvas
    '''

    portrayal = {"Shape": "rect", "h": 1.0, "w": 1.0 ,"Filled": "true", "Layer": 0}

    if agent.type == 0:
        portrayal["Color"] = "Red"
    else:
        portrayal["Color"] = "Green"
    if agent is None:
        portrayal["Color"] = "Black"
        #return
    return portrayal


happy_element = HappyElement()
canvas_element = CanvasGrid(schelling_draw, 50, 50, 500, 500)
happy_chart = ChartModule([{"Label": "happy", "Color": "Black"}])

model_params = {
    "height": 50,
    "width": 50,
    "density": UserSettableParameter("slider", "Agent density", 0.9, 0.1, 1.0, 0.05),
    "minority_pc": UserSettableParameter("slider", "Fraction minority", 0.5, 0.00, 1.0, 0.05),
    "homophily": UserSettableParameter("slider", "Homophily", 5, 0, 8, 1)
}

server = ModularServer(SchellingModel,
                       [canvas_element, happy_element, happy_chart],
                       "Schelling", model_params)
server.launch()
