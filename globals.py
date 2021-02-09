import spacy
import re
import en_core_web_sm
from imdb import IMDb
from difflib import SequenceMatcher
import json
import pandas as pd
import scripts
from collections import Counter

# The official list of awards
OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']


# Initializing tweets from json
# Load in the tweets json
with open('data/gg2013.json') as f:
    tweets = json.load(f)[:]


# Initializing IMDb API and spacy language model
ia = IMDb()
nlp = spacy.load("en_core_web_sm")

# AwardsTree - A tree structured from AwardNodes.
# This tree is the key construct that allows us to aggregate similar award names, thus making finding the proper
# relations much easier. 
# It starts off with a single AwardNode named 'ROOT', which has no parent, a tally of infinity, and is at depth 0.
# 
# When the name of an award is found by findAward(), self.foundAward(award_name) is called. This method uses spacy
# to tokenize the award name and convert each token to its lemma (root form). Then, only those lemmas with a 
# part-of-speech tag of NOUN, PROPN, ADJ, ADV, and VERB are kept. These remaining lemmas make up the keywords.
#
# For example, the keywords for 'best performance by an actress in a motion picture - drama' are:
# [good, performance, actress, motion, picture, drama]
#
# These keywords are then use to traverse the tree, with 'good' being the parent of 'performance', 
# 'performance' the parent of 'actress', etc. In self.foundAward, if a node doesn't exist, it is created, whereas 
# in self.getAward, it simply returns False.
#
# You can visualize the tree by calling self.show(depth, tally_requirements, show_rels).
# Parameters:
#   depth              - An integer of the maximum depth of nodes to visualize (from ROOT)
#   tally_requirements - A dictionary mapping each depth to the minimum tally needed for a node to be visualized at that depth.
#   show_rels          - A boolean, determines whether or not to show the dictionary of relations for each node in the tree.
#
# The default parameter values are depth=6, tally_requirements={1:10, 2:2, 3:2, 4:2}, show_rels=False, so just calling
# self.show() should result in an adequate tree visualization.
class AwardsTree():
    def __init__(self):
        self.root = AwardNode("ROOT", None, float('inf'), 0)
        self.allowed_pos = ["NOUN", "PROPN", "ADJ", "ADV", "VERB"]

    # Converts 'award_name' to keywords and traverses the tree, adding new nodes if necessary, and tallying visited nodes.
    def foundAward(self, award_name):
        keywords = [token.lemma_ for token in DecomposedText(award_name).doc if token.pos_ in self.allowed_pos]
        keywords = adjustLemmas(keywords)
        currNode = self.root
        for i, word in enumerate(keywords):
            if not word:
                continue

            inChildren = False
            for child in currNode.children:
                if child.name == word:
                    inChildren = True
                    child.tally += 1
                    currNode = child
                    break
            if not inChildren:
                newNode = AwardNode(word, currNode, 1, currNode.depth + 1)
                currNode.add_child(newNode)
                currNode = newNode

    # Converts 'award_name' to keywords and traverses tree. Once the last node in the keywords is reached,
    # or if the current node also contains 'entity_name' in its dictionary for 'type', it adds/tallies 'entity_name'
    # in the dictionary 'type'.
    def foundRelation(self, type, award_name, entity_name):
        keywords = [token.lemma_ for token in DecomposedText(award_name).doc if token.pos_ in self.allowed_pos]
        keywords = adjustLemmas(keywords)
        currNode = self.root
        for i, word in enumerate(keywords):
            if not word:
                continue

            for child in currNode.children:
                if child.name == word:
                    currNode = child
                    break

            if i == len(keywords) - 1 or entity_name in currNode.dict[type]:
                currNode.foundRelation(type, award_name, entity_name)

                # If 'motion picture' is further specified in children, add relation to them too.
                c1 = currNode.getChild('motion')
                if c1:
                    c2 = c1.getChild('picture')
                    if c2:
                        c2.foundRelation(type, award_name, entity_name)

    # Converts 'award_name' to keywords and traverses tree. Once the last node in the keywords is reached, 
    # it returns a tuple containing the last node's dictionary as well as the list of nodes it visited along the path.
    def getAward(self, award_name):
        keywords = [token.lemma_ for token in DecomposedText(award_name).doc if token.pos_ in self.allowed_pos]
        keywords = adjustLemmas(keywords)
        currNode = self.root
        visited = []
        for i, word in enumerate(keywords):
            if not word:
                continue

            found_child = False
            for child in currNode.children:
                if child.name == word:
                    found_child = True
                    visited.append(child)
                    currNode = child
                    break

            if not found_child:
                # print("Award name not found.")
                return False

        return (currNode.dict, visited)

    # 
    def show(self, depth=6, tally_requirements={1:10, 2:2, 3:2, 4:2}, show_rels=False):
        self.root.show(depth, tally_requirements, show_rels)


# AwardNode - The base unit that makes up an AwardsTree.
# Each node contains a dictionary of dictionaries for presenters, nominees, and winners.
#
# Node fields:
#   name     - The name of the node
#   depth    - The depth of the node from the ROOT node
#   tally    - How many times this node has been visited
#   dict     - The dictionary of dictionaries
#   parent   - The parent node
#   children - The list of children nodes
class AwardNode():
    def __init__(self, name, parent, tally, depth):
        self.name = name
        self.depth = depth
        self.tally = tally
        self.dict = {
            "presenters": {},
            "nominees": {},
            "winners": {}
        }
        self.parent = parent
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

    def getChild(self, name):
        for child in self.children:
            if child.name == name:
                return child
        return False

    def getUncles(self):
        if self.parent:
            if self.parent.parent:
                return self.parent.parent.children
        return False

    def foundRelation(self, type, award_name, entity_name):
        if entity_name in self.dict[type]:
            self.dict[type][entity_name] += 1
        else:
            self.dict[type][entity_name] = 1

    def show(self, depth, tally_reqs, show_rels):
        tally_req = tally_reqs[self.depth] if (
            tally_reqs and self.depth in tally_reqs) else 1
        if self.depth <= depth and self.tally >= tally_req:
            if show_rels:
                print('|   '*self.depth + self.name +
                      ":", self.tally, self.dict)
            else:
                print('|   '*self.depth + self.name + ":", self.tally)
            for child in self.children:
                child.show(depth, tally_reqs, show_rels)

# The one and only, grandiose awardsTree object 
awardsTree = AwardsTree()


# Text decomposer: Creates an object that allows one to access the tokenized form of a texxt along with its
# part-of-speech tagging, lemmas, and relations to other words.
class DecomposedText():
    def __init__(self, text):
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
        print(pd.DataFrame({'Text': self.text, 'Lemma': self.lemma,
                            'Pos': self.pos, 'Parent': self.parent, 'Children': self.children}))
        print(self.nouns)


# This function returns a metric (0 to 1) for how similar strings a and b are.
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


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

# This function adjusts the lemmas in the keywords for the AwardsTree functions, removing and combining 
# certain words in the keywords
def adjustLemmas(words):
    new_words = words
    switch = False
    for i, word in enumerate(words):
        for original, new in {
            "best":"good", 
            "well":"good", 
            "support":"supporting", 
            "performance":"", 
            "role":"",
            "language":"",
            "television":"tv"
            }.items():
            if word == original: new_words[i] = new
            if i < len(new_words) - 1 and word in ["actor", "actress"] and new_words[i + 1] == "supporting":
                switch = (i, i + 1)
    
    if switch: 
        new_words[switch[0]], new_words[switch[1]] = new_words[switch[1]], new_words[switch[0]]
    return new_words

