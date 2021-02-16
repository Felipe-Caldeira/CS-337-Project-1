from globals import *
from results_generator import LoadResults

# Award name finder - Extracts the name of an award in a text and returns it. Utilizes the AWARDS script.
def findAward(text):
    awards = {}

    for script in scripts.AWARDS:
        p = scripts.scriptToRegex(script[0], "")
        matches = p.search(text)

        if matches:
            award = matches.group('award')
            if award in awards:
                awards[award] += script[1]
            else:
                awards[award] = script[1]

    if not awards: return False
    awards = Counter(awards).most_common(5)
    for award in awards:
        award = award[0]
        if not containsAnyOf(award, ['golden', 'globe']):
            for str in ["winner", "(", ")"]:
                award = award.replace(str, '')
            return award if award else False
    return False

# Name finder - Takes in a string, an award name, and a list of scripts. Using the given list of scripts,
# it extracts and returns the most common of matched names.
def findNames(str, award_name, script_list, num_names=1):
    names = {}

    if containsAnyOf(award_name, ['original song', 'screenplay', 'original score']) and script_list == scripts.WINNERS:
        script_list = scripts.ALT_WINNER

    for script in script_list:
        p = scripts.scriptToRegex(script[0], award_name)
        matches = p.search(str)

        if matches:
            name = matches.group('name')
            try: name2 = matches.group('name2')
            except: name2 = False
            for name in [name, name2]:
                if not name: continue
                if name in names:
                    names[name] += script[1]
                else:
                    names[name] = script[1]

    if not names: return False
    names = Counter(names).most_common(num_names)

    return [name[0].strip() for name in names if len(name[0]) > 2]

# Relation finder - Takes in a text and an award name, finding relations between found names and the award.
# It adds the relation to the respective award_name node in the awardsTree.
def findRelations(text, award_name):
    # Winners:
    winner = findNames(text, award_name, scripts.WINNERS)
    if winner:
        awardsTree.foundRelation('winners', award_name, winner[0])

    # Nominees:
    # nominees = findNames(text, award_name, scripts.NOMINEES)
    # if nominees:
    #     for nominee in nominees: awardsTree.foundRelation('nominees', award_name, nominee)

    # Presenters: 
    presenters = findNames(text, award_name, scripts.PRESENTERS, 2)
    if presenters and presenters[0]:
        awardsTree.foundRelation('presenters', award_name, presenters[0])
        if len(presenters) > 1 and presenters[1]:
            awardsTree.foundRelation('presenters', award_name, presenters[1])
    return presenters

# Hosts finder - Finds names of hosts
def findHosts(text):
    if "host" not in text: return
    hosts = findNames(text, "", scripts.HOSTS, 2)
    if hosts:
        for host in hosts:
            if host in hostsDict:
                hostsDict[host] += 1
            else:
                hostsDict[host] = 1


# Best dressed finder - Finds names of best dressed 'candidates'
def findBestDressed(text):
    if not containsAnyOf(text, ["best dressed", "Best Dressed"]): return
    candidates = findNames(text, "", scripts.BEST_DRESSED, 10)
    individual_candidates = []
    for names in candidates:
        names_split = re.findall(scripts.NAMES_SPLITTER, names)
        for actual_name in [x[0] for x in names_split]:
            actual_name = actual_name.strip().lower()
            individual_candidates.append(actual_name) 

    if individual_candidates:
        for candidate in individual_candidates:
            if not containsAnyOf(candidate, ['best', 'red', 'carpet']): awardsTree.foundRelation('winners', 'best dressed', candidate)


# Nominees finder - Finds names of nominees given knowledge of the winners 
def findNominees(text, winners_list):
    if not containsAnyOf(text.lower(), ["beat", "lost to"]): return
    for winner_award in winners_list:
        if winner_award[0] in text.lower():
            nominees = []

            for script in scripts.NOMINEES_2:
                p = scripts.scriptToRegex(script[0], '')
                matches = p.search(text)

                if matches:
                    name = matches.group('name')
                    try: name2 = matches.group('name2') 
                    except: name2 = False
                    try: name3 = matches.group('name3')
                    except: name3 = False
                    try: names = matches.group('names')
                    except: names = False
                    for found_names in [name2, name3, names]:
                        if not found_names: continue
                        names_split = re.findall(scripts.NAMES_SPLITTER, found_names)
                        for actual_name in [x[0] for x in names_split]:
                            actual_name = actual_name.strip().lower()
                            if actual_name != winner_award[0]:
                                awardsTree.foundRelation('nominees', winner_award[1], actual_name)


# Person and Movie identifier - Takes in a string and determines if it is the name of a person or a movie.
# Returns either "Person", "Movie", or False, as well as the official name of the person/movie.
def personOrMovie(name, force_type=False):
    name = name.lower()
    people = ia.search_person(name)
    movies = ia.search_movie(name)

    person = people[0] if people else False
    movie = movies[0] if movies else False

    person_match = similar(person['name'].lower(), name) if person else 0.0
    movie_match_l = similar(movie['long imdb title'].lower(), name) if movie else 0.0
    movie_match_s = similar(movie['title'].lower(), name) if movie else 0.0
    movie_match_avg = (movie_match_l + movie_match_s) / 2

    # print("Person match:", person_match)
    # print("Movie match (long):", movie_match_l)
    # print("Movie match (short):", movie_match_s)
    # print("Movie match (avg)", movie_match_avg)
    if not force_type:
        (entity, match, type) = (person['name'], person_match, "person") if person_match > movie_match_avg else \
        (movie['title'], movie_match_avg, "movie") if movie else (False, 0.0, False)
        if match < .65:
            return (False, False)
    else:
        if force_type == 'person':
            if person_match < .65: return (False, False)
            else: return ('person', person['name'])
        else:
            if movie_match_avg < .65: return (False, False)
            else: return ('movie', movie['title'])

    return (type, entity)
