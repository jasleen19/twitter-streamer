#!/usr/bin/env python
# imports
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from json import loads
from threading import Timer
from http.client import IncompleteRead
from pprint import pprint
import os
# from kafka import SimpleProducer, KafkaClient

class StreamListener(StreamListener):
    '''StreamListener class: This class works as a handler for the incoming stream'''
    def on_data(self, data):
        '''on_data class_method: handle data by loading into a json and appending to global repository of tweets,
        based on minute as index'''
        global tweets, i
        # producer.send_messages("streamer", data.encode('utf-8'))
        tweet_json = loads(data)
        if 'user' in tweet_json:
            tweets[i-1].append({'user': tweet_json['user']['screen_name'], 'user_statuses': tweet_json['user']['statuses_count'] })
        return True

    def on_error(self, status):
        '''on_error class_method: handle the errors are most frequently on server side/connection related and few, pass them'''
        pass

def printer():
    '''printer function: run a self-calling throad to be called every 60 seconds on the clock (not equivalent to sleep!)'''
    global tweets, i, keyword
    tweets.append([]) # append (current_minute + 1)s list
    i = i + 1
    Timer(10.0, printer).start() # called every minute
    if i != 1:
        print("\nUsers who tweeted about {} in last 1 minute:".format(keyword))
        pprint(sum(tweets[-6:-1], []))

def main():
    '''main function: initialize tokens, validate them, run printer thread and start streaming'''
    # token information, intialize this if empty or use runtime input
    access_token = ""
    access_token_secret = ""
    consumer_key = ""
    consumer_secret = ""

    # CHECK CREDENTIALS
    if consumer_key == "" or consumer_secret == "" or access_token == "" or access_token_secret == "":
        print("Some values were not defined in the program! Create them at https://apps.twitter.com/")
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
    keyword = input()

    # COPIED
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    # kafka = KafkaClient("localhost:9092")
    # producer = SimpleProducer(kafka)

    # GLOBAL VARIABLES DECLARED AND INITIALIZED - need to remove the need to have global variables
    tweets = [[]]
    i = 0

    # START PRINTING
    print("\nConsuming the stream...")
    printer() # THIS WILL BECOME AN INDEPENDENT PROCESS

    l = StreamListener()

    # START STORING
    while True:
        try:
            stream = Stream(auth, l)
            stream.filter(track=[keyword]) # THIS FUNCTION IS RUNNING AS `MAIN` PROCESS
        except (Exception, IncompleteRead) as e:
            continue
        except KeyboardInterrupt:
            os._exit(1) # kill kernel - need to address this

if __name__ == '__main__':
    main()