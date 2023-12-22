from PMSLPSolution import *
from mip import *
from math import floor


class PMSLPMIPModel1:
    def __init__(self,instance,periodsAmount = None):
        self.instance = instance
        self.model = None
        self.setup = None
        self.affectations = None
        self.starts = None


        #fixe le nombre de période si rien n'est donné en paramètre
        if periodsAmount == None:
            self.periodsAmount = floor(instance.latestStart)
            for taskIndex in range(instance.nbTasks):
                self.periodsAmount += instance.durations[taskIndex]
            print(self.periodsAmount, "periods")
        else:
            self.periodsAmount = periodsAmount

        self.getPeriodModel()
        self.status = None

    def getPeriodModel(self):
        instance = self.instance
        model = Model(name = "period model", solver_name="CBC")

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

        #variables de décision de début de tâche
        starts = []
        for taskIndex in range(instance.nbTasks):
            starts += [[]]
            for period in range(self.periodsAmount):
                starts[taskIndex] += [model.add_var(name="s_"+str(taskIndex)+"_"+str(period),var_type=BINARY)]

        #variables de décision d'exécution de tâche
        active = []
        for taskIndex in range(instance.nbTasks):
            active += [[]]
            for locationIndex in range(instance.nbLocations):
                active[taskIndex] += [[]]
                for period in range(self.periodsAmount):
                    active[taskIndex][locationIndex] += [model.add_var(name="a_"+str(taskIndex)+"_"+str(locationIndex)+"_"+str(period),var_type=BINARY)]

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

        #contrainte, il faut commencer les tâches à un période
        for taskIndex in range(instance.nbTasks):
            model += (xsum(starts[taskIndex][t] for t in range(self.periodsAmount)) >= 1)

        #contrainte, on fixe les variables d'exécution à partir de celles de départ
        for j in range(instance.nbTasks):
            for k in range(instance.nbLocations):
                for t in range(self.periodsAmount):
                    model += (active[j][k][t] >= affectations[j][k] -1 + xsum(starts[j][u] for u in range(t-instance.durations[j]+1,t+1)))

        #contrainte, une seule tâche exécutée à la fois
        for k in range(instance.nbLocations):
            for t in range(self.periodsAmount):
                model += (xsum(active[j][k][t] for j in range(instance.nbTasks)) <= 1)

        #contrainte, fixe la valeur du retard des tâche
        for j in range(instance.nbTasks):
            model += (lateness[j] >= xsum(starts[j][t]*t for t in range(self.periodsAmount)) + instance.durations[j] -instance.duedates[j] + xsum(affectations[j][k]*instance.distances[k][j]/instance.travelSpeed for k in range(instance.nbLocations)))

        #contraintes de disponibilités
        for j in range(instance.nbTasks):
            model += (xsum(starts[j][t]*t for t in range(self.periodsAmount)) >= xsum(affectations[j][k]*instance.distances[k][j]/instance.travelSpeed for k in range(instance.nbLocations)))

        self.model = model
        self.setup = setup
        self.affectations = affectations
        self.starts = starts
        return model,setup,affectations,starts,lateness




    def getSolution(self):
        if self.status not in [OptimizationStatus.OPTIMAL,OptimizationStatus.FEASIBLE]:
            print("No feasable solution found")
            return

        installations = []
        for locationIndex in range(self.instance.nbLocations):
            if self.setup[locationIndex].x >= 0.99:
                installations += [locationIndex]

        affectationsRes = [None]*self.instance.nbTasks
        startDates = [None]*self.instance.nbTasks
        for taskIndex in range(self.instance.nbTasks):

            for period in range(self.periodsAmount):
                if self.starts[taskIndex][period].x >= 0.99:
                    startDates[taskIndex] = period
                    break

            for locationIndex in range(self.instance.nbLocations):
                if self.affectations[taskIndex][locationIndex].x >= 0.99:
                    affectationsRes[taskIndex] = locationIndex

        return PMSLPSolution(self.instance,installations,affectationsRes,startDates)

    def solve(self,maxTime=10,talking=False):
        self.model.max_seconds = maxTime
        self.model.verbose = talking
        self.status = self.model.optimize()
