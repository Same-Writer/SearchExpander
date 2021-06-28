## V1 -- Sam Reiter

import argparse
import sys, os, time
import urllib.request
import webbrowser
import yaml
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

sys.path.insert(1, 'etc/Emails/')
from EmailClient import send_email


def import_rosetta():
    with open("etc/rosetta.yaml", "r") as stream:
        try:
            # print(yaml.safe_load(stream))
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def uri_exists_stream(uri: str) -> bool:
    try:
        with requests.get(uri, stream=True) as response:
            try:
                response.raise_for_status()
                return True
            except requests.exceptions.HTTPError:
                return False
    except requests.exceptions.ConnectionError:
        return False


def get_citycodes_from_state(state):

    citycodes = []

    rs = import_rosetta()
    for key, value in rs.items():
        if key == state:
            #print(key + " : " + str(value))
            for x, y in value.items():
                #print(x + " : " + y)
                citycodes.append(y)

    return citycodes


def get_citycodes_from_citylist(citylist):

    citycodes = []

    rs = import_rosetta()
    for key, value in rs.items():
        for city in citylist:
            if city in value:
                y = value[city]
                citycodes.append(y)

    return citycodes


def openURL(url, OS="Linux"):

    if OS == "Mac":
        # MacOS
        chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    elif OS == "Windows":
        # Windows
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    elif OS == "Linux":
        # Linux
        chrome_path = '/usr/bin/google-chrome %s'
    else:
        chrome_path = '/usr/bin/google-chrome %s'

    # https://stackoverflow.com/questions/38574629/webbrowser-not-opening-new-windows

    # TODO: figure out how to stop this "opening in existing browser session" output & occasional error
    # https://stackoverflow.com/questions/2323080/how-can-i-disable-the-webbrowser-message-in-python

    webbrowser.get(chrome_path).open(url)


def getSearchStrings(file) -> list:
    strings = []

    file1 = open(file, 'r')
    lines = file1.readlines()

    for line in lines:
        s = line.split("craigslist.org", 1)[1].rstrip()
        strings.append(s)

    return strings


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", nargs='+', default=[],
                        help="Run search terms over given list of states")
    parser.add_argument("--cities", nargs='+', default=[],
                        help="Run search terms over given list of states")
    args = parser.parse_args()

    return args


def open_searches_chrome(cities, parameters):
    for string in parameters:
        for city in cities:
            site = str("https://" + str(city) + ".craigslist.org" + string)
            if uri_exists_stream(site):
                openURL(site)
            elif uri_exists_stream(site):   # try a second time, just to be sure
                openURL(site)
            else:
                print("https://" + city + ".craigslist.org is not a valid URL.")
            time.sleep(.1)
    if not cities:
        print("No cities or states provided to search. Use --cities or --states arguments when running this script")


def scrape_and_log_results(cities, parameters):
    listings = []
    for string in parameters:
        for city in cities:
            source = urllib.request.urlopen("https://" + city + ".craigslist.org" + string).read()
            clPage = BeautifulSoup(source, 'lxml')

            results = clPage.find(id="search-results",class_='rows')

            for result in results.findAll(class_="result-info"):
                data = dict(
                    postID=result.find(class_='result-title hdrlnk').get('data-id'),
                    listTitle=result.find(class_='result-heading').a.text,
                    listDate=result.find(class_='result-date').get('title'),
                    listDateTime=result.find(class_='result-date').get('datetime'),
                    listPrice=result.find(class_='result-price').text,
                    postURL=result.find(class_='result-title hdrlnk').get('href'),
                )
                if not data in listings:
                    listings.append(data)
    #print(*listings, sep="\n")

    with open('results.yaml', 'w') as outfile:
        yaml.dump(listings, outfile, default_flow_style=False)

    return listings

def notify_if_new(results_list, tthresh=5):

    for results in results_list:
        posttime = datetime.strptime((results.get('listDateTime')), "%Y-%m-%d %H:%M")
        #print(str(posttime) + " " + str(results))
        #print("current time: " + str(datetime.now()))
        #print("post time: " + str(posttime))
        #print("threshold time: " + str(posttime + timedelta(minutes=tthresh)))
        #print(str(datetime.now() < posttime + timedelta(minutes=tthresh)))
        if datetime.now() < posttime + timedelta(minutes=tthresh):
           print("Email Sent!!!")
           send_email(str(results), ['sam.reiter88@gmail.com'])

def searcher():

    args = parse_args()     # take in CLI arguments
    states = args.states
    c = args.cities         # add cities to search

    sleeptime = 2    # how often should we rerun the search (minutes)

    for state in states:
        for city in get_citycodes_from_state(state):
            c.append(city)

    c = list(set(c))        # remove duplicates
    ss = getSearchStrings("searches.txt")

    #open_searches_chrome(c, ss)

    while True:
        l = scrape_and_log_results(c, ss)
        notify_if_new(l, 20)
        time.sleep(sleeptime)
        print('loop done!')

if __name__  ==  "__main__" :
    searcher()