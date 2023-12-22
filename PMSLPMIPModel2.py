from PMSLPSolution import *
from mip import *



class PMSLPMIPModel2:
    def __init__(self,instance):
        self.instance = instance
        self.model = None
        self.setup = None
        self.affectations = None
        self.starts = None

        self.getContinuousModel()

    def getContinuousModel(self):
        instance = self.instance
        model = Model(name = "continuous model", solver_name="CBC")


        #variables de décision d'installation sur site
        setup = []
        for locationIndex in range(instance.nbLocations):
            setup += [model.add_var(name="y_"+str(locationIndex),var_type=BINARY)]

        #variables de décision d'affectation d'une tâche à un site
        affectations = []
        for taskIndex in range(instance.nbTasks):
            affectations += [[]]
            for locationIndex in range(instance.nbLocations):
                affectations[taskIndex] += [model.add_var(name="x_"+str(taskIndex)+"_"+str(locationIndex),var_type=BINARY)]

        #variables de décision de précédence entre deux tâches
        preceding = []
        for taskIndex1 in range(instance.nbTasks):
            preceding += [[]]
            for taskIndex2 in range(instance.nbTasks):
                if taskIndex1 != taskIndex2:
                    preceding[taskIndex1] += [model.add_var(name="z_"+str(taskIndex1)+"_"+str(taskIndex2),var_type=BINARY)]
                else:
                    preceding[taskIndex1] += [None]

        #variables de décision de début de tâche
        starts = []
        for taskIndex in range(instance.nbTasks):
            starts += [model.add_var(name="s_"+str(taskIndex),var_type=CONTINUOUS,lb=0)]

        #variables de décision de retard d'une tâche
        lateness = []
        for taskIndex in range(instance.nbTasks):
            lateness += [model.add_var(name="T_"+str(taskIndex),var_type=CONTINUOUS,lb=0)]

        #fonction objectif
        model.objective = minimize( instance.openingWeight*xsum(setup[locationIndex]*instance.fixedCosts[locationIndex] for locationIndex in range(instance.nbLocations)) +
                                    instance.travelWeight*xsum(xsum(affectations[taskIndex][locationIndex]*instance.distances[locationIndex][taskIndex]*instance.travelCost for taskIndex in range(instance.nbTasks)) for locationIndex in range(instance.nbLocations)) +
                                    instance.tardinessPenalty*xsum( lateness[taskIndex] for taskIndex in range(instance.nbTasks)) )

        #contrainte, un nombre précis de sites à ourvrir
        model += (xsum(setup[locationIndex] for locationIndex in range(instance.nbLocations)) == instance.nbMachines)

        #contrainte, toutes les tâches doivent être effectuées
        for taskIndex in range(instance.nbTasks):
            model += (xsum(affectations[taskIndex][locationIndex] for locationIndex in range(instance.nbLocations)) == 1)

        #contrainte, il faut affecter les tâches à des sites ouverts
        for taskIndex in range(instance.nbTasks):
            for locationIndex in range(instance.nbLocations):
                model += (affectations[taskIndex][locationIndex] <= setup[locationIndex])

        #contrainte, si deux tâches sont sur un site alors une doit précéder l'autre
        for taskIndex1 in range(instance.nbTasks):
            for taskIndex2 in range(taskIndex1+1,instance.nbTasks):
                for locationIndex in range(instance.nbLocations):
                    model += (preceding[taskIndex1][taskIndex2]+preceding[taskIndex2][taskIndex1] >= affectations[taskIndex1][locationIndex]+affectations[taskIndex2][locationIndex]-1)

        bigM = instance.latestStart
        for taskIndex in range(instance.nbTasks):
            bigM += instance.durations[taskIndex]

        #contrainte, une machine ne peut pas faire deux tâches en même temps
        for taskIndex1 in range(instance.nbTasks):
            for taskIndex2 in range(instance.nbTasks):
                if taskIndex1 != taskIndex2:
                    model += (starts[taskIndex1]+instance.durations[taskIndex1]<=starts[taskIndex2]+bigM*(1-preceding[taskIndex1][taskIndex2]))
                    pass

        #contrainte, fixe la valeur du retard des tâche
        for taskIndex in range(instance.nbTasks):
            model += (lateness[taskIndex] >= starts[taskIndex] + instance.durations[taskIndex] -instance.duedates[taskIndex] + xsum(affectations[taskIndex][locationIndex]*instance.distances[locationIndex][taskIndex]/instance.travelSpeed for locationIndex in range(instance.nbLocations)))

        #contraintes de disponibilités
        for taskIndex in range(instance.nbTasks):
            model += (starts[taskIndex] >= xsum(affectations[taskIndex][locationIndex]*instance.distances[locationIndex][taskIndex]/instance.travelSpeed for locationIndex in range(instance.nbLocations)))

        self.model = model
        self.setup = setup
        self.affectations = affectations
        self.starts = starts
        return model,setup,affectations,starts,lateness

    def getSolution(self):
        installations = []
        for locationIndex in range(self.instance.nbLocations):
            if self.setup[locationIndex].x >= 0.99:
                installations += [locationIndex]

        affectationsRes = [None]*self.instance.nbTasks
        startDates = [None]*self.instance.nbTasks
        for taskIndex in range(self.instance.nbTasks):
            startDates[taskIndex] = self.starts[taskIndex].x
            for locationIndex in range(self.instance.nbLocations):
                if self.affectations[taskIndex][locationIndex].x >= 0.99:
                    affectationsRes[taskIndex] = locationIndex

                    #travelTime = self.instance.distances[locationIndex][taskIndex]/self.instance.travelSpeed #debug
                    #print("Lateness",taskIndex,":",round(lateness[taskIndex].x,1)) #debug
                    #print("start:",round(starts[taskIndex].x,1),"duration:",round(self.instance.durations[taskIndex],1),"travel:",round(travelTime,1),"d+t:",round(travelTime+self.instance.durations[taskIndex],1),"duedate:",round(self.instance.duedates[taskIndex],1)) #debug

        return PMSLPSolution(self.instance,installations,affectationsRes,startDates)

    def solve(self,maxTime=10,talking=False):
        self.model.max_seconds = maxTime
        self.model.verbose = talking
        self.model.optimize()
