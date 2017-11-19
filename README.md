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

## TO-DO existing
- remove global variable usage
- add argument parsing
- segregate class and helper functions
- maintenance unit tests (removed TDD tests)
- fix the kernel killed issue in jupyter notebook (has to be restarted, preferrably with output cleared)

## TO-DO future
- mini data mining and aggregation features
- maybe use pandas

## how it works
- printer function and main function run in separate threads
- main function has the instantiation of streamer class (tweepy) which accesses the global state of tweets data and current minute
- streamer saves incoming tweets accordingly
- since a kafka or some other server is needed to completely exhaust Twitter's streaming API, just ignore exceptions to connection loss
- reconnect to connection if connection last

## coding references
- http://docs.tweepy.org/en/v3.5.0/streaming_how_to.html 
- https://stackoverflow.com/questions/16578652/threading-timer 
- https://stackoverflow.com/a/30975520
- https://github.com/john-kurkowski/tldextract
- https://stackoverflow.com/questions/19130512/stopword-removal-with-nltk
- https://stackoverflow.com/questions/41610543/corpora-stopwords-not-found-when-import-nltk-library
- https://stackoverflow.com/questions/24399820/expression-to-remove-url-links-from-twitter-tweet