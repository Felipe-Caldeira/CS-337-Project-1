from langdetect import detect
from info_extraction import *
import math

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

        # text = tweet['text']
        # if containsAnyOf(text, ['present', 'jessica alba', 'aziz', 'christian bale', 'kriten bell', 'halle berry', 'josh brolin', 'bill clinton', 'megan fox', 'dennis quaid', 'john goodman', 'jennifer garner', 'jamie foxx', 'robert pattison', 'julia roberts']) and "best dress" not in text:
        #     test_awards.append(text)

        # Clean tweet, and skip to next tweet if it's not relevant/useful.
        text = cleanTweet(tweet['text'])
        if not text: continue

        # Information extraction function which actually extracts info and relations and adds them to the awardsDict.
        extractInfo(text)
        # if containsAnyOf(text, ['miniseries', 'mini-series', 'mini']):
        #     test_awards.append(text)


# Clean Tweet - Determines if Tweet is usable for information extraction and cleans the text.
# Ignores retweets, removes hashtags, @ mentions, urls
def cleanTweet(text):
    if len(text) < 20: return False
    text = demoji(text)
    if "RT" in text: return False
    if not containsAnyOf(text.lower(), ["best", "award", "nominee", "host", "present", "worst"]): return False
    for word in ["goldenglobes", "goldenglobe", "golden", "globe", "@"]:
        text = text.replace(word, '')
    text = text.replace('miniseries', 'mini-series')
    text = text.replace('mini series', 'mini-series')
    # text = " ".join(filter(lambda x: x[0] != '#', text.split()))
    # text = " ".join(filter(lambda x: x[0] != '@', text.split()))
    text = " ".join(filter(lambda x: x[:4] != 'http', text.split()))
    return text.lower()


# Information extraction - Takes in a valid Tweet's text and attempts to extract information from it.
def extractInfo(text):
    findHosts(text)
    award_name = findAward(text)
    if containsAnyOf(text, ['miniseries', 'mini-series', 'mini series']):
        test_awards.append(award_name)
        test_nominees.append(text)
    if award_name and len(award_name) > 5:
        awardsTree.foundAward(award_name)
        findRelations(text, award_name)


# Show results - Temporary function to show how well our extraction is for 'type'.
def ShowResults(type, num_ents=1):
    for award_name in OFFICIAL_AWARDS:
        award = awardsTree.getAward(award_name)
        dictCopy = award[0].dict[type].copy() if award else False
        entity = 'None'
        if award:
            for name, tal in dictCopy.items():
                for name2, tal2 in dictCopy.items():
                    if name != name2 and name in name2:
                        dictCopy[name] += len(name)
                    if not containsAnyOf(award_name, ['best motion picture', 'film', 'score', 'song', 'score', 'best television', 'best mini']):
                        if len(name.split()) == 2 and name2 in name:
                            dictCopy[name] += 2*len(name)
            entity = Counter(dictCopy).most_common(num_ents)
        print("{}: {}".format(award_name, entity))


def GetHosts():
    hosts = Counter(hostsDict).most_common(2)
    if not len(hosts) >= 2: 
        return []
    if not hosts[1][1] >= hosts[0][1]/2:
        hosts = hosts[0]
    return [x[0] for x in hosts]


# Relations getter
def GetRelation(award_name, type, num_ents=1):
    award = awardsTree.getAward(award_name)
    dictCopy = award[0].dict[type].copy() if award else False
    entity = [('None')]
    if award:
        for name, tal in dictCopy.items():
            for name2, tal2 in dictCopy.items():
                if name != name2 and name in name2:
                    dictCopy[name] += len(name)
                if not containsAnyOf(award_name, ['best motion picture', 'film', 'score', 'song', 'score', 'best television', 'best mini']):
                    if len(name.split()) == 2 and name2 in name:
                        dictCopy[name] += 2*len(name)
        entity = Counter(dictCopy).most_common(num_ents)
    return [x[0] for x in entity]

def main():
    AnalyzeTweets()
    ShowResults('winners')


if __name__ == "__main__":
    main()
