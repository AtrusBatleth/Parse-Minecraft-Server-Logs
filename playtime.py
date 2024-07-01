# This module scans data from the logs array prepared using the readFiles.py module and calculates various
# total and weekly playtime statistics. The readFiles.py module is called automatically via import so this
# is the only module you need to run (probably bad coding style but hey, it works).

import os # Used to write output csv files
import datetime # Used for datetime objects
import copy # Used for copy.copy() function to copy class instances.
import readFiles # Separate module that reads all the input files into logs array.
logs:str = readFiles.logs # Array containing all log file contents.

class Session: # Class to keep track of a single play session.
    def __init__(self, join, left):
        self.join = join
        self.left = left
        self.duration = left - join
        self.hourlyTime = []
        for hour in range(24): # Initialize all 24 hours to 0:0:0.
            self.hourlyTime.append(datetime.timedelta())

        # Tally hours of the day for this session.
        # upper is the time rounded up to the next hour, while lower is the starting time (initially the join time,
        # but later will be the even hour beginning).
        lower = join
        upper = lower + datetime.timedelta(hours=1)
        upper = datetime.datetime(upper.year, upper.month, upper.day, upper.hour, 0, 0)
        while left > upper: # End of session is beyond the current hour block of time.
            self.hourlyTime[lower.hour] += upper - lower
            lower += datetime.timedelta(hours=1)
            lower = datetime.datetime(lower.year, lower.month, lower.day, lower.hour, 0, 0)
            upper += datetime.timedelta(hours=1) # upper always starts as a rounded hour so no need to zero the min/sec.
        # Add the final segment.
        self.hourlyTime[lower.hour] += left - lower

class Week: # Class to keep track of weekly statistics.
    def __init__(self, weekStart, weekTime):
        self.weekStart = weekStart
        self.weekEnd = weekStart + datetime.timedelta(days=6)
        self.weekTime = weekTime
        self.hourlyTime = []
        for hour in range(24): # Initialize all 24 hours to 0:0:0.
            self.hourlyTime.append(datetime.timedelta())

class Player: # Class to keep track of total playtime stats for a single player.
    def __init__(self, name):
        self.name = name
        self.playtime = datetime.timedelta() # Total playtime across all input log files.
        self.rank = 0 # Rank of total playtime.
        self.sessions = []
        self.weeks = []
    # Adds a new play session. The join and left arguments are intended to be datetime.datetime objects.
    def add_session(self, join, left):
        self.sessions.append(Session(join, left))
        self.playtime += left - join
    # Adds a new week for weekly playtime.
    def add_week(self, weekStart, weekTime):
        self.weeks.append(Week(weekStart, weekTime))

Players = [] # Master array of class Player.
weeksTotal = [] # Array of total weekly server playtimes.

# Function to calculate total weekly server playtimes.
def calc_weeks_total(weeksTotal, Players):
    # First populate the list of weeks in the weeksTotal array.
    for player in Players:
        if len(player.weeks) > len(weeksTotal): # This player has more weeks than the weeksTotal array.
            weeksTotal = [] # First delete the existing weeksTotal array.
            for week in player.weeks: # Add this players list of weeks to the weeksTotal array.
                # Need to use the copy.copy() function otherwise it will just copy a pointer to the class instance.
                weeksTotal.append(copy.copy(week))
    # Now the list of weeks is populated, but need to reset the times recorded in each.
    for weekTotal in weeksTotal:
        weekTotal.weekTime = datetime.timedelta()
    # Loop through each player and add their weekly playtimes.
    for player in Players:
        for week in player.weeks:
            # For each player week data, loop through the weeksTotal array to find a matching start date.
            for weekTotal in weeksTotal:
                if week.weekStart == weekTotal.weekStart:
                    weekTotal.weekTime += week.weekTime # Add this players time to the total.
    # Loop through each week and for each player, add hourly playtimes for that week.
    for week in weeksTotal:
        for player in Players:
            for session in player.sessions:
                if session.join > week.weekStart and session.join < week.weekStart + datetime.timedelta(days=7):
                    for hour in range(24):
                        week.hourlyTime[hour] += session.hourlyTime[hour]
    return weeksTotal

