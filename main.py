from PMSLPData import *
from PMSLPSolution import *
from PMSLPMIPModel1 import *
from PMSLPMIPModel2 import *


testInstance = PMSLPData("Instances/A_instances/A_instance_2_2_0.dat")
testInstance.print()
print()

model = PMSLPMIPModel2(testInstance)


maxTime = 3000
verbose = True
model.solve(maxTime,verbose)

sol = model.getSolution()
sol.print()


#la solution n'est pas valide, c'est juste un test pour voir l'écriture dans les fichier
#testSol = PMSLPSolution([1]*4,[i for i in range(10)],[2*i-1 for i in range(10)])
#testSol.outputSolution(testInstance,"testSolutionFile.txt")

#listes d'instances
#Ainstances,Binstances = getAllInstances()
#Ainstances[4].print()
