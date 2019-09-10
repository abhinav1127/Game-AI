'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *
import Queue

from constants import *
from utils import *
from core import *
from mycreatepathnetwork import *
from mynavigatorhelpers import *


###############################
### AStarNavigator
###
### Creates a path node network and implements the A* algorithm to create a path to the given destination.

class AStarNavigator(NavMeshNavigator):

	def __init__(self):
		NavMeshNavigator.__init__(self)


	### Create the path node network.
	### self: the navigator object
	### world: the world object
	def createPathNetwork(self, world):
		self.pathnodes, self.pathnetwork, self.navmesh = myCreatePathNetwork(world, self.agent)
		return None

	### Finds the shortest path from the source to the destination using A*.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., its current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		self.setPath(None)
		### Make sure the next and dist matrices exist
		if self.agent != None and self.world != None:
			self.source = source
			self.destination = dest
			### Step 1: If the agent has a clear path from the source to dest, then go straight there.
			###   Determine if there are no obstacles between source and destination (hint: cast rays against world.getLines(), check for clearance).
			###   Tell the agent to move to dest
			### Step 2: If there is an obstacle, create the path that will move around the obstacles.
			###   Find the path nodes closest to source and destination.
			###   Create the path by traversing the self.next matrix until the path node closest to the destination is reached
			###   Store the path by calling self.setPath()
			###   Tell the agent to move to the first node in the path (and pop the first node off the path)
			if clearShot(source, dest, self.world.getLinesWithoutBorders(), self.world.getPoints(), self.agent):
				self.agent.moveToTarget(dest)
			else:
				start = findClosestUnobstructed(source, self.pathnodes, self.world.getLinesWithoutBorders())
				end = findClosestUnobstructed(dest, self.pathnodes, self.world.getLinesWithoutBorders())
				if start != None and end != None:
					newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates())
					closedlist = []
					path, closedlist = astar(start, end, newnetwork)
					if path is not None and len(path) > 0:
						path = shortcutPath(source, dest, path, self.world, self.agent)
						self.setPath(path)
						if self.path is not None and len(self.path) > 0:
							first = self.path.pop(0)
							self.agent.moveToTarget(first)
		return None

	### Called when the agent gets to a node in the path.
	### self: the navigator object
	def checkpoint(self):
		myCheckpoint(self)
		return None

	### This function gets called by the agent to figure out if some shortcuts can be taken when traversing the path.
	### This function should update the path and return True if the path was updated.
	def smooth(self):
		return mySmooth(self)

	def update(self, delta):
		myUpdate(self, delta)


def unobstructedNetwork(network, worldLines):
	newnetwork = []
	for l in network:
		hit = rayTraceWorld(l[0], l[1], worldLines)
		if hit == None:
			newnetwork.append(l)
	return newnetwork




def astar(init, goal, network):
	path = []
	open = Queue.PriorityQueue()
	closed = []
	### YOUR CODE GOES BELOW HERE ###
	current = (distance(init, goal), init, [init], 0)

	while current[1] != None and goal != current[1]:
		closed.append(current[1])
		for edge in network:
			# print "yeet"
			if edge[0] == current[1] and edge[1] not in closed:
				newList = list(current[2])
				newList.append(edge[1])
				open.put((distance(edge[0], edge[1]) + current[3] + distance(edge[1], goal), edge[1], newList, distance(edge[0], edge[1]) + current[3]))
			elif edge[1] == current[1] and edge[0] not in closed:
				newList = list(current[2])
				newList.append(edge[0])
				# print newList
				open.put((distance(edge[0], edge[1]) + current[3] + distance(edge[0], goal), edge[0], newList, distance(edge[0], edge[1]) + current[3]))
				# print (distance(edge[0], edge[1]) + current[0], edge[0], newList)


		if open.qsize() != 0:
			current = open.get()
		else:
			return path, closed

	if current[1] == goal:
		path = current[2]

	### YOUR CODE GOES ABOVE HERE ###
	return path, closed


def myUpdate(nav, delta):
	# print "this is my update"
	# print "nav.path = "
	# print nav.path
	if nav.path != None and len(nav.path) != 0:
		if rayTraceWorld(nav.agent.position, nav.agent.moveTarget, nav.world.getGates()):
			nav.agent.stopMoving()

	### YOUR CODE GOES ABOVE HERE ###
	return None



def myCheckpoint(nav):
	## YOUR CODE GOES BELOW HERE ###
	# print "this is my checkpoint"
	# for i in range(0, len(nav.path)):
	# 	for j in range(i + 1, len(nav.path)):
	# 		if rayTraceWorld(nav.path[i], nav.path[j], nav.world.getGates()):
	# 			print "replanning"
	# 			# pathNetworkwoGates = list(nav.pathnetwork)
	# 			# for path in pathNetworkwoGates:
	# 			# 	if rayTraceWorld(path[0], path[1], nav.world.getGates()):
	# 			# 		pathNetworkwoGates.remove(path)
	# 			# newPath = astar(nav.agent.position, nav.path(-1), pathNetworkwoGates)
	# 			# if newPath[0] == None:
	# 			# 	nav.path = []
	# 			# else:
	# 			# 	nav.setPath(newPath[0])
	# 			# break
	# 			nav.agent.stopMoving()
	# 			break


	### YOUR CODE GOES ABOVE HERE ###
	return None


### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
	### YOUR CODE GOES BELOW HERE ###
	radius = agent.getRadius()

	clearShot = False
	line = (p1, p2)

	if rayTraceWorld(p1,p2, worldLines) == None:
		clearShot = True
		for k in worldPoints:
			if minimumDistance(line, k) < agent.getRadius():
				clearShot = False
				break

	return clearShot

	### YOUR CODE GOES ABOVE HERE ###
	return False