from datetime import datetime
startTime = datetime.now()
from fitparse import *

fitfile = FitFile('run06-05.FIT')

def semicircleToDegrees(semicircles):
    return semicircles * ( 180 / 2**31 )

def parseFitFile(file):
    #Variable to hold the key for every entry in the dictionary
    point = 1
    dataDict = {}
    for record in fitfile.get_messages('record'):
        #List will hold values for each key in dictionary
        dataList = []
        
        # Go through all the data entries in this record    
        for record_data in record:
            if (record_data.name == 'speed'or record_data.name == 'distance'):
                        
                 dataList.append(record_data.value)
                 
            if (record_data.name == 'position_long' or record_data.name == 'position_lat'):
                #Values provdied from the fitfiles have lat, lon in semicircles
                dataList.append(semicircleToDegrees(record_data.value))

            if (record_data.name == 'timestamp'):
                t = record_data.value
                time = t.strftime('%H-%M-%S')
                dataList.append(time)
                
        dataDict[point] = dataList
        point += 1
    return dataDict

def recursiveString(i):
    inputlist = dataDict[i]
    inputlist2 = dataDict[i+1]
    pos1 = inputlist[1:3]
    pos2 = inputlist2[1:3]
    #Reverse coordinates to get lat first
    pos1.reverse()
    pos2.reverse()
    prop1 = str(inputlist[0])
    stringformat = ('{"type": "Feature","geometry":{"type":"LineString","coordinates":[%s,%s]},"properties":{"distance": "%s"}}' % (pos1, pos2, prop1))

    if (i == len(dataDict) - 1):
       return stringformat
    else:
        string = stringformat + ','
        return string + recursiveString(i+1)

dataDict = parseFitFile(fitfile)
geojsonStart = '{"type": "FeatureCollection", "features": ['
geojsonMid = recursiveString(1) #Must start at one -> first key name in dictionary
geojsonEnd = ']}'

print(geojsonStart + geojsonMid + geojsonEnd, file=open("run_GeoJson.geojson", "w"))
 
print(datetime.now() - startTime)
