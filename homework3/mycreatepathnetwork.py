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

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *
from random import shuffle

from constants import *
from utils import *
from core import *

# Creates a path node network that connects the midpoints of each nav mesh together
def myCreatePathNetwork(world, agent = None):
	nodes = []
	edges = []
	polys = []
	### YOUR CODE GOES BELOW HERE ###

	tempCorners = world.getPoints()
	triangleLines = []


	# shuffle(tempCorners)


	for i in range(0, len(tempCorners)):

		# possibleSuccessors = []

		# for j in range(i + 1, len(tempCorners)):
		# 	if rayTraceDiffLines(tempCorners[i],tempCorners[j], world.getLines()) == None and rayTraceDiffLines(tempCorners[i],tempCorners[j], triangleLines) == None:
		# 		possibleSuccessors.append(tempCorners[j])
        #
        #
		# for j in range(0, len(possibleSuccessors)):
		# 	for k in range(1, len(possibleSuccessors)):
		# 		if rayTraceDiffLines(possibleSuccessors[j],possibleSuccessors[k], world.getLines()) == None and rayTraceDiffLines(possibleSuccessors[j],possibleSuccessors[k], triangleLines)== None:
		# 			if not isInside(tempCorners[i], possibleSuccessors[j], possibleSuccessors[k], world.getPoints()) and not triangleInObstacle(tempCorners[i], possibleSuccessors[j], possibleSuccessors[k], world.getObstacles()) :
		# 				triangleLines.append((tempCorners[i], possibleSuccessors[j]))
		# 				triangleLines.append((possibleSuccessors[j], possibleSuccessors[k]))
		# 				triangleLines.append((tempCorners[i], possibleSuccessors[k]))
		# 				polys.append((tempCorners[i], possibleSuccessors[j], possibleSuccessors[k]))

		for j in range(i + 1, len(tempCorners)):
			a = tempCorners[i]
			b = tempCorners[j]
			if rayTraceDiffLines(a,b, world.getLines()) == None and rayTraceDiffLines(a,b, triangleLines) == None:
				for k in range(j + 1, len(tempCorners)):
					c = tempCorners[k]
					if rayTraceDiffLines(a, c, world.getLines()) == None and rayTraceDiffLines(b,c, world.getLines()) == None and rayTraceDiffLines(a,c, triangleLines)== None and rayTraceDiffLines(b,c, triangleLines)== None:
						if not isInside(a, b, c, world.getPoints()) and not triangleInObstacle(a, b, c, world.getObstacles()) :
							triangleLines.append((a, b))
							triangleLines.append((b, c))
							triangleLines.append((a, c))
							polys.append((a, b, c))


	changed = True

	while changed:
		changed = False
		for i in range(0, len(polys)):
			for j in range(i + 1, len(polys)):
				result = polygonsCanCombine(polys[i], polys[j])

				if result[0] == True:
					del polys[j]
					del polys[i]
					polys.append(tuple(result[1]))
					changed = True
					break

			if changed:
				break


	# for poly in list(polys):
	# 	print
	# 	poly = list(poly)
	# 	print poly
	# 	i = 0
	# 	while i < len(poly):
	# 		print poly
	# 		print poly[i]
	# 		print poly[i][0]
	# 		if i != len(poly) - 1:
    #
    #
	# 			x = poly[i][0] + poly[i + 1][0] / 2
	# 			y = poly[i][1] + poly[i + 1][1] / 2
	# 		else:
	# 			x = poly[i][0] + poly[-1][0] / 2
	# 			y = poly[i][1] + poly[-1][1] / 2
    #
    #
	# 		print x
	# 		print y
	# 		nodes.append((x, y))
	# 		i += 1

	for poly in polys:
		for i in range(0, len(poly)):
			if i == len(poly) - 1:
				x = (poly[i][0] + poly[0][0]) / 2
				y = (poly[i][1] + poly[0][1]) / 2
			else:
				x = (poly[i][0] + poly[i + 1][0]) / 2
				y = (poly[i][1] + poly[i + 1][1]) / 2

			onPolygon = False
			# for o in world.getObstacles():
			# 	print world.getPoints()
			# 	if pointOnPolygon((x,y), o.getLines()):
			# 		onPolygon = True
			# 		break

			for l in world.getLines():
				if minimumDistance(l, (x,y)) < agent.getMaxRadius():
					onPolygon = True
					break

			if not onPolygon:
				nodes.append((x,y))


	for poly in polys:
		centroid = [sum(p) / len(poly) for p in zip(*poly)]

		onPolygon = False
		for l in world.getLines():
			if minimumDistance(l, centroid) < agent.getMaxRadius():
				onPolygon = True
				break

		if not onPolygon:
			nodes.append(centroid)



	### YOUR CODE GOES BELOW HERE ###

	i = 0
	for i in range(0, len(nodes)):
		for j in range(i + 1, len(nodes)):

			result = False
			line = (nodes[i], nodes[j])

			if rayTraceWorld(nodes[i], nodes[j], world.getLines()) == None:
				for k in world.getPoints():
					if minimumDistance(line, k) < agent.getMaxRadius():
						result = True

				if result == False:
					edges.append(line)
				#
				# if result == False:
				# 	x = (poly[0][0] + poly[1][0]) / 2
				# 	y = (poly[0][1] + poly[1][1]) / 2
				# 	inside = False
				# 	for p in world.getPoints():
				# 		if pointInsidePolygonPoints((x, y), p):
				# 			inside = True
				# 			break
				# 	if not inside:
				# 		edges.append(line)


	### YOUR CODE GOES ABOVE HERE ###
	return nodes, edges, polys

