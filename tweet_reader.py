from langdetect import detect
from info_extraction import *
import math

# These are just lists used to store certain tweets relating to awards/nominees/etc to analyze what they look like.
test_awards = []
test_nominees = []


# Main pipeline

limit = 10_000  # Limit how many tweets to read.


def AnalyzeTweets():
    for i, tweet in enumerate(tweets):
        # Progress meter:
        if i % 1000 == 0:
            progress = i/limit
            print("{}{} {}/{} tweets analyzed.".format("█"*math.floor(progress*50), "░"*(50 - math.floor(progress*50)), i, limit))

        # Clean tweet, and skip to next tweet if it's not relevant/useful.
        text = cleanTweet(tweet['text'].lower())
        if not text: continue

        # Information extraction function which actually extracts info and relations and adds them to the awardsDict.
        extractInfo(text)

        if i >= limit:
            print("Finished analyzing tweets.")
            break



# Clean Tweet - Determines if Tweet is usable for information extraction and cleans the text.
# Ensures text is in English, removes emojis, etc.
def cleanTweet(text):
    if len(text) < 24: return False
    text = demoji(text)
    if not containsAnyOf(text, ["best", "award", "nominee", "host"]): return False
    try:
        if detect(text) != 'en': return False
    except:
        return False
    return text

# Information extraction - Takes in a valid Tweet's text and attempts to extract information from it.
# NOTE - For now, it just extracts awards, as that is the most crucial part to get right.
def extractInfo(text):
    # for (type, award, entity) in findRelations(text):
    #     if award:
    #         awardsDict.foundRelation(type, award, entity)

    award_name = findAward(text)
    if award_name:
        awardsDict.foundAward(award_name)


def main():
    AnalyzeTweets()


if __name__ == "__main__":
    main()
