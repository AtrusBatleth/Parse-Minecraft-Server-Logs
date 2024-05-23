# This module scans data from the logs array prepared using the readFiles.py module and calculates various
# total and weekly playtime statistics. The readFiles.py module is called automatically via import so this
# is the only module you need to run (probably bad coding style but hey, it works).

import os # Used to write output csv files
import datetime # Used for datetime objects
import readFiles # Separate module that reads all the input files into logs array.
logs:str = readFiles.logs # Array containing all log file contents.
playtimes = [] #Array of player names, total playtime, and rank.

# Open output files and check that the files are writeable.
bFileSes:bool = False
temp = input("\nDo you wish to save all session times? (Y/N, defaults to N): ")
if temp.lower() == "y" or temp.lower() == "yes":
    bFileSes = True
if bFileSes:
    try:
        outFileSes = open(readFiles.path + input("Output csv filename for all session times: "), "a")
        if outFileSes.writable() == False:
            print("Error creating sessions output file. Program will now exit.")
            exit(1)
    except:
        print("Invalid sessions output filename. Program will now exit.")
        exit(1)
    outFileSes.writelines("Player,Joined,Left,Session Time,Seconds\n")
bFileWeek:bool = False
temp = input("\nDo you wish to save weekly statistics? (Y/N, defaults to N): ")
if temp.lower() == "y" or temp.lower() == "yes":
    bFileWeek = True
if bFileWeek:
    try:
        outFileWeek = open(readFiles.path + input("Output csv filename for weekly statistics: "), "a")
        if outFileWeek.writable() == False:
            print("Error creating weekly output file. Program will now exit.")
            exit(1)
    except:
        print("Invalid weekly output filename. Program will now exit.")
        exit(1)
    outFileWeek.writelines("Player,Week Starting,Playtime,Seconds\n")

# Loop through logs looking for list of players and log start/end times.
bFindStart:bool = True # Look for starting log entry. Once the first date is set, the search is called off.
logStart = datetime.datetime(2050, 1, 1) # Bounding late date
logEnd = datetime.datetime(2009, 1, 1) # Bounding early date
for line in logs:

    # Search for log start time.
    if bFindStart:
        if line[0] == "[":
            # Update the logStart date, rounded down to the nearest hour.
            logStart = datetime.datetime(int(line[1:5]), int(line[6:8]), int(line[9:11]), int(line[12:14]),
                                         0, 0)
            bFindStart = False # Call off the search. Probably saves computing time vs continuing to compare log times.

    # Look for log entries of players joining and populate the list of player names.
    # Technically this will not identify players who were already online and never logged off or who never rejoined.
    if "joined the game" in line and "[Server thread/INFO]:" in line:
        # The split() function splits the string into individual words (space delimited), and in the case of joining
        # server log entries, the username is the 4th word in the line. Exception is when the player was afk when they
        # previously left, when they re-join it shows their name as "[AFK] name". So the replace() function removes
        # that to avoid name mis-matches.
        name = line.replace("[AFK]", "").split()[4]

        # Special case for first player name.
        if len(playtimes) == 0:
            playtimes += [[name, datetime.timedelta(), 0]] # timedelta() object is initialized as 0:0:0

        # Try to find the player name in the players array, and if it's not found, add it.
        nameFound = False
        for player in playtimes:
            if player[0] == name:
                nameFound = True
        if nameFound == False:
            playtimes += [[name, datetime.timedelta(), 0]] # timedelta() object is initialized as 0:0:0

    # Update the logEnd date; at the end of the loop this should reflect the final log entry.
    if line[0] == "[":
        logEnd = datetime.datetime(int(line[1:5]), int(line[6:8]), int(line[9:11]), int(line[12:14]), int(line[15:17]),
                                   int(line[18:20]))

# Round up logEnd to the nearest hour. Typically the log will end near the end of the day.
logEnd = (datetime.datetime(logEnd.year, logEnd.month, logEnd.day, logEnd.hour, 0, 0) +
          datetime.timedelta(hours=1))

