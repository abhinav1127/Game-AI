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
from moba2 import *
from btnode import *
import random

###########################
### SET UP BEHAVIOR TREE


def treeSpec(agent):
	myid = str(agent.getTeam())
	spec = None
	### YOUR CODE GOES BELOW HERE ###
	# spec = [(Sequence, 1), [(HitpointDaemon, 0.8), (Retreat, 0.8)], (ChaseHero, 1)]
	# spec = [(Sequence, 1), (MoveToTarget, (175, 175)), (Retreat, -0.1)]
	# spec = [(Selector, 1), [(RetreatDaemon, 0.5, 2), (Retreat, 0.5, 3)],
	# 		[(Selector, 4), [(BuffDaemon, 2, 5), [(Sequence, 6), (ChaseHero, 7), (KillHero, 8)]],
	# 		 [(Sequence, 9), (ChaseMinion, 10), (KillMinion, 11)]]]
	# spec = [(Sequence, 1), (MoveToCenter, 2), (ChaseMinion, 7), (KillMinion, 8), (ChaseHero, 11), (KillHero, 12)]
	spec = [(Selector, 1), [(RetreatDaemon, 0.3, 2), [(Sequence, 3), (Retreat, 4), (MoveToCenter, 5)]], [(Sequence, 6), (ChaseHero, 9), (KillHero, 10)]]
	### YOUR CODE GOES ABOVE HERE ###
	return spec

def myBuildTree(agent):
	myid = str(agent.getTeam())
	root = None
	### YOUR CODE GOES BELOW HERE ###

	### YOUR CODE GOES ABOVE HERE ###
	return root

### Helper function for making BTNodes (and sub-classes of BTNodes).
### type: class type (BTNode or a sub-class)
### agent: reference to the agent to be controlled
### This function takes any number of additional arguments that will be passed to the BTNode and parsed using BTNode.parseArgs()
def makeNode(type, agent, *args):
	node = type(agent, args)
	return node

###############################
### BEHAVIOR CLASSES:


##################
### Taunt
###
### Print disparaging comment, addressed to a given NPC
### Parameters:
###   0: reference to an NPC
###   1: node ID string (optional)

class Taunt(BTNode):

	### target: the enemy agent to taunt

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		# First argument is the target
		if len(args) > 0:
			self.target = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target is not None:
			print "Hey", self.target, "I don't like you!"
		return ret

##################
### MoveToTarget
###
### Move the agent to a given (x, y)
### Parameters:
###   0: a point (x, y)
###   1: node ID string (optional)

class MoveToTarget(BTNode):
	
	### target: a point (x, y)
	
	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		# First argument is the target
		if len(args) > 0:
			self.target = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def enter(self):
		BTNode.enter(self)
		self.agent.navigateTo(self.target)

	def execute(self, delta=0):
		ret = BTNode.execute(self, delta)
		if self.target == None:
			# failed executability conditions
			print "exec", self.id, "false"
			return False
		elif distance(self.agent.getLocation(), self.target) < self.agent.getRadius():
			# Execution succeeds
			print "exec", self.id, "true"
			return True
		else:
			##Mine
			self.dodgeIfNeeded(self.agent.world.getBullets())
			enemyNearby = False
			nearest = None
			dist = 1000000000
			for enemy in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
				if distance(enemy.getLocation(), self.agent.getLocation()) < BIGBULLETRANGE:
					enemyNearby = True
					if isinstance(enemy, Hero):
						nearest = enemy
						dist = distance(enemy.getLocation(), self.agent.getLocation())
					if dist > distance(enemy.getLocation(), self.agent.getLocation()):
						nearest = enemy
						dist = distance(enemy.getLocation(), self.agent.getLocation())

			if nearest:
				self.agent.turnToFace(nearest.getLocation())
				self.agent.shoot()
				if dist < self.agent.getMaxRadius() * AREAEFFECTRANGE:
					self.agent.areaEffect()
				return False
			# executing
			return None
		return ret


	def dodgeIfNeeded(self, bullets):
		if self.agent.canDodge():
			maxDamage = 0
			incoming = None
			for bullet in bullets:
				if bullet.getOwner().team != self.agent.team and distance(self.agent.getLocation(), bullet.getLocation()) < 20:
					if bullet.getDamage() > maxDamage:
						maxDamage = bullet.getDamage()
						incoming = bullet
			if incoming:
				self.agent.dodge(incoming.orientation + 90)

##################
### Retreat
###
### Move the agent back to the base to be healed
### Parameters:
###   0: percentage of hitpoints that must have been lost to retreat
###   1: node ID string (optional)


class Retreat(BTNode):
	
	### percentage: Percentage of hitpoints that must have been lost
	
	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.percentage = 0.5
		# First argument is the factor
		if len(args) > 0:
			self.percentage = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def enter(self):
		BTNode.enter(self)
		base = self.agent.world.getBaseForTeam(self.agent.getTeam())
		if base:
			self.agent.navigateTo(base.getLocation())
	
	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.agent.getHitpoints() > self.agent.getMaxHitpoints() * self.percentage:
			# fail executability conditions
			print "exec", self.id, "false"
			return False
		elif self.agent.getHitpoints() == self.agent.getMaxHitpoints():
			# Exection succeeds
			print "exec", self.id, "true"
			return True
		else:
			##Mine
			self.dodgeIfNeeded(self.agent.world.getBullets())
			enemyNearby = False
			nearest = None
			dist = 1000000000
			for enemy in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
				if distance(enemy.getLocation(), self.agent.getLocation()) < BIGBULLETRANGE:
					enemyNearby = True
					if isinstance(enemy, Hero):
						nearest = enemy
						dist = distance(enemy.getLocation(), self.agent.getLocation())
					if dist > distance(enemy.getLocation(), self.agent.getLocation()):
						nearest = enemy
						dist = distance(enemy.getLocation(), self.agent.getLocation())

			if nearest:
				self.agent.turnToFace(nearest.getLocation())
				self.agent.shoot()
				if dist < self.agent.getMaxRadius() * AREAEFFECTRANGE:
					self.agent.areaEffect()
				return False
			# executing
			return None
		return ret

	def dodgeIfNeeded(self, bullets):
		if self.agent.canDodge():
			maxDamage = 0
			incoming = None
			for bullet in bullets:
				if bullet.getOwner().team != self.agent.team and distance(self.agent.getLocation(),
																		  bullet.getLocation()) < 20:
					if bullet.getDamage() > maxDamage:
						maxDamage = bullet.getDamage()
						incoming = bullet
			if incoming:
				self.agent.dodge(incoming.orientation + 90)

##################
### ChaseMinion
###
### Find the closest minion and move to intercept it.
### Parameters:
###   0: node ID string (optional)


class ChaseMinion(BTNode):

	### target: the minion to chase
	### timer: how often to replan

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		self.timer = 120
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]

	def enter(self):
		BTNode.enter(self)
		self.timer = 120
		enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		if len(enemies) > 0:
			best = None
			dist = 0
			for e in enemies:
				if isinstance(e, Minion):
					d = distance(self.agent.getLocation(), e.getLocation())
					if best == None or d < dist:
						best = e
						dist = d
			self.target = best
		if self.target is not None:
			navTarget = self.chooseNavigationTarget()
			if navTarget is not None:
				self.agent.navigateTo(navTarget)


	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target == None or self.target.isAlive() == False:
			# failed execution conditions
			print "exec", self.id, "false"
			return False
		elif self.target is not None and distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE:
			# succeeded
			print "exec", self.id, "true"
			return True
		else:
			##mine
			self.dodgeIfNeeded(self.agent.world.getBullets())

			enemyNearby = False
			nearest = None
			dist = 1000000000
			for enemy in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
				if distance(enemy.getLocation(), self.agent.getLocation()) < BIGBULLETRANGE:
					enemyNearby = True
					if isinstance(enemy, Hero):
						nearest = enemy
						dist = distance(enemy.getLocation(), self.agent.getLocation())
					if dist > distance(enemy.getLocation(), self.agent.getLocation()):
						nearest = enemy
						dist = distance(enemy.getLocation(), self.agent.getLocation())
			if enemyNearby:
				return True

			if distance(self.agent.getLocation(), self.agent.world.getEnemyBases(self.agent.team)[0].position) < TOWERBULLETRANGE:
				return False

			# executing
			self.timer = self.timer - 1
			if self.timer <= 0:
				self.timer = 120
				navTarget = self.chooseNavigationTarget()
				if navTarget is not None:
					self.agent.navigateTo(navTarget)
			return None
		return ret

	def dodgeIfNeeded(self, bullets):
		if self.agent.canDodge():
			maxDamage = 0
			incoming = None
			for bullet in bullets:
				if bullet.getOwner().team != self.agent.team and distance(self.agent.getLocation(), bullet.getLocation()) < 20:
					if bullet.getDamage() > maxDamage:
						maxDamage = bullet.getDamage()
						incoming = bullet
			if incoming:
				self.agent.dodge(incoming.orientation + 90)

	def chooseNavigationTarget(self):
		if self.target is not None:
			return self.target.getLocation()
		else:
			return None

