from PMSLPSolution import *
from random import sample,randint,random
from copy import copy
from time import time


class PMSLPHeuristic:
    def __init__(self,instance):
        self.instance = instance
        self.priorityList = self.getPriorityOrder()
        self.bestSolution = None
        self.bestValue = 1000000000
        self.searches = 0


    def search(self):
        solution = self.getSolution()
        solution.computeValue()
        value = solution.value
        self.searches += 1
        if value < self.bestValue:
            self.bestValue = value
            self.bestSolution = solution
        return value


    def solve(self,maxTime=5):
        startTime = time()

        while (time()-startTime) < maxTime:
            self.search()

        print(self.searches,"searches done")
        return self.bestSolution


    def getSolution(self):
        instance = self.instance

        installations = sample([k for k in range(instance.nbLocations)],instance.nbMachines)
        affectations = [None]*instance.nbTasks
        startDates = [None]*instance.nbTasks

        siteTasks = [[] for k in range(instance.nbLocations)]
        siteTime = [0]*instance.nbLocations

        for j in self.priorityList:
            minDist = 1000000000
            bestSite = None
            for k in installations:
                dist = instance.distances[k][j]
                if dist < minDist:
                    minDist = dist
                    bestSite = k
            affectations[j] = bestSite
            siteTasks[bestSite] += [j]


            travelTime = instance.distances[bestSite][j]/instance.travelSpeed
            start = max(siteTime[bestSite],travelTime)
            siteTime[bestSite] = start+instance.durations[j]
            startDates[j] = start


        return PMSLPSolution(instance,installations,affectations,startDates)

    def getPriorityOrder(self):
        instance = self.instance
        priority = [instance.durations[j]+ instance.duedates[j] for j in range(instance.nbTasks)]
        priorityList = [(j,priority[j]) for j in range(instance.nbTasks)]
        priorityList.sort(key=takeSecond)
        priorityList = [priorityList[j][0] for j in range(instance.nbTasks)]
        return priorityList


def takeSecond(elem):
    return elem[1]
