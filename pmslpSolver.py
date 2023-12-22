import sys
from PMSLPData import *
from PMSLPSolution import *
from PMSLPMIPModel1 import *
from PMSLPMIPModel2 import *


filePath = sys.argv[1]
methodName = sys.argv[2]
print(methodName)
maxTime = int(sys.argv[3])


if methodName == "MIP1":
    instance = PMSLPData(filePath)
    instance.print()
    print()
    model = PMSLPMIPModel1(instance)
    verbose = True
    model.solve(maxTime,verbose)
    solution = model.getSolution()
    if solution != None:
        solution.print()

elif methodName == "MIP2":
    instance = PMSLPData(filePath)
    instance.print()
    print()
    model = PMSLPMIPModel2(instance)
    verbose = True
    model.solve(maxTime,verbose)
    solution = model.getSolution()
    if solution != None:
        solution.print()

elif methodName == "H":
    print("Pas d'heuristique")
else:
    print("Unkown method name")