##################
### KillMinion
###
### Kill the closest minion. Assumes it is already in range.
### Parameters:
###   0: node ID string (optional)


class KillMinion(BTNode):

	### target: the minion to shoot

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]

	def enter(self):
		BTNode.enter(self)
		self.agent.stopMoving()
		enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		if len(enemies) > 0:
			best = None
			dist = 0
			for e in enemies:
				if isinstance(e, Minion):
					d = distance(self.agent.getLocation(), e.getLocation())
					if best == None or d < dist:
						best = e
						dist = d
			self.target = best


	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target == None or distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE:
			# failed executability conditions
			print "exec", self.id, "false"
			return False
		elif self.target.isAlive() == False:
			# succeeded
			print "exec", self.id, "true"
			return True
		else:
			# executing
			self.shootAtTarget()

			###Mine
			self.agent.navigateTo(self.target.getLocation())
			self.dodgeIfNeeded(self.agent.world.getBullets())
			self.areaAttack(self.agent.world.getEnemyNPCs(self.agent.getTeam()))

			enemyNearby = False
			nearest = None
			dist = 1000000000
			for enemy in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
				if isinstance(enemy, Hero) and distance(enemy.getLocation(), self.agent.getLocation()) < BIGBULLETRANGE:
					return False

			if distance(self.agent.getLocation(), self.agent.world.getEnemyBases(self.agent.team)[0].position) < TOWERBULLETRANGE:
				return False

			return None
		return ret

	def shootAtTarget(self):
		if self.agent is not None and self.target is not None:
			self.agent.turnToFace(self.target.getLocation())
			self.agent.shoot()

	def dodgeIfNeeded(self, bullets):
		if self.agent.canDodge():
			maxDamage = 0
			incoming = None
			for bullet in bullets:
				if bullet.getOwner().team != self.agent.team and distance(self.agent.getLocation(), bullet.getLocation()) < 20:
					if bullet.getDamage() > maxDamage:
						maxDamage = bullet.getDamage()
						incoming = bullet
			if incoming:
				self.agent.dodge(incoming.orientation + 90)

	def areaAttack(self, enemies):
		for enemy in enemies:
			if distance(enemy.getLocation(), self.agent.getLocation()) < self.agent.getMaxRadius() * AREAEFFECTRANGE:
				self.agent.areaEffect()
				break



##################
### ChaseHero
###
### Move to intercept the enemy Hero.
### Parameters:
###   0: node ID string (optional)

