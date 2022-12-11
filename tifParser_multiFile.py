'''
tifParser.py
Eric Christie
10/18/22
BYU QCX Project

Summary: Same as tifParser_singleFile, but configured to 
            process multiple files with the same name and
            incrementing numeric designations.
            Ex: test_000.tif, test_001.tif, ...
'''

from PIL import Image
import numpy as np

##### Things to update #####

# file information
folder = "testFiles"
filename = "dryRun_noSource"
startDigit = 0
stopDigit = 4

# Optical Path Information
dist_difference = 0 #in meters
ch_shorterPath = 0
ch_longerPath = 1


##### Constants and Functions #####

# Masks
specialEvent_mask = 0x8000 #bit 15 (MSB)
rolloverEvent_mask = 0x0100 #checks rollover vs end of buffer
rolloverCh_mask = 0x000F #last nibble, 0x810x
ch_mask = 0x6000 #bits 14-13
energy_mask = 0x1FFF #bits 12-0

# Constants
clockPeriod = 20 * 10**-9 #20 ns
rollover_timeValue = 2**32
energy_22keV_lowerLimit = 0 #energy distribution
energy_22keV_upperLimit = 8191

# Functions
def combineTo32bits(num1, num2): #combines 2 word numbers
    output = (num1 << 16) + num2
    if output < 0:
        output += 2**32
    return output

def calculateLineDelay(dist): #returns num of clks in lineDelay
    c = 299792458 #m/s
    timeDifference = dist / c # (m) / (m/s) = (s)
    numClocks = timeDifference / clockPeriod # (s) / (s/clk) = (clk)
    return int(numClocks)

def checkTime(timeVal, time_pair): #logic of checking coincidence timing (+/-1 clk)
    if timeVal == time_pair: #exact match
        return True
    elif timeVal == (time_pair -1) % rollover_timeValue: #-1 clk
        return True
    elif timeVal == (time_pair +1) % rollover_timeValue: #+1 clk
        return True
    else:                   #no match
        return False

def checkEnergy(energy1, energy2): #logic for checking energy
    energySum = energy1 + energy2
    if energySum > energy_22keV_lowerLimit and energySum < energy_22keV_upperLimit:
        return True
    else:
        return False

# parser, calls coincidenceCount algorithm, returns coincidences and total time
def parseData(filepath):

    # open file as array
    im = Image.open(filepath)
    rawArray = np.array(im)
    rawArray = rawArray[0] 
    
    # begin parsing
    eventData = []
    ch_overruns = [0,0,0,0] #records num of time overruns for ch0-1
    eventsPerCh = [0,0,0,0]

    #arrange data array into event tuples: [ch, energy, timestamp]
    for i in range(256, len(rawArray), 3):
        word = rawArray[i]
        if(word & specialEvent_mask): #adds timer overrun count to channel
            if (word & rolloverEvent_mask): #channel timer overrun
                ch = word & rolloverCh_mask
                ch_overruns[ch] += 1
        
        else: #regular photon event
            ch = int((word & ch_mask) >> 13)
            energy = word & energy_mask
            timeStamp = combineTo32bits(rawArray[i+2], rawArray[i+1])
            event = [ch, energy, timeStamp]

            if not(event == [0,0,0]): #clears null data (fills unused section of buffer)
                eventData.append(event)
                eventsPerCh[ch] += 1
    
    #calls coincidence Count
    coincidenceCount = coincidenceCounter(eventData)

    #output time elapsed during file
    timeStart = eventData[0][2]
    timeEnd = eventData[len(eventData) -1][2]
    num_overruns = ch_overruns[ch_shorterPath] #should be equal
    
    totalClks = (rollover_timeValue - timeStart) + timeEnd + (num_overruns * rollover_timeValue)
    totalTime_sec = totalClks * clockPeriod # clks * sec/clk = sec
    totalTime_min = totalTime_sec / 60

    return [coincidenceCount, totalTime_min]


# counts coincidences from data array, returns num coincidences
def coincidenceCounter(eventData):
    coincidenceCount = 0
    coincidenceTime = calculateLineDelay(dist_difference)
    for i in range(len(eventData)):
        if eventData[i][0] == ch_shorterPath:
            time_pair = (eventData[i][2] + coincidenceTime) % rollover_timeValue #projects time value, accounts for rollover

            for j in range(i+1, len(eventData)): #looks ahead at photons
                if eventData[j][2] > time_pair+1: #won't look past expected time
                    break
                elif eventData[j][0] == ch_longerPath: #expected ch
                    if checkTime(eventData[j][2], time_pair): #expected time
                        if checkEnergy(eventData[i][1], eventData[j][1]): #expected energy sum
                            coincidenceCount += 1
    return coincidenceCount



##### Begin Computation Loop #####
print("\nFilename : [ coincidences, totalTime (min) ]")
dataFromFiles = []
for i in range(startDigit, stopDigit+1):
    filename_full = folder + "/" + filename + "_" + f'{i:03d}' + ".tif"
    fileData = parseData(filename_full)
    dataFromFiles.append(fileData)

    print(filename_full + ": " + str(fileData))

totalCoincidences = 0
totalTime = 0
for results in dataFromFiles:
    totalCoincidences += results[0]
    totalTime += results[1]

print()
print("Total Files: " + str(stopDigit - startDigit + 1))
print("Total Coincidences: " + str(totalCoincidences))
print("Total Time: " + str(totalTime))
print("Overall Rate: " + str(totalCoincidences / totalTime))
print()


