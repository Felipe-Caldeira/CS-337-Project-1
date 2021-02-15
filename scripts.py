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
    (r"wins (?P<award>best[a-z ]+?) at ", 11),
    (r"wins (?P<award>best[a-z ]+?) (for|globe[s*]|golden|and) ", 10),
    (r"wins (?P<award>best [a-z \/\-]*?)(for |globe[s*] |golden |at |and |\.|$)", 8), # CHECK IF GOOD 
    (r"(?P<award>best [a-z ]*?)([:-])", 8),
    (r"(?P<award>best [a-z,\/ \(\)\-]+?) ?(:|-|—|goes to|from|to|!) ", 6),
    (r"(?P<award>best (?!thing)[a-z,\/ \(\)\-]+?) (is|but)", 4),
    (r"(?P<award>best [a-z,/ \(\)\-]+(musical|comedy|drama))", 5),
    (r"(receiv.* the|receives|present.* the) (?P<award>(?!golden)[a-z .]{1,20} award)", 5),
    (r"premio (?P<award>[a-z \.]*?) (por|a)", 4),
    (r"(?P<award>(?!golden)([a-z.]{2,7} ){3}award)", 3),
    (r"(?P<award>best[a-z ]+?) nominee", 4)
]

# Winners
WINNERS = [
    (r"*[NAME] wins", 8),
    (r"*[NAME] won", 8),
    (r"*[NAME] receives (the )?", 8),
    (r"[AWARD]: [NAME] for", 8),
    (r"[AWARD] goes to( |\.*)[NAME]", 8),
    (r"[AWARD] goes to( |\.*)[NAME] for", 6),
    (r"[AWARD](: |-| - )[NAME]([PUNCT]| -)", 4),
    (r"goes to( |\.*)[NAME]([PUNCT]|$| in)", 2),
    (r"winner [PERSON]", 6),
    (r"congra.* to [PERSON]", 3),
    (r"[PERSON] accept", 3)
]

ALT_WINNER = [
    (r"(to | - |for |: )\"(?P<name>[a-z]*)\"", 9),
    (r"(picture|song):(?P<name>[a-z ]*) by", 8),
    (r"(\"|\()(?P<name>[a-z ]*)(\"|\))", 5),
    (r"best.* goes to [a-z ]* for (?P<name>[a-z ]*)", 5)
]

# Nominees
NOMINEES = [
    (r"wanted (?P<name>[a-z ]*) to win", 7),
    (r"\"(?P<name>[a-z ]*)\".* (lost|not .*(win|won))", 4),
    (r"^(?P<name>[a-z ]*) (was|is) nominated", 4),
    (r"(but|and) (?P<name>[a-z ]*) should have won", 4),
    (r"(but|beat|and) (?P<name>[a-z ]*) for", 4),
    (r"(and|but) (?P<name>[a-z ]*) didn't win", 6),
    (r"i hope (?P<name>[a-z ]*) win", 5),
    (r"[AWARD] nominee [PERSON]", 5),
    (r"[AWARD] nominee (?P<name>[a-z ]*?) ?(is|should|[.,!])", 5),
    (r"nominee (?P<name>[a-z ]*?) ?(is|should|[.,!])", 3)
]

# Presenters
PRESENTERS = [
    (r"(?P<name>[a-z ]+?\b) and (?P<name2>[a-z ]+?\b) present", 8),
    (r"(?P<name>[a-z ]+?\b) and (?P<name2>[a-z ]+?\b) introduce", 7),
    (r"(?P<name>[a-z]+ [a-z]+?\b) present", 5),
    (r"(?P<name>[a-z]+ [a-z]+?\b) introduce", 6),
    (r"present.*goes to (?P<name>[a-z]+ [a-z]+?\b) and (?P<name2>[a-z]+ [a-z]+?\b)", 4),
    (r"(^|p)(?P<name>[a-z, ]*)\.? present", 4),
    (r"(?P<name>[a-z]* [a-z]*) (and|&amp;) (?P<name2>[a-z]* [a-z]*) (present|award).*to", 5)
]

# Hosts
HOSTS = [
    (r"(?P<name>[a-z]* [a-z]*\b) and (?P<name2>[a-z]* [a-z]*\b) (host|are)", 10),
    (r"host (?P<name>[a-z]* [a-z]*\b)", 7),
    (r"(?P<name>[a-z]* [a-z]*\b) host", 4),
    (r"(?P<name>[a-z]* [a-z]*\b) as host", 4)
]

# Best Dressed
BEST_DRESSED = [
    (r"best dressed(: |\.{3,} |was )[PERSON]", 8),
    (r"best dressed.*?: [PERSON]", 10),
    (r"[PERSON] is my (pick|best dressed|fav)", 7),
    (r"[PERSON](,| and) ", 5)
]

# Converts scripts to actual regex patterns
def scriptToRegex(script, award_name):
    script = script.replace("*[NAME]", r'(^|[.,!:] )(?P<name>[\w. ]+?\b)')
    script = script.replace("[NAME]", r'(?P<name>[\w. ]+?\b)')
    script = script.replace("[PUNCT]", r'[.,!?\-()#]')
    script = script.replace("[PERSON]", r'(?P<name>[a-z]* [a-z]*\b)')
    script = script.replace("[AWARD]", award_name)
    return re.compile(script)


