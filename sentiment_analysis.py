from gg_api import *
from globals import *
from info_extraction import  *
from tweet_reader import *
from textblob import TextBlob
import Levenshtein
import sys

def host_in_tweet(tweet, hosts):
    '''
    checks to see if the text of the tweet contains either of these textual situations

    ex: host is "tina fey"
    this function checks to see if "tina", "fey", "tina fey", or "tinafey"
    occurs in the tweet's text

    if it finds any of these in the tweet's text
    then it returns a 2 element tuple

    the first being a double representing a weight, for when it calculates
    polarity later in this program
    so it'll assign a larger weight (1.0) to tweets with "tina fey", or "tinafey"
    and a weight of 0.7 for tweets with "tina" or "fey"

    I decided to use a weight since I thought like, just because
    a tweet has the name "Amy" doesn't necessarily mean it's referring to the
    host

    the second element is the original tweet
    '''

    hosts_partial_names = [] # to store first and last names of each host
    for host in hosts:
        # splitting each host name into the first and last
        # ex: "tina fey" -> "tina", "fey"
        hosts_partial_names += [part_of_name for part_of_name in host.split(" ")]

    host_names_without_space = []
    for host in hosts:
        # aaccounting for the possibility that the
        # names were combined without a space
        # ex: should be "tina fey" but the tweet
        # has "tinafey"
        host_names_without_space.append(host.replace(" ", ''))

    host_related_words = ["host", "hosted", "hosts"]

    # splitting the tweet's text into individual words and
    # searching for either of the hosts' first or last name, or the whole name
    # (with or without a space)
    split_tweet_text = tweet['text'].split(" ")

    # tests if two strings are fairly similar
    def are_similar(str1, str2):
        return Levenshtein.ratio(str1, str2) >= 0.9

    # checking first for any approx. matches between a host name (like "tina fey"(
    # and anything in the tweet's text, the are_similar tries to account for
    # mispellings
    for host_name in hosts:
        poss_match = [word for word in tweet["text"] if are_similar(host_name, word)]
        if poss_match:
            return (1.0, tweet)

    # checking second for approx. matches between a host name w/o a space
    # like "tinafey"
    for host_name in host_names_without_space:
        poss_match = [word for word in split_tweet_text if are_similar(host_name, word)]
        if poss_match:
            return (1.0, tweet)

    # checking third for matches between a host first or last name
    # like "tina" or "fey"
    for host_partial_name in hosts_partial_names:
        poss_match = [word for word in split_tweet_text if are_similar(host_name, word)]
        if poss_match:
            return (0.7, tweet)

    # checking last for matches between host related words (like "hosts", "hosted")
    for host_related_word in host_related_words:
        poss_match = [word for word in split_tweet_text if are_similar(word, host_related_word)]
        if poss_match:
            return (0.7, tweet)

    # this tweet likely isn't associated with either host
    return False

def sa_pipeline(year):
    hosts = get_hosts(year)  # obtain the hosts found for given year
    all_tweets = loadTweets(year) # load all tweets for filtering

    # mapping the host_in_tweet function (which returns (True, 1.0 or 0.7) or False)
    # on all tweets
    print("Scanning all tweets for ones that have a strong association with either of the hosts")
    host_name_filtered_tweets = list(map(lambda tweet: host_in_tweet(tweet, hosts), all_tweets))

    polarity_sum = 0
    num_tweet_with_host_names = 0 # keep track of num of tweets that are assoc. w/ a host name
    for tweet_tuple in host_name_filtered_tweets:
        if not tweet_tuple: # meaning that host_in_tweet returned False
            continue
        else:
            num_tweet_with_host_names += 1

            # tweet_tuple[1] accesses the tweet itself
            tweet = tweet_tuple[1]
            tweet_text = cleanTweet(tweet["text"]) # clean the tweet before calc. polarity
            if not tweet_text: continue

            # polarity is calculated by the TextBlob module,
            # it is in the range of [-1.0, 1.0]
            tweet_polarity = (TextBlob(tweet_text)).sentiment.polarity
            weight = tweet_tuple[0]

            polarity_sum += (tweet_polarity * weight)

    avg_polarity = polarity_sum / num_tweet_with_host_names

    result_str = "The sentiment associated with the hosts: "
    result_str += ", and ".join(hosts)
    result_str += ", seems to be..."
    if -0.3 <= avg_polarity <= 0.3:
        result_str += "\nFairly neutral! Average Polarity (-1 - negative, +1 - positive): " + str(avg_polarity)

    if -1.0 <= avg_polarity < -0.3:
        result_str += "\nFairly negative! Average Polarity (-1 - negative, +1 - positive): " + str(avg_polarity)

    if 0.3 < avg_polarity <= 1.0:
        result_str += "\nFairly positive! Average Polarity (-1 - negative, +1 - positive): " + str(avg_polarity)

    return result_str



if __name__ == "__main__":
    print(sa_pipeline(sys.argv[1]))