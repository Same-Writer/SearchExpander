
# Search Expander
Application for scraping craigslist search results across multiple search strings, cities and states. Includes optional SMPT email notification client

**./searches.txt**

Contains search strings to run. Add Craigslist search URLs, one per line. The city of the search in this file doesn't matter - it will be stripped out and replaced with search cities given in --cities and --states arguments. 

**./settings.yaml**

TODO: will contain global settings and filepaths for the program

**./bin/***

ToDo - these do nothing now. 

**./etc/Emails/***

Contains supporting files for SMTP email client. 

**./etc/rosetta.yaml**

Translates common city names like "colorado springs" to the craigslist city URL identifier "cosprings". Similarly, groups cities into states. 

**./etc/testRosetta.py**

Tests the city URL identifiers for validity. #TODO: make sure there aren't duplicates across different states (e.g. bloomington, IN = https://bloomington.craigslist.org while bloomington, IL = https://bn.craigslist.org)
