from globals import *
from info_extraction import  *
from tweet_reader import *
import Levenshtein
import sys
from emotions import emotions

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
    # this tweet likely isn't associated with either host
    return False

def sa_pipeline(year):
    hosts = LoadResults()['hosts'] # obtain the hosts found for given year
    print("Loading Tweets...")
    all_tweets = loadTweets(year) # load all tweets for filtering

    # mapping the host_in_tweet function (which returns (True, 1.0 or 0.7) or False)
    # on all tweets
    host_name_filtered_tweets = []
    limit = 200_000
    print("Scanning tweets for ones that have a strong association with the host(s)...")
    for i, tweet in enumerate(all_tweets):
        r = host_in_tweet(tweet, hosts)
        if r:
                host_name_filtered_tweets.append(r)
        # Progress meter:
        if i % 1000 == 0 or i + 1 >= limit:
            progress = (i+1)/limit
            print("{}{} {}/{} tweets scanned.".format("="*math.floor(progress*50), "-"*(50 - math.floor(progress*50)), i+1, min(limit, len(all_tweets))), end='\r')
            if i + 1 >= limit: 
                print("\nFinished scanning tweets.")
                break
    
    #host_name_filtered_tweets = list(map(lambda tweet: host_in_tweet(tweet, hosts), all_tweets))

    sentiments = {}
    for t in host_name_filtered_tweets:
        for emotion in emotions:
            if t and emotion in t[1]["text"]:
                if emotion in sentiments:
                    sentiments[emotion] += 1
                else:
                    sentiments[emotion] = 1
    

    hosts = [host.title() for host in hosts]
    top_emotion = Counter(sentiments).most_common(1)[0][0]
    result_str = "The sentiment associated with the host(s), "
    result_str += " and ".join(hosts)
    result_str += ", seems to be mostly: " + top_emotion + ".\n"

    for t in host_name_filtered_tweets:
        if t and top_emotion in t[1]["text"]:
            result_str +="For example \n"
            result_str += t[1]["text"]
            break
    return result_str



if __name__ == "__main__":
    print(sa_pipeline(sys.argv[1]))