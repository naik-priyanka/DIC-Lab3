import urllib2
import json
import datetime
import time
import sys, os
from urllib2 import HTTPError
from ConfigParser import SafeConfigParser

# helper function to get json into a form I can work with       
def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

# helpful function to figure out what to name individual JSON files        
def getJsonFileName(year, month, json_file_path):
    json_file_name = "_".join([str(year), str(month)])
    json_file_name = "".join([json_file_name, ".", 'json'])
    json_file_name = "".join([json_file_path,json_file_name])
    return json_file_name
    
# get the articles from the NYTimes Article API    
def getArticles(year, month, api_key, json_file_path):
        try:
            request_string = "http://api.nytimes.com/svc/archive/v1/" + str(year) + "/" + str(month) + ".json?api-key=" + api_key
            print request_string
            response = urllib2.urlopen(request_string)
            content = response.read()
            if content:
                articles = convert(json.loads(content))
                # if there are articles here
                if len(articles["response"]["docs"]) >= 1:
                    json_file_name = getJsonFileName(year, month, json_file_path)
                    json_file = open(json_file_name, 'w')
                    json_file.write(content)
                    json_file.close()
                # if no more articles, go to next date
                else:
                    return
            time.sleep(3) # wait so we don't overwhelm the API
        except HTTPError as e:
            print("HTTPError for month %s (err no. %s: %s) Here's the URL of the call: %s", month, e.code, e.reason, request_string)
            if e.code == 403:
                print "Script hit a snag and got an HTTPError 403. Check your log file for more info."
                return
            if e.code == 429:
                print "Waiting. You've probably reached an API limit."
                time.sleep(30) # wait 30 seconds and try again
        except:
            print("Error for month %s: %s", month, sys.exc_info()[0])

# Main function where stuff gets done
def main():
    api_key = "67736f1f941b44dc95f63619f6bdc9fb"
    try:
        for month in range(12, 0, -1):
            json_file_path = "input-archive/"
            try:
                if not os.path.exists(os.path.dirname(json_file_path)):
                    os.makedirs(os.path.dirname(json_file_path))
            except OSError as err:
                print(err)
            getArticles(2016, month, api_key, json_file_path)
    except:
        print("Unexpected error: %s", str(sys.exc_info()[0]))
    finally:
        print("Finished.")

if __name__ == '__main__' :
    main()
