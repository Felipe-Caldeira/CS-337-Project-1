from langdetect import detect
from info_extraction import *
import math
from globals import similar, replaceLemmas, adjustLemmas, DecomposedText, PERSON_AWARDS, MOVIE_AWARDS, ia
import difflib
from pprint import pprint
import string

# Generate Results - Generates the JSON that will contain our result
def GenerateResults(long=False):
    print("Generating results...")
    results = {}
    results["hosts"] = GetHosts()
    results["award_names"] = GetAwardNames()
    results["award_data"] = {award: {} for award in OFFICIAL_AWARDS}
    for award in OFFICIAL_AWARDS:
        results["award_data"][award]['nominees'] = GetRelation(award, 'nominees', 4, long=long)
        results["award_data"][award]['presenters'] = GetRelation(award, 'presenters', 2, long=long)
        results["award_data"][award]['winner'] = GetRelation(award, 'winners', 1, long=long)[0]
    results["additional_goals"] = {"best dressed": GetRelation("best dressed", 'winners', 1, long=long)[0]
    }
    print("Finished generating results.")
    return results


def GetAwardNames():
    return [x[0] for x in condense(Counter(awardsTree.awardNamesDict).most_common(110)) if (containsAnyOf(x[0][:4], ['best', 'ceci']) and len(x[0].split()) > 3)][:26]
    # our_award_guesses = []
    # i = 1
    # while(len(our_award_guesses) < 100):
    #     top_award_names = Counter(awardsTree.awardNamesDict).most_common(i)
    #     x = top_award_names[i - 1][0]x
    #     # only keep award name guesses that start with reasonable words
    #     if (containsAnyOf(x[:4], ['best', 'ceci'])
    #         # and are long enough
    #         and len(x.split()) > 3
    #         # and aren't basically already in our guess list
    #             and x.translate(str.maketrans('', '', string.punctuation)) not in [y.translate(str.maketrans('', '', string.punctuation)) for y in our_award_guesses]):
    #         our_award_guesses.append(x.strip())
    #     i = i+1
    # return condense(our_award_guesses)[:26]


def StoreResults(results):
    with open('results.json', 'w') as file:
        json.dump(results, file, ensure_ascii=False)

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
def GetRelation(award_name, type, num_ents=1, long=False):
    award = awardsTree.getAward(award_name)
    dictCopy = award[0].dict[type].copy() if award else False
    entity = [('', 0)]
    if award:
        if 'best dressed' not in award_name:
            for name, tal in dictCopy.items():
                for name2, tal2 in dictCopy.items():
                    if name != name2 and similar(name, name2) > .9:
                        dictCopy[name] *= 2
                    if name != name2 and name in name2:
                        dictCopy[name] += len(name)
                    if containsAnyOf(award_name, PERSON_AWARDS):
                        if len(name.split()) == 2 and name2 in name and name != name2:
                            dictCopy[name] += 2*dictCopy[name2]
        entity = Counter(dictCopy).most_common(num_ents)
    
    if not len(entity) > 0: return ['']
    if containsAnyOf(award_name, PERSON_AWARDS) or type == 'presenters':
        search_res = []
        for name in entity:
            if not name: continue
            if len(name[0]) < 6 or long:
                search = ia.search_person(name[0])
                if search: search_res.append(search[0]['name'].replace(' nickname', '').strip().lower())
            else: 
                search_res.append(name[0])
        return search_res if search_res else ['']
    
    if containsAnyOf(award_name, MOVIE_AWARDS):
        search_res = []
        for title in entity:
            if not title: continue
            if len(title[0]) < 6 or long:
                search = ia.search_movie(title[0])
                if search: search_res.append(search[0]['title'].strip().lower())
            else:
                search_res.append(title[0])
        return search_res if search_res else ['']
    return [x[0] for x in entity] if len(entity) > 0 else ['']

def condense(awards_list):
    condensed = awards_list[:]
    for award in awards_list:
        for another in awards_list:
            if award != another and \
                (award in another) and \
                    award in condensed:
                condensed.remove(award)
    return condensed
