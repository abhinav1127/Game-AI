import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *
from randomnavmeshnavigator import *
			
			
			
			
nav = RandomNavMeshNavigator()
	
			
world = GameWorld(SEED, (1000,1000), (1000,1000))
agent = Agent(AGENT, (300, 300), 0, SPEED, world)
world.setPlayerAgent(agent)
polygons = [[(840.0, 126.0), (740.0, 870.0), (680.0, 126.0)], [(525.0, 38.0), (425.0, 265.0), (405.0, 38.0)], [(200.0, 92.0), (130.0, 640.0), (40.0, 92.0)], [(680.0, 974.0), (560.0, 220.0), (440.0, 560.0), (350.0, 380.0), (350.0, 974.0)]]
world.initializeTerrain(polygons, (255, 0, 0), 2)
world.setPlayerAgent(agent)
agent.setNavigator(nav)
nav.setWorld(world)
world.initializeRandomResources(NUMRESOURCES)
world.debugging = True
world.run()
