# A simple script to pull product end of life dates from https://endoflife.date/
import requests
import json
import time
import csv

allProducts = []
eolDates = {}
starttime = time.time()

def grabAll():
    url = "https://endoflife.date/api/all.json"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)   
    jsonData = response.json()
    for item in jsonData:
        allProducts.append(item)

def grabCycles(product): # Grabs all cycles within a given product
    baseurl = "https://endoflife.date/api/"
    fullurl = baseurl + product + ".json"
    headers = {"Accept": "application/json"}
    response = requests.get(fullurl, headers=headers)
    jsonData = response.json()
    numOfCycles = len(jsonData)
    allCycles = []
    for i in range(numOfCycles):
        newjson = jsonData[i]
        allCycles.append(newjson['cycle'])
        try:
            prodAndCycle = product + " " + newjson['cycle']
            eolDates[prodAndCycle] = str(newjson['eol'])
            print(product + "," + str(newjson['cycle']) + "," + str(newjson['eol']))
        except KeyError: # KeyError is returned if no 'eol' key exists in the JSON returned
            prodAndCycle = product + " " + newjson['cycle']
            eolDates[prodAndCycle] = "None"
            print(product + "," + str(newjson['cycle']) + ",None")

def exportCSV():
    with open('eoldates.csv', 'w') as file:
        writer = csv.writer(file)
        for key, value in eolDates.items():
            writer.writerow([key, value])

if __name__ == "__main__":
    grabAll()
    for product in allProducts:
        grabCycles(product)
    # exportCSV() # uncomment this if you want to auto export csv. I prefer having the three columns so I just do a "python3 eolgrabber.py >> eoldates.csv"
    endtime = time.time()
    elapsedtime = endtime - starttime
    # print('execution time: ' + str(elapsedtime) + 'seconds') # Left for debugging.
