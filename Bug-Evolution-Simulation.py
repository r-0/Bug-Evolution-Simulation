###################################################################################
### Import graphics library (pygame) and numerics library (numpy) ###
###################################################################################
import pygame                               # Python Animation Library
from pygame.locals import *
from numpy import *                         # Python fast arrays library
from numpy import round as npround          # Overwrite the default Python round function with the NumPy function
WIDTH = 640                                 # Screen size [in pixels]
HEIGHT = 640
PI15 = pi/180*15                            # Some useful numerical constants (faster than computing them every time)
PI45 = pi/180*45
PI315 = pi/180*315
PI345 = pi/180*345

def Heaviside(x):
    return 0.5*(sign(x)+1)

###################################################################################
### Define some basic objects ###
###################################################################################
class NeuralNet:
    def __init__(self, Weights, Biases):
        """ Weights is a tuple of numpy matrices, one for each network inbetween
        neurons. The matrices are mxn, where m = # neurons at the exit and
        n = # neurons at the entrance to the network """
        self.NLayers = len(Weights)
        self.Weights = Weights
        self.Biases = Biases
        
    def think(self, inputs, out_loud = 0): # inputs must be the same length as Weights[0], returns tuple of length Weights[end]
        for i in range(self.NLayers):
            inputs = dot(self.Weights[i], inputs) + self.Biases[i]
            if out_loud: print npround(inputs, 2)
            inputs = Heaviside(inputs)
            if out_loud: print inputs
        return inputs

    def rawgenome(self):
        genome = array([])
        for w in self.Weights:
            concatenate((genome, reshape(w, size(w))))

class Critter:
    def __init__(self, env):
        weights = [random.randn(10,3)/3, random.randn(10,10)/10, random.randn(3,10)/10]
        biases = [random.randn(10)*0, random.randn(10)*0, random.randn(3)*0]
        self.brain = NeuralNet(weights, biases)
        self.energy = 0
        self.env = env
        
        self.angle = 0
        self.x = random.random()*WIDTH
        self.y = random.random()*HEIGHT
        self.draw()

    def move(self):
        seefront = 0; seeleft = 0; seeright = 0;
        for f in self.env.foods:                                    # process vision
            r2 = (f.x-self.x)**2+(f.y-self.y)**2                    # distance to the food
            if r2<1600 and f.eaten == 0:
                if r2<100:
                    f.eat()
                    self.energy += 1
                else:
                    theta = (self.angle - arctan2(f.y-self.y, f.x-self.x))%2*pi
                    if PI15<theta and theta<PI45:
                        seeright = 1
                    elif theta<PI15 or theta>PI345:
                        seefront = 1
                    elif PI315<theta and theta<345:
                        seeleft = 1
        [l,speed,r] = self.brain.think([seeleft,seefront,seeright])
        if r and l: speed = 2                                       # go at double speed if it tries to turn left and right at the same time 
        if r: self.angle -= pi/20
        if l: self.angle += pi/20
        self.x = (self.x + speed*cos(self.angle)) % WIDTH
        self.y = (self.y + speed*sin(self.angle)) % HEIGHT

    def draw(self):
        self.rect = display.blit(bugimage, [self.x,self.y])         # draw the background where the bug used to be
        self.env.dirtyrects.append(self.rect)                       # Add this region to the list of regions to update when rendering

    def erase(self):
        self.env.dirtyrects.append(display.blit(background, self.rect, self.rect))

class Environment:
    def __init__(self):
        self.NCreatures = 20
        self.NFood = 20
        self.ItsPerGen = 30000
        self.n = 0;

        self.dirtyrects = []                                        # For updating only regions of the display that have stuff on them

        self.critters = []
        for i in range(self.NCreatures):
            self.critters.append(Critter(self))
        self.foods = []
        for i in range(self.NFood):
            self.foods.append(Food(self))

    def update(self):
        self.n += 1
        if self.n > self.ItsPerGen:                                 # Start over
            self.newgeneration()
        
        if random.random()<0.01 and len(self.foods)<50:
            self.foods.append(Food(self))

        self.eatenfoods = []

    def newgeneration(self):
        for c in self.critters:
            print c.energy
            if c.energy > max(self.energies): self.bestcritter = c
            self.energies.append(c.energy)
        display.blit(background, [0,0])
        self.__init__()
        pygame.display.update()
    
        print self.bestcritter.energy
        print self.bestcritter.brain.think([0,0,0])
        print self.bestcritter.brain.think([1,0,0])
        print self.bestcritter.brain.think([0,1,0])
        print self.bestcritter.brain.think([0,0,1])

class Food:
    def __init__(self, env):
        self.x = random.random()*WIDTH
        self.y = random.random()*HEIGHT
        self.eaten = 0
        self.env = env
        self.rect = display.blit(foodimage, [self.x,self.y])
        self.env.dirtyrects.append(self.rect)
        
    def eat(self):
        self.env.eatenfoods.append(self)
        self.eaten = 1
        self.env.dirtyrects.append(display.blit(background, self.rect, self.rect))


def mainloop():
    env = Environment()
    env.energies = [0]

    exit_sim = 0
    while not exit_sim:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                exit_sim = 1
            if event.type == KEYDOWN:
                print event.key
        
        env.update()
        
        for c in env.critters:
            c.erase()
            c.move()
        
        for f in env.eatenfoods:
            env.foods.remove(f)
        
        for c in env.critters:
            c.draw()
        
        pygame.display.update(env.dirtyrects)
        env.dirtyrects = []

    return env

###################################################################################
### Initialize the display window ###
###################################################################################
pygame.init()
display = pygame.display.set_mode ((WIDTH, HEIGHT), HWSURFACE)
background = display.convert()

bugimage = pygame.image.load("bug.bmp")
foodimage = pygame.image.load("food.bmp")

###################################################################################
### Define parameters for the simulation and run ###
###################################################################################

env = mainloop()

    
print "End of simulation"


