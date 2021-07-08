# ===============================
# AUTHOR:   SAM REITER
# CREATE DATE: JUL-2021
# PURPOSE:  CRAIGSLIST SCRAPER & EMAIL CLIENT
# ==================================

import argparse
import sys
import time
import urllib.request
import webbrowser
import yaml
import requests
from bs4 import BeautifulSoup
from socket import error as SocketError
from sys import platform

sys.path.insert(1, 'lib/')
from sendSMTP import send_email
from settingsparse import SettingsParser


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
                return False
    except requests.exceptions.ConnectionError:
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
            print("\nWARNING: Found multiple cities named \'" + str(c) + "\'. Try adding \'<two letter state code>-\' to your city. e.g. \'jacksonville\' becomes either \'fl-jacksonville\' or \'nc-jacksonville\'.")
        i=0

    for key, value in rs.items():       # Adds citycodes to list
        for city in citylist:
            if city.lower() in value:
                y = value[city.lower()]
                citycodes.append(y)

    citycodes = list(set(citycodes))  # remove duplicates

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
    #print("number of citycodes entered: " + str(len(citycodes)))
    #print("number of citiesstates objects created: " + str(len(cities_states)))

    return cities_states

def get_search_strings(urls) -> list:

    strings = []

    for item in urls:
        s = item.split("craigslist.org", 1)[1].rstrip()
        strings.append(s)

    return strings


def scrape_link(link, delay, get_next_page=True):

    listings = []

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

        if result.find(class_='result-price'):  # TODO all scrapes should be in this if/else format
            list_price = result.find(class_='result-price').text
        else:
            list_price = "N/A"

        if result.find(class_='result-hood'):
            neighborhood = result.find(class_='result-hood').text
        else:
            neighborhood = "N/A"

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
            postURL=result.find(class_='result-title hdrlnk').get('href'),
            postHood=neighborhood)

        if not data in listings:
            listings.append(data)

    meta = cl_page.find(class_="no-js")
    if get_next_page and meta.find("link", rel="next"):
        if meta.find("link", rel="next"):
            nextpage = meta.find("link", rel="next").get("href")
            listings.append(scrape_link(nextpage, delay, get_next_page=True))

    return listings


def scrape_and_log_results(cities, parameters, delay=0) -> list:

    for string in parameters:
        for city in cities:
            searchurl = str("https://" + city + ".craigslist.org" + string)
            scraped_results = scrape_link(searchurl, delay, get_next_page=True)

    with open('results/results.yaml', 'w+') as outfile:
        yaml.dump(scraped_results, outfile, default_flow_style=False)

    return scraped_results


def notify_if_changed(new_results, old_results, settings) -> None:

    for new in new_results:
        if not new in old_results:

            print("Email Sent!!!")

            title, body = pretty_listing(new)
            title, body_condensed = pretty_listing(new, True)

            if settings.notify_email:
                send_email(
                    settings.smtp_addr,
                    settings.smtp_pw,
                    title,
                    body,
                    settings.email_recipients)

            site = new.get('postURL')

            if settings.open_browser:
                if uri_exists_stream(site):
                    open_url(site)
                elif uri_exists_stream(site):  # try a second time, just to be sure
                    open_url(site)
                else:
                    print(str(site) + " is not a valid URL.")


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
    scrape_and_log_results(cities, searchstrings, settings.search_delay)
    end = time.time()

    print("\nEXECUTING THESE " + str(len(searchstrings)*len(cities)) + " SCRAPES TAKES " + str(int(end) - int(start)) + " SECONDS.")


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

    if settings.notify_email and settings.smtp_test:    # send test email, if enabled
        print("\nSending test email to recipients in settings.txt...")
        send_email(
            settings.smtp_addr,
            settings.smtp_pw,
            "Test Email",
            str("Sending test notification email."),
            settings.email_recipients)

    cities = get_citycodes_from_citylist(settings.cities, settings.rosetta_path)   # import list of cities from settings
    states = settings.states
    if states:
        for state in states:
            for city in get_citycodes_from_state(state, settings.rosetta_path):        # import list of states from settings
                cities.append(city)     # append to list of cities
    cities = list(set(cities))      # remove duplicates from cities list

    searchstrings = get_search_strings(settings.search_urls)    # import search URLs from settings

    print_scrape_overview(searchstrings, cities, settings)

    # This loop is the meat of the program
    while True:
        newresults = scrape_and_log_results(cities, searchstrings, settings.search_delay)

        if oldresults:
            notify_if_changed(newresults, oldresults, settings)

        oldresults = newresults.copy()


if __name__ == "__main__":
    try:
        searcher()
    except KeyboardInterrupt:
        exit()
