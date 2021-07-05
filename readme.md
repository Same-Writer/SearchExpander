
# Search Expander
Application for scraping craigslist search results across multiple search strings, cities and states. Includes optional SMPT email notification client

## Install instructions

- Install Python3 
> sudo apt-get update \
> sudo apt-get install python3 git
- Install venv 
> python3 -m pip install --user --upgrade pip \
> python3 -m pip install --user virtualenv
- Clone SearchExpander
> git clone https://github.com/Same-Writer/SearchExpander.git \
> cd SearchExpander
- Create & activate virtual environment, install requriements
> python3 -m venv venv && source venv/bin/activate \
> pip install -r requirements.txt

## Execution instructions
> source venv/bin/activate \
> python3 clsearch.py

## Settings File overview

File location: **./etc/settings.yaml**

Contains settings and search configurations for running the application. 

### SMTP Client configuration
* In order to configure email notifications, you must set up an SMTP server. This can be done for free with Gmail (limit of 100 messages sent / day). Current recommendation is to make a throw-away gmail address and use the email and PW for that account.
* Once an account is created, you need to enable 'less secure apps'. Setting can be found at:
  * Account >> Manage Your Google Account >> Security >> Less Secure Apps >> Turn on access.
* Add this new SMTP account's email and password to etc/settings.yaml, and set 'send test : True' 
* Moving this SMTP to a secure access method is a to-do item, but for now a throwaway gmail account the recommendation. 
  
### App Settings
* __rosetta path__ :    File path to the rosetta file. See additional details on file below. 
* __log results__ :     Currently non-functional. Will turn detailed logging on and off.
* __results path__ :    Path to save results. Will create file if none exists, but must be pointed to an existing directory.
* __verbose__ :         Currently non-functional. Will toggle verbose command line output
* __searchdelay__ :     Time delay in between URL queries. Use this to reduce load on your internet link, if needed
  
### Search Parameters
* __run__ :             Currently non-functional. Toggle running these search parameters or not.
* __openbrowser__ :     When a new / changed listing is detected, open the listing's URL in a new chrome tab. 
* __notifyemail__ :     When a new / changed listing is detected, use the configured SMTP server to send an email to recipients listed in the 'email' field below. 
* __email__:            Email Recipients in a list below. Use an indented hyphen for each recipient
* __cities__:           These are the cities that your search(es) will be run across. 
    * Use the city name that you see on https://www.craigslist.org/about/sites, or check rosetta.yaml for a valid city name.
    * Searches for cities specified here will be combined with cities in the states listed below.
* __states__:           These are the states that your search(es) will be run across. 
    * It will include all cities listed under the state on https://www.craigslist.org/about/sites
    * Searches across states specified here will be combined with cities listed in 'cities' above
* __searchURLs__:       These are the craigslist search URLS that will be run over all cities & states above. 
    * Set up your full search with filters on craigslist.org and copy-paste the URL into these bulleted-fields
    * BEST PRACTICE: Use search narrowing methods, listed here to block out 'noise' in your search: https://www.craigslist.org/about/help/search
    * BEST PRACTICE: Sort by 'newest' rather than relevant. We don't dig past the first page of results, so make sure the latest results are on top. 
    * BEST PRACTICE: Set a min price of $0, rather than leaving it blank. Results without a price field make this program very sad.

**./etc/rosetta.yaml**

Lookup table for Craigslist searching. 
* Translates city names  (e.g. "colorado springs") to the craigslist city URL identifier (e.g. "cosprings").
  * This city URL identifier is then added into the craigslist URL format (e.g. https://cosprings.craigslist.org)
* Some grouped city names used by Craigslist (e.g. 'fresno / madera' : fresno) are also broken out into their individual names and all reference the same URL identifier ('fresno / madera' : fresno, 'fresno' : fresno, 'madera' : fresno)
* Groups cities into states.
* If you're importing this with another app, use a routine to remove duplicate URLs

**./bin/***

ToDo - these do nothing now. They'll include setup and run for the program. For now, just use install instructions above

**./etc/tests/**

These contain various tests for this app. 


SEO: Craigslist, scraper, scraping, facebook marketplace, email, notification, craigslist state, scrape and notify 