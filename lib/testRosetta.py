import time
from clsearch import uri_exists_stream, import_rosetta


def testrosetta():
    # https://stackoverflow.com/questions/3160699/python-progress-bar

    failed = False
    j = 0
    print("\nTesting rosetta.yaml - this will take a few minutes")
    rs = import_rosetta()

    for key, value in rs.items():
        i = value.items()
        print("\n" + key,end='')
        for city in value:
            #print(value[city])
            site = str("https://" + str(value[city]) + ".craigslist.org")
            verdict = uri_exists_stream(site)
            if not verdict:
                time.sleep(3)   # wait 3 seconds and retry before throwing fail
                if uri_exists_stream(site):
                    print("\n" + key + " => " + city + " : \t https://" + value[city] + ".craigslist.org does not exist")
                    failed = True
            else:
                print('.',end='')

    if failed:
        print("\n\nUnable to resolve all URLs in rosetta.yaml. See output above.")
    else:
        print("\n\nAll Craigslist URLs created from rosetta.yaml are accessible")


if __name__ == "__main__":
    testrosetta()