from langdetect import detect
from info_extraction import *
import math
from globals import similar, replaceLemmas, adjustLemmas, DecomposedText
from results_generator import *
import viztracer

# These are just lists used to store certain tweets relating to awards/nominees/etc to analyze what they look like.
test_awards = []
test_nominees = []

def main(year):
    # Load tweets and limit how many tweets to read
    tweets = loadTweets(year)
    limit = len(tweets)
    AnalyzeTweets(tweets, limit)
    print("Finished!")

# Main pipeline
def AnalyzeTweets(tweets, limit):
    limit = min(limit, len(tweets))
    # Part 1:
    # tracer = viztracer.VizTracer()
    # tracer.start()
    print("Analyzing tweets for Award Names and Winners...")
    for i, tweet in enumerate(tweets):
        # Progress meter:
        if i % 1000 == 0 or i + 1 >= limit:
            progress = (i+1)/limit
            print("{}{} {}/{} tweets analyzed.".format("="*math.floor(progress*50), "-"*(50 - math.floor(progress*50)), i+1, limit), end='\r')
            if i + 1 >= limit: 
                print("\nFinished analyzing tweets (Part 1).")
                break

        # Clean tweet, and skip to next tweet if it's not relevant/useful.
        text = cleanTweet(tweet['text'])
        if not text: continue

        # Information extraction function which actually extracts info and relations and adds them to the awardsDict.
        try: extractInfo(text)
        except: continue
    
    # tracer.stop()
    # tracer.save()
    # Generate the results in the correct json format
    results = GenerateResults()

    # Part 2:
    winners_awards_list = [(results['award_data'][award]['winner'], award) for award in results['award_data']]

    print("Analyzing tweets for Nominees and Presenters...")
    for i, tweet in enumerate(tweets):
        if i % 1000 == 0 or i + 1 >= limit:
            progress = (i+1)/limit
            print("{}{} {}/{} tweets analyzed.".format("="*math.floor(progress*50), "-"*(50 - math.floor(progress*50)), i+1, limit), end='\r')
            if i + 1 >= limit:
                print("\nFinished analyzing tweets (Part 2).")
                break

        text = cleanTweetPt2(tweet['text'])
        if not text: continue
        if not containsAnyOf(text.lower(), ['best dressed'] + [winners[0] for winners in winners_awards_list]): continue

        try: extractInfoPt2(text, winners_awards_list) 
        except: continue

    results = GenerateResults(long=True)
    StoreResults(results)



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

def cleanTweetPt2(text):
    if len(text) < 20: return False
    text = demoji(text)
    if 'RT' in text: return False
    if not containsAnyOf(text.lower(), ["beat", "lost to", "best dressed", "present"]): return False
    text = text.replace("@", '')
    text = " ".join(filter(lambda x: x[:4] != 'http', text.split()))
    return text


# Information extraction - Takes in a valid Tweet's text and attempts to extract information from it.
def extractInfo(text):
    findHosts(text)
    award_name = findAward(text)
    if award_name and len(award_name) > 5:
        awardsTree.foundAward(award_name)
        findRelations(text, award_name)

def extractInfoPt2(text, winners_list):
    findNominees(text, winners_list)
    findBestDressed(text)
    if 'present' in text:
        test_awards.append(text)
    # findPresenters(text)


if __name__ == "__main__":
    main(2013)
