import re
# Scripts for information extraction
#
# Each list of scripts is composed of tuples, each containing a regex string and a 'priority' score.
# Common regex strings are abstracted here as [NAME], [PERSON], and [AWARD], which are converted to actual
# regex patterns in scriptToRegex().

# [NAME]   - Pattern for the general name of a person, movie, or show.
# [PERSON] - Pattern for the name of a person (structured as "firstname lastname")
# [AWARD]  - A variable which is used in scripts other than AWARDS; represents the name of an award (found through 
# findAward()) which is passed into scriptToRegex() to make the actual award_name be a part of the pattern.

# Awards
AWARDS = [
    (r"wins (?P<award>best[a-z ]+?) (for|globe[s*]|golden|at|and)", 10),
    (r"(?P<award>best [a-z ]*-[a-z ]+)([:-])", 8),
    (r"(?P<award>best [a-z]*-?[a-z,\/ \(\)]+?) *(:|-|—|goes to|from)", 6),
    (r"(?P<award>best (?!thing)[a-z,\/ \(\)\-]+?) (is|but)", 4),
    (r"(?P<award>best [a-z,/ \(\)\-]+(musical|comedy|drama))", 5),
    (r"(receiv.* the|receives) (?P<award>(?!golden)[\w .]{1,20} award)", 5)
]

# Winners
WINNERS = [
    (r"*[NAME] wins", 8),
    (r"*[NAME] won", 8),
    (r"*[NAME] receives (the )*[AWARD]", 8),
    (r"[AWARD]: [NAME] for", 8),
    (r"[AWARD] goes to [NAME][PUNCT]", 8),
    (r"[AWARD] goes to [NAME] for", 6),
    (r"[AWARD](: |-)[NAME]([PUNCT]| -)", 4),
    (r"goes to [NAME][PUNCT]", 2),
    (r"winner [PERSON]", 6),
    (r"congra.* to [PERSON]", 5),
    (r"[PERSON] accepting", 3)
]

# Converts scripts to actual regex patterns
def scriptToRegex(script, award_name):
    script = script.replace("*[NAME]", r'(^|[.,!:] )(?P<name>[a-z ]+\b)')
    script = script.replace("[NAME]", r'(?P<name>[a-z ]+\b)')
    script = script.replace("[PUNCT]", r'[.,!?\-()]')
    script = script.replace("[PERSON]", r'(?P<name>[a-z]* [a-z]*\b)')
    script = script.replace("[AWARD]", award_name)
    return re.compile(script)
