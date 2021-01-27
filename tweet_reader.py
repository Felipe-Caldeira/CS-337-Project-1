from langdetect import detect
from info_extractor import *


# Main pipeline
limit = 10000
def AnalyzeTweets():
    for i, tweet in enumerate(tweets):
        if i % 1000 == 0:
            print("{}/{} tweets analyzed.".format(i, limit))

        text = validateTweet(tweet['text'].lower())
        if not text: continue

        #print("Tweet {}:".format(i), text)
        extractInfo(text)

        if i >= limit:
            print("Finished analyzing tweets.")
            break



# Tweet Validations - Determines if Tweet is usable for information extraction.
# Ensures text is in English, that it's not just an image or emojis, etc.
def validateTweet(text):
    if len(text) < 10: return False
    text = demoji(text)
    if not any(map(text.__contains__, ["best", "award", "nominee", "host"])): return False
    try:
        if detect(text) != 'en': return False
    except:
        return False
    return text

# Information extraction - Takes in a valid Tweet's text and attempts to extract information from it.
def extractInfo(text):
    doc = nlp(text)

    award = extractAward(doc)
    if award:
        print("Award found:", award)
        if award in awardsDict.dict:
            awardsDict.tallyAward(award)
        else:
            awardsDict.newAward(award)
        
        # Get related presenters, nominees, winners

def main():
    AnalyzeTweets()


if __name__ == "__main__":
    main()
