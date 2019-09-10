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

from constants import *
from utils import *
from core import *
from moba import *

class MyMinion(Minion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.states = [Idle]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###
		self.states.append(Move)
		self.states.append(AttackTower)
		self.states.append(StandStill)
		self.states.append(AttackBase)
		# self.states.append(DodgeMode)

		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Minion.start(self)
		self.changeState(Idle)

############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###

		if len(self.agent.world.getEnemyBases(self.agent.team)) != 0 \
				or  len(self.agent.world.getEnemyTowers(self.agent.team)) != 0:
			self.agent.changeState(Move)

		### YOUR CODE GOES ABOVE HERE ###
		return None

##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)

class Taunt(State):

	def parseArgs(self, args):
		self.victim = args[0]

	def execute(self, delta = 0):
		if self.victim is not None:
			print "Hey " + str(self.victim) + ", I don't like you!"
		self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:

class Move(State):

	def enter(self, oldstate):
		# sets move to target to first tower, or if not base
		if self.agent.world.getEnemyTowers(self.agent.team):
			self.agent.navigateTo(self.agent.world.getEnemyTowers(self.agent.team)[0].position)
		elif self.agent.world.getEnemyBases(self.agent.team):
			self.agent.navigateTo(self.agent.world.getEnemyBases(self.agent.team)[0].position)

		else:
			self.agent.changeState(Idle)

	def execute(self, delta = 0):

		attackingBase = False
		if self.agent.world.getEnemyTowers(self.agent.team):
			target = self.agent.world.getEnemyTowers(self.agent.team)[0]
		elif self.agent.world.getEnemyBases(self.agent.team):
			target = self.agent.world.getEnemyBases(self.agent.team)[0]
			attackingBase = True
		else:
			self.agent.changeState(Idle)
			return


		if not self.agent.isMoving(): #or target.position != self.agent.position: #or target not in self.agent.world.getEnemyTowers(self.agent.team) or target not in self.agent.world.getEnemyBases(self.agent.team):
			if self.agent.world.getEnemyTowers(self.agent.team):
				self.agent.navigateTo(target.position)
			elif self.agent.world.getEnemyBases(self.agent.team):
				self.agent.navigateTo(target.position)
				attackingBase = True


		for enemy in self.agent.world.getEnemyNPCs(self.agent.team):
			if enemy in self.agent.getVisible() and distance(self.agent.position, enemy.position) < 150 and distance(self.agent.position, target.position) > 200:
				self.agent.turnToFace(enemy.position)
				self.agent.shoot()
				break

		if not attackingBase:
			for tower in self.agent.world.getEnemyTowers(self.agent.team):
				if tower in self.agent.getVisible() and distance(self.agent.position, tower.position) < 150:
					self.agent.turnToFace(tower.position)
					self.agent.shoot()
				if tower in self.agent.getVisible() and distance(self.agent.position, tower.position) < 100:
					self.agent.changeState(AttackTower, tower)
		else:
			if target in self.agent.getVisible() and distance(self.agent.position, target.position) < 100:
				self.agent.changeState(AttackTower, target)
			if target in self.agent.getVisible() and distance(self.agent.position, target.position) < 150:
				self.agent.changeState(AttackBase, target)

		for friend in self.agent.world.getNPCsForTeam(self.agent.team):
			if friend != self.agent and distance(self.agent.position, friend.position) < 30 and friend.isMoving():
				self.agent.changeState(StandStill, self)


class AttackTower(State):

	def enter(self, oldstate):
		# self.agent.stopMoving()
		self.agent.turnToFace(self.target.position)
		self.agent.shoot()

		self.point1 = (self.target.position[0] + 65, self.target.position[1] + 65)
		self.point2 = (self.target.position[0] + 65, self.target.position[1] - 65)
		self.point3 = (self.target.position[0] - 65, self.target.position[1] - 65)
		self.point4 = (self.target.position[0] - 65, self.target.position[1] + 65)

		self.currTarget = self.point1
		currDistance = distance(self.agent.getLocation(), self.point1)

		if distance(self.point2, self.agent.getLocation()) < currDistance:
			self.currTarget = self.point2
			currDistance = distance(self.point2, self.agent.getLocation())

		if distance(self.point3, self.agent.getLocation()) < currDistance:
			self.currTarget = self.point3
			currDistance = distance(self.point3, self.agent.getLocation())

		if distance(self.point4, self.agent.getLocation()) < currDistance:
			self.currTarget = self.point4
			currDistance = distance(self.point4, self.agent.getLocation())

		self.agent.moveToTarget(self.currTarget)


	def parseArgs(self, args):
		self.target = args[0]

	def execute(self, delta=0):
		# if self.target in self.agent.getVisible() and distance(self.agent.position, self.target.position) < 150:
		self.agent.turnToFace(self.target.position)
		self.agent.shoot()

		if self.target.getHitpoints() == 0:
			self.agent.changeState(Move)

		if distance(self.currTarget, self.agent.position) < 20:
			if self.currTarget == self.point1:
				self.currTarget = self.point2
			elif self.currTarget == self.point2:
				self.currTarget = self.point3
			elif self.currTarget == self.point3:
				self.currTarget = self.point4
			elif self.currTarget == self.point4:
				self.currTarget = self.point1
			self.agent.moveToTarget(self.currTarget)


		# if distance(self.target.position, self.agent.position) < 100:
		# 	# self.agent.changeState(DodgeMode, self.target)
		# 	self.agent.stopMoving()

		# for friend in self.agent.world.getNPCsForTeam(self.agent.team):
		# 	if friend != self.agent and distance(self.agent.position, friend.position) < 30 and friend.isMoving():
		# 		self.agent.changeState(StandStill, self)


class AttackBase(State):

	def enter(self, oldstate):
		# self.agent.stopMoving()
		self.agent.turnToFace(self.target.position)
		self.stopped = False

	def parseArgs(self, args):
		self.target = args[0]

	def execute(self, delta=0):
		# if self.target in self.agent.getVisible() and distance(self.agent.position, self.target.position) < 150:
		self.agent.turnToFace(self.target.position)
		self.agent.shoot()

		if self.target.getHitpoints() == 0:
			self.agent.changeState(Move)

		if not self.stopped and distance(self.target.position, self.agent.position) < 100:
			# self.agent.changeState(DodgeMode, self.target)
			self.agent.stopMoving()
			# print "diff"
			# print abs(self.target.position[0] - self.agent.position[0]) > abs(self.target.position[1] - self.agent.position[1])
			# if abs(self.target.position[0] - self.agent.position[0]) > abs(self.target.position[1] - self.agent.position[1]):
			# 	print "a"
			# 	self.point1 = (self.agent.position[0] + 140, self.agent.position[1])
			# else:
			# 	print "b"
			# 	self.point1 = (self.agent.position[0], self.agent.position[1] + 140)
			if self.agent.team == 1:
				self.point1 = (self.target.position[0] - 90, self.target.position[0] - 90)
			else:
				self.point1 = (self.target.position[0] + 90, self.target.position[0] + 90)
			self.point2 = (self.agent.position[0], self.agent.position[1])
			self.currTarget = self.point1
			self.agent.moveToTarget(self.currTarget)
			self.stopped = True
		elif self.stopped:
			if distance(self.currTarget, self.agent.position) < 15:
				if self.currTarget == self.point1:
					self.currTarget = self.point2
				elif self.currTarget == self.point2:
					self.currTarget = self.point1
				self.agent.moveToTarget(self.currTarget)


# for friend in self.agent.world.getNPCsForTeam(self.agent.team):
		# 	if friend != self.agent and distance(self.agent.position, friend.position) < 30 and friend.isMoving():
		# 		self.agent.changeState(StandStill, self)


class StandStill(State):

	def enter(self, oldstate):
		self.agent.stopMoving()

	def execute(self, delta = 0):
		friendTooClose = True
		for friend in self.agent.world.getNPCsForTeam(self.agent.team):
			if friend != self.agent and distance(self.agent.position, friend.position) < 30 and friend.isMoving():
				self.agent.stopMoving()
				friendTooClose = True
				break
			else:
				friendTooClose = False

		if friendTooClose == False:
			self.agent.changeState(Move)

