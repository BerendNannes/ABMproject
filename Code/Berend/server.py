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
		return ("<b>Neighborhood Status: " + str(round(model.S,2))+ "<br/>" +
				"\n <div style='color: blue'>Average Income: " + str(round(model.mean_income,2))+ "</div><br/>" +
				"\n <div style='color: green'>Average Property Condition: " + str(round(model.mean_condition,2)) + "</div></b>")


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
	
	if agent is None:
		portrayal["Color"] = "Black"
		#return
	return portrayal

grid_size = 50
happy_element = HappyElement()
canvas_element = CanvasGrid(schelling_draw, grid_size, grid_size, 500, 500)
happy_chart = ChartModule([{"Label": "status", "Color": "Black"},
							{"Label": "income", "Color": "Blue"},
							{"Label": "condition", "Color": "Green"}])

model_params = {
	"height": grid_size,
	"width": grid_size,
	"initial_condition": UserSettableParameter("slider", "Initial Neighborhood Condition", 0.25, 0.00, 1.00, 0.05),
	"abandon_factor": UserSettableParameter("slider", "Abandonment Factor", 0.02, 0.00, 0.10, 0.005),
	"status_var": UserSettableParameter("slider", "Status Variability (Noise)", 0.025, 0.00, 0.10, 0.005),
	"det_rate": UserSettableParameter("slider", "Deterioration Rate", 0.001, 0.00, 0.01, 0.001)


}

server = ModularServer(SchellingModel,
	[canvas_element, happy_element, happy_chart],
	"Schelling", model_params)
server.launch()
