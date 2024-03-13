import os

numCrits = 0
numHighs = 0
numMeds = 0
numLows = 0
numNegligible = 0
numUnknown = 0

containerList = []
dirPath = '/home/nate/python/grype/'

def countCVE(container):
	file = open(dirPath + container, 'r') # open file
	data = file.read()
	global numCrits
	global numHighs
	global numMeds
	global numLows
	global numNegligible
	global numUnknown

	thisCrits = data.count("Critical")
	numCrits = numCrits + thisCrits
	thisHighs = data.count("High")
	numHighs = numHighs + thisHighs
	thisMeds = data.count("Medium")
	numMeds = numMeds + thisMeds
	thisLows = data.count("Low")
	numLows = numLows + thisLows
	thisNegligible = data.count("Negligible")
	numNegligible = numNegligible + thisNegligible
	thisUnknown = data.count("Unknown")
	numUnknown = numUnknown + thisUnknown
	print(container + " has: " + str(thisCrits) + " criticals, " + str(thisHighs) + " highs, " + str(thisMeds) + " mediums, " + str(thisLows) + " lows, " + str(numNegligible) + " negligibles, and " + str(thisUnknown) + " unknowns. ")

#countCVE()
def enumerateFiles():
	for path in os.listdir(dirPath):
	    # check if current path is a file
	    if os.path.isfile(os.path.join(dirPath, path)):
	        containerList.append(path)

def main():
	enumerateFiles()
	print(len(containerList))
	for container in containerList:
		countCVE(container)
main()
print("Average for: hriticals: " + str(numCrits / len(containerList)) + " highs: " + str(numHighs / len(containerList)) + " meds: " + str(numMeds / len(containerList)) + " lows: " + str(numLows / len(containerList)) + " negligibles: " + str(numNegligible / len(containerList)) + " unknowns: " + str(numUnknown / len(containerList)))