def rayTraceDiffLines(p1, p2, worldLines):
	for l in worldLines:
		if (l[0] != p1 and l[0] != p2 and l[1] != p1 and l[1] != p2):
			hit = rayTraceNoEndpoints(p1, p2, l)
			if hit != None:
				return hit
	return None


# A utility function to calculate area
# of triangle formed by (x1, y1),
# (x2, y2) and (x3, y3)

def area(x1, y1, x2, y2, x3, y3):

	return abs((x1 * (y2 - y3) + x2 * (y3 - y1)
				+ x3 * (y1 - y2)) / 2.0)


# A function to check whether point P(x, y)
# lies inside the triangle formed by
# A(x1, y1), B(x2, y2) and C(x3, y3)
def isInside(p1, p2, p3, worldPoints):


	x1 = p1[0]
	y1 = p1[1]

	x2 = p2[0]
	y2 = p2[1]

	x3 = p3[0]
	y3 = p3[1]

	for l in worldPoints:

		if l != p1 and l !=p2 and l != p3:
			# Calculate area of triangle ABC
			A = area(x1, y1, x2, y2, x3, y3)

			# Calculate area of triangle PBC
			A1 = area(l[0], l[1], x2, y2, x3, y3)

			# Calculate area of triangle PAC
			A2 = area(x1, y1, l[0], l[1], x3, y3)

			# Calculate area of triangle PAB
			A3 = area(x1, y1, x2, y2, l[0], l[1])

			# Check if sum of A1, A2 and A3
			# is same as A
			if (A == A1 + A2 + A3):
				return True

	return False

def centerTriangle(p1, p2, p3):
	x = (p1[0] + p2[0] + p3[0]) / 3
	y = (p1[1] + p2[1] + p3[1]) / 3
	return (x,y)

def triangleInObstacle(p1, p2, p3, obstacles):
	for o in obstacles:
		if pointInsidePolygonLines(centerTriangle(p1,p2,p3), o.getLines()):
			return True

	return False

def polygonsCanCombine(poly1, poly2):

	similarPoints = []
	for s1 in poly1:
		for s2 in poly2:
			if s1 == s2:

				similarPoints.append(s1)


	if len(similarPoints) < 2:
		return [False, None]

	newPolygon = []
	for s1 in range(0, len(similarPoints)):
		for s2 in range(s1 + 1, len(similarPoints)):

			# found = False
            #
			# for p1 in poly1:
			# 	if found:
			# 		newPolygon.append(p1)
			# 	else:
			# 		if p1 == similarPoints[s1]:
			# 			found = True
            #
			# for p2 in poly1:
			# 	if found:
			# 		if p2 == similarPoints[s2]:
			# 			found = False
			# 		else:
			# 			newPolygon.append(p2)
            #
			# newPolygon.append(similarPoints[s2])
            #
			# #found is currently False
            #
			# for p2 in poly2:
			# 	if found:
			# 		newPolygon.append(p2)
			# 	else:
			# 		if p2 == similarPoints[s2]:
			# 			found = True
            #
			# for p1 in poly2:
			# 	if found:
			# 		newPolygon.append(p1)
			# 	else:
			# 		if p1 == similarPoints[s1]:
			# 			found = False

			# for p1 in poly1:
			# 	found = False
            #
			# 	if p1 == similarPoints[s1] or p1 == similarPoints[s2]:
			# 		if p1 == similarPoints[s1]:
			# 			newPolygon.append(p1)
			#
			# 			for p2 in poly2:
			#
			# 				if found:
            #
				# else:
				# 	newPolygon.append(p1)

			copy1 = list(copy.deepcopy(poly1))
			copy2 = list(copy.deepcopy(poly2))

			copy1.remove(similarPoints[s1])
			copy1.remove(similarPoints[s2])
			copy2.remove(similarPoints[s1])
			copy2.remove(similarPoints[s2])

			copy1.append(similarPoints[s1])
			copy1.extend(copy2)
			copy1.append(similarPoints[s2])


			newPolygon = tuple(copy1)

			if isConvex(newPolygon) == True:
				return [True, newPolygon]

	return [False, None]

def myDoDebug(nav, world, point):
	# Draw green cross at mouse location
	drawCross(world.debug, point, (0, 255, 0), 10, 2)
	for poly in nav.navmesh:
		if pointInsidePolygonPoints(point, poly):
			# Draw the polygon red if the point is inside
			drawPolygon(poly, world.debug, (255, 0, 0), 3, False)
			centroid = [sum(p)/len(poly) for p in zip(*poly)]
			# Draw a cross in the center of the polygon
			drawCross(world.debug, centroid, (255, 0, 0), 5, 2)