class ChaseHero(BTNode):

	### target: the hero to chase
	### timer: how often to replan

	def ParseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		self.timer = 120
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]

	def enter(self):
		BTNode.enter(self)
		self.timer = 120
		enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		for e in enemies:
			if isinstance(e, Hero):
				self.target = e
				navTarget = self.chooseNavigationTarget()
				if navTarget is not None:
					self.agent.navigateTo(navTarget)
				return None


	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target == None or self.target.isAlive() == False:
			# fails executability conditions
			print "exec", self.id, "false"
			return False
		elif distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE:
			# succeeded
			print "exec", self.id, "true"
			return True
		else:
			##mine
			self.dodgeIfNeeded(self.agent.world.getBullets())
			enemyNearby = False
			nearest = None
			dist = 1000000000
			for enemy in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
				if distance(enemy.getLocation(), self.agent.getLocation()) < BIGBULLETRANGE:
					enemyNearby = True
					if isinstance(enemy, Hero):
						nearest = enemy
						dist = distance(enemy.getLocation(), self.agent.getLocation())
					if dist > distance(enemy.getLocation(), self.agent.getLocation()):
						nearest = enemy
						dist = distance(enemy.getLocation(), self.agent.getLocation())

			if nearest:
				self.agent.turnToFace(nearest.getLocation())
				self.agent.shoot()
				if dist < self.agent.getMaxRadius() * AREAEFFECTRANGE and distance(self.target.getLocation(), self.agent.getLocation()) > 100:
					self.agent.areaEffect()

			if distance(self.agent.getLocation(), self.agent.world.getEnemyBases(self.agent.team)[0].position) < TOWERBULLETRANGE:
				return False

			# executing
			self.timer = self.timer - 1
			if self.timer <= 0:
				navTarget = self.chooseNavigationTarget()
				if navTarget is not None:
					self.agent.navigateTo(navTarget)
			return None
		return ret

	def chooseNavigationTarget(self):
		if self.target is not None:
			return self.target.getLocation()
		else:
			return None

	def shootAtTarget(self):
		if self.agent is not None and self.target is not None:
			self.agent.turnToFace(self.target.getLocation())
			self.agent.shoot()

	def dodgeIfNeeded(self, bullets):
		if self.agent.canDodge():
			maxDamage = 0
			incoming = None
			for bullet in bullets:
				if bullet.getOwner().team != self.agent.team:
					if distance(self.agent.getLocation(), bullet.getLocation()) < 30:
						if bullet.getDamage() > maxDamage:
							maxDamage = bullet.getDamage()
							incoming = bullet
			if incoming:
				self.agent.dodge(incoming.orientation + 90)

	def areaAttack(self, enemies):
		for enemy in enemies:
			if distance(enemy.getLocation(), self.agent.getLocation()) < self.agent.getMaxRadius() * AREAEFFECTRANGE:
				self.agent.areaEffect()
				break

##################
### KillHero
###
### Kill the enemy hero. Assumes it is already in range.
### Parameters:
###   0: node ID string (optional)


class KillHero(BTNode):

	### target: the minion to shoot

	def ParseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]

	def enter(self):
		BTNode.enter(self)
		self.agent.stopMoving()
		enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		for e in enemies:
			if isinstance(e, Hero):
				self.target = e
				return None

	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target == None or distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE:
			# failed executability conditions
			if self.target == None:
				print "foo none"
			else:
				print "foo dist", distance(self.agent.getLocation(), self.target.getLocation())
			print "exec", self.id, "false"
			return False
		elif self.target.isAlive() == False:
			# succeeded
			print "exec", self.id, "true"
			return True
		else:
			#Mine
			if distance(self.agent.getLocation(), self.target.getLocation()) < 30:
				x = random.randint(-60, 60)
				y = random.randint(-60, 60)
				self.agent.navigateTo((x,y))
			else:
				self.agent.navigateTo(self.target.getLocation())
			self.dodgeIfNeeded(self.agent.world.getBullets())
			self.areaAttack(self.agent.world.getEnemyNPCs(self.agent.getTeam()))

			if distance(self.agent.getLocation(), self.agent.world.getEnemyBases(self.agent.team)[0].position) < TOWERBULLETRANGE:
				return False

			#executing
			self.shootAtTarget()
			return None
		return ret

	def shootAtTarget(self):
		if self.agent is not None and self.target is not None:
			self.agent.turnToFace(self.target.getLocation())
			self.agent.shoot()

	def dodgeIfNeeded(self, bullets):
		if self.agent.canDodge():
			maxDamage = 0
			incoming = None
			for bullet in bullets:
				if bullet.getOwner().team != self.agent.team and distance(self.agent.getLocation(), bullet.getLocation()) < 30 and isinstance(bullet.getOwner(), Hero):
					if bullet.getDamage() > maxDamage:
						maxDamage = bullet.getDamage()
						incoming = bullet
			if incoming:
				self.agent.dodge(incoming.orientation + 90)

	def areaAttack(self, enemies):
		for enemy in enemies:
			if distance(enemy.getLocation(), self.agent.getLocation()) < self.agent.getMaxRadius() * AREAEFFECTRANGE:
				self.agent.areaEffect()
				break

##################
### HitpointDaemon
###
### Only execute children if hitpoints are above a certain threshold.
### Parameters:
###   0: percentage of hitpoints that must be remaining to pass the daemon check
###   1: node ID string (optional)


