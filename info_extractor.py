from globals import *

# Person and Movie identifier - Takes in a string and determines if it is the name of a person or a movie.
# Returns either "Person", "Movie", or False, as well as the official name of the movie.
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


    (entity, match, type) = (person['name'], person_match, "person") if person_match > movie_match_avg else (movie['title'], movie_match_avg, "movie") if movie else (False, 0.0, False)
    if match < .65:
        return (False, False)
    return (type, entity)


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
