from globals import *

# Award recognizer - Takes in a spacy doc and returns the name of an award mentioned in the tweet, or False if none found.
def extractAward(doc):
    lemmas = [token.lemma_ for token in doc]
    deps = [token.dep_ for token in doc]
    award_keywords = ["award", "nominee"]
    for keyword in award_keywords:
        if keyword in lemmas:
            idx = lemmas.index(keyword)
            if idx < len(deps) - 1 and deps[idx + 1] == 'prep':
                return (doc[idx + 2:deps.index('ROOT')])
    return False

