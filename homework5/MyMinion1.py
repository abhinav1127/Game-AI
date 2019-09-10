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

    def __init__(self, position, orientation, world, image=NPC, speed=SPEED, viewangle=360, hitpoints=HITPOINTS,
                 firerate=FIRERATE, bulletclass=SmallBullet):
        Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
        self.states = [Idle]
        ### Add your states to self.states (but don't remove Idle)
        ### YOUR CODE GOES BELOW HERE ###
        self.states.append(Move)

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

    def execute(self, delta=0):
        State.execute(self, delta)
        ### YOUR CODE GOES BELOW HERE ###

        if len(self.agent.world.getEnemyBases(self.agent.team)) != 0 \
                or len(self.agent.world.getEnemyTowers(self.agent.team)) != 0:
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

    def execute(self, delta=0):
        if self.victim is not None:
            print "Hey " + str(self.victim) + ", I don't like you!"
        self.agent.changeState(Idle)


##############################
### YOUR STATES GO HERE:

class Move(State):

    def enter(self, oldstate):
        #250,100
        # self.agent.moveToTarget((250,250))
        self.point1 = (200, 50)
        self.point2 = (300, 50)
        self.point3 = (300, 150)
        self.point4 = (200, 150)
        self.moveTarget = self.point1


    def execute(self, delta=0):
        if not self.agent.isMoving():
            if self.moveTarget == self.point1:
                self.agent.moveToTarget(self.point2)
                self.moveTarget = self.point2
            elif self.moveTarget == self.point2:
                self.agent.moveToTarget(self.point3)
                self.moveTarget = self.point3
            elif self.moveTarget == self.point3:
                self.agent.moveToTarget(self.point4)
                self.moveTarget = self.point4
            else:
                self.agent.moveToTarget(self.point1)
                self.moveTarget = self.point1


