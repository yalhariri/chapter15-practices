# Chapter 15 — companion materials

Companion code and data for **"Computational Methods for Studying Online
Polarization, an Arabic Social Media Case Study"**, Chapter 15 of *Recent
Advances in Arabic Digital Humanities* (John Benjamins).

Youssef Al Hariri, Walid Magdy, Maria Wolters.

## Scope

There are two ways in, and they answer different questions.

**Check the chapter.** The monthly category shares behind Figures 15.3 and 15.4
ship in `data/`, one CSV per community. Everything downstream of them is
recomputed at run time — the 36 bars of Figure 15.3, the retention table, the bar
sums, the peak month. No number is stored and read back.

**Apply the method.** `chapter15_end_to_end.ipynb` runs the whole pipeline on a
folder of tweets: language identification, Farasa stemming, vocabulary filtering,
LDA, the grouping of topics into categories, monthly shares, and both figures.

What neither does is reproduce the published study, for two reasons that are
worth stating plainly. The corpus is not here and cannot be — it was not retained
beyond the original project (chapter §15.7), and what ships instead is the
derived aggregate, carrying no tweet text, no account names and no identifiers.
And the model behind the chapter was trained without a random seed, so it cannot
be retrained to the same result; the notebook loads the saved model when it
reproduces the chapter, and sets a seed of its own when it trains on your data,
so that *your* run is repeatable even though the original is not.

## Quick start

```bash
pip install -r requirements.txt
python verify_chapter_numbers.py    # recompute every figure the chapter states
python make_figure_15_3.py          # writes figure_15_3.png
python make_figure_15_4.py          # writes figure_15_4.png
jupyter notebook chapter15_walkthrough.ipynb
```

`verify_expected_output.txt` is what that first command printed on the authors'
machine. You should see the same thing.

`chapter15_walkthrough.ipynb` also runs in Google Colab: upload it with
`topic_groups.py` and the five CSVs from `data/`, and its first cell does the
rest. Readers with no Python installed can work through the chapter that way.

`chapter15_end_to_end.ipynb` needs more: your own tweets, Java for Farasa, and
the fastText language-identification model. Its second cell reports what is
present and what each missing piece costs you.

## What is here

Independent entry points, plus two shared modules. Nothing has to be run in order.

| file | what it does | needs a corpus |
|---|---|---|
| `verify_chapter_numbers.py` | recomputes every figure the chapter states, from the shares in `data/` | no |
| `make_figure_15_3.py` | redraws Figure 15.3 from the shares in `data/` | no |
| `make_figure_15_4.py` | redraws Figure 15.4 from the shares in `data/` | no |
| `chapter15_walkthrough.ipynb` | the same two figures with the reasoning, and the exercises | no |
| `chapter15_end_to_end.ipynb` | the whole pipeline, raw tweets to figures | yes |
| `topic_groups.py` | the 50 topics to 18 categories mapping, the residual, and the retained nine | — |
| `common.py` | reads the CSVs | — |
| `data/` | the monthly shares: one CSV per community, plus one for all four combined | — |

## The method in one page

**Topics.** A 50-topic LDA model (gensim `LdaMulticore`, 20 passes) over the
Farasa-stemmed corpus. The vocabulary drops any word occurring in fewer than 5
tweets or in more than 2% of them.

**One topic per tweet.** LDA gives each tweet a mixture, but the analysis keeps
only the highest-probability topic. This is a simplification, and it is the
reason the counts can be added up at all. A tweet that genuinely spans two topics
is counted once.

**Categories.** The 50 topics were read and grouped by hand into 18 thematic
categories plus a residual `Others` covering 11 topics that did not form a
coherent theme. The mapping is in `topic_groups.py`. It is an interpretive
decision, not an output of the algorithm; a different reader could group them
differently, and `Suffering` is the clearest case — it merges one topic about
illness, treatment and the coronavirus with one about anger and misfortune.

**Communities.** A tweet belongs to a community if at least one account of that
community retweeted it. Membership therefore records what a community amplified,
not what its members wrote. The four sets were built independently, so a tweet
several communities retweeted is counted in each, and together they hold 670,275
of the 1,107,728 tweets in the window.

**Monthly share.** For each community and month, a category's share is its count
divided by that month's total *excluding* `Others`. Shares, not counts, are what
the figures draw: tweet volume rises over the window, so counts would show that
rise rather than shifts in attention.

**Which categories are shown.** A category is retained when the sum of its 42
monthly shares reaches 1.25 within a community — a mean monthly share of about
3%. Eight categories clear that bar in all four communities. `Football Clubs`
clears it in two, among theists and rationalists, and is shown anyway because it
separates the communities more sharply than any category that clears it
everywhere. It was therefore selected for its contrast, which should not be read
as typical. `verify_chapter_numbers.py` prints the table, so the rule can be
checked rather than taken on trust.

**Window.** 42 months, January 2018 to June 2021. The corpus extends earlier; the
figures do not.

## Known limits

- **One label per tweet** discards the mixture LDA produces.
- **The grouping is interpretive**, made once, by hand. This code makes the
  mapping inspectable; it does not make it right.
- **Communities overlap by construction**, since the sets are built independently
  from the retweeters field, and about 40% of the tweets in the window belong to
  none of the four.
- **The retention rule has a declared exception**, printed by the verify script.
- **Co-occurrence is not cause.** A spike aligning with a public event is a
  starting point for reading tweets, nothing more.
- **The model behind the chapter cannot be retrained to the same result.**

## Citing

Please cite the chapter. If you use the aggregates, please also link to this
repository.

## License

Code: MIT. Data files in `data/`: CC BY 4.0.
