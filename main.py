from PMSLPData import *
from PMSLPSolution import *
from models import *


testInstance = PMSLPData("Instances/A_instances/A_instance_2_2_0.dat")
testInstance.print()

solveObject = PMSLPMIPModel2(testInstance)
maxTime = 1200
verbose = True
testSolution = solveObject.solve(maxTime,verbose)
print()
testSolution.print()


#la solution n'est pas valide, c'est juste un test pour voir l'écriture dans les fichier
#testSol = PMSLPSolution([1]*4,[i for i in range(10)],[2*i-1 for i in range(10)])
#testSol.outputSolution(testInstance,"testSolutionFile.txt")

#listes d'instances
#Ainstances,Binstances = getAllInstances()
#Ainstances[4].print()
