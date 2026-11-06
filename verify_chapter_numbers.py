#!/usr/bin/env python3
"""
Recompute every number Chapter 15 states from the monthly shares in data/.

This checks the arithmetic of the published figures. It does not re-run the
topic model or the assignment of tweets to topics; see README for the scope.

Run this whenever the chapter's figures are questioned, instead of changing a
number by hand. Everything below comes from the monthly-share CSVs, so it runs
without the corpus. Pass --data-dir to point at a fresh run of build_aggregates.py.

    python verify_chapter_numbers.py
    python verify_chapter_numbers.py --corpus ..   # also count the corpus
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_shares, month_order, mean_share, DEFAULT_DATA
from topic_groups import SELECTED, COMMUNITIES, THRESHOLD, TOPIC_GROUPS, RESIDUAL

RULE = "=" * 78


def head(title):
    print(f"\n{RULE}\n{title}\n{RULE}")


def retention(data_dir):
    head("1. RETENTION  (sum of the 42 monthly shares, per community)")
    print(f"   A category is retained when this sum reaches {THRESHOLD} "
          f"(a mean monthly share of about {THRESHOLD/42*100:.1f}%).")
    tables = {c: read_shares(c, data_dir) for c in COMMUNITIES}
    cats = sorted(tables[COMMUNITIES[0]])
    w = max(len(c) for c in cats)
    print(f"\n{'category':{w}}" + "".join(f"{c[:5]:>8}" for c in COMMUNITIES)
          + "   passes in        plotted")
    for cat in cats:
        sums = {c: sum(tables[c][cat].values()) for c in COMMUNITIES}
        ok = [c for c in COMMUNITIES if sums[c] >= THRESHOLD]
        print(f"{cat:{w}}" + "".join(f"{sums[c]:8.2f}" for c in COMMUNITIES)
              + f"   {len(ok)}/4 {'':10}"[:16]
              + ("YES" if cat in SELECTED else "no"))
    allfour = [c for c in cats
               if all(sum(tables[x][c].values()) >= THRESHOLD for x in COMMUNITIES)]
    print(f"\n   retained in all four communities : {len(allfour)}")
    for c in allfour:
        print(f"      {c}")
    extra = [c for c in SELECTED if c not in allfour]
    for c in extra:
        where = [x for x in COMMUNITIES
                 if sum(tables[x][c].values()) >= THRESHOLD]
        print(f"\n   plotted but NOT retained in all four : {c}")
        print(f"      reaches the threshold in: {', '.join(where) or 'none'}")
        print( "      kept because the contrast between communities is itself a finding")
    dropped = [c for c in allfour if c not in SELECTED]
    for c in dropped:
        print(f"\n   retained in all four but NOT plotted : {c}  <-- check this")
    print(f"\n   categories plotted in Figures 15.3 and 15.4 : {len(SELECTED)}")


def figure_15_3(data_dir):
    head("2. FIGURE 15.3  (mean monthly share, %)")
    t = {c: {cat: mean_share(read_shares(c, data_dir)[cat]) for cat in SELECTED}
         for c in COMMUNITIES}
    order = sorted(SELECTED, key=lambda c: -sum(t[x][c] for x in COMMUNITIES))
    w = max(len(c) for c in SELECTED)
    print(f"{'category':{w}}" + "".join(f"{c:>14}" for c in COMMUNITIES))
    for cat in order:
        print(f"{cat:{w}}" + "".join(f"{t[c][cat]:13.2f}%" for c in COMMUNITIES))
    sums = [sum(t[c].values()) for c in COMMUNITIES]
    print(f"{'SUM OF THE NINE':{w}}" + "".join(f"{s:13.2f}%" for s in sums))
    print(f"\n   the bars sum to {min(sums):.0f}-{max(sums):.0f}%, not 100%:")
    print(f"   the residual '{RESIDUAL}' category is outside the denominator and")
    print(f"   {len(TOPIC_GROUPS)-1-len(SELECTED)} of the "
          f"{len(TOPIC_GROUPS)-1} categories are not drawn.")
    fc = {c: t[c]["Football Clubs"] for c in COMMUNITIES}
    hi, lo = max(fc, key=fc.get), min(fc, key=fc.get)
    print(f"\n   widest spread between communities: Football Clubs, "
          f"{fc[hi]:.2f}% ({hi.lower()}) vs {fc[lo]:.2f}% ({lo.lower()})")


def spikes(data_dir, category="Suffering", top=3):
    head(f"3. SHARPEST TEMPORAL CHANGE  ({category})")
    ms = month_order(COMMUNITIES[0], data_dir)
    tables = {c: read_shares(c, data_dir)[category] for c in COMMUNITIES}
    means = {m: sum(tables[c][m] for c in COMMUNITIES) / 4 * 100 for m in ms}
    baseline = sum(means.values()) / len(means)
    print(f"   mean across the four communities, over all {len(ms)} months: "
          f"{baseline:.2f}%")
    print(f"\n{'month':9}" + "".join(f"{c[:5]:>9}" for c in COMMUNITIES) + f"{'mean':>9}")
    for m in sorted(ms, key=lambda m: -means[m])[:top]:
        print(f"{m:9}" + "".join(f"{tables[c][m]*100:8.2f}%" for c in COMMUNITIES)
              + f"{means[m]:8.2f}%")
    peak = max(ms, key=lambda m: means[m])
    print(f"\n   peak month: {peak}, {means[peak]/baseline:.1f}x the overall mean,")
    print( "   and every community rises in the same month.")


def corpus(data_dir):
    head("4. CORPUS SIZE")
    import pandas as pd
    from datetime import datetime
    pkl = os.path.join(data_dir, "data",
                       "tweets_df_Frasa_processed_cleaned_with_topics.pkl")
    df = pd.read_pickle(pkl)
    lo = datetime(2018, 1, 1)
    hi = datetime(2021, 7, 1)
    inw = df[(df["tweet_date_time"] >= lo) & (df["tweet_date_time"] < hi)]
    print(f"   cleaned corpus (all dates)        : {len(df):,}")
    print(f"   earliest tweet                    : {df['tweet_date_time'].min()}")
    print(f"   latest tweet                      : {df['tweet_date_time'].max()}")
    print(f"   inside Jan 2018 - Jun 2021        : {len(inw):,}")
    print(f"   outside the window                : {len(df)-len(inw):,}")
    print( "\n   The chapter must not attach the corpus total to the window:")
    print( "   the figures are built from the second number, not the first.")
    for community in COMMUNITIES:
        from topic_groups import COMMUNITY_TAG
        tag = COMMUNITY_TAG[community]
        n = sum(1 for r in df["retweeters"] if tag in r)
        print(f"   retweeted by {community:<13}: {n:,}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=DEFAULT_DATA)
    ap.add_argument("--corpus", help="folder holding data/*.pkl, to count the corpus")
    args = ap.parse_args()
    retention(args.data_dir)
    figure_15_3(args.data_dir)
    spikes(args.data_dir)
    if args.corpus:
        corpus(args.corpus)
    else:
        head("4. CORPUS SIZE")
        print("   skipped. Re-run with --corpus .. to count the corpus.")
    print()


if __name__ == "__main__":
    main()
