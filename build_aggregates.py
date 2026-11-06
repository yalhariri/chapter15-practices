#!/usr/bin/env python3
"""
How the monthly shares in data/ were produced.

*** This script cannot be run with the published materials. *** It needs the
tweet corpus, which was not retained beyond the original project and is not
distributed here (see README). It is included so that the step between the
tweets and the published numbers can be read rather than only described, and so
that the method can be applied to a corpus of your own:

    python build_aggregates.py --pickle /path/to/your/tweets.pkl \
                               --model /path/to/lda_model.obj --out data

The figures and the verification script work from the CSVs in data/ and need
none of this.

Method, as implemented in the original notebooks:
  1. Each tweet is assigned to exactly ONE LDA topic: the one with the highest
     probability in get_document_topics (argmax), not a mixture.
  2. Topic counts are summed per month into the 19 categories of topic_groups.
  3. The monthly share of a category is its count divided by the total count of
     that month EXCLUDING the residual "Others" category.
  4. A tweet belongs to a community if at least one account of that community
     retweeted it. The four sets are built independently and a tweet could in
     principle appear in more than one.
"""
import argparse
import csv
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from topic_groups import (TOPIC_GROUPS, RESIDUAL, COMMUNITIES, COMMUNITY_TAG,
                          months, START_YEAR, START_MONTH, END_YEAR, END_MONTH)


def month_bounds(year, month):
    start = datetime(year, month, 1)
    end = datetime(year + (month == 12), month % 12 + 1, 1)
    return start, end


def counts_by_month(df, lda_model, label=""):
    """{category: {YYYY_M: count}} over the observation window.

    Rows whose bow_c is not a list are skipped and counted; a non-empty skip
    count means the bag-of-words column is incomplete and the result is NOT
    comparable with the published figures.
    """
    out = {k: {m: 0 for m in months()} for k in TOPIC_GROUPS}
    skipped = used = 0
    for key in months():
        y, m = (int(x) for x in key.split("_"))
        start, end = month_bounds(y, m)
        sel = df[(df["tweet_date_time"] >= start) & (df["tweet_date_time"] < end)]
        if len(sel) == 0:
            continue
        bows = [b for b in sel["bow_c"].values if isinstance(b, list)]
        skipped += len(sel) - len(bows)
        used += len(bows)
        per_topic = {}
        for doc_topics in lda_model.get_document_topics(bows):
            if not doc_topics:
                continue
            top = max(doc_topics, key=lambda t: t[1])[0]
            per_topic[top] = per_topic.get(top, 0) + 1
        for cat, topic_ids in TOPIC_GROUPS.items():
            out[cat][key] = sum(per_topic.get(t, 0) for t in topic_ids)
    print(f"    {label}{used:,} tweets used" +
          (f", {skipped:,} SKIPPED - bow_c unusable" if skipped else ""))
    return out


def rebuild_bow(df, model_dir):
    """Recompute bow_c from processed_docs, as the training notebook did."""
    import gensim
    path = os.path.join(model_dir, "dictionary_object")
    print(f"rebuilding bow_c from {path}")
    dictionary = gensim.corpora.dictionary.Dictionary.load(path)
    dictionary.filter_extremes(no_below=5, no_above=0.02, keep_n=1_000_000)
    print(f"  vocabulary after filtering: {len(dictionary):,}")
    df = df.copy()
    df["bow_c"] = [dictionary.doc2bow(d) for d in df["processed_docs"].values]
    return df


def shares(counts):
    """Monthly share per category; the denominator excludes RESIDUAL."""
    cats = [c for c in counts if c != RESIDUAL]
    total = {m: sum(counts[c][m] for c in cats) for m in months()}
    return {c: {m: (counts[c][m] / total[m] if total[m] else 0.0) for m in months()}
            for c in cats}


def write_csv(path, share_table, columns):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL)
        w.writerow(["Year-month"] + columns)
        for m in months():
            w.writerow([m] + [share_table[c][m] for c in columns])
    print(f"  wrote {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pickle", required=True,
                    help="pandas pickle of the corpus (not distributed here)")
    ap.add_argument("--model", required=True,
                    help="saved gensim LDA model (not distributed here)")
    ap.add_argument("--out", default="data")
    ap.add_argument("--rebuild-bow", action="store_true",
                    help="recompute bow_c from processed_docs (slow) when the "
                         "stored column is incomplete")
    args = ap.parse_args()

    pkl, model_path = args.pickle, args.model
    for label, path in (("corpus", pkl), ("model", model_path)):
        if not os.path.exists(path):
            sys.exit(f"{label} not found: {path}\n"
                     "The tweet corpus and the trained model are not part of this\n"
                     "package; see README. Nothing here needs them except this\n"
                     "script, which documents how the files in data/ were made.")

    import gensim
    import pandas as pd

    print(f"loading {pkl}")
    df = pd.read_pickle(pkl)
    print(f"  {len(df):,} tweets in the cleaned corpus")

    in_window = df[(df["tweet_date_time"] >= datetime(START_YEAR, START_MONTH, 1)) &
                   (df["tweet_date_time"] < month_bounds(END_YEAR, END_MONTH)[1])]
    print(f"  {len(in_window):,} tweets inside {START_YEAR}-{START_MONTH:02d}"
          f" .. {END_YEAR}-{END_MONTH:02d}")
    print(f"  earliest tweet: {df['tweet_date_time'].min()}")
    print(f"  latest   tweet: {df['tweet_date_time'].max()}")

    bad = sum(1 for b in df["bow_c"].values if not isinstance(b, list)) \
        if "bow_c" in df.columns else len(df)
    if bad:
        print(f"  WARNING: {bad:,} rows have an unusable bow_c column")
        if not args.rebuild_bow:
            print("  rerun with --rebuild-bow")

    print(f"loading {model_path}")
    lda = gensim.models.LdaMulticore.load(model_path)

    if args.rebuild_bow:
        df = rebuild_bow(df, os.path.dirname(model_path) or ".")

    os.makedirs(args.out, exist_ok=True)

    print("whole corpus:")
    allcounts = counts_by_month(df, lda, "")
    allshares = shares(allcounts)
    write_csv(os.path.join(args.out, "Topics_Discussed_by_All.csv"),
              allshares, sorted(allshares))

    for community in COMMUNITIES:
        tag = COMMUNITY_TAG[community]
        sub = df[[tag in r for r in df["retweeters"]]]
        print(f"{community}: {len(sub):,} tweets (whole corpus, all dates)")
        tbl = shares(counts_by_month(sub, lda, ""))
        write_csv(os.path.join(args.out, f"Topics_Discussed_by_{community}.csv"),
                  tbl, sorted(tbl))

    print("\nDone. Now run verify_chapter_numbers.py and compare its output "
          "with the numbers printed in the chapter.")


if __name__ == "__main__":
    main()
