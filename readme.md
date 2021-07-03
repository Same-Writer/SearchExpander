
# Search Expander
Application for scraping craigslist search results across multiple search strings, cities and states. Includes optional SMPT email notification client

__Install instructions__
>
__Execution instructions__
>
**./etc/settings.yaml**

Contains settings and search configurations for running the application. 

* **SMTP Client configuration**
    * In order to configure email notifications, you must set up an SMTP server. Current recommendation is to make a throw-away gmail address and use the email and PW for that account. 
    * Once an account is created, you need to follow Account >> Manage Your Google Account >> Security >> Less Secure Apps >> Turn in access.
    * Moving this SMTP to a secure access method is a to-do item, but for now a throwaway gmail account is recommended. 

**./etc/rosetta.yaml**

Translates common city names like "colorado springs" to the craigslist city URL identifier "cosprings". Similarly, groups cities into states. Currently these are case sensitive, so check rosetta.yaml if you get a lookup error. 

**./bin/***

ToDo - these do nothing now. They'll include setup and run for the email client

**./etc/tests/**

These contain various tests for this app. 