class HitpointDaemon(BTNode):
	
	### percentage: percentage of hitpoints that must be remaining to pass the daemon check
	
	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.percentage = 0.5
		# First argument is the factor
		if len(args) > 0:
			self.percentage = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.agent.getHitpoints() < self.agent.getMaxHitpoints() * self.percentage:
			# Check failed
			print "exec", self.id, "fail"
			return False
		else:
			# Check didn't fail, return child's status
			return self.getChild(0).execute(delta)
		return ret

##################
### BuffDaemon
###
### Only execute children if agent's level is significantly above enemy hero's level.
### Parameters:
###   0: Number of levels above enemy level necessary to not fail the check
###   1: node ID string (optional)

class BuffDaemon(BTNode):

	### advantage: Number of levels above enemy level necessary to not fail the check

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.advantage = 0
		# First argument is the advantage
		if len(args) > 0:
			self.advantage = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		hero = None
		# Get a reference to the enemy hero
		enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		for e in enemies:
			if isinstance(e, Hero):
				hero = e
				break
		if hero == None or self.agent.level <= hero.level + self.advantage:
			# fail check
			print "exec", self.id, "fail"
			return False
		else:
			# Check didn't fail, return child's status
			return self.getChild(0).execute(delta)
		return ret





#################################
### MY CUSTOM BEHAVIOR CLASSES

##################
### RetreatDaemon
###
### Only execute children if hitpoints are below a certain threshold.
### Parameters:
###   0: percentage of hitpoints that must be remaining to pass the daemon check
###   1: node ID string (optional)


class RetreatDaemon(BTNode):

	### percentage: percentage of hitpoints that must be remaining to fail the daemon check

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.percentage = 0.5
		# First argument is the factor
		if len(args) > 0:
			self.percentage = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def execute(self, delta=0):
		ret = BTNode.execute(self, delta)
		if self.agent.getHitpoints() > self.agent.getMaxHitpoints() * self.percentage:
			# Check failed
			print "exec", self.id, "fail"
			return False
		else:
			# Check didn't fail, return child's status
			return self.getChild(0).execute(delta)
		return ret


### MoveToTarget
###
### Move the agent to a given (x, y)
### Parameters:
###   0: node ID string (optional)

class MoveToCenter(BTNode):

	### target: a point (x, y)

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		if self.agent.team == 1:
			self.target = (375, 526)
		else:
			self.target = (650, 741)
		# else:
		# 	self.target =
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]

	def enter(self):
		BTNode.enter(self)
		self.agent.navigateTo(self.target)

	def execute(self, delta=0):
		ret = BTNode.execute(self, delta)
		if self.target == None:
			# failed executability conditions
			print "exec", self.id, "false"
			return False
		elif distance(self.agent.getLocation(), self.target) < self.agent.getRadius():
			# Execution succeeds
			print "exec", self.id, "true"
			return True
		else:
			##Mine
			self.dodgeIfNeeded(self.agent.world.getBullets())
			enemyNearby = False
			nearest = None
			dist = 1000000000
			for enemy in self.agent.world.getEnemyNPCs(self.agent.getTeam()):
				if distance(enemy.getLocation(), self.agent.getLocation()) < BIGBULLETRANGE:
					enemyNearby = True
					if isinstance(enemy, Hero):
						nearest = enemy
						dist = distance(enemy.getLocation(), self.agent.getLocation())
					if dist > distance(enemy.getLocation(), self.agent.getLocation()):
						nearest = enemy
						dist = distance(enemy.getLocation(), self.agent.getLocation())

			if nearest:
				self.agent.turnToFace(nearest.getLocation())
				self.agent.shoot()
				if dist < self.agent.getMaxRadius() * AREAEFFECTRANGE:
					self.agent.areaEffect()
				return False
			# executing
			return None
		return ret

	def dodgeIfNeeded(self, bullets):
		if self.agent.canDodge():
			maxDamage = 0
			incoming = None
			for bullet in bullets:
				if bullet.getOwner().team != self.agent.team and distance(self.agent.getLocation(), bullet.getLocation()) < 20:
					if bullet.getDamage() > maxDamage:
						maxDamage = bullet.getDamage()
						incoming = bullet
			if incoming:
				self.agent.dodge(incoming.orientation + 90)