from PIL import Image
import numpy as np
import random

#number of events for two detectors
ch0_numEvents = random.randint(128, 156)
ch1_numEvents = random.randint(128, 156)
ch2_numEvents = 0
ch3_numEvents = 0
numEvents = [ch0_numEvents, ch1_numEvents, ch2_numEvents, ch3_numEvents]
totalEvents = sum(numEvents)

#Header Generation
fillerBits = 0xBEEF #fills in data not necessary for us
zeroedBits = 0x0000 # bits set to zero

buffer = [0x55AA, 0xAA55, 256, 3] #0-3, general
for i in range(4): #4-7, buffer info
    buffer.append(fillerBits)
for i in range(3): #8-10, pixel info
    buffer.append(zeroedBits)
for i in range(13): #11-23, channel and MCA info
    buffer.append(fillerBits)
buffer.append(zeroedBits) #24
buffer.append(totalEvents*3 / 0xFFFF) #25-26, total num of words broken into higher and lower uint16
buffer.append(totalEvents*3 % 0xFFFF)
for i in range(5+32): #27-31, 32-63 add in b/c no user words set
    buffer.append(zeroedBits)
buffer.append(2) #64, list-mode variant: Energy plus Clock Time
buffer.append(3) #65, words per event
buffer.append(totalEvents / 0xFFFF) #66-67, totalEvents broken into higher and lower uint16
buffer.append(totalEvents % 0xFFFF)
for ch in range(4): #68-115, ch0-3 (starting indeces: 68, 80, 92, 104)
    buffer.append(numEvents[ch] / 0xFFFF) #+0-1, num ch events broken into higher and lower uint16
    buffer.append(numEvents[ch] % 0xFFFF)
    for i in range(2): #+2-3, first event num
        buffer.append(fillerBits)
    for i in range(2): #+4-5, ch0 upper time word, set to zero for example
        buffer.append(zeroedBits) 
    for i in range(6): #+6-11, misc channel info
        buffer.append(fillerBits)
buffer.append(zeroedBits) #116-117, num special events, set to zero for example
buffer.append(zeroedBits)
for i in range(138): #118-255
    buffer.append(zeroedBits)

if len(buffer) != 256:
    print("ERROR: Incorrect Buffer Length, " + str(len(buffer)))


#Data Generation
eventsRecorded = [0,0,0,0] #keeps track of how many events have been generated for each channel
maxEnergy = 2**13 #13 bits to store energy data
eventEnergies = [int(maxEnergy*2/7), int(maxEnergy*4/7)] # representation of 11 and 22 keV
timeStamp = 0

for i in range(sum(numEvents)):
    while(True): #repeats until break statement
        ch = random.randint(0,1)
        if eventsRecorded[ch] < numEvents[ch]: #hasn't reached numEvents for this channel
            eventsRecorded[ch] += 1

            #event data - use bitwise operator shift (<<) to put bits in correct places
            specialEventFlag = 0 #no runover events for this example
            eventData = specialEventFlag << 15 #saves flag to 15th bit (MSB)
            eventData += (ch << 13) #saves ch to 14-13th bits
            eventData += eventEnergies[random.randint(0,1)] # saves energy to bits 12-0

            #time data - 2 uint16 words
            timeStamp += random.randint(0,30)
            timeUpper = int(timeStamp / 0xFFFF)
            timeLower = timeStamp % 0xFFFF

            #save to buffer
            buffer.append(eventData)
            buffer.append(timeUpper)
            buffer.append(timeLower)
            break




#convert to array
dataArray = np.asarray(buffer, dtype=np.uint16)

'''
#Show Data
for i in range(256):
    print(str(i) + ": " + str(dataArray[i]))
ch_mask = 0x6000
energy_mask = 0x1FFF
for i in range(256, len(buffer), 3):
    print("Event " + str(int((i-256)/3)) + ": " + str((buffer[i] & ch_mask) >> 13) + ", " + str(buffer[i] & energy_mask))
    print("\t" + str((buffer[i+1] << 16) + buffer[i+2]))
'''

#save buffer to .tiff file
im = Image.fromarray(dataArray)
im.save('exampleFile.tif')