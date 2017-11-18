# twitter-streamer
This is an application which processes Tweets containing a keyword in real time using Twitter Streaming API.

## code preview
https://nbviewer.jupyter.org/github/jasleen19/twitter-streamer/blob/master/streamer.ipynb 

## pre-requisites
### required
- build essentials
- python3
- pip
- pip : tweepy
- pip : tabulate
### optional
- make
- jupyter

## build
Install required packages using `pip install -r requirements.txt`

## check
Four ways to check the code (`make` and `jupyter` need to be installed for last two):
- `./streamer.py`
- `python streamer.py`
- `make`
- `jupyter notebook streamer.ipynb`

## TO-DO
### critical
- Print the total number of links included in the tweets followed by a list of the unique domains sorted by the count. Any shortened links should be expanded
- Print the number of unique words used in the tweets followed by the list of top 10 words sorted by occurence. Remove the common function words like a, an, the, of, with etc. (articles, pronouns, propositions and conjunctions)
### improvements
- switch to multiprocessing instead of multithreading
- remove global variable usage
- add optional argument parsing
- fix the kernel killed issue in jupyter notebook (has to be restarted, preferrably with output cleared)
- mini data mining and aggregation features

## how it works
- printer.printer() method and main function run in separate threads
- main function 
  - has the instantiation of `StreamListener` class (tweepy) which accesses the global state of tweets data and current minute
  - `StreamListener` saves incoming tweets according to current global value of `i`
  - only `StreamListener` can change the value of global variable `durations`, so that there are no race conditions
- printer.printer() method
  - calls itself every `duration` seconds and is the only one who can update `i`, so that there are no race conditions
  - prints out `durations` dictionary for the last `unit` durations each of `duration` seconds (using OrderedDict's slicing)
  - to achieve the above aggregation, it merges all the dictionaries of last `unit` durations which contain `{ username: counts }` values for each of the last elapsed `units`
- since a kafka or some other server is needed to completely exhaust Twitter's streaming API, it just ignores connection loss exceptions (IncompleteRead) and tries to reconnect indefinitely in a loop

## coding references
- http://docs.tweepy.org/en/v3.5.0/streaming_how_to.html 
- https://stackoverflow.com/questions/16578652/threading-timer 
- https://stackoverflow.com/a/30975520
- https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression
