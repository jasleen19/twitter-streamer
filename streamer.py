#!/usr/bin/env python3
# Imports
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from json import loads
from threading import Timer
from http.client import IncompleteRead
from pprint import pprint
import os

# StreamListener class to process Twitter stream using Tweepy Stream object
class StreamListener(StreamListener):
    '''StreamListener class: This class works as a handler for the incoming
    stream'''
    def on_data(self, data):
        '''on_data class_method: handle data by loading into a json and
        appending to global repository of tweets,
        based on minute as index'''
        global users, i
        tweet_json = loads(data)
        if 'user' in tweet_json:
            username = tweet_json['user']['screen_name']
            # increase count or add user to key and then increase count
            users[username] = users.get(username, 0) + 1
            # # debug print
            # if users[username] == 1:
            #     print("Minute {}: {} tweeted!".format(i, username))
            # else:
            #     print("Minute {}: {} tweeted AGAIN! Count = {}".format(i,
            #     username, users[username]))
        return True

    def on_error(self, status):
        '''on_error class_method: handle the errors are most frequently on
        server side/connection related and few, pass them'''
        pass

def printer():
    '''printer function: run a self-calling throad to be called every 60
    seconds on the clock (not equivalent to sleep!)'''
    global users, i, keyword, duration
    i = i + 1
    # called every minute; change value to 10 seconds to test faster
    Timer(duration, printer).start()
    if i != 1:
        print("\nUsers who tweeted about {} in last {} seconds:".format(keyword,
         duration))
        pprint(users)
        print("\n")
    # empty dictionary every 5 minutes
    if i % duration == 0:
        users = {}

# GLOBAL VARIABLES DECLARED AND INITIALIZED - need to remove the need to have
#   global variables
users = {}
i = 0
keyword = ""
# change this parameter to make the printing/storing faster or slower. Default
#   is 60 seconds
duration = 60.0

def main():
    '''main function: initialize tokens, validate them, run printer thread and
     start streaming'''
    # token information, intialize this if empty or use runtime input
    access_token = ""
    access_token_secret = ""
    consumer_key = ""
    consumer_secret = ""

    # CHECK CREDENTIALS
    if consumer_key == "" or consumer_secret == "" or access_token == "" or \
        access_token_secret == "":
        print("Some values were not defined in the program! Create them at \
            https://apps.twitter.com/")
    if consumer_key == "":
        print("Enter consumer key:")
        consumer_key = input()
    elif consumer_secret == "":
        print("Enter consumer secret:")
        consumer_secret = input()
    elif access_token == "":
        print("Enter access token:")
        access_token = input()
    elif access_token_secret == "":
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
    printer()

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
