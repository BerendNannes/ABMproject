import random
import numpy as np

from mesa import Model, Agent
from mesa.time import SimultaneousActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

class SchellingAgent(Agent):
	'''
	Schelling segregation agent
	'''
	def __init__(self, pos, model, income):
		'''
		Create a new Schelling agent.

		Args:
			unique_id: Unique identifier for the agent.
			x, y: Agent initial location.
			agent_type: Indicator for the agent's type (minority=1, majority=0)
		'''
		super().__init__(pos, model)
		self.pos = pos

		# assign wealth to agent types
		self.income = income
		self.p_move = 0

	def step(self):
		neighbors_income = 0
		n_neighbors = 0
		for neighbor in self.model.grid.neighbor_iter(self.pos):
			neighbors_income += neighbor.income
			n_neighbors += 1
		income_gap = np.absolute(self.income - (neighbors_income/n_neighbors))

		#If unhappy, move:
		self.p_move = self.model.abandon_factor*(1.5 - self.model.S + income_gap)
			
	def advance(self):
		if random.random() < self.p_move:
			self.model.grid.remove_agent(self)
			self.model.schedule.remove(self)
	
			
class SchellingModel(Model):
	'''
	Model class for the Schelling segregation model.
	'''

	def __init__(self, height, width, initial_condition, status_var, abandon_factor, det_rate):
		'''
		'''

		self.height = height
		self.width = width
		self.abandon_factor = abandon_factor
		self.status_var = status_var

		self.schedule = SimultaneousActivation(self)
		self.grid = SingleGrid(height, width, torus=True)
		
		# set conditions of properties
		self.initial_condition = initial_condition
		self.conditions = np.zeros((width,height))
		for i in range(width):
			for j in range(height):
				self.conditions[i][j] = bounded_normal(self.initial_condition,0.1,0,1)

		self.happy = 0

		self.datacollector = DataCollector(
			model_reporters={"status": lambda self: self.S,
							 "income": lambda self: self.mean_income,
							 "condition": lambda self: self.mean_condition},
			agent_reporters={"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]})
		
		self.S = self.initial_condition
		
		self.det_rate = det_rate
		self.running = True

		# Set up agents
		# We use a grid iterator that returns
		# the coordinates of a cell as well as
		# its contents. (coord_iter)
		for cell in self.grid.coord_iter():
			x = cell[1]
			y = cell[2]

			agent = SchellingAgent((x, y), self, self.conditions[x][y])
			self.grid.position_agent(agent, (x, y))
			self.schedule.add(agent)
			
		self.mean_income = self.calc_mean_income()
		self.mean_condition = np.mean(self.conditions)

	def step(self):
		'''
		Run one step of the model. If All agents are happy, halt the model.
		'''
		self.schedule.step()
		
		# fill empty cells
		while self.grid.exists_empty_cells() == True:
			pos = self.grid.find_empty()
			price = self.calc_price(pos)
			rent_gap = self.calc_rent_gap(pos)
			temp = 0
			while True:
				temp += 1
				income = bounded_normal(0.5*(self.S+price), 0.1, 0.25*(self.S+price), min(0.75*(self.S+price),1))
				if income >= price:
					break
				if temp > 10 or price > 0.97:
					income = price
					rent_gap = 0
					break
					
			if rent_gap > 0 and income > self.conditions[pos[0]][pos[1]]:
				self.conditions[pos[0]][pos[1]] += bounded_normal(self.S - self.conditions[pos[0]][pos[1]],0.1,0,0.5)
				np.clip(self.conditions,0,1)
				
			agent = SchellingAgent(pos, self, income)
			self.grid.place_agent(agent,pos)
			self.schedule.add(agent)

			
		# update property condition
		self.conditions -= self.det_rate
		self.conditions = np.clip(self.conditions,0,1)
		
		prev_income = self.mean_income
		prev_condition = self.mean_condition
		
		# update neighborhood status
		self.mean_income = self.calc_mean_income()
		self.mean_condition = np.mean(self.conditions)
		self.S += (self.mean_income + self.mean_condition) - (prev_income + prev_condition) + np.random.randn()*self.status_var
		self.S = np.clip(self.S,0,1)
		
		self.datacollector.collect(self)
			
			
	def calc_mean_income(self):
		return np.mean([cell[0].income for cell in self.grid.coord_iter()])
		
			
	def calc_price(self, pos):
		n_neighbors = 0
		radius = 1
		while n_neighbors == 0:
			neighbors_income = 0
			for neighbor in self.grid.get_neighbors(pos,True,radius):
				neighbors_income += neighbor.income
				n_neighbors += 1	
			radius += 1
		avg_income = neighbors_income/n_neighbors
		return np.clip((self.conditions[pos[0]][pos[1]]+avg_income)/2,0,1)
		
	def calc_rent_gap(self, pos):
		total_condition = 0
		n_neighbors = 0
		for neighbor in self.grid.get_neighborhood(pos,True):
			total_condition += self.conditions[neighbor[0]][neighbor[1]]
			n_neighbors += 1
		avg_condition = total_condition/n_neighbors
		return self.conditions[pos[0]][pos[1]] - avg_condition
			
def bounded_normal(mu,sigma,minimum,maximum):
	mu = np.clip(mu,minimum,maximum)
	result = sigma*np.random.randn() + mu
	return np.clip(result,minimum,maximum)
	