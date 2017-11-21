#!/usr/bin/env python3
# Imports
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from json import loads
from threading import Timer
from http.client import IncompleteRead
from tabulate import tabulate
from collections import OrderedDict
from itertools import islice
import os
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
import tldextract
import re

# RUN THIS ONCE
import nltk
nltk.download('stopwords')

class StreamListener(StreamListener):
    '''StreamListener class: This class works as a handler for the incoming
    Twitter stream using Tweepy object'''
    stop_words = set(stopwords.words('english'))
    stop_words.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}'])
    def on_data(self, data):
        '''on_data class_method: handle data by loading into a json and
        appending to global repository of tweets,
        based on minute as index'''
        global i, durations
        current_i = i
        tweet_json = loads(data)
        if 'user' in tweet_json:
            # if minute not in `durations` dictionary, add it
            if current_i not in durations:
                durations[current_i] = {
                    'users': {},
                    'domains': {},
                    'words': {}
                }
            # store reporting data
            self.__update_username(current_i, tweet_json)
            self.__update_domains(current_i, tweet_json)
            self.__update_words(current_i, tweet_json)
        return True
    
    def __update_username(self, current_i, tweet_json):
        username = tweet_json['user']['screen_name']
        durations[current_i]['users'][username] = durations[current_i]['users'].get(username, 0) + 1
        
    def __update_domains(self, current_i, tweet_json):
        for url in tweet_json['entities']['urls']:
            domain_object = tldextract.extract(url['expanded_url'])
            domain = domain_object.domain
            durations[current_i]['domains'][domain] = durations[current_i]['domains'].get(domain, 0) + 1
            
    def __update_words(self, current_i, tweet_json):
        text = tweet_json['text']
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r'[?|$|.|!]',r'', text)
        text = re.sub(r'[^a-zA-Z0-9 ]',r'', text)
        filtered = [j.lower() for j in wordpunct_tokenize(text) if j.lower() not in self.stop_words]
        for word in filtered:
            durations[current_i]['words'][word] = durations[current_i]['words'].get(word, 0) + 1
                                         
    def on_error(self, status):
        '''on_error class_method: handle the errors are most frequently on
        server side/connection related and few, pass them'''
        pass

class Printer():
    '''Printing class: This class works as a handler for printing every 
    `duration` seconds'''
    def printer(self):
        '''printer function: run a self-calling throad to be called every 
        60 seconds on the clock (not equivalent to sleep!)'''
        global i, keyword, duration, durations, units,domains
        i = i + 1
        # called every minute; change to 10 seconds to test faster
        Timer(duration, self.printer).start()
        # don't call for i = 1 as here i represents the duration [i-1,i] 
        #   which has not finished yet
        if i != 1:
            # create an ordered dict so that slicing is possible
            ordered = dict(OrderedDict(islice(durations.items(), 
                max(0,i-units-1), i-1)))
            merged_users = {}
            merged_domains = {}
            merged_words = {}
            # merge all the dictionaries of counts for last `units * duration` 
            #   seconds
            for k,v in ordered.items():
                merged_users = {**merged_users, **v['users']}
                merged_domains = {**merged_domains, **v['domains']}
                merged_words = {**merged_words, **v['words']}
            print("\nDuration unit {}: Twitter report for `{}` in last {} seconds:"
                .format(i-1, keyword, int(min((i-1) * duration, units * duration))))
            print("=======================================================================")
            print(tabulate([(k, v) for k,v in merged_users.items()] , 
                headers=['Username', 'Count of Tweets']))
            print("\nTotal number of links: {}\n".format(sum(merged_domains.values())))
            print(tabulate([(k, merged_domains[k]) for k in sorted(merged_domains, key=merged_domains.get, reverse=True)], 
                headers=['Domains', 'Count']))
            print("\nTop 10 words:\n")
            print(tabulate([(k, merged_words[k]) for k in sorted(merged_words, key=merged_words.get, reverse=True)][:10], 
                headers=['Words', 'Count']))
            print("=======================================================================\n")

# GLOBAL VARIABLES DECLARED AND INITIALIZED
durations = {}
i = 0
# change this to allow printing frequency (float: in seconds)
duration = 60.0
# duration units to go back to
units = 5
keyword = ""

def main():
    '''main function: initialize tokens, validate them, run printer thread and
     start streaming'''
    # token information, intialize this if empty or use runtime input
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""

    # CHECK CREDENTIALS
    if consumer_key == "" or consumer_secret == "" or access_token == "" or \
        access_token_secret == "":
        print("Some values were not defined in the program!")
        print("Create them at https://apps.twitter.com/")
    if consumer_key == "":
        print("Enter consumer key:")
        consumer_key = input().strip()
    if consumer_secret == "":
        print("Enter consumer secret:")
        consumer_secret = input().strip()
    if access_token == "":
        print("Enter access token:")
        access_token = input().strip()
    if access_token_secret == "":
        print("Enter access token secret:")
        access_token_secret = input().strip()

    # TAKE INPUT
    print("Enter your keyword:")
    global keyword, duration, units
    keyword = input()

    # COPIED
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # START PRINTING
    print("\nDuration: {}".format(duration))
    print("periodic time (seconds) after which printing is done")
    print("\nDuration Units: {}".format(units))
    print("time units to look back to, each of length `Duration`")
    print("\nConsuming the stream...")
    print("`ctrl/cmd + c` twice to exit cleanly")
    # THIS WILL BECOME AN INDEPENDENT PROCESS
    p = Printer()
    p.printer()

    l = StreamListener()

    # START STORING
    while True:
        try:
            stream = Stream(auth, l)
            # THIS FUNCTION IS RUNNING AS `MAIN` PROCESS
            stream.filter(track=[keyword])
        except (Exception, IncompleteRead) as e:
            continue
        # kill kernel - need to address this
        except KeyboardInterrupt:
            os._exit(1)

if __name__ == '__main__':
    main()
