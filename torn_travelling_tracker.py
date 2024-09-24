import requests
from config import API_KEY

finalResultList = [[],[],[],[]]
count = [0] * 11
def counter(x):
    if x == 0:
        count[x] +=1
    elif x == 1:
        count[0] +=1
    elif x%2 == 1:
        count[int((x-1)/2)] +=1
    elif x%2 == 0:
        count[int(x/2)] +=1


def compiler(name, status,detectedLocation):
    if "Traveling" in status:
        resultString =  name + " is "+ status
        index = destinations.index(detectedLocation)
        counter(index)
        finalResultList[1].append(resultString)
    elif "Returning" in status:
        resultString =  name + " is "+ status
        finalResultList[2].append(resultString)
    elif "hospital" in status:
        resultString =  name + " is "+ status
        index = destinations.index(detectedLocation)
        counter(index)
        finalResultList[3].append(resultString)
    else:
        resultString =  name +"   is in    " + detectedLocation
        index = destinations.index(detectedLocation)
        counter(index)
        finalResultList[0].append(resultString)

def writer():
    with open("traveling_enemies.txt",'w') as f:
        for y in range(0,4):
            for x in range(len(finalResultList[y])):
                f.write(finalResultList[y][x] + "\n")
    summarizer(count)

def printer():
    for y in range(0,4):
        for x in range(len(finalResultList[y])):
            print(finalResultList[y][x])
    summarizer(count)

def summarizer(count):
    for x in range(len(destinations)):
        if x ==0:
            print(destinations[x] + "   " + str(count[x]))
        elif x%2 == 0:
            print(destinations[x] + "   " + str(count[int(x/2)]))

enemyFactionId = 30023

destinations = ["Hawaii","Hawaiian", "Canada","Canadian", "Switzerland","Swiss", "United Kingdom", "British","Argentina","Argentinian","UAE","Emirati", "Japan", "Japanese", "China","Chinese","Mexico","Mexican", "Cayman Islands", "Caymanian", "South Africa", "South African"]
factionReportUrl = "https://api.torn.com/faction/" + str(enemyFactionId)+ "?selections=&key=" + API_KEY
response = requests.get(factionReportUrl)
data = response.json()

for key in data["members"]:
    name = data["members"][key]["name"]
    travelStatus = data["members"][key]["status"]["description"]
    for x in range(len(destinations)):
        if destinations[x] in travelStatus:
            detectedLocation = destinations[x]
            compiler(name, travelStatus, detectedLocation)

printer()
#writer()
stopper = input()