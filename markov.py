import numpy
from my_api import api
import twitter

# my_api should be of the following form
#import twitter
#api = twitter.Api(consumer_key='',
#    consumer_secret='',
#    access_token_key='',
#    access_token_secret='')

INPUT = "aloofAbacus"
OUTPUT = "aloofAsshat"
FILE = "aidan.npy"
NOMENTIONS = True # False if you want to @ people

def generate_chain(tweets):
    # Create counts of everything
    counters = {}
    sums = {}
    for tweet in tweets:
        tweet = tweet.split()
        prior_word = 0
        for word in tweet:
            if prior_word not in counters:
                counters[prior_word] = {}
                sums[prior_word] = 0
            if word in counters[prior_word]:
                counters[prior_word][word] = counters[prior_word][word] + 1
            else:
                counters[prior_word][word] = 1
            sums[prior_word] = sums[prior_word] + 1
            prior_word = word
        if prior_word not in counters:
            counters[prior_word] = {}
            sums[prior_word] = 0
        counters[prior_word][0] = 1
        sums[prior_word] = sums[prior_word] + 1
    
    # Create a Markov chain from the counts
    chain = {}
    seeds = {}
    for prior in counters:
        if prior == 0:
            for word in counters[prior]:
                seeds[word] = counters[prior][word] * 1.0 / sums[prior]
            continue
        for word in counters[prior]:
            if prior not in chain:
                chain[prior] = {}
            chain[prior][word] = counters[prior][word] * 1.0 / sums[prior]
    return chain, seeds

def generate_tweet(chain, seeds):
    word = numpy.random.choice(list(seeds.keys()), p=list(seeds.values()))
    slen = len(word) + 1
    tweet = [word]
    while slen <= 140:
        curr = chain[word]
        try:
            word = numpy.random.choice(list(curr.keys()), p=list(curr.values()))
        except ValueError:
            break
        if word == 0:
            break
        slen = slen + len(word) + 1
        tweet.append(word)
    while slen > 140:
        slen = slen - len(tweet.pop()) - 1
    stweet = ""
    for word in tweet:
        stweet = stweet + word + " "
    if NOMENTIONS:
        stweet = stweet.replace("@", "")
    return stweet[0:-1]

def get_tweets():
    statuses = api.GetUserTimeline(screen_name=INPUT, include_rts=False, exclude_replies=True)
    return [s.text for s in statuses]

def tweet(count):
    tweets = get_tweets()
    chain, seeds = generate_chain(tweets)
    for i in range(count):
        tweet = generate_tweet(chain, seeds)
        try:
            api.PostUpdate(tweet)
        except twitter.error.TwitterError:
            print("failed tweet: " + tweet)

tweet(20)
