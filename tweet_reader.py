from langdetect import detect
from info_extraction import *
import math

# These are just lists used to store certain tweets relating to awards/nominees/etc to analyze what they look like.
test_awards = []
test_nominees = []

# Limit how many tweets to read
limit = len(tweets)


# Main pipeline
limit = min(limit, len(tweets))
def AnalyzeTweets():
    for i, tweet in enumerate(tweets):
        # Progress meter:
        if i % 1000 == 0:
            progress = i/limit
            print("{}{} {}/{} tweets analyzed.".format("="*math.floor(progress*50), "-"*(50 - math.floor(progress*50)), i, limit))
        if i >= limit - 1:
            print("{} {}/{} tweets analyzed.".format("="*50, limit, limit))
            print("Finished analyzing tweets.")
            break

        # Clean tweet, and skip to next tweet if it's not relevant/useful.
        text = cleanTweet(tweet['text'])
        if not text: continue

        # Information extraction function which actually extracts info and relations and adds them to the awardsDict.
        extractInfo(text)
        # award = findAward(text)
        # if award:
        #     test_awards.append(award)
        #     test_nominees.append(text)


# Clean Tweet - Determines if Tweet is usable for information extraction and cleans the text.
# Ignores retweets, removes hashtags, @ mentions, urls
def cleanTweet(text):
    if len(text) < 20: return False
    text = demoji(text)
    if "RT" in text: return False
    if not containsAnyOf(text.lower(), ["best", "award", "nominee", "host"]): return False
    text = " ".join(filter(lambda x: x[0] != '#', text.split()))
    text = " ".join(filter(lambda x: x[0] != '@', text.split()))
    text = " ".join(filter(lambda x: x[:4] != 'http', text.split()))
    return text.lower()


# Information extraction - Takes in a valid Tweet's text and attempts to extract information from it.
def extractInfo(text):
    award_name = findAward(text)
    if award_name:
        awardsTree.foundAward(award_name)
        findRelations(text, award_name)

# Show winners - Temporary function to show how well our winners extraction is.
def ShowWinners():
    for award in OFFICIAL_AWARDS:
        winner = awardsTree.getAward(award)
        if winner:
            winner = winner[0]['winners']
            winner = max(winner, key=winner.get)
        print("{}: {}".format(award, winner))

def main():
    AnalyzeTweets()
    ShowWinners()


if __name__ == "__main__":
    main()
