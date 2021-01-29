from langdetect import detect
from info_extractor import *

test_awards = []
test_nominees = []
# Main pipeline
limit = 10000
def AnalyzeTweets():
    for i, tweet in enumerate(tweets):
        if i % 1000 == 0:
            print("{}/{} tweets analyzed.".format(i, limit))

        text = cleanTweet(tweet['text'].lower())
        if not text: continue

        #print("Tweet {}:".format(i), text)
        extractInfo(text)

        # if containsAnyOf(text, ["best motion picture", "best performance", 
        # "best supporting", "best director", "best screenplay", "best animated"]):
        #     test_awards.append(text)

        # if containsAnyOf(text, ["i hope", "my bet", "will win", "doesn't win", "didn't win"]):
        #     test_nominees.append(text)

        if i >= limit:
            print("Finished analyzing tweets.")
            break



# Clean Tweet - Determines if Tweet is usable for information extraction and cleans the text.
# Ensures text is in English, removes emojis, @ mentions, #goldenglobe
def cleanTweet(text):
    if len(text) < 10: return False
    text = demoji(text)
    if not containsAnyOf(text, ["best", "award", "nominee", "host"]): return False
    try:
        if detect(text) != 'en': return False
    except:
        return False
    return text

# Information extraction - Takes in a valid Tweet's text and attempts to extract information from it.
def extractInfo(text):
    for (type, award, entity) in findRelations(text):
        if award:
            awardsDict.foundRelation(type, award, entity)


def main():
    AnalyzeTweets()


if __name__ == "__main__":
    main()
