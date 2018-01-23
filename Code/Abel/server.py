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

    @staticmethod
    def ascii_agent(a):
        '''
        Minority agents are X, Majority are O.
        '''
        if a.income < 0.4:
            return 'L'
        elif a.income < 0.6:
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
        return "Status: " + str(round(model.status,3))

class ConditionElement(TextElement):
    def __init__(self):
        pass
    def render(self, model):
        return "Average Property Condition: " + str(round(
                                    model.average_conditions, 3))
class IncomeElement(TextElement):
    def __init__(self):
        pass
    def render(self, model):
        return "Average Income: " + str(round(model.average_income, 3))

class LegendElement(TextElement):
    '''
    Display a text count of how many happy agents there are.
    '''

    def __init__(self):
        pass

    def render(self, model):
        return  "Red: Low Income\n Purple: Middle Income \n Blue: High Income \n"
    

def schelling_draw(agent):
    '''
    Portrayal Method for canvas
    '''
    portrayal = {"Shape": "rect", "h": 1.0, "w": 1.0 ,"Filled": "true", "Layer": 0}
    if agent.income == 0.:
        portrayal["Color"] = "Green"
    elif agent.income < 0.4:
        portrayal["Color"] = "Red"
    elif agent.income < 0.6:
        portrayal["Color"] = "Purple"
    else:
        portrayal["Color"] = "Blue"
    return portrayal


status_element = StatusElement()
legend_element = LegendElement()
condition_element = ConditionElement()
income_element = IncomeElement()
canvas_element = CanvasGrid(schelling_draw, 50, 50, 500, 500)
status_chart = ChartModule([{"Label": "Status", "Color": "Black"},
                            {"Label": "Condition", "Color": "Green"},
                            {"Label": "Income", "Color": "Yellow"}])

model_params = {
    "height": 50,
    "width": 50,
    "density": UserSettableParameter("slider", "Agent density", 0.9, 0.1, 1.0, 0.05),
    "deprate": UserSettableParameter("slider", "Depreciation Rate", 0.0028, 0.00, 0.1, 0.01),
    "sdelta": UserSettableParameter("slider", "Sdelta", 0.025, 0, .1, 0.01),
    "pa": UserSettableParameter("slider", "Pa", 0.0125, 0, .1, 0.01)
}

server = ModularServer(SchellingModel,
                       [canvas_element, legend_element, condition_element, income_element,
                        status_element, status_chart],
                       "Schelling", model_params)
server.launch()