# Function to write session csv output file.
def write_ses(outFileSes, Players):
    outFileSes.writelines("Player,Joined,Left,Session Time,Seconds\n")
    for player in Players:
        for session in player.sessions:
            outFileSes.writelines(player.name + "," + str(session.join) + "," + str(session.left) + "," +
                                  str(session.duration) + "," + str(session.duration.total_seconds()) + "\n")
    outFileSes.close()
    print("\nSession times output file " + os.path.basename(outFileSes.name) + " successfully written.")

# Function to write weekly csv output file.
def write_week(outFileWeek, weeksTotal, Players):
    outFileWeek.writelines("Player,Week Starting,Playtime,Seconds,Hours,00,01,02,03,04,05,06,07,08,09,10,11,12," +
                           "13,14,15,16,17,18,19,20,21,22,23\n")
    for week in weeksTotal:
        outFileWeek.writelines("Total," + str(week.weekStart.date()) + ",\"" + str(week.weekTime) + "\"," +
                               str(week.weekTime.total_seconds()) + "," + str(week.weekTime.total_seconds()/3600) + "," +
                               str(week.hourlyTime[0].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[1].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[2].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[3].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[4].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[5].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[6].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[7].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[8].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[9].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[10].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[11].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[12].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[13].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[14].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[15].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[16].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[17].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[18].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[19].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[20].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[21].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[22].total_seconds()/3600/7) + "," +
                               str(week.hourlyTime[23].total_seconds()/3600/7) + "," + "\n")
    for player in Players:
        for week in player.weeks:
            outFileWeek.writelines(player.name + "," + str(week.weekStart.date()) + ",\"" + str(week.weekTime) + "\"," +
                                   str(week.weekTime.total_seconds()) + "," +
                                   str(week.weekTime.total_seconds() / 3600) + "\n")
    outFileWeek.close()
    print("\nWeekly statistics output file " + os.path.basename(outFileWeek.name) + " successfully written.")

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
    # Looking for [Server thread/INFO] in line[22:44] ensures it is actually a log entry generated by the server
    # and not a player typing "[Server thread/INFO]" in chat (as unlikely as that would be).
    if "joined the game" in line and "[Server thread/INFO]:" in line[22:44]:
        # The split() function splits the string into individual words (space delimited), and in the case of joining
        # server log entries, the username is the 4th word in the line. Exception is when the player was afk when they
        # previously left, when they re-join it shows their name as "[AFK] name". So the replace() function removes
        # that to avoid name mis-matches.
        name = line.replace("[AFK]", "").split()[4]

        # Special case for first player name.
        if len(Players) == 0:
            Players.append(Player(name))

        # Try to find the player name in the players array, and if it's not found, add it.
        nameFound = False
        for player in Players:
            if player.name == name:
                nameFound = True
        if nameFound == False:
            Players.append(Player(name))

    # Update the logEnd date; at the end of the loop this should reflect the final log entry.
    if line[0] == "[":
        logEnd = datetime.datetime(int(line[1:5]), int(line[6:8]), int(line[9:11]), int(line[12:14]), int(line[15:17]),
                                   int(line[18:20]))

# Round up logEnd to the nearest hour. Typically the log will reflect a complete calendar day where the final log
# entry will be something like [23:59:00]. We want to round that up since logEnd is used to calculate playtime for
# players still logged in at the end of the final log file.
logEnd = (datetime.datetime(logEnd.year, logEnd.month, logEnd.day, logEnd.hour, 0, 0) +
          datetime.timedelta(hours=1))

