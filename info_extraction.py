from globals import *

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

    if containsAnyOf(award_name, ['original song', 'screenplay']) and script_list == scripts.WINNERS:
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

    return [name[0].strip() for name in names]

# Relation finder - Takes in a text and an award name, finding relations between found names and the award.
# It adds the relation to the respective award_name node in the awardsTree.
def findRelations(text, award_name):
    # Winners:
    winner = findNames(text, award_name, scripts.WINNERS)
    if winner:
        awardsTree.foundRelation('winners', award_name, winner[0])

    # Nominees: TODO

    # Presenters: TODO
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



# Person and Movie identifier - Takes in a string and determines if it is the name of a person or a movie.
# Returns either "Person", "Movie", or False, as well as the official name of the person/movie.
def personOrMovie(name):
    name = name.lower()
    people = ia.search_person(name)
    movies = ia.search_movie(name)

    person = people[0] if people else False
    movie = movies[0] if movies else False

    person_match = similar(person['name'].lower(), name) if person else 0.0
    movie_match_l = similar(
        movie['long imdb title'].lower(), name) if movie else 0.0
    movie_match_s = similar(movie['title'].lower(), name) if movie else 0.0
    movie_match_avg = (movie_match_l + movie_match_s) / 2

    # print("Person match:", person_match)
    # print("Movie match (long):", movie_match_l)
    # print("Movie match (short):", movie_match_s)
    # print("Movie match (avg)", movie_match_avg)

    (entity, match, type) = (person['name'], person_match, "person") if person_match > movie_match_avg else (
        movie['title'], movie_match_avg, "movie") if movie else (False, 0.0, False)
    if match < .65:
        return (False, False)
    return (type, entity)