# Set start date for weekly statistics. Defaults to Monday 2024-03-11.
if bFileWeek: # User wants the weekly statistics csv output file.
    print("\nThe initial start-of-week date is used to define weekly intervals for all weeks that follow.")
    print("It may be a date prior to the start of your log files, but if it is 7 days or more prior,")
    print("then the csv output file will include rows with 0 data. If the start-of-week date is later")
    print("than the start of your log files, then the first row of data will represent more than one")
    print("weeks worth. If no date is entered, it defaults to 2024-03-11.\n")
    temp = input("Enter the start-of-week date in format YYYY-MM-DD: ")
    # If the length is too small or any of the expected numbers are non-decimal, the date is invalid.
    if len(temp) < 10 or temp[0:4].isdecimal() == False or temp[5:7].isdecimal() == False or temp[8:10].isdecimal() == False:
        print("Invalid or no start-of-week entered. Defaulting to 2024-03-11.")
        temp = "2024-03-11"
    # Check that year/month/day numbers are within a reasonable range.
    elif int(temp[0:4]) < 2009 or int(temp[0:4]) > 2050 or int(temp[5:7]) < 1 or int(temp[5:7]) > 12 or int(temp[8:10]) < 1 or int(temp[8:10]) > 31:
        print("Invalid start-of-week entered (outside range year 2009-2050, month 01-12, or day 01-31).")
        print("Defaulting to 2024-03-11")
        temp = "2024-03-11"
    startDate = datetime.datetime(int(temp[0:4]), int(temp[5:7]), int(temp[8:10]))
    # The refDate will update as the log file is scanned each iteration, then get reset to startDate for each player.
    refDate = startDate

# Loop through each line in logs for each player and calculate playtimes.
join = datetime.datetime(2009,1,1) # Can't initialize blank so just set this to an arbitrary date.
left = datetime.datetime(2009,1,1)
weekTime = datetime.timedelta()
for playtime in playtimes: # Each playtime array has player name as [0], playtime as [1], and playtime rank as [2].
    bUnknownStatus:bool = True # For each player, this is set to false once the initial join/left log entry is found.
    # Enumerate puts the text from each element of the logs array into the line string like a regular for loop, but
    # also tracks the counter for which line it's on. This is used later when we define a small j loop.
    for i, line in enumerate(logs):

        # If the online status is unknown because the initial log entry has not been found yet, then search for
        # a log entry of leaving the server. This is because players may already be online at the very start of
        # the log data.
        if bUnknownStatus:
            if playtime[0] in line and "[Server thread/INFO]:" in line and "left the game" in line:
                join = logStart # Player was online at the start of the log files.

                # If start-of-week date is over a week before start of logs, print inactive weeks data until caught up.
                if bFileWeek:
                    while join > refDate + datetime.timedelta(days=7):
                        outFileWeek.writelines(playtime[0] + "," + str(refDate.date()) + ",\"" + str(weekTime) + "\"," +
                                               str(weekTime.total_seconds()) + "\n")
                        refDate = refDate + datetime.timedelta(days=7)
                        weekTime = datetime.timedelta() # Resets to 0:0:0

                left = datetime.datetime(int(line[1:5]), int(line[6:8]), int(line[9:11]), int(line[12:14]),
                                         int(line[15:17]), int(line[18:20]))
                bUnknownStatus = False # From here on out, we know the online status of the player.

                # If session spans multiple weeks (when weekly output is desired), split into 2 separate sessions.
                if bFileWeek and left > refDate + datetime.timedelta(days=7):
                    mid = refDate + datetime.timedelta(days=7)
                    sessionTime = mid - join
                    weekTime += sessionTime
                    playtime[1] += sessionTime
                    outFileWeek.writelines(playtime[0] + "," + str(refDate.date()) + ",\"" + str(weekTime) + "\"," +
                                           str(weekTime.total_seconds()) + "\n")
                    if bFileSes:
                        outFileSes.writelines(playtime[0] + "," + str(join) + "," + str(mid) + "," + str(sessionTime) +
                                              "," + str(sessionTime.total_seconds()) + "\n")
                    refDate = refDate + datetime.timedelta(days=7)
                    weekTime = datetime.timedelta() # Resets to 0:0:0
                    join = refDate

                # Calculate playtime for this initial partial session and add it to the running total for this player.
                sessionTime = left - join
                weekTime += sessionTime
                playtime[1] += sessionTime

                # Print data to session csv file.
                if bFileSes:
                    outFileSes.writelines(playtime[0] + "," + str(join) + "," + str(left) + "," + str(sessionTime) +
                                          "," + str(sessionTime.total_seconds()) + "\n")

                # Reset join/left variables for next iteration for the same player.
                join = datetime.datetime(2009, 1, 1)
                left = datetime.datetime(2009, 1, 1)

        # Search for the join time.
        if playtime[0] in line and "[Server thread/INFO]:" in line and "joined the game" in line:
            join = datetime.datetime(int(line[1:5]), int(line[6:8]), int(line[9:11]), int(line[12:14]),
                                     int(line[15:17]), int(line[18:20]))
            bUnknownStatus = False # From here on out, we know the online status of the player.

            # Join date is in a new week, so print out the previous week stats and reset for the new week.
            # While loop will continue to print inactive weeks data until caught up.
            if bFileWeek:
                while join > refDate + datetime.timedelta(days=7):
                    outFileWeek.writelines(playtime[0] + "," + str(refDate.date()) + ",\"" + str(weekTime) + "\"," +
                                           str(weekTime.total_seconds()) + "\n")
                    refDate = refDate + datetime.timedelta(days=7)
                    weekTime = datetime.timedelta() # Resets to 0:0:0

            # Now search for the corresponding left time.
            isOnline = True # If a left time is found this will be changed to false.
            for j in range(i+1, len(logs)): # i is the counter for the main "line" loop, from the enumerate function.
                if playtime[0] in logs[j] and "[Server thread/INFO]:" in logs[j] and "left the game" in logs[j]:
                    left = datetime.datetime(int(logs[j][1:5]), int(logs[j][6:8]), int(logs[j][9:11]),
                                             int(logs[j][12:14]), int(logs[j][15:17]), int(logs[j][18:20]))
                    isOnline = False
                    break # Break out of the j loop.

            # If the player was still connected at the end of the log, set left time to end of log.
            if isOnline:
                left = logEnd

            # If session spans multiple weeks (when weekly output is desired), split into 2 separate sessions.
            if bFileWeek and left > refDate + datetime.timedelta(days=7):
                mid = refDate + datetime.timedelta(days=7)
                sessionTime = mid - join
                weekTime += sessionTime
                playtime[1] += sessionTime
                outFileWeek.writelines(playtime[0] + "," + str(refDate.date()) + ",\"" + str(weekTime) + "\"," +
                                       str(weekTime.total_seconds()) + "\n")
                if bFileSes:
                    outFileSes.writelines(playtime[0] + "," + str(join) + "," + str(mid) + "," + str(sessionTime) +
                                          "," + str(sessionTime.total_seconds()) + "\n")
                refDate = refDate + datetime.timedelta(days=7)
                weekTime = datetime.timedelta()  # Resets to 0:0:0
                join = refDate

            # Calculate playtime for this session and add it to the running total for this player.
            sessionTime = left - join
            weekTime += sessionTime
            playtime[1] += sessionTime

            # Print data to session output csv file.
            if bFileSes:
                outFileSes.writelines(playtime[0] + "," + str(join) + "," + str(left) + "," + str(sessionTime) + "," +
                                      str(sessionTime.total_seconds()) + "\n")

            # Reset join/left variables for next iteration for the same player.
            join = datetime.datetime(2009, 1, 1)
            left = datetime.datetime(2009, 1, 1)

    # Output final week stats for this player.
    if bFileWeek:
        outFileWeek.writelines(playtime[0] + "," + str(refDate.date()) + ",\"" + str(weekTime) + "\"," +
                               str(weekTime.total_seconds()) + "\n")
        # Reset week stats variables for next player.
        refDate = startDate
        weekTime = datetime.timedelta()

