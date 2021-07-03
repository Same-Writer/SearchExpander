import sys
sys.path.insert(1, '..')

import time
from clsearch import uri_exists_stream, import_rosetta


def check_urls(rosetta_stream):
    failed = False
    j = 0

    for key, value in rosetta_stream.items():
        i = value.items()
        print("\n" + key, end='')
        for city in value:
            # print(value[city])
            site = str("https://" + str(value[city]) + ".craigslist.org")
            verdict = uri_exists_stream(site)
            if not verdict:
                time.sleep(3)  # wait 3 seconds and retry before throwing fail
                if uri_exists_stream(site):
                    print(
                        "\n" + key + " => " + city + " : \t https://" + value[city] + ".craigslist.org does not exist")
                    failed = True
            else:
                print('.', end='')

    if failed:
        print("\n\nUnable to resolve all URLs in rosetta.yaml. See output above.")
    else:
        print("\n\nURL validity check passed!")


def check_redundant_url(rosetta_stream):

    failed = False

    for state in rosetta_stream:
        for city in rosetta_stream[state]:
            for state1 in rosetta_stream:
                if state != state1:
                    for city1 in rosetta_stream[state1]:
                        if rosetta_stream[state][city] == rosetta_stream[state1][city1]:
                            print("\nFound redundant URL across states!")
                            print(state + " : " + city + " : " + rosetta_stream[state][city] + " = " + state1 + " : " + city1 + " : " + rosetta_stream[state1][city1])
                            failed = True

    if failed:
        print("\n\nSome cities in rosetta.txt are redundant across states. See output above.")
    else:
        print("\nRedundancy check passed!")

def check_redundant_citykey(rosetta_stream):

    failed = False

    for state in rosetta_stream:
        for city in rosetta_stream[state]:
            for state1 in rosetta_stream:
                if state != state1:
                    for city1 in rosetta_stream[state1]:
                        if city == city1:
                            print("\nFound redundant cityname across states!")
                            print(state + " : " + city +  " = " + state1 + " : " + city1)
                            failed = True

    if failed:
        print("\n\nSome cities in rosetta.txt are redundant across states. See output above.")
    else:
        print("\nRedundancy check passed!")


def testrosetta():
    # https://stackoverflow.com/questions/3160699/python-progress-bar

    print("\nTesting rosetta.yaml - this will take a few minutes")
    rs = import_rosetta("../../etc/rosetta.yaml")

    #check_urls(rs)

    #check_redundant_url(rs)

    check_redundant_citykey(rs)


if __name__ == "__main__":
    testrosetta()