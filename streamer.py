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

# StreamListener class to process Twitter stream using Tweepy Stream object
class StreamListener(StreamListener):
    '''StreamListener class: This class works as a handler for the incoming
    stream'''
    def on_data(self, data):
        '''on_data class_method: handle data by loading into a json and
        appending to global repository of tweets,
        based on minute as index'''
        global i, minutes
        tweet_json = loads(data)
        if 'user' in tweet_json:
            username = tweet_json['user']['screen_name']
            # if minute not in `minutes` dictionary, add it
            if i not in minutes:
                minutes[i] = {}
            # check if username is being tracked in current minute and
            #   increase count
            minutes[i][username] = minutes[i].get(username, 0) + 1
            # debug print
            # if minutes[i][username] == 1:
            #     print("Minute {}: {} tweeted!".format(i, username))
            # else:
            #     print("Minute {}: {} tweeted AGAIN! Count = {}".format(i,
            #     username, minutes[i][username]))
        return True
    
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
        global i, keyword, duration, minutes
        i = i + 1
        # called every minute; change value to 10 seconds to test faster
        Timer(duration, self.printer).start()
        # don't call for i = 1 as here i represents the duration [i-1,i] 
        #   which has not finished yet
        if i != 1:
            # create an ordered dict so that slicing is possible
            ordered = dict(OrderedDict(islice(minutes.items(), 
                max(0,i-int(duration)-1), i-1)))
            merged = {}
            # merge all the dictionaries of counts for last `duration` 
            #   minutes
            for j, (k,v) in enumerate(ordered.items()):
                merged = {**merged, **v}
            print("\nMinute {}: Tweeters about {} in last {} seconds:".format(i-1, 
                keyword, duration))
            print(tabulate([(k, v) for k,v in merged.items()] , 
                headers=['Username', 'Count of Tweets']))

# GLOBAL VARIABLES DECLARED AND INITIALIZED - need to remove the need to have
#   global variables
minutes = {}
i = 0
# change this to allow printing frequency (float: in seconds)
duration = 5.0
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
        print("Some values were not defined in the program! Create them at \
            https://apps.twitter.com/")
    if consumer_key == "":
        print("Enter consumer key:")
        consumer_key = input()
    if consumer_secret == "":
        print("Enter consumer secret:")
        consumer_secret = input()
    if access_token == "":
        print("Enter access token:")
        access_token = input()
    if access_token_secret == "":
        print("Enter access token secret:")
        access_token_secret = input()

    # TAKE INPUT
    print("Enter your keyword:")
    global keyword
    keyword = input()

    # COPIED
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # START PRINTING
    print("\nConsuming the stream...")
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
