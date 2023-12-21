import glob
from math import sqrt


class PMSLPData:
    def __init__(self,filename):
        self.name = filename
        self.nbTasks = None
        self.nbLocations = None
        self.nbMachines = None
        self.openingWeight = 1 #lambda 1
        self.travelWeight = 1 #lambda 2
        self.tardinessPenalty = None #lambda 3
        self.durations = None
        self.taskPositions = None
        self.locationPositions = None
        self.fixedCosts = None
        self.duedates = None
        self.travelSpeed = 1 #identical for all instances
        self.travelCost = 3 #identical for all instances

        self.distances = None

        try:
            file = open(filename,"r")
            lines = file.readlines()
            file.close()
        except:
            print("/!\        /!\        /!\        /!\ ")
            print("Could not open '"+filename+"'")
            print("Bad instance constructed")
            print("/!\        /!\        /!\        /!\ ")
            return

        taskLine = lines[0].split()
        self.nbTasks = int(taskLine[-1])

        locationLine = lines[1].split()
        self.nbLocations = int(locationLine[-1])

        machineLine = lines[2].split()
        self.nbMachines = int(machineLine[-1])

        tardLine = lines[3].split()
        self.tardinessPenalty = float(tardLine[-1])

        durationLine = clearBadListString(lines[4])
        durationLine = durationLine.split()[2:]
        self.durations = []
        for taskIndex in range(self.nbTasks):
            self.durations += [int(durationLine[taskIndex])]

        taskPosLine = clearBadListString(lines[5])
        taskPosLine = taskPosLine.split()[2:]
        self.taskPositions = []
        for taskIndex in range(self.nbTasks):
            self.taskPositions += [[int(taskPosLine[2*taskIndex]),int(taskPosLine[2*taskIndex+1])]]

        locationPosLine = clearBadListString(lines[6])
        locationPosLine = locationPosLine.split()[2:]
        self.locationPositions = []
        for locationIndex in range(self.nbLocations):
            self.locationPositions += [[int(locationPosLine[2*locationIndex]),int(locationPosLine[2*locationIndex+1])]]

        fixedCostLine = clearBadListString(lines[7])
        fixedCostLine = fixedCostLine.split()[2:]
        self.fixedCosts = []
        for locationIndex in range(self.nbLocations):
            self.fixedCosts += [int(fixedCostLine[locationIndex])]

        datesLine = clearBadListString(lines[8])
        datesLine = datesLine.split()[2:]
        self.duedates = []
        for taskIndex in range(self.nbTasks):
            self.duedates += [int(datesLine[taskIndex])]

        self.computeDistances()

    def computeDistances(self):
        self.distances = []
        for locationIndex in range(self.nbLocations):
            self.distances += [[]]
            for taskIndex in range(self.nbTasks):
                locationX = self.locationPositions[locationIndex][0]
                locationY = self.locationPositions[locationIndex][1]
                taskX = self.taskPositions[taskIndex][0]
                taskY = self.taskPositions[taskIndex][1]
                self.distances[locationIndex] += [sqrt((locationX-taskX)**2 + (locationY-taskY)**2)]


    #prints the instance
    def print(self):
        print(self.name)
        print("tasks amount:",self.nbTasks)
        print("locations amount:",self.nbLocations)
        print("machines amount:",self.nbMachines)
        print("tardiness penalty:",self.tardinessPenalty)

        print("tasks:")
        for taskIndex in range(self.nbTasks):
            line = "task "+str(taskIndex)+" "
            line += "duration "+str(self.durations[taskIndex])+" "
            line += "pos "+str(self.taskPositions[taskIndex])+" "
            line += "duedate "+str(self.duedates[taskIndex])+" "
            print(line)

        print("locations:")
        for locationIndex in range(self.nbLocations):
            line = "location "+str(locationIndex)+" "
            line += "cost "+str(self.fixedCosts[locationIndex])+" "
            line += "pos "+str(self.locationPositions[locationIndex])+" "
            print(line)

#gets all instances in the folder Instances
def getAllInstances():
    AfileNames = glob.glob('Instances/A_instances/*')
    BfileNames = glob.glob('Instances/B_instances/*')

    Ainstances = []
    for filename in AfileNames:
        Ainstances += [PMSLPData(filename)]
    Binstances = []
    for filename in BfileNames:
        Binstances += [PMSLPData(filename)]

    #returns two lists of instances
    return Ainstances,Binstances


def clearBadListString(str):
    str = str.replace(","," ")
    str = str.replace("]"," ")
    str = str.replace("["," ")
    return str