# Done with player loop, so done writing csv output files.
if bFileSes:
    outFileSes.close()
    print("\nSession times output file " + os.path.basename(outFileSes.name) + " successfully written.")
if bFileWeek:
    outFileWeek.close()
    print("\nWeekly statistics output file " + os.path.basename(outFileWeek.name) + " successfully written.")

# Loop through to assign ranks to playtimes array.
for i, playtime in enumerate(playtimes):
    high = datetime.timedelta() # Records the highest playtime in the current iteration.
    for player in playtimes:
        # Rank is not yet assigned and playtime is highest so far.
        if player[2] == 0 and player[1] > high:
            high = player[1]

    # Assign rank
    for player in playtimes:
        if player[1] == high:
            player[2] = i+1

# Print playtimes in ranked order.
totalPlaytime = datetime.timedelta() # Total man-hours of all players.
# Round down 1 hour because logEnd was previously rounded up for calculating playtimes, but now we want the correct
# date. Usually the log ends at the end of the day so logEnd will be something like YYYY-01-02 00:00:00, but we want
# to report the last day of log data as YYYY-01-01.
logEndRounded = logEnd - datetime.timedelta(hours=1)
print("\nRanked playtimes from " + str(logStart.date()) + " to " + str(logEndRounded.date()) + " (in hours):")
for i, playtime in enumerate(playtimes):
    for player in playtimes:
        if player[2] == i+1:  # Found the next rank to print out.
            out = '{:5s}'.format(str(player[2]) + ". ")
            out = '{:25s}'.format(out + player[0] + ": ")
            hours = '{:6.1f}'.format(player[1].total_seconds() / 3600)
            out += hours
            totalPlaytime += player[1] # Adds this player to the total for all players.
            print(out)
print("\nTotal playtime of all players combined: " + '{:7.1f}'.format(totalPlaytime.total_seconds() / 3600) + " hours.")