This is a Python script I wrote to parse playtime data from Minecraft server logs. It scans all the log files in the folder and modifies the timestamps to include date+timestamp (without modifying the original log files). Optionally, it can write the combined log to an output file if you want to more easily search for other things.

The playtime.py script has the following features:
- Calculates total playtime for each player and prints out a ranked list.
- Option to export a session csv file containing data on all play sessions (player name, join time, left time, session duration, total seconds of each session).
- Option to export a weekly statistics csv file containing the following data:
  - Total server playtime for each week (in human-readable format as well as total seconds and hours).
  - Hourly time-of-day playtime for each week (in hours). This is an average for the week, but summed for each player, so it effectively calculates average number of players online for each hour of the day.
  - Total player playtime for each week (in human-readable format as well as total seconds and hours). There is a separate table of data for each individual player.

The exe file was compiled using pyinstaller and should work on any Windows machine. Or you can run the playtime.py script using your favorite Python interpreter. The readFiles.py script is automatically called by the main playtime.py script, but if all you wanted to do was output a merged log file with dates added to the timestamps, you could run readFiles.py independently.

I'm new to Github so I don't know if I've created this repository/project correctly. If you find this little script useful, great. If not, feel free to leave comments but I may or may not do anything with them. I just wanted others to be able to benefit from this script since I couldn't find any existing code to do what I wanted. Also I'm using this program to learn the basics of coding in Python (my first Python program).
