from langdetect import detect
from info_extraction import *
import math
from globals import similar, replaceLemmas, adjustLemmas, DecomposedText
from results_generator import *

# These are just lists used to store certain tweets relating to awards/nominees/etc to analyze what they look like.
test_awards = []
test_nominees = []

# Load tweets and limit how many tweets to read
tweets = loadTweets(2013)
limit = len(tweets)

# Main pipeline
limit = min(limit, len(tweets))
def AnalyzeTweets():
    for i, tweet in enumerate(tweets):
        # Progress meter:
        if i % 1000 == 0 or i + 1 >= limit:
            progress = (i+1)/limit
            print("{}{} {}/{} tweets analyzed.".format("="*math.floor(progress*50), "-"*(50 - math.floor(progress*50)), i+1, limit), end='\r')
            if i + 1 >= limit: 
                print("Finished analyzing tweets.")
                break

        # Clean tweet, and skip to next tweet if it's not relevant/useful.
        text = cleanTweet(tweet['text'])
        if not text: continue

        # Information extraction function which actually extracts info and relations and adds them to the awardsDict.
        extractInfo(text)


# Clean Tweet - Determines if Tweet is usable for information extraction and cleans the text.
# Ignores retweets, removes hashtags, @ mentions, urls
def cleanTweet(text):
    if len(text) < 20: return False
    text = demoji(text)
    if "RT" in text: return False
    text = text.lower()
    if not containsAnyOf(text, ["best", "award", "nominee", "nominated", "host", "present", "worst", "beat"]): return False
    for word in ["goldenglobes", "goldenglobe", "golden", "globe", "@"]:
        text = text.replace(word, '')
    text = text.replace('mini-series', 'miniseries')
    text = text.replace('mini series', 'miniseries')
    text = " ".join(filter(lambda x: x[:4] != 'http', text.split()))
    return text


# Information extraction - Takes in a valid Tweet's text and attempts to extract information from it.
def extractInfo(text):
    findHosts(text)
    award_name = findAward(text)
    if award_name and len(award_name) > 5:
        # if containsAnyOf(text, [
        #     'connie britton',
        #     'glenn close',
        #     'michelle dockery',
        #     'julianna marguiles',
        #     'nathan fillion',
        #     'lea michele'
        # ]) and 'claire danes' in text:
        #     test_awards.append(award_name)
        #     test_nominees.append(text)
        # pass
        awardsTree.foundAward(award_name)
        findRelations(text, award_name)


def main():
    AnalyzeTweets()
    GenerateResults()
    print("Finished!")

if __name__ == "__main__":
    main()
