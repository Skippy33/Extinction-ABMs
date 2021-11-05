from seaCowAgent import seaCowAgent
from mesa import Agent, Model, model
from mesa import time
from mesa.time import RandomActivation
from mesa.space import Grid, MultiGrid
from mesa.datacollection import DataCollector
from random import randint, choices, randrange, choice, shuffle
from math import sqrt as square_root
from time import sleep
global killList
killList = []
#collects kelp data
def kelpDataCollector(model):
    totalKelp = 0
    for agent in model.schedule.agents:
        if agent.type == "kelp":
            totalKelp += agent.availableFood

    return totalKelp

#collects sea cow amount
def seaCowDataCollector(model):
    totalCows = 0
    for agent in model.schedule.agents:
        if agent.type == "seaCow":
            totalCows += 1

    return totalCows

class MoneyModel(Model):
    def __init__(self, kelpAmnt, seaCowAmnt, width, height):
        #starts a grid and a scheduler
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.modelType = "additive"
        self.running = True

        # Create agents
        self.uniqueIDcounter = 0
        for i in range(kelpAmnt):
            self.uniqueIDcounter += 1
            a = kelpAgent(self.uniqueIDcounter, self)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = randrange(self.grid.width)
            y = randrange(self.grid.height)
            #if the location selected is not emty, keep retrying till you get an empty place
            while not self.grid.is_cell_empty([x, y]):
                x = randrange(self.grid.width)
                y = randrange(self.grid.height)
            #place the agent
            self.grid.place_agent(a, (x, y))

        for j in range(seaCowAmnt):
            #creates an agent
            self.uniqueIDcounter += 1
            a = seaCowAgent(self.uniqueIDcounter, self)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = randrange(self.grid.width)
            y = randrange(self.grid.height)
            #if the location selected is not empty, keep retrying till you get an empty place
            while not self.grid.is_cell_empty([x, y]):
                x = randrange(self.grid.width)
                y = randrange(self.grid.height)
            #place the agent
            self.grid.place_agent(a, (x, y))

        self.kelpCollector = DataCollector(
            model_reporters={"Total Kelp Available": kelpDataCollector}
        )
        self.seaCowCollector = DataCollector(
            model_reporters={"Total Sea Cows": seaCowDataCollector}
        )

    #just tells it to collect data and run scheduler every step
    def step(self):
        global killList
        self.schedule.step()

        #remove all dead agents
        for x in killList:
            self.grid.remove_agent(x)
            self.schedule.remove(x)
        #clear killlist
        killList = []
        #collect data
        self.kelpCollector.collect(self)
        self.seaCowCollector.collect(self)



class kelpAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        #sets type, starting food and the food timer
        self.availableFood = choices([0,1], weights=(30, 70), k=1)[0]
        self.timeToGrow = randint(1, 7)
        self.type = "kelp"

    def step(self):
        #if it's full, just skip
        if self.availableFood >= 3:
            return
        #if the growing timer is up, add food. Otherwise, remove from the growing timer
        if self.timeToGrow == 0:
            self.availableFood += 1
            self.timeToGrow = randint(5, 10)
        self.timeToGrow -= 1
        
