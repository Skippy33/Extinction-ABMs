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
            self.timeToGrow = randint(1, 7)
        self.timeToGrow -= 1
        


class seaCowAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        #sets type, starting food, age and the food timer
        self.currentFood = randint(3,5)
        self.type = "seaCow"
        self.matingThreshhold = 15
        self.age = 1
        #self.timeToDie = choices([0,1,2,3,4,5,6,7], weights=(30, 70), k=1)[0]

    #when it steps
    def step(self):
        self.age += 1
        if self.currentFood >= self.matingThreshhold:
            self.matingThreshhold = 10
            self.target = self.findMate()
        else:
            self.target = self.findFood()
        #pathfind
        self.pathfinding()
        #if outa food, die
        if self.currentFood <= 0:
            killList.append(self)
    
    #how to pathfind using A*
    def pathfinding(self):
        #get the nearest food or a random place to go

        if type(self.target) != tuple:
            self.targetpos = self.target.pos
        else:
            self.targetpos = self.target

        #if there is no food, return
        if self.target == "no food":
            return

        #if the selected kelp has no food, choose a different one
        if type(self.target) != tuple:
            if self.target.type != "seaCow":
                if self.target.availableFood < 1:
                    self.target = self.findFood()

        #get vars for the actual A* movement
        foodx, foody = self.targetpos
        selfx, selfy = self.pos
        possiblePlaces = self.model.grid.get_neighborhood(pos = self.pos, moore=True, include_center=False)
        placesFs = []
        placesGs = []

        #get the F values for each of the possible moves
        for neighbor in possiblePlaces:
            #if it can eat, do so
            
            if self.targetpos == neighbor and type(self.target) != tuple:
                #breeds
                if self.target.type == "seaCow":
                    #creates an agent
                    self.model.uniqueIDcounter += 1
                    a = seaCowAgent(self.model.uniqueIDcounter, self.model)
                    #add to scheduler and creat
                    self.model.schedule.add(a)
                    self.model.grid.place_agent(a, self.pos)
                    #select a new food target
                    self.matingThreshhold = 15
                    self.target = self.findFood()

                elif self.target.type == "kelp":
                    self.eat()


            #get the x and y of the neighbor
            neihborx, neighbory = neighbor
            #get the H, G, and F values
            H = square_root((abs(neihborx-foodx)**2 + (abs(neighbory-foody))**2))
            G = square_root((abs(neihborx-selfx)**2 + (abs(neighbory-selfy))**2))
            F = G + H
            #append F to the list
            placesFs.append(F)
            placesGs.append(G)
        
        # G = cost from start to intermediate
        # H = estimate distance to end (use pythagoras)
        # F = G + H, estimate of how good this location is to move to

        #get the coord of the best place to move to
        minF = min(placesFs)
        placeInList = placesFs.index(minF)
        
        #have it eat
        self.currentFood -= (placesGs[placeInList]/2)

        #finally move that agent, anything after this won't be ran
        self.model.grid.move_agent(self, possiblePlaces[placeInList])


    #identifies location of a food
    def findFood(self):
        i = 0
        #while it has not spotted food
        while i < 100:
            #continue the counter
            i += 1
            #get the neighborhood as an iterable
            neighborhood = self.model.grid.iter_neighbors(
            pos = tuple(self.pos), 
            include_center = False, 
            radius = i, 
            moore = True)
            randomizerList = []
            #for each position in the iterable, check if it's occupied
            for gridLocation in neighborhood:
                #if empty, pass over it
                if self.model.grid.is_cell_empty(gridLocation.pos):
                    pass
                #if it is, check to see if the agent is the right type
                else:
                    #if it is, than check if it has food
                    if gridLocation.type == 'kelp':
                        #if it does, than return its location
                        if gridLocation.availableFood > 0:
                            randomizerList.append(gridLocation)
                        else:
                            pass
            
            if randomizerList:
                shuffle(randomizerList)
                return randomizerList[0]
    
        self.target = None

        if self.target == None:
            #sets a random nearby location if there's no food
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False,
                radius = 1
            )
            #says that movement has already happened if there's no food
            return choice(possible_steps)


    def findMate(self):
        i = 0
        #while it has not spotted food
        while i < 10:
            #continue the counter
            i += 1
            #get the neighborhood as an iterable
            neighborhood = self.model.grid.iter_neighbors(pos = tuple(self.pos), include_center = False, radius = i, moore = True)
            #for each position in the iterable, check if it's occupied
            for gridLocation in neighborhood:
                #if empty, pass over it
                if self.model.grid.is_cell_empty(gridLocation.pos):
                    pass
                #if it is, check to see if the agent is the right type
                else:
                    #if it is, than check if it has food
                    if gridLocation.type == 'seaCow':
                        #if it does, than return its location
                        if gridLocation.currentFood > 15:
                            return gridLocation
                        else:
                            pass
        return self.findFood()


    
    def eat(self):
        #add all food from plant to self, set the kelp to have no food
        self.currentFood += self.target.availableFood
        self.target.availableFood = 0
