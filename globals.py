import spacy
import re
import en_core_web_sm
from imdb import IMDb
from difflib import SequenceMatcher
import json
import pandas as pd

# This function returns a metric (0 to 1) for how similar strings a and b are.
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# Initializing IMDb API and spacy language model
ia = IMDb()
nlp = spacy.load("en_core_web_sm")

# Initializing tweets from json
# Load in the tweets json
with open('data/gg2013.json') as f:
    tweets = json.load(f)[0000:]


# Awards class - Contains all extracted awards as keys, whose values are dictionaries containing their
# extraction tally, related presenters, nominees, winners.
class Awards():
    def __init__(self):
        self.dict = {}

    def foundRelation(self, type, award_name, entity_name): # 'type' can be 'presenters', 'nominees', 'winner', or False
        self.foundAward(award_name)
        if not type: return
        
        if entity_name in self.dict[award_name][type]:
            self.dict[award_name][type][entity_name] += 1
        else:
            self.dict[award_name][type][entity_name] = 1

    def foundAward(self, award_name):
        if award_name in self.dict:
            self.dict[award_name]['tally'] += 1
        else:
            self.newAward(award_name)

    def newAward(self, award_name):
        self.dict[award_name] = {
            "tally" : 1,
            "presenters" : {},
            "nominees" : {},
            "winner" : {}
        }

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

def containsAnyOf(str, strList):
    return any(map(str.__contains__, strList))


# Text decomposer: Creates an object that allows one to access the tokenized form of a texxt along with its 
# part-of-speech tagging, lemmas, and relations to other words.
class DecomposedText():
    def __init__(self, text):
        text = text.lower()
        self.full_text = text
        self.doc = nlp(text)
        self.text = []
        self.lemma = []
        self.pos = []
        self.parent = []
        self.children = []
        self.nouns = []

        for token in self.doc:
            self.text.append(token.text)
            self.lemma.append(token.lemma_)
            self.pos.append(token.pos_)
            self.parent.append(token.head)
            self.children.append([child for child in token.children])

        self.nouns = [chunk for chunk in self.doc.noun_chunks]

    def show(self):
        print(pd.DataFrame({'Text':self.text, 'Lemma':self.lemma, 'Pos':self.pos, 'Parent':self.parent, 'Children':self.children}))
        print(self.nouns)

