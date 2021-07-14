# ===============================
# AUTHOR:   SAM REITER
# CREATE DATE: JUL-2021
# PURPOSE:  CRAIGSLIST SCRAPER & EMAIL CLIENT
# ==================================

import argparse
import sys
import time
from datetime import datetime
import urllib.request
import webbrowser
import yaml
import requests
from bs4 import BeautifulSoup
from socket import error as SocketError
from sys import platform
from alive_progress import alive_bar, config_handler
import logging

sys.path.insert(1, 'lib/')
from sendSMTP import send_email
from settingsparse import SettingsParser

logger = logging.getLogger('SearchExpander')


def import_rosetta(file):

    with open(file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit("Error loading etc/rosetta.yaml check that file exists and permissions are correct.")


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("--states", nargs='+', default=[],
                        help="Run search terms over given list of states")
    parser.add_argument("--cities", nargs='+', default=[],
                        help="Run search terms over given list of states")
    parser.add_argument("--settings", nargs='?', default='settings.yaml',  type=str,
                        help="use this to specify non-default settings file in the etc/ directory")

    args = parser.parse_args()

    return args


def uri_exists_stream(uri: str) -> bool:
    # checks that a given link exists. supposedly does this w/o loading all data from site

    try:
        with requests.get(uri, stream=True) as response:
            try:
                response.raise_for_status()
                return True
            except requests.exceptions.HTTPError:
                logger.info("Accessing " + str(uri) + " not successful")
                return False
    except requests.exceptions.ConnectionError:
        logger.info("Accessing " + str(uri) + " not successful")
        return False


def open_url(url) -> None:

    if platform == "darwin":
        chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    elif platform == "win32":
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    elif platform == "linux" or platform == "linux2":
        chrome_path = '/usr/bin/google-chrome %s'
    else:
        #chrome_path = '/usr/bin/google-chrome %s'
        pass

    logger.info("Accessing: " + str(url) + 'in Chrome')
    logger.info("Chrome path: " + str(chrome_path))
    webbrowser.get(chrome_path).open(url)


def open_searches_chrome(cities, parameters) -> None:

    for string in parameters:
        for city in cities:
            site = str("https://" + str(city) + ".craigslist.org" + string)
            if uri_exists_stream(site):
                open_url(site)
            elif uri_exists_stream(site):   # try a second time, just to be sure
                open_url(site)
            else:
                print("https://" + city + ".craigslist.org is not a valid URL.")
            time.sleep(.1)  # helps mitigate warnings thrown from chrome
    if not cities:
        print("No cities or states provided to search. add cities and states to settings.yaml")


def get_citycodes_from_state(state, rosetta_path) -> list:

    citycodes = []

    rs = import_rosetta("etc/rosetta.yaml")

    for key, value in rs.items():
        if key.lower() == state.lower():
            for x, y in value.items():
                citycodes.append(y)

    citycodes = list(set(citycodes))        #remove duplicates

    logger.info("States -> CityURLs from rosetta.txt... State: " + state + " Cities: " + str(citycodes))

    return citycodes


def get_citycodes_from_citylist(citylist, rosetta_path) -> list:

    citycodes = []
    i=0

    rs = import_rosetta("etc/rosetta.yaml")

    for c in citylist:              # Logic to check that cities specified in settings.yaml are unique. Print warning if not.
        for state in rs:
            for cc in rs[state]:
                if c.lower() == cc.lower():
                    i += 1
        if i > 1:
            logger.warning("Found multiple cities named \'" + str(c) + "\'. Try adding \'<two letter state code>-\' to your city. e.g. \'jacksonville\' becomes either \'fl-jacksonville\' or \'nc-jacksonville\'.")
        i=0

    for key, value in rs.items():       # Adds citycodes to list
        for city in citylist:
            if city.lower() in value:
                y = value[city.lower()]
                citycodes.append(y)

    citycodes = list(set(citycodes))  # remove duplicates

    logger.info("Cities -> CityURLs from rosetta.txt: " + str(citycodes))

    return citycodes


def get_city_state_from_citycode(citycodes, rosetta_path) -> list:

    cities_states = [{'state': '', 'city': '', 'url': ''}]

    rs = import_rosetta(rosetta_path)
    for cityurl in citycodes:
        for state, city in rs.items():
            for key, value in city.items():
                if value == cityurl:
                    cities_states.append({'state': state, 'city': key, 'url': cityurl})
                    break

    cities_states.pop(0)
    logger.info("number of citycodes entered: " + str(len(citycodes)))
    logger.info("number of citiesstates objects created: " + str(len(cities_states)))

    return cities_states


def get_search_strings(urls) -> list:

    strings = []

    for item in urls:
        s = item.split("craigslist.org", 1)[1].rstrip()
        strings.append(s)

    logger.info("Search Strings to be used: " + str(strings))

    return strings


def scrape_link(link, delay, get_next_page=False):

    listings = []
    #print(link)
    while True:
        try:
            time.sleep(delay)
            source = urllib.request.urlopen(link).read()
        except SocketError as e:
            print("SocketError: " + str(e))
            continue
        break

    cl_page = BeautifulSoup(source, 'lxml')
    results = cl_page.find(id="search-results", class_='rows')

    for result in results.findAll(class_="result-info"):

        if result.find(class_='result-price'):
            list_price = result.find(class_='result-price').text
        else:
            list_price = "N/A"

        if result.find(class_='result-hood'):
            neighborhood = result.find(class_='result-hood').text
        else:
            neighborhood = "N/A"

        data = dict(
            postID=result.find(class_='result-title hdrlnk').get('data-id'),
            listTitle=result.find(class_='result-heading').a.text,
            listDate=result.find(class_='result-date').get('title'),
            listDateTime=result.find(class_='result-date').get('datetime'),
            listPrice=list_price,
            postURL=result.find(class_='result-title hdrlnk').get('href'))

        if not data in listings:
            listings.append(data)

    meta = cl_page.find(class_="no-js")
    if get_next_page and meta.find("link", rel="next"):
        if meta.find("link", rel="next"):
            nextpage = meta.find("link", rel="next").get("href")
            for listing in scrape_link(nextpage, delay, get_next_page):
                listings.append(listing)

    return listings


def save_to_yaml(results, append=False):
    with open(results, 'w+') as outfile:
        yaml.dump(results, outfile, default_flow_style=False)
        #logger.info("Dumping results to " + str(results))


def scrape_and_save_results(cities, parameters, settings, bar=None) -> list:

    scraped_results = []

    for string in parameters:
        for city in cities:
            if bar:
                bar()
            searchurl = str("https://" + city + ".craigslist.org" + string) # build working CL URLs from city/search
            results_on_page = scrape_link(searchurl, settings.search_delay, settings.scrape_next)   # scrape URL
            for search_results in results_on_page:
                scraped_results.append(search_results)      # build list of results

    save_to_yaml(settings.results_path)

    return scraped_results


def notify_if_changed(new_results, old_results, settings) -> None:

    changed = False
    changes = []

    for new in new_results:
        if new not in old_results:
            logger.info("NEW/CHANGED RESULT: " + str(new))
            logger.info("Previously stored results: " + str(old_results))

            changed = True
            changes.append(new)

            title, body = pretty_listing(new)
            title, body_condensed = pretty_listing(new, True)

            if settings.notify_email:
                send_email(
                    settings,
                    title,
                    body,
                    settings.email_recipients)
                print("Email Sent!!!")

            site = new.get('postURL')

            if settings.open_browser:
                if uri_exists_stream(site):
                    open_url(site)
                elif uri_exists_stream(site):  # try a second time, just to be sure
                    open_url(site)
                else:
                    print(str(site) + " is not a valid URL.")

    return changed, changes


def pretty_listing(listing, condensed=False) -> str:

    if condensed == True:
        title =  str("Listing Title: " + listing["listTitle"])
        body = str("URL: " + listing["postURL"])
    else:
        title =  str("Listing Title: " + listing["listTitle"])
        body =   str("Price: " + listing["listPrice"] + "\n"
                   + "Date: " + listing["listDate"] + "\n"
                   + "URL: " + listing["postURL"] + "\n"
                   + "Post ID: " + listing["postID"])
    logger.info("Condensed = " + condensed)
    logger.info(title)
    logger.info(body)
    return title, body


def print_scrape_overview(searchstrings, cities, settings) -> None:

    ss = []
    cc = []

    for s in searchstrings:
        ss.append("\thttps://<CITY>.craigslist.org" + str(s))
    csu = get_city_state_from_citycode(cities, settings.rosetta_path)

    for i, c in enumerate(csu):
        if cities[i] == c['url']:
            cc.append("\t" +  c['state'] + " : " + c['city'] + " : https://" + c['url'] + ".craigslist.org")
    cc.sort()

    print("\nRUNNING THE FOLLOWING SEARCH STRINGS:")
    print("\t", sep="")
    print(*ss, sep="\n")
    print("\nOVER THE FOLLOWING CITIES:\n")
    print(*cc, sep="\n")

    start = time.time()
    results = scrape_and_save_results(cities, searchstrings, settings)
    end = time.time()

    print("\nEXECUTING THESE " + str(len(searchstrings)*len(cities)) + " SCRAPES RETURNS " + str(len(results)) + " RESULTS IN " + str(int(end) - int(start)) + " SECONDS.\n")


def searcher():

    oldresults= []

    args = parse_args()     # take in CLI arguments

    if args.settings == 'settings.yaml':                # read in settings file
        settings = SettingsParser('etc/settings.yaml')
        print("\nUsing settings file: etc/settings.yaml")
    else:
        path = str('etc/' + args.settings)
        settings = SettingsParser(path)
        print("\nUsing settings file: etc/" + args.settings)

    settings.parse_settings()                           # parse settings

    logger.setLevel(settings.log_level)                             # configure logging
    filehandler_dbg = logging.FileHandler('log/' + logger.name + '-debug.log', mode='w')
    filehandler_dbg.setLevel('DEBUG')
    streamformatter = logging.Formatter(fmt='%(levelname)s:%(threadName)s:%(funcName)s:\t\t%(message)s',
                                        datefmt='%H:%M:%S')  # We only want to see certain parts of the message
    filehandler_dbg.setFormatter(streamformatter)
    logger.addHandler(filehandler_dbg)

    logger.info("Run started on : " + str(datetime.now()) + "\n")
    logger.info("Settings File: " + settings.settings_path)

    # loop over a list of all non-method attributes of the settings class, log names and values.
    for prop in [a for a in dir(settings) if not a.startswith('__') and not callable(getattr(settings, a))]:
        logger.info(prop + " = " + str(eval('settings.%s' %prop)))

    if settings.notify_email and settings.smtp_test:    # send test email, if enabled
        logger.info("Sending test email to recipients in settings.txt")
        send_email(
            settings,
            "Test Email",
            str("Sending test notification email."),
            settings.email_recipients)

    cities = get_citycodes_from_citylist(settings.cities, settings.rosetta_path)   # import list of cities from settings
    states = settings.states
    if states:
        for state in states:
            for city in get_citycodes_from_state(state, settings.rosetta_path):        # import list of states from settings
                cities.append(city)     # append to list of cities
    cities = list(set(cities))          # remove duplicates from final cities list
    logger.info("All CityURLs (duplicates removed): " + str(cities))

    searchstrings = get_search_strings(settings.search_urls)    # import search URLs from settings

    print_scrape_overview(searchstrings, cities, settings)

    config_handler.set_global(length=6, bar='blocks')   # set up progress bar - refreshed for each search
    with alive_bar(force_tty=True) as bar:

        # This loop is the meat of the program
        while True:
            newresults = scrape_and_save_results(cities, searchstrings, settings, bar)
            if oldresults:
                notify_if_changed(newresults, oldresults, settings)
            else:
                logger.info("First full scrape results: ")
                for listing in newresults:
                    logger.info(listing)

            oldresults = newresults.copy()


if __name__ == "__main__":
    try:
        searcher()
    except KeyboardInterrupt:
        exit()
