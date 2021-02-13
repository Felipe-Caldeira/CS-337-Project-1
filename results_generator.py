from langdetect import detect
from info_extraction import *
import math
from globals import similar, replaceLemmas, adjustLemmas, DecomposedText
import difflib
from pprint import pprint 

# Generate Results - Generates the JSON that will contain our result
def GenerateResults():
    results = {}
    results["hosts"] = GetHosts()
    results["award_data"] = {award: {} for award in OFFICIAL_AWARDS}
    for award in OFFICIAL_AWARDS:
        results["award_data"][award]['nominees'] = GetRelation(
            award, 'nominees', 4)
        results["award_data"][award]['presenters'] = GetRelation(
            award, 'presenters', 2)
        results["award_data"][award]['winner'] = GetRelation(award, 'winners', 1)[
            0]

    with open('results.json', 'w') as file:
        json.dump(results, file, ensure_ascii=False)

# Generate Results - Generates our award name guesses in a JSON


def GenerateAwardNameResults():
    results = {}
    our_award_guesses = []
    i = 1
    while(len(our_award_guesses) < 50):
        top_award_names = Counter(awardsTree.awardNamesDict).most_common(i)
        x = top_award_names[i - 1]
        # only keep award name guesses that are long enough and start with reasonable words
        if (containsAnyOf(x[0][:4], ['best', 'ceci']) and len(x[0].split()) > 3):
            our_award_guesses.append(x[0])
        i = i+1
    results["our_guess"] = condense(our_award_guesses)[:26]
    results["translation"] = calc_translation(
        our_award_guesses, OFFICIAL_AWARDS)
    with open('award_name_results.json', 'w') as file:
        json.dump(results, file, ensure_ascii=False)


def LoadResults():
    try:
        with open('results.json') as file:
            return json.load(file)
    except:
        print('results.json not found.')


def LoadAwardNameResults():
    try:
        with open('award_name_results.json') as file:
            return json.load(file)
    except:
        print('award_name_results.json not found.')


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
                if similar(name, name2) > .9:
                    dictCopy[name] *= 2
                if name != name2 and name in name2:
                    dictCopy[name] += len(name)
                if not containsAnyOf(award_name, ['best motion picture', 'film', 'score', 'song', 'score', 'best television', 'best mini']):
                    if len(name.split()) == 2 and name2 in name:
                        dictCopy[name] += 2*len(name)
        entity = Counter(dictCopy).most_common(num_ents)

    return [x[0] for x in entity] if len(entity) > 0 else [('None')]


def spell_check(r, a, s, scores, weight=1):
    change = weight*(1-(similar(r, a)/float(max(len(r), len(a)))))
    if s in scores:
        # penalty for returning multiple of the same result when
        # one instance is incorrectly spelled
        return (scores[s] + change)/2.0
    else:
        return change


allowed_pos = ["NOUN", "PROPN", "ADJ", "ADV", "VERB"]
kw_cache = {}
awardNamesDict = {}

# Converts 'award_name' to keywords


def toKeywords(award_name):
    award_name = award_name.replace('mini-serie', 'miniserie')
    if award_name in kw_cache:
        return kw_cache[award_name]
    else:
        keywords = [token.lemma_ for token in DecomposedText(
            award_name).doc if token.pos_ in allowed_pos]
        keywords = adjustLemmas(keywords)
        keywords = replaceLemmas(keywords, ['mini', 'series'], ['miniserie'])
        refined = []
        [refined.append(x) for x in keywords if (x and x not in refined)]
        keywords = refined
        if "miniserie" in keywords:
            keywords = replaceLemmas(
                keywords, ['series', 'miniserie', 'motion', 'picture'], [])
            keywords = replaceLemmas(keywords, ['motion', 'picture', 'tv'], [])
        kw_cache[award_name] = keywords
    return keywords


def norm_text(textstring):
    """Takes a string of text and returns a string of normalized text."""
    return "".join([c.lower() for c in textstring if c.isalnum() or c.isspace()])


def text(resultstr, answerstr):
    """Accepts two normalized texts, as output by the norm_text
    function, and returns a score based on the match length relative
    to the longest text length."""

    result = resultstr.split()
    answer = answerstr.split()

    len_result = len(result)
    len_answer = len(answer)

    if (resultstr in answerstr) or (answerstr in resultstr):
        textscore = min(len_result, len_answer) / \
            float(max(len_result, len_answer))
    else:
        s = difflib.SequenceMatcher(None, result, answer)

        longest = s.find_longest_match(0, len_result, 0, len_answer)
        longest = longest.size/float(max(len_result, len_answer))

        if longest > 0.3:
            matchlen = sum([m[2] for m in s.get_matching_blocks() if m[2] > 1])
            textscore = float(matchlen)/max(len_result, len_answer)
        else:
            textscore = longest

    return textscore


def calc_translation(result, answer):
    """Accepts two lists of strings, determines the best matches
    between them, and returns a translation dictionary and
    score."""

    resultmap = {" ".join(toKeywords(norm_text(r))): r for r in result}
    answermap = {" ".join(toKeywords(norm_text(a))): a for a in answer}
    result = set(resultmap.keys())
    answer = set(answermap.keys())

    intersection = result.intersection(answer)
    translation = {resultmap[i]: answermap[i] for i in intersection}
    scores = dict(list(zip(list(translation.values()), [1]*len(intersection))))
    score_by_results = {}
    score_by_answers = {}

    # loop through results that didn't have a perfect match
    # and get a score for each of them.
    comp = list(result - intersection)

    for r in comp:
        score_by_results[r] = Counter()
        for a in answer:
            if a not in score_by_answers:
                score_by_answers[a] = Counter()

            score_by_results[r][a] = text(r, a)
            score_by_answers[a][r] = score_by_results[r][a]
    #print("score_by_results:")
    #pprint(score_by_results)
    #print("score_by_answers:")
    #pprint(score_by_answers)
    #print("length of comp:")
    #print(len(comp))
    for r in score_by_results:
        cnt = 0
        ranking = score_by_results[r].most_common()
        flag = True
        while flag:
            # The answer that best matches the result
            answer_match = ranking[cnt][0]
            # The top result matching that answer
            max_result = score_by_answers[answer_match].most_common(1)[0]

            if (max_result[0] == r) or (score_by_results[r][answer_match] > score_by_answers[answer_match][max_result[0]]):
                # if the top result matching that answer is our current result or
                # if the current result's score is greater than the previous top result
                translation[resultmap[r]] = answermap[answer_match]
                scores[answermap[answer_match]] = spell_check(
                    r, answer_match, answer_match, scores)

                flag = False

            cnt += 1
            if cnt == len(ranking):
                flag = False

    if scores:
        return sum(scores.values())/float(len(scores)), translation
    else:
        return 0, translation


def condense(awards_list):
    condensed = awards_list[:]
    for award in awards_list:
        for another in awards_list:
            if award != another and \
                (award in another) and \
                    award in condensed:
                condensed.remove(award)
    return condensed