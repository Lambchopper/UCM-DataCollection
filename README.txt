UC Auto Command Script

This script will take a list of Cisco UC Nodes and login to their CLI then execute a command and log the results to a text file.

Used for when we need CLI output from every node in large clusters

I've used a modified version of this script (hard coded the uesr input) to run scheduled data collection.
For example, when troubleshooting intermittant connectivity, I scheduled this to run traceroute commands ever 5 minutes from select UC Nodes then
collected the results after the next end user problem report.

Requires Python Library Paramiko to automate the SSH session.