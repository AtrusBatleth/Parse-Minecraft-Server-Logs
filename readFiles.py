# This module retrieves a list of files in a directory and does some checking that they are valid
# Minecraft log filenames. The valid files are read into the logs array and dates are added to the
# log timestamps. Optionally, the combined logs may be written to an output file.
#
# This module is not intended to be run by itself. It is imported into the playtime.py file, which
# is the module you should be running.

import os  # Used for listing files in folder via os.listdir() and for using os.path.basename().
logs:str = [] # This is the master string array that will contain all log data.

# Get folder path with log files and determine whether to enforce strict filename checks.
logFiles:str = []
path:str = input("Enter the folder path with Minecraft server log files (defaults to d:\\logs\\): ")
if path == "":
    path = "d:\\logs\\"
if path.endswith("\\") == False:
    path += "\\"
files:str = os.listdir(path)
bStrict:bool = True
print("\nStrict filename checks only allow files in the format: \"YYYY-MM-DD-N.log\", Where:")
print("  YYYY must be between 2009 and 2050 and be 4 digits,")
print("  MM must be between 01 and 12 and be 2 digits,")
print("  DD must be between 01 and 31 and be 2 digits,")
print("  Filename must end in .log extension,")
print("  3 dashes (-) must be positioned exactly as shown,")
print("  N can be any arbitrary length of numbers or characters.\n")
temp = input("Enforce strict filename checks? (Y/N, defaults to Y): ")
if temp.lower() == "n" or temp.lower() == "no":
    bStrict = False

# Loop through all files from os.listdir() (which includes sub-folder names) and identify valid filenames.
for file in files:
    bValidFile:bool = True  # Assume filename is valid until one of the checks fails
    if os.path.isfile(path + file) == False:  # This will eliminate sub-folder names
        bValidFile = False
    if bStrict:  # Perform strict filename checks
        if len(file) < 16:  # 16 is the minimum length of filename with format YYYY-MM-DD-N.log
            bValidFile = False
        if file.lower().endswith(".log") == False:
            bValidFile = False
        if file[0:4].isdecimal(): # Prevents error using int() with non-decimal characters
            if int(file[0:4]) < 2009 or int(file[0:4]) > 2050:  # Check that year in filename is valid
                bValidFile = False
        else:  # Expected year is not a decimal, so not a valid filename
            bValidFile = False
        if file[5:7].isdecimal(): # Prevents error using int() with non-decimal characters
            if int(file[5:7]) < 1 or int(file[5:7]) > 12:  # Check that month in filename is valid
                bValidFile = False
        else:  # Expected month is not a decimal, so not a valid filename
            bValidFile = False
        if file[8:10].isdecimal(): # Prevents error using int() with non-decimal characters
            if int(file[8:10]) < 1 or int(file[8:10]) > 31:  # Check that day in filename is valid
                bValidFile = False
        else:  # Expected day is not a decimal, so not a valid filename
            bValidFile = False
        if file[4] != "-" or file[7] != "-" or file[10] != "-":
            bValidFile = False
    if bValidFile:
        logFiles.append(file) # Only add valid filenames to logFiles
print("\n" + str(len(logFiles)) + " valid log files identified.")

# Loop through each file and read contents into logData, modify timestamps, then write to logs array.
print("\nReading log files...")
for file in logFiles:
    try:
        logFile = open(path + file, "r")
        if logFile.readable() == False:
            print("Error opening log file " + file + ". Program will now exit.")
            exit(1)
    except:
        print("Invalid log file " + file + ". Program will now exit.")
        exit(1)
    logData = logFile.readlines()
    logFile.close()

    # Loop through each line of data and add date to timestamp
    for line in logData:
        if line[0] == "[": # Any line whose first character is a [ should be a timestamp log entry.
            # Original log format is "[HH:MM:SS]", this changes it to:
            # "[YYYY-MM-DD HH:MM:SS]"
            line = "[" + file[0:10] + " " + line[1:]

        # Append this modified line to the combined logs array.
        logs.append(line)
    print(file) # Echos each filename that was successfully read.
print("\nSuccessfully read " + str(len(logFiles)) + " log files.")

# Output the logs array to a file if desired.
bOutFile:bool = False
temp = input("\nDo you wish to save all log data in a combined log output file? (Y/N, defaults to N): ")
if temp.lower() == "y" or temp.lower() == "yes":
    bOutFile = True
if bOutFile:
    try:
        outFile = open(path + input("Enter combined log output filename: "), "a")
        if outFile.writable() == False:
            print("Error creating combined log output file. Program will now exit.")
            exit(1)
    except:
        print("Invalid combined log output filename. Program will now exit.")
        exit(1)
    outFile.writelines(logs)
    outFile.close()
    print("\nCombined log output file " + os.path.basename(outFile.name) + " successfully written.")