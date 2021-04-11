from datetime import datetime
startTime = datetime.now()
from fitparse import *
import os

def semicircleToDegrees(semicircles):
    return semicircles * ( 180 / 2**31 )

def parseFitFile(fitfile):
    #Variable to hold the key for every entry in the dictionary
    point = 1
    dataDict = {}
    for record in fitfile.get_messages('record'):
        #List will hold values for each key in dictionary
        dataList = []
        # Go through all the data entries in this record    
        for record_data in record:
            
            if ((record_data.name == 'speed' or record_data.name == 'distance') and type(record_data.value) == float):  
                 dataList.append(record_data.value)

            if ((record_data.name == 'position_long' or record_data.name == 'position_lat') and type(record_data.value) == int):
                #Values provdied from the fitfiles have lat, lon in semicircles (int)
                dataList.append(semicircleToDegrees(record_data.value))

            if (record_data.name == 'timestamp'):
                t = record_data.value
                time = t.strftime('%H-%M-%S')
                dataList.append(time)
        #Only add record of all five datapoints are present        
        if (len(dataList)==5):   
            dataDict[point] = dataList
            point += 1
    return dataDict

def recursiveString(dataDict):
    stringformat = ""
    stringList = []
    i = 1
    while i < len(dataDict) - 1:        
        inputlist = dataDict[i]
        inputlist2 = dataDict[i+1]
        pos1 = inputlist[1:3]
        pos2 = inputlist2[1:3]
        #Reverse coordinates to get lat first
        pos1.reverse()
        pos2.reverse()
        cumulativeDist = inputlist[0]
        speed = inputlist[3]
        stringformat = ('{"type": "Feature","geometry":{"type":"LineString","coordinates":[%s,%s]},"properties":{"distance": %s, "speed":%s}},' % (pos1, pos2, cumulativeDist, speed)) 
        stringList.append(stringformat)
        i = i + 1
    return stringList


def main():
    userPath = input("Enter the path for a directory containing .FIT files: ") 
    if(os.path.exists(userPath)):
        fitFileList=[]
        for filename in os.listdir(userPath):
            if filename.endswith(".FIT"):
                fitFileList.append(filename)

        if(len(fitFileList) > 0):
            try:
                for fitfile in fitFileList:
                    fit = FitFile(fitfile)
                    dataDict = parseFitFile(fit)
                    geojsonStart = '{"type": "FeatureCollection", "features": ['
                    geojsonMid = ''.join([str(elem) for elem in recursiveString(dataDict)]) #Must start at one -> first key name in dictionary
                    geojsonEnd = ']}'

                    print(geojsonStart + geojsonMid[:-1] + geojsonEnd, file=open(fitfile + ".geojson", "w"))
                    print(datetime.now() - startTime)
            except:
                print("Something unexpected happened while running the script.")
                
        else:
            print("No .FIT files found in directory")
        
    else:
        print("Enter a valid input directory")

if __name__ == "__main__":
    main()
