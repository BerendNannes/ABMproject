import random
import numpy as np
import scipy.signal

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.time import SimultaneousActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

class SchellingAgent(Agent):
    '''
    Schelling segregation agent
    '''
    def __init__(self, pos, model, income, pa = 0.0125):
        '''
        Create a new Schelling agent.

        Args:
                unique_id: Unique identifier for the agent.
                x, y: Agent initial location.
                agent_type: Indicator for the agent's type (minority=1, majority=0)
        '''
        super().__init__(pos, model)
        self.pos = pos
        self.income = income
        self.pa = pa
        self.move = False
        self.other = False
        
            
    def step(self):
        x, y = self.pos[0], self.pos[1]
        #move to
        if self.income == 0.:
            income = bounded_repeated_normal(0.5*(self.model.status + self.model.property_prices[x,y]), 0.1, 0., 1.)
            self.future_income = income
            self.other == True
            if self.model.property_prices[x,y] < income:
                self.move = True
            else:
                self.move = False
                
        #move away
        elif self.pa*(1.5 - self.model.status + self.model.income_gap[x,y]) < random.random():
            self.move = True
            self.other = False
        #renovate
        elif  self.model.income_gap[x,y] > 0 and self.income > self.model.condition_matrix[x, y]:
            self.move = False
            self.other = False

        
    def advance(self):
        x, y = self.pos[0], self.pos[1]
        #move to
        if self.move:
            if self.other:
                self.income = self.future_income
                self.model.income_matrix[x,y] = self.future_income
            #move away
            else:
                self.model.property_prices[x, y] = 0.5*(self.model.condition_matrix[x,y]
                                                    + self.model.average_income_matrix[x,y])
                self.model.income_matrix[x, y] = 0
        
        #not sold
        else:
            if self.other:
                self.model.property_prices[x,y] = 0.5*( self.model.property_prices[x,y] + self.future_income)
                
            #renovate
            else:
                self.model.condition_matrix[x, y] += bounded_repeated_normal(self.model.status
                                                    - self.model.condition_matrix[x, y], 0.1, 0, .5)
        

			
class SchellingModel(Model):
    '''
    Model class for the Schelling segregation model.
    '''
    def __init__(self, height, width, density,
                 deprate=0.0028, sdelta=0.025, pa = 0.0125):
        '''
        '''

        self.height = height
        self.width = width
        self.density = density

        self.schedule = SimultaneousActivation(self)
        self.grid = SingleGrid(height, width, torus=True)

        self.status = 0.5
        self.deprate = deprate
        self.sdelta = sdelta
        self.pa = pa

##        self.datacollector = DataCollector(
##                model_reporters={"happy": lambda self: self.happy},
##                agent_reporters={"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]})
        self.datacollector = DataCollector(
                model_reporters={"Status": lambda self: self.status,
                                 "Condition": lambda self: self.average_conditions,
                                 "Income": lambda self: self.average_income},
                agent_reporters={"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]})

        self.running = True


        # set conditions of properties
        #giving condition variable values in the range 0.258–0.774.
        self.condition_matrix = np.random.uniform(.258, 0.774, (width,height))
        
        self.income_matrix = np.zeros((height,width))

        # Set up agents
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if random.random() < self.density:
                income = self.condition_matrix[x,y] + bounded_repeated_normal(0., 0.025, 0., 1.)
                agent = SchellingAgent((x, y), self, income, pa=self.pa)
                self.grid.position_agent(agent, (x, y))
                self.schedule.add(agent)
                self.income_matrix[x,y] = agent.income
            else:
                income = 0
                agent = SchellingAgent((x, y), self, income, pa=self.pa)
                self.grid.position_agent(agent, (x, y))
                self.schedule.add(agent)
                self.income_matrix[x,y] = agent.income
                
                        
        #calculate average income
        self.average_income_matrix = scipy.signal.convolve2d(self.income_matrix, moore,
                                                             mode='same', boundary='wrap')/9
        #calculate average condition
        self.average_condition_matrix = scipy.signal.convolve2d(self.condition_matrix, moore,
                                                             mode='same', boundary='wrap')/9
        # set prices of properties 
        self.property_prices = 0.5*(self.condition_matrix + self.average_income_matrix)

        #Initialize rent gap
        self.rent_gap = np.maximum(self.average_condition_matrix - self.condition_matrix, 0)

        #Initialize income gap
        self.income_gap = np.maximum(self.income_matrix - self.average_income_matrix, 0)

        self.average_income = np.mean(self.income_matrix)
        self.average_conditions = np.mean(self.condition_matrix)

    def update(self):
        #status - old condition and old income
        self.status -= self.average_conditions +  self.average_income

        #update averages
        self.average_income = np.mean(self.income_matrix)
        self.average_conditions = np.mean(self.condition_matrix)
        
        self.average_income_matrix = scipy.signal.convolve2d(self.income_matrix, moore,
                                                             mode='same', boundary='wrap')/9

        #status + new condition and new income + random
        self.status += self.average_conditions +  self.average_income + bounded_repeated_normal(0,
                                                                            self.sdelta, -.5, 0.5)
        self.status = np.clip(self.status, 0., 1.)

        #Update rent gap
        self.rent_gap = np.maximum(self.average_condition_matrix - self.condition_matrix, 0)

        #Update income gap
        self.income_gap = np.maximum(self.income_matrix - self.average_income_matrix, 0)
        

            
##    def step(self):
##        '''
##        Run one step of the model. If All agents are happy, halt the model.
##        '''
##        self.happy = 0  # Reset counter of happy agents
##        self.schedule.step()
##        self.datacollector.collect(self)
##
##        if self.happy == self.schedule.get_agent_count():
##                self.running = False
        
    def step(self):
        '''
        Run one step of the model. 
        '''
        # Depricate house conditions and update house values
        self.condition_matrix -= self.deprate
        self.condition_matrix = np.maximum(self.condition_matrix, 0)
        self.property_prices = 0.5*(self.condition_matrix + self.average_income_matrix) #
        
        #update
        self.update()
        
        # Let agents move out of the neighborhood
        self.schedule.step()

        #Collect data
        self.datacollector.collect(self)
      
def bounded_repeated_normal(mu,sigma,minimum,maximum):
    mu = np.clip(mu,minimum,maximum)
    result = sigma*np.random.randn() + mu
    while result<minimum or result>maximum:
        result = sigma*np.random.randn() + mu
    return result
moore = np.array([[1,1,1], [1,1,1], [1,1,1]])

