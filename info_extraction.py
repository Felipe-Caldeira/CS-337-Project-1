from globals import *


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


# Relation finder - Takes in a text and finds relations between awards and entities.
# Returns a list of relations, which are tuples in the form: (type, award, entity), where 
# 'type' is 'nominees', 'winner', and 'presenters'; 'award' is the name of the award; and 
# 'entity' is the name of the person/movie.
def findRelations(text):
    Text = DecomposedText(text)
    relations = []
    # print(Text.nouns)

    # Nominees and Awards
    keywords = ["win", "nominate"]

    for i, token in enumerate(Text.doc):
        if token.lemma_ in keywords:
            type = False
            award = False
            entity = False

            for child in token.children:
                if not entity and child.pos_ in ['NOUN', 'PROPN']:
                    entity = [noun for noun in Text.nouns if child in noun]
                    if not entity: continue
                    (type, entity) = personOrMovie(entity[0].text)
                    continue
                if not award and child.pos_ in ['NOUN', 'ADP']:
                    if child.pos_ == 'ADP':
                        child = [c for c in child.children]
                        if not child: continue
                        child = child[0]
                    award = [noun for noun in Text.nouns if child in noun]
                    if not award: continue
                    award = award[0].text
                    break

            relations.append(("nominees", award, entity))
    return relations


# Award finder - This function specifically finds award names and adds them to the awardsDict. 
# It's somewhat effective, though it does have a couple hardcoded words which is isn't ideal.
award_pos = ["ADJ", "NOUN", "ADP", "DET", "PUNCT", "CCONJ"]


def findAward(text):
    Text = DecomposedText(text)
    start = False
    end = False
    dash = False

    # check if 'goes' is in the tweet, make sure 'to' comes right after. Extract 'Best Award' from tweet and return
    if 'goes' in Text.text:
        goesidx = Text.text.index('goes')
        if Text.text[goesidx + 1] == 'to':
            if 'Best' in Text.text:
                award_name = 'Best' + Text.text[Text.text.index('Best') + 1]
                return award_name
            elif 'best' in Text.text:
                award_name = 'Best' + Text.text[Text.text.index('best') + 1]
                return award_name





    for i, pos in enumerate(Text.pos):
        if not start and i >= len(Text.text) - 2: break

        # Start reading potential award
        if not start and pos == "ADJ" and (
                Text.pos[i + 1] == "NOUN" or Text.pos[i + 1] == "ADJ" or Text.pos[i + 1] == "VERB") and (
                Text.lemma[i] == "good"):
            start = i
            continue

        # Restrict certain words from counting as award
        if start and pos in ["ADP", "DET", "PUNCT", "CCONJ"]:
            if Text.text[i] not in ["in", "a", "-", "or"]:
                end = i
                break

        # Stop reading award if encountering a second dash, or if the word after the first dash isn't valid.
        if start and Text.text[i] == "-":
            if dash or (Text.pos[i + 1] != "NOUN") or (
                    Text.text[i + 1] not in ["drama", "musical", "comedy", "foreign", "animated"]):
                end = i
                break
            dash = True

        # Continue reading until not valid award pos, unless it's only the second in the sequence
        if start and pos not in award_pos:
            if i == start + 1:
                continue
            end = i
            break

    # If reading an award and reached the end of the text, stop reading. 
    # If shorter than 3 words, ignore it (though 2 words would be useful for 'best dressed')
    if start and not end: end = len(Text.text)
    if not (end - start >= 3):
        return False

    award_name = Text.doc[start:end].text
    # print(award_name)
    return award_name