# Set start date for weekly statistics. Defaults to logStart
if bFileWeek: # User wants the weekly statistics csv output file.
    print("\nThe initial start-of-week date is used to define weekly intervals for all weeks that follow.")
    print("It may be a date prior to the start of your log files, but if it is 7 days or more prior,")
    print("then the csv output file will include rows with 0 data. If the start-of-week date is later")
    print("than the start of your log files, then the first row of data will represent more than one")
    print("weeks worth. If no date is entered, it defaults to the first date found in the log files.")
    print("(Which is " + str(logStart.year) + "-" + '{:02d}'.format(logStart.month) + "-" + '{:02d}'.format(logStart.day) + ")")
    temp = input("Enter the start-of-week date in format YYYY-MM-DD: ")
    # If the length is too small or any of the expected numbers are non-decimal, the date is invalid.
    if len(temp) < 10 or temp[0:4].isdecimal() == False or temp[5:7].isdecimal() == False or temp[8:10].isdecimal() == False:
        temp = str(logStart.year) + "-" + '{:02d}'.format(logStart.month) + "-" + '{:02d}'.format(logStart.day)
    # Check that year/month/day numbers are within a reasonable range.
    elif int(temp[0:4]) < 2009 or int(temp[0:4]) > 2050 or int(temp[5:7]) < 1 or int(temp[5:7]) > 12 or int(temp[8:10]) < 1 or int(temp[8:10]) > 31:
        print("Invalid start-of-week entered (outside range year 2009-2050, month 01-12, or day 01-31).")
        temp = str(logStart.year) + "-" + '{:02d}'.format(logStart.month) + "-" + '{:02d}'.format(logStart.day)
    print("Using start-of-week " + temp)
    startDate = datetime.datetime(int(temp[0:4]), int(temp[5:7]), int(temp[8:10]))
    # The refDate will update as the log file is scanned each iteration, then get reset to startDate for each player.
    refDate = startDate

# Loop through each line in logs for each player and calculate playtimes.
weekTime = datetime.timedelta()
for player in Players:
    bUnknownStatus:bool = True # For each player, this is set to false once the initial join/left log entry is found.
    # Enumerate puts the text from each element of the logs array into the line string like a regular for loop, but
    # also tracks the counter for which line it's on. This is used later when we define a small j loop.
    for i, line in enumerate(logs):

        # If the online status is unknown because the initial log entry has not been found yet, then search for
        # a log entry of leaving the server. This is because players may already be online at the very start of
        # the log data.
        if bUnknownStatus:
            # Need to check length of split() to prevent crash in if statement immediately following.
            if len(line.replace("[AFK]", "").replace("AFK ", "").split()) > 4:
                # Checking player name in split()[4] ensures it is the proper player name for this log entry, because
                # if a player changes their name the log entry will say "new-player (formerly known as old-player)".
                if player.name == line.replace("[AFK]", "").replace("AFK ", "").split()[4] and "[Server thread/INFO]:" in line[22:44] and "left the game" in line:
                    join = logStart # Player was online at the start of the log files.

                    # If start-of-week date is over a week before start of logs, create inactive weeks data until caught up.
                    if bFileWeek: # User wants weekly csv file output.
                        while join > refDate + datetime.timedelta(days=7):
                            player.add_week(refDate, datetime.timedelta())
                            refDate = refDate + datetime.timedelta(days=7)
                            weekTime = datetime.timedelta() # Resets to 0:0:0

                    left = datetime.datetime(int(line[1:5]), int(line[6:8]), int(line[9:11]), int(line[12:14]),
                                            int(line[15:17]), int(line[18:20]))
                    bUnknownStatus = False # From here on out, we know the online status of the player.

                    # If session spans multiple weeks (when weekly output is desired), split into 2 separate sessions.
                    if bFileWeek and left > refDate + datetime.timedelta(days=7):
                        mid = refDate + datetime.timedelta(days=7)
                        sessionTime = mid - join
                        player.add_session(join, mid)
                        player.add_week(refDate, sessionTime)
                        refDate = refDate + datetime.timedelta(days=7)
                        weekTime = datetime.timedelta() # Resets to 0:0:0
                        join = refDate

                    # Calculate playtime for this initial partial session and add it to the running total for this player.
                    sessionTime = left - join
                    weekTime += sessionTime
                    player.add_session(join, left)

        # Search for the join time.
        # Checking player name in split()[4] ensures it is the proper player name for this log entry, because
        # if a player changes their name the log entry will say "new-player (formerly known as old-player)".
        # Need to check length of split() to prevent crash in if statement immediately following.
        if len(line.replace("[AFK]", "").replace("AFK ", "").split()) > 4:
            if player.name == line.replace("[AFK]", "").replace("AFK ", "").split()[4] and "[Server thread/INFO]:" in line[22:44] and "joined the game" in line:
                join = datetime.datetime(int(line[1:5]), int(line[6:8]), int(line[9:11]), int(line[12:14]),
                                         int(line[15:17]), int(line[18:20]))
                bUnknownStatus = False # From here on out, we know the online status of the player.

                # Join date is in a new week, so save the previous week stats and reset for the new week.
                # While loop will continue to create inactive weeks data until caught up.
                if bFileWeek:
                    while join > refDate + datetime.timedelta(days=7):
                        player.add_week(refDate, weekTime)
                        refDate = refDate + datetime.timedelta(days=7)
                        weekTime = datetime.timedelta() # Resets to 0:0:0

                # Now search for the corresponding left time.
                isOnline = True # If a left time is found this will be changed to false.
                for j in range(i+1, len(logs)): # i is the counter for the main "line" loop, from the enumerate function.
                    # Need to check length of split() to prevent crash in if statement immediately following.
                    if len(logs[j].replace("[AFK]", "").replace("AFK ", "").split()) > 4:
                        if player.name == logs[j].replace("[AFK]", "").replace("AFK ", "").split()[4] and "[Server thread/INFO]:" in logs[j][22:44] and "left the game" in logs[j]:
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
                    player.add_session(join, mid)
                    player.add_week(refDate, weekTime)
                    refDate = refDate + datetime.timedelta(days=7)
                    weekTime = datetime.timedelta()  # Resets to 0:0:0
                    join = refDate

                # Calculate playtime for this session and add it to the running total for this player.
                sessionTime = left - join
                weekTime += sessionTime
                player.add_session(join, left)

    # Save final week stats for this player.
    if bFileWeek:
        player.add_week(refDate, weekTime)
        # Reset week stats variables for next player.
        refDate = startDate
        weekTime = datetime.timedelta()

