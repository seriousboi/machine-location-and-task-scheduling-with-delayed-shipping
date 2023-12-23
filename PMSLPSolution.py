from math import ceil


class PMSLPSolution:
    def __init__(self,instance,installations,affectations,startDates):
        self.instance = instance
        self.installations = installations
        self.affectations = affectations
        self.startDates = startDates
        self.value = None
        self.openingValue = None
        self.travelValue = None
        self.latenessValue = None

    def print(self,onlyValue = False):
        self.computeValue()
        print("cost:",round(self.value,1))
        print("lateness cost:",round(self.latenessValue,1))
        print("travel cost:",round(self.travelValue,1))
        print("opening cost:",round(self.openingValue,1))
        print()

        if not onlyValue:
            line = "Locations opened: "
            for installation in self.installations:
                line += str(installation)+" "
            print(line,"\n")

            for taskIndex in range(self.instance.nbTasks):
                print("Task",taskIndex,"in",self.affectations[taskIndex],"at",round(self.startDates[taskIndex],1))

    def computeValue(self):
        if self.value != None:
            return

        self.openingValue = 0
        for siteIndex in self.installations:
            self.openingValue += self.instance.fixedCosts[siteIndex]
        self.openingValue = self.openingValue*self.instance.openingWeight

        self.travelValue = 0
        for taskIndex in range(self.instance.nbTasks):
            locationIndex = self.affectations[taskIndex]
            self.travelValue += self.instance.distances[locationIndex][taskIndex]
        self.travelValue = self.travelValue*self.instance.travelCost
        self.travelValue = self.travelValue*self.instance.travelWeight

        self.latenessValue = 0
        for taskIndex in range(self.instance.nbTasks):
            locationIndex = self.affectations[taskIndex]
            travelTime = self.instance.distances[locationIndex][taskIndex]/self.instance.travelSpeed
            taskLateness = self.startDates[taskIndex] + self.instance.durations[taskIndex] + travelTime - self.instance.duedates[taskIndex]
            taskLateness = max(0,taskLateness)
            self.latenessValue += taskLateness
            #print("Lateness task",taskIndex,":",round(taskLateness,1)) #debug
            #print("start:",round(self.startDates[taskIndex],1),"duration:",round(self.instance.durations[taskIndex],1),"travel:",round(travelTime,1),"d+t:",round(travelTime+self.instance.durations[taskIndex],1),"duedate:",round(self.instance.duedates[taskIndex],1)) #debug

        self.latenessValue = self.latenessValue*self.instance.tardinessPenalty

        self.value = self.openingValue+self.travelValue+self.latenessValue

    #writes solution in a file
    def outputSolution(self,outputFile=None):
        if  outputFile == None:
            outputFile = "j"+str(self.instance.nbTasks)+"_k"+str(self.instance.nbLocations)+"_m"+str(self.instance.nbMachines)+".sol"
        lines = []
        for taskIndex in range(self.instance.nbTasks):
            line = str(self.affectations[taskIndex]+1)+" "+str(ceil(self.startDates[taskIndex]))+"\n"
            lines += [line]
        file= open(outputFile,"w")
        file.writelines(lines)
        file.close()
