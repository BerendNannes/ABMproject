import random
import numpy as np

from mesa import Model, Agent
from mesa.time import SimultaneousActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

def bounded_normal(mu,sigma,minimum,maximum):
    mu = np.clip(mu,minimum,maximum)
    while True:
        X = np.random.normal(mu,sigma)
        if X >= minimum and X <= maximum:
            return X

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
        '''
        super().__init__(pos, model)
        self.pos = pos
        self.income = income
        self.empty = False
        self.move_out = False

    def step(self):
        # shortened references
        model = self.model
        conditions = model.conditions

        neighbors = model.grid.get_neighbors(self.pos,True)
        neighborhood = model.grid.get_neighborhood(self.pos,True)

        # Calculate income gap
        neighbor_incomes = [neighbor.income for neighbor in neighbors]
        mean_income = sum(neighbor_incomes) / len(neighbor_incomes) 
        income_gap = max(0.0, self.income - mean_income)

        x,y = self.pos

        # Decide if occupant moves out
        U = np.random.uniform()
        if not self.empty and U < model.mobility*(1.5 - model.status + income_gap):
            self.move_out = True
            self.empty = True
            self.price = 0.5*(conditions[x,y]+mean_income)

        if self.empty:
            # Prepare list with neighboring property conditions
            neighborhood_conditions = []
            for cell in neighborhood:
                neighborhood_conditions.append(conditions[cell[0],cell[1]])

            # Calculate rent gap
            mean_condition = sum(neighborhood_conditions) / len(neighborhood_conditions)
            self.rent_gap = max(0.0, mean_condition - conditions[x,y])

    def advance(self):
        # shortened references
        model = self.model
        conditions = model.conditions

        if self.move_out:
            model.income_change -= self.income
            self.income = 0
            self.move_out = False

        elif self.empty:
            bound = model.status+self.price            
            income = bounded_normal(0.5*bound,0.1,0.25*bound,min(1.0,0.75*bound))

            if income > self.price:
                model.income_change += income - self.income
                self.income = income

                x,y = self.pos

                # Decide if new owners improve the property
                if self.rent_gap > 0 and income > conditions[x,y]:
                    improvement = bounded_normal(model.status-conditions[x,y],0.1,0.0,0.5)
                    conditions[x,y] = np.clip(conditions[x,y]+improvement,0,1)

                self.empty = False

            else:
                self.price = 0.5*(self.price + income)

class SchellingModel(Model):
    '''
    Model class for the Schelling segregation model.
    '''

    def __init__(self, height, width, depreciation_rate, mobility, status, stat_var):
        # Set model parameters
        self.depreciation_rate = depreciation_rate
        self.mobility = mobility
        self.status = status
        self.stat_var = stat_var

        # Global tracking variables
        self.mean_income = 0.0

        self.schedule = SimultaneousActivation(self)
        self.grid = SingleGrid(height, width, torus=True)
        
        self.datacollector = DataCollector(
            model_reporters={"status": lambda m : m.status, 
                             "income": lambda m : m.mean_income,
                             "condition": lambda m: m.mean_condition},
            agent_reporters={"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]})

        self.running = True

        self.conditions = np.zeros((width,height))

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cell in self.grid.coord_iter():
            x,y = cell[1],cell[2]

            self.conditions[x,y] = bounded_normal(0.5,0.1,0.0,1.0)

            # Income initially differs little from property conditions
            while True:
                income = self.conditions[x,y] + np.random.normal(0.0,0.025)
                if income >= 0.0 and income <= 1.0:
                    self.mean_income += income
                    break

            agent = SchellingAgent((x, y), self, income)
            self.grid.position_agent(agent, (x, y))
            self.schedule.add(agent)

        self.mean_condition = np.sum(self.conditions) / self.conditions.size
        self.mean_income /= self.conditions.size

    def step(self):
        '''
        Run one step of the model.
        '''

        # For tracking change
        old_conditions = np.copy(self.conditions)

        # Initialize change tracking variables
        self.income_change = 0.0

        self.schedule.step()

        # Update property conditions
        self.conditions -= self.depreciation_rate
        self.conditions = np.clip(self.conditions,0,1)

        conditions_change = self.conditions - old_conditions

        # Update neighborhood status
        self.status += (self.income_change + np.sum(conditions_change)) / (conditions_change.size)
        self.status += np.random.normal(0.0, self.stat_var)
        self.status = np.clip(self.status,0,1)

        # Update datacollector variables
        self.mean_income += self.income_change / self.conditions.size
        self.mean_condition = np.sum(self.conditions) / self.conditions.size

        self.datacollector.collect(self)
