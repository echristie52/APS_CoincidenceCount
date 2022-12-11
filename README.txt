Author: Eric Christie
Purpose: Coincidence Counting Files for use by BYU QCX Research Group at APS


Files:

coincidenceCount_inputData.py
    Input a filename of coordinated photon data (time-tagged photon events from both detectors),
    the time interval of the experiment (likely standard), and delay in line used.
    It counts the number of coincidences in the data and divides by time interval of the experiment
    to calculate the rate of coincidences. 
    The rate and delay are recorded in 'coincidenceRates.txt' in the following format:
    <delay>:<rate>

coincidenceCount_displayData.py
    Imports delay and rate data from 'coincidenceRates.txt' and plots the avg rates for each delay 
    for visual inspection of HOM dip.
    Also calculates potential location of dip using min()