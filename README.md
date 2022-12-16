# APS_CoincidenceCount

Accepts binary .tif files from the XIA XMAP. Configure in List Mode and E & Clock.
The program interprets, parses, and analyzes the output data for photon coincidences.
Several elements must be known in order to detect coincidences. These can be found
    at the top of the program.

Description of programs:
- tifParser_multiFile.py: parses and analyzes multiple files. Necessary information is found at top. 
                        Use this one for data processing on site.
- tifParser_singleFile.py: same as multiFile, but for a single file at a time. Used for development.
                        Use this one to check individual coincidences.
- tifDiagnostic.py: contains booleans to display different data about a single file, including energy distributions.
                        Use this to check that data is what we expect.
- coincidenceRates.txt: can output calculated coincidence counts and total times to this file for record-keeping.
- folder testFiles: contains files from Dry Run. Can be used to show how file access works
- experimentalConditions.txt: records information needed for computation

Before Use:
Incoming energies are binned, meaning the absolute value of 22 keV likely won't be known until it's measured.
Record some data on the Vortex's detecting 22 keV (if possible, another run with both 22 and 11 keV would be helpful)
and run this through the tifDiagnostic.py program, setting "plot_energy_distribution" to True. Once the graph
is displayed, identify the range of the 22 keV peak. Use the upper and lower limit values in tifParser_multiFile.py
to accurately detect photon energies that are split from 22 keV. They are currently set to the largest and smallest 
possible energies, effectively allowing any two energies to be counted as a coincidence if the other criteria are met.

These values may also be possible to see in the XMAP's on screen tools or other measurements, but a comparison of the
values with those output to the binary file would assure that these numbers are accurate during computation.



How to use:
1) Download the code to a python IDE (I use VSCode).
2) Create folder for experiment files to go into.
3) Populate folder with experiment files. (Group experiments by name and increment by number, "day1_run5_000.tif").
4) Update folder, filename, start/stop digits, which channel has the shorter optical path, and the difference in 
    the optical paths at the head of "tifParser_multiFile.py".
5) Run the file and see the output to the terminal.
6) The totals from all files ran will be uploaded into "coincidenceRates.txt" (not done yet)




Explanation of file formats:

XMAP: The XMAP records photon events by encoding the channel number, energy, and time into a string of binary numbers.
When an output .tif file is generated, it creates a header full of statistics followed by all the event
information. This is basically a huge array of 16-bit binary numbers.

Python: The Python parser goes through this huge array and extracts the channel number, energy, and time from
each event packet. This tuple is then saved in an array. After the whole file has been processed, it looks over
the data to look for the correcrt sequence of channels (shorter, then longer optical path), the correct time
separation, and the correct energies (this needs to be tuned on site).

If using "tifParser_singleFile.py", it will print the photon data for each coincidence to the terminal for you
to see, along with the final count at the end.
If using "tifParser_multiFile.py", it will only include the final counts for each file, and the summed counts
for the whole batch.