import spacy
import re
import en_core_web_sm
from imdb import IMDb
from difflib import SequenceMatcher
import json

# This function returns a metric (0 to 1) for how similar strings a and b are.
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# Initializing IMDb API and spacy language model
ia = IMDb()
nlp = spacy.load("en_core_web_sm")

# Initializing tweets from json
# Load in the tweets json
with open('data/gg2013.json') as f:
    tweets = json.load(f)


# Awards class - Contains all extracted awards as keys, whose values are dictionaries containing their
# extraction tally, related presenters, nominees, winners.
# global awards_dict

class Awards():
    def __init__(self):
        self.dict = {}

    def newAward(self, award_name):
        self.dict[award_name] = {
            "tally" : 1,
            "presenters" : {},
            "nominees" : {},
            "winner" : {}
        }

    def tallyAward(self, award_name):
        self.dict[award_name].tally += 1

    def newPresenter(self, award_name, presenter_name):
        self.dict[award_name].presenters[presenter_name] = 1

    def tallyPresenter(self, award_name, presenter_name):
        self.dict[award_name].presenters[presenter_name] += 1

    def newNominee(self, award_name, nominee_name):
        self.dict[award_name].nominees[nominee_name] = 1

    def tallyNominee(self, award_name, nominee_name):
        self.dict[award_name].nominees[nominee_name] += 1

    def newWinner(self, award_name, winner_name):
        self.dict[award_name].winner[presenter_name] = 1

    def tallyWinner(self, award_name, winner_name):
        self.dict[award_name].winner[presenter_name] += 1

awardsDict = Awards()



# Clean emojis from tweets
def demoji(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U0001F1F2-\U0001F1F4"  # Macau flag
        u"\U0001F1E6-\U0001F1FF"  # flags
        u"\U0001F600-\U0001F64F"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U0001F1F2"
        u"\U0001F1F4"
        u"\U0001F620"
        u"\u200d"
        u"\u2640-\u2642"
        "]+", flags=re.UNICODE)

    return emoji_pattern.sub(r'', text)