# Write session csv output file if requested.
if bFileSes:
    write_ses(outFileSes, Players)

# Write weekly csv output file if requested.
if bFileWeek:
    weeksTotal = calc_weeks_total(weeksTotal, Players)
    write_week(outFileWeek, weeksTotal, Players)

# Loop through to assign ranks to players.
for i, OuterLoop in enumerate(Players):
    high = datetime.timedelta() # Records the highest playtime in the current iteration.
    for player in Players:
        # Rank is not yet assigned and playtime is highest so far.
        if player.rank == 0 and player.playtime > high:
            high = player.playtime

    # Assign rank
    for player in Players:
        if player.playtime == high:
            player.rank = i+1

# Print playtimes in ranked order.
totalPlaytime = datetime.timedelta() # Total man-hours of all players.
# Round down 1 hour because logEnd was previously rounded up for calculating playtimes, but now we want the correct
# date. Usually the log ends at the end of the day so logEnd will be something like YYYY-01-02 00:00:00, but we want
# to report the last day of log data as YYYY-01-01.
logEndRounded = logEnd - datetime.timedelta(hours=1)
print("\nRanked playtimes from " + str(logStart.date()) + " to " + str(logEndRounded.date()) + " (in hours):")
for i, OuterLoop in enumerate(Players):
    for player in Players:
        if player.rank == i+1:  # Found the next rank to print out.
            out = '{:5s}'.format(str(player.rank) + ". ")
            out = '{:25s}'.format(out + player.name + ": ")
            hours = '{:6.1f}'.format(player.playtime.total_seconds() / 3600)
            out += hours
            totalPlaytime += player.playtime # Adds this player to the total for all players.
            print(out)
print("\nTotal playtime of all players combined: " + '{:7.1f}'.format(totalPlaytime.total_seconds() / 3600) + " hours.")

temp = input("\nPress Enter to exit program.")