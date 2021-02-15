from langdetect import detect
from info_extraction import *
import math
from globals import similar, replaceLemmas, adjustLemmas, DecomposedText
import difflib
from pprint import pprint
import string

# Generate Results - Generates the JSON that will contain our result
def GenerateResults():
    results = {}
    results["hosts"] = GetHosts()
    results["award_names"] = GetAwardNames()
    results["award_data"] = {award: {} for award in OFFICIAL_AWARDS}
    for award in OFFICIAL_AWARDS:
        results["award_data"][award]['nominees'] = GetRelation(award, 'nominees', 4)
        results["award_data"][award]['presenters'] = GetRelation(award, 'presenters', 2)
        results["award_data"][award]['winner'] = GetRelation(award, 'winners', 1)[0]
    results["additional_goals"] = {"best dressed": GetRelation("best dressed", 'winners', 1)[0]
    }

    with open('results.json', 'w') as file:
        json.dump(results, file, ensure_ascii=False)


def GetAwardNames():
    our_award_guesses = []
    i = 1
    while(len(our_award_guesses) < 100):
        top_award_names = Counter(awardsTree.awardNamesDict).most_common(i)
        x = top_award_names[i - 1][0]
        # only keep award name guesses that start with reasonable words
        if (containsAnyOf(x[:4], ['best', 'ceci'])
            # and are long enough
            and len(x.split()) > 3
            # and aren't basically already in our guess list
                and x.translate(str.maketrans('', '', string.punctuation)) not in [y.translate(str.maketrans('', '', string.punctuation)) for y in our_award_guesses]):
            our_award_guesses.append(x.strip())
        i = i+1
    return condense(our_award_guesses)[:26]


def LoadResults():
    try:
        with open('results.json') as file:
            return json.load(file)
    except:
        print('results.json not found.')


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
                if name != name2 and similar(name, name2) > .9:
                    dictCopy[name] *= 2
                if name != name2 and name in name2:
                    dictCopy[name] += len(name)
                if not containsAnyOf(award_name, ['best motion picture', 'film', 'score', 'song', 'score', 'best television', 'best mini']):
                    if len(name.split()) == 2 and name2 in name and name != name2:
                        dictCopy[name] += 2*dictCopy[name2]
        entity = Counter(dictCopy).most_common(num_ents)

    return [x[0] for x in entity] if len(entity) > 0 else [('None')]

def condense(awards_list):
    condensed = awards_list[:]
    for award in awards_list:
        for another in awards_list:
            if award != another and \
                (award in another) and \
                    award in condensed:
                condensed.remove(award)
    return condensed
