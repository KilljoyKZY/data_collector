# -*- coding: utf-8 -*-
"""
Yelp Fusion API code sample.
This program demonstrates the capability of the Yelp Fusion API
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.
Please refer to http://www.yelp.com/developers/v3/documentation for the API
documentation.
This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.
Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import csv
import numpy
from datetime import datetime
import time
import urllib



try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode



API_KEY= ""


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
EVENT_PATH = '/v3/events'
sriptname = ''
# Defaults for our simple example.
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
inputfilename = ""
outputfilename = ""
starttime = ""
endtime = ""
cityname = ""
SEARCH_LIMIT = 50
glob_la = []
glob_lo = []
result_rating = []
result_r_count = []
result_price = []
std_rating = []
std_price = []
std_r_count = []
price = []
rating = []
r_count = []
b_count = []
count = 0
scriptname = ''
term = ''
result_business = []
raidus = 0

def takecsvinput():
    #let user to enter the filename they want to auto process.
	#read locations of each station in the file into global lists
	#double check the index before deplorement
    global glob_la
    global glob_lo
    global count
    global inputfilename
    global outputfilename
    global cityname
    global station_id
    global price
    global r_count
    global rating
    global radius
    global constumkey
    global  std_rating
    global std_price
    global std_r_count
    global  result_price
    global  result_rating
    global  result_r_count
    global term
    global result_business
    global starttime
    global  endtime
    scriptname = input("Please enter the file name\n")
    file = open(scriptname,"r")
    inputfilename = file.readline().rstrip('\n')
    outputfilename = file.readline().rstrip('\n')
    cityname = file.readline().rstrip('\n')
    radius = file.readline().rstrip('\n')
    if int(radius) > 50000:
        print("Wrong input detected\n Exiting program\n")
        exit(1)
    term = file.readline().rstrip('\n')
    starttime = file.readline().rstrip('\n')
    endtime = file.readline().rstrip('\n')
    constumkey = file.readline().rstrip('\n')
    count = len(open(inputfilename,'rU').readlines())#get the line number of  current open filename
    initial_value = 0
    glob_la = [ initial_value for i in range(count)] #inilized the global list before using
    glob_lo = [ initial_value for i in range(count)]
    rating = [ initial_value for i in range(50)]
    price = [ initial_value for i in range(50)]
    r_count = [ initial_value for i in range(50)]
    result_r_count = [ initial_value for i in range(count)]
    result_rating = [ initial_value for i in range(count)]
    result_price = [ initial_value for i in range(count)]
    std_price = [ initial_value for i in range(count)]
    std_r_count = [ initial_value for i in range(count)]
    std_rating = [ initial_value for i in range(count)]
    result_business =  [ initial_value for i in range(count)]

    station_id = [ initial_value for i in range(count)]
    with open(inputfilename) as f:
        reader = list(csv.reader(f))
        for x in range (0,count):
            glob_la[x] = reader[x][1]
            glob_lo[x] = reader[x][2]
            station_id[x] = reader[x][0]


def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    #print(u'Querying {0} ...'.format(url))
    response = requests.request('GET', url, headers=headers, params=url_params)
    print(response.url)
    return response.json()


def search(api_key, term, latitude,longtidue):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location':cityname,
        'longtitude': longtidue,
        'latitude': latitude,
        'radius':int(radius),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def get_business(api_key, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)

def get_event(api_key):
    syear,smonth,sday = starttime.split("-")
    eyear,emonth,eday = endtime.split("-")
    start_date = datetime(year =int(syear),month=int(smonth),day=int(sday))
    end_date = datetime(year=int(eyear),month=int(emonth),day=int(eday))
    unix_s = time.mktime(start_date.timetuple())
    unix_e = time.mktime(end_date.timetuple())
    print(unix_e)
    print(unix_s)
    url_params = {
        'term': term.replace(' ', '+'),
        'location':cityname,
        'radius': int(radius),
        'start_date':int(unix_s),
        'end_date':int(unix_e),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, EVENT_PATH, api_key, url_params=url_params)


def query_api(term,latitude,longtitude):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    global price
    global rating
    global  r_count
    global b_count
    response = search(API_KEY, term, latitude,longtitude)
    with open("test.json", "w") as fd:
        json.dump(response,fd)

    businesses = response.get('businesses')
    if not businesses:
        print(u'No businesses for {0} in {1},{2} found.'.format(term, latitude,longtitude))
        return

    #business_id = businesses[1]['id']
    b_count = len(businesses)
    for x in range (0,b_count):
        try:
            if businesses[x]["price"] == "$":
                price[x] = 1
               #print( price[x])
            elif businesses[x]["price"] == "$$":
                price[x] = 2
                #print(price[x])
            elif businesses[x]["price"] == "$$$":
                price[x] = 3
                #print(price[x])
            elif businesses[x]['price'] == "$$$$":
                price[x] = 4
                #print(price[x])
        except KeyError as error:
            price[x] = -1
        rating[x] = businesses[x]['rating']
        #print("rating")
        #print(rating[x])
        r_count[x] = businesses[x]['review_count']
        #print("review counts")
        #print(r_count[x])


    #print(u'{0} businesses found, querying business info ' \
     #   'for the top result "{1}" ...'.format(
      #      len(businesses), business_id))
    #response = get_business(API_KEY, business_id)

    #print(u'Result for business "{0}" found:'.format(business_id))
    #pprint.pprint(response, indent=2)

def write_out(filename,targenemt):
    with open(filename,'r') as inputf:
        with open(targenemt,'w') as outputf:
            writer = csv.writer(outputf,lineterminator='\n')
            reader = csv.reader(inputf)
            all = []
            row = next(reader)
            row.append("Business number")
            row.append("Business review count average")
            row.append("Business review count std")
            row.append("Business price average")
            row.append("Business price std")
            row.append("Business rating average")
            row.append("Business rating std")
            all.append(row)
            x = 1
            for row in reader:
                row.append(result_business[x])
                row.append(result_r_count[x])
                row.append(std_r_count[x])
                row.append(result_price[x])
                row.append(std_price[x])
                row.append(result_rating[x])
                row.append(std_rating[x])
                all.append(row)
                x = x+1
            writer.writerows(all)

def main():
    takecsvinput()
    #print(term)
    for i in range (1,count):
        try:
            query_api(term,glob_la[i],glob_lo[i])
        except HTTPError as error:
            sys.exit(
                'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                    error.code,
                    error.url,
                    error.read(),
                )
            )
        result_r_count[i] = sum(r_count)/float(b_count)
        result_price[i] = sum(price) / float(b_count)
        result_rating[i] = sum(rating)/float(b_count)
        data1 = numpy.array(rating)
        data2 = numpy.array(price)
        data3 = numpy.array(r_count)
        std_price[i] = numpy.std(data2)
        std_rating[i] = numpy.std(data1)
        std_r_count[i] = numpy.std(data3)
        result_business[i] = b_count
    write_out(inputfilename,outputfilename)
    event = get_event(API_KEY)
    with open("test1.json", "w") as fd:
        json.dump(event,fd)



if __name__ == '__main__':
    main()
