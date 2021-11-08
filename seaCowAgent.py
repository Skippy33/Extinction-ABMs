from mesa import Agent
from random import randint, choice, shuffle, choices
from math import sqrt as square_root
from math import hypot as hypotenuse
from time import time



class seaCowAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, age = 1):
        super().__init__(unique_id, model)
        #sets type, starting food, age and the food timer
        self.currentFood = randint(4,7)
        self.type = "seaCow"
        self.matingThreshhold = 15
        self.age = age

    #when it steps
    def step(self):
        self.age += .1
        if self.currentFood >= self.matingThreshhold and self.age > 15 and self.age < 50:
            self.matingThreshhold = 10
            self.target = self.findMate()
        else:
            self.target = self.findFood()
        #pathfind
        self.pathfinding()
        #if outa food, die
        if self.age > 70:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            print("old age")
            return
        if self.currentFood <= 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            print("starved")
            return
        if self.age < 15:
            if choices([True, False], weights=(1, 100), k=1)[0]:
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                print("died as child")
                return
    
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
            if self.target.type == "kelp":
                self.target = self.findFood()

        #get vars for the actual A* movement
        foodx, foody = self.targetpos
        selfx, selfy = self.pos
        possiblePlaces = self.model.grid.get_neighborhood(pos = self.pos, moore=True, include_center=False)
        placesFs = []
        placesGs = []

        #get the F values for each of the possible moves
        for neighbor in possiblePlaces:
            if self.targetpos == neighbor and type(self.target) != tuple:
                #breeds
                if self.target.type == "seaCow":
                    #creates an agent
                    self.model.uniqueIDcounter += 1
                    a = seaCowAgent(self.model.uniqueIDcounter, self.model)
                    #add to scheduler and create
                    self.model.schedule.add(a)
                    self.model.grid.place_agent(a, self.pos)
                    #select a new food target
                    self.matingThreshhold = 15
                    self.target = self.findFood()

                elif self.target.type == "kelp":
                    self.eat()


            #get the x and y of the neighbor
            neighborx, neighbory = neighbor
            #get the H, G, and F values
            H = hypotenuse(abs(foodx-neighborx), abs(foody-neighbory))
            G = hypotenuse(abs(neighborx-selfx), abs(neighbory-selfy))
            if self.age < 15:
                G *= 1.1
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
        self.currentFood -= (placesGs[placeInList]/2.5)

        #finally move that agent, anything after this won't be ran
        self.model.grid.move_agent(self, possiblePlaces[placeInList])

        if self.targetpos == self.pos and type(self.target) != tuple:
            #breeds
            if self.target.type == "seaCow":
                #creates an agent
                if choices([True, False], weights=(20, 100), k=1)[0]:
                    self.model.uniqueIDcounter += 1
                    a = seaCowAgent(self.model.uniqueIDcounter, self.model)
                    #add to scheduler and create
                    self.model.schedule.add(a)
                    self.model.grid.place_agent(a, self.pos)
                    #select a new food target
                    self.matingThreshhold = 15
                    self.target = self.findFood()
                self.model.uniqueIDcounter += 1
                a = seaCowAgent(self.model.uniqueIDcounter, self.model)
                #add to scheduler and create
                self.model.schedule.add(a)
                self.model.grid.place_agent(a, self.pos)
                #select a new food target
                self.matingThreshhold = 15
                self.target = self.findFood()
            elif self.target.type == "kelp":
                self.eat()



    #identifies location of a food
    def findFood(self):
        i = 1
        #while it has not spotted food
        while i < 100:
            #continue the counter
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
                    #optimizes, basically checks if the location has already been checked
                    x, y = self.pos
                    constraintupx = x+i
                    constraintdownx = x-i
                    constraintupy = y+i
                    constraintdowny = y-i
                    x, y = gridLocation.pos
                    if x>constraintupx or x<constraintdownx or y>constraintupy or y<constraintdowny:
                        pass
                    else:
                        #if it is, than check if it has food
                        if gridLocation.type == 'kelp':
                            #if it does, than return its location
                            randomizerList.append(gridLocation)

            i += 1
            if randomizerList:
                shuffle(randomizerList)
                return randomizerList[0]
        


            #sets a random nearby location if there's no food
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False,
            radius = 1
            )
        #says that movement has already happened if there's no food
        i += 2
        return choice(possible_steps)


    def findMate(self):
        i = 0
        #while it has not spotted food
        while i < 7:
            #continue the counter
            i += 1
            #get the neighborhood as an iterable
            neighborhood = self.model.grid.iter_neighbors(pos = tuple(self.pos), 
            include_center = False, 
            radius = i, 
            moore = True)
            #for each position in the iterable, check if it's occupied

            for gridLocation in neighborhood:
                #if empty, pass over it
                
                if self.model.grid.is_cell_empty(gridLocation.pos):
                    pass
                #if it is, check to see if the agent is the right type
                else:
                    #optimizes, basically checks if the location has already been checked
                    x, y = self.pos
                    constraintupx = x+i
                    constraintdownx = x-i
                    constraintupy = y+i
                    constraintdowny = y-i
                    x, y = gridLocation.pos
                    if x>constraintupx or x<constraintdownx or y>constraintupy or y<constraintdowny:
                        pass

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
        #if this is the additive model, do its style of eating
        if self.model.modelType == "additive":
            self.currentFood += self.target.availableFood
            self.target.availableFood = 0
            self.target = self.findFood()
        #elif it is the duplicative model, do its style of eating
        elif self.model.modelType == "duplicative":
            self.currentFood += 1
            self.model.grid.remove_agent(self.target)
            self.model.schedule.remove(self.target)
