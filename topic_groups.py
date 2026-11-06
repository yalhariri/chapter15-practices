"""
Mapping from the 50 LDA topics to the thematic categories used in Chapter 15.

Transcribed verbatim from the `topics_dict` cell of the analysis notebooks
(Tweets_Analysis_All_(Farasa).ipynb and the four per-community notebooks).
Do not edit without re-running build_aggregates.py: every number in the
chapter depends on this mapping.
"""

# 19 labels over the 50 topics of lda_gensim_model_50.obj.
# "Others" is a residual bucket and is EXCLUDED from every denominator.
TOPIC_GROUPS = {
    "Arguing and Discussing Metaphysics": [26, 38],
    "Attitudes": [21, 22, 23, 39],
    "Business": [37],
    "Events Relevant to Time and History": [10],
    "Football Clubs": [4],
    "Freedom": [18],
    "Gov., Nation and Socio-Political in Middle East": [1, 9, 36],
    "Health And Well-being": [7, 31],
    "Marriage and Women": [11],
    "Multimedia": [40],
    "News and Events": [45],
    "Others": [8, 12, 25, 27, 30, 32, 33, 41, 44, 46, 47],
    "Relationship and Interactions": [3, 17, 34],
    "Political and Religious Confrontations and Violence": [13, 29, 42, 48],
    "Religious Legislation": [2],
    "Suffering": [15, 49],
    "Theism, Belief and Disbelief": [14, 16, 19, 20, 24, 35],
    "Thoughts and Logic": [6, 28, 43],
    "Universe, Creator and Existence": [0, 5],
}

RESIDUAL = "Others"

# The nine categories plotted in Figures 15.3 and 15.4.
# Eight of them reach the retention threshold in ALL four communities.
# "Football Clubs" does not: it reaches it among theists and rationalists only,
# and was retained because that contrast is itself a finding (see README).
SELECTED = [
    "Attitudes",
    "Football Clubs",
    "Gov., Nation and Socio-Political in Middle East",
    "Relationship and Interactions",
    "Political and Religious Confrontations and Violence",
    "Suffering",
    "Theism, Belief and Disbelief",
    "Thoughts and Logic",
    "Universe, Creator and Existence",
]

# Retention threshold: sum of a category's 42 monthly shares, within a community.
# 1.25 over 42 months is a mean monthly share of about 3.0%.
THRESHOLD = 1.25

# Colours used in Figure 15.4, transcribed from the notebooks.
TOPIC_COLORS = {
    "Arguing and Discussing Metaphysics": "#A44B21",
    "Attitudes": "#CC79A7",
    "Events Relevant to Time and History": "#D55E00",
    "Football Clubs": "#4F2BFD",
    "Gov., Nation and Socio-Political in Middle East": "#0072B2",
    "Health And Well-being": "#9673C4",
    "Marriage and Women": "#78B389",
    "Political and Religious Confrontations and Violence": "#009E73",
    "Relationship and Interactions": "#E78540",
    "Suffering": "#F70F64",
    "Theism, Belief and Disbelief": "#22D68F",
    "Thoughts and Logic": "#56B4E9",
    "Universe, Creator and Existence": "#F0E442",
}

COMMUNITIES = ["Atheists", "Theists", "Rationalists", "Tanweeris"]

# The label stored in the `retweeters` list for each community.
COMMUNITY_TAG = {
    "Atheists": "Atheist",
    "Theists": "Theist",
    "Rationalists": "Rationalist",
    "Tanweeris": "Tanweeri",
}

# Observation window: 42 months.
START_YEAR, START_MONTH = 2018, 1
END_YEAR, END_MONTH = 2021, 6


def months():
    """The 42 'YYYY_M' keys, in order, exactly as the notebooks wrote them."""
    out = []
    y, m = START_YEAR, START_MONTH
    while (y, m) <= (END_YEAR, END_MONTH):
        out.append(f"{y}_{m}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out
