#!/usr/bin/env python3
"""
Redraw Figure 15.3 from the monthly shares in data/.

Each bar is the mean of a category's 42 monthly shares within one community.
The denominator of every monthly share excludes the residual "Others"
category, and only nine of the eighteen categories are drawn, so the bars of
a community sum to roughly 80% rather than 100%.

    python make_figure_15_3.py              # writes figure_15_3.png
    python make_figure_15_3.py --table      # print the numbers only
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_shares, mean_share, DEFAULT_DATA
from topic_groups import SELECTED, COMMUNITIES


def table(data_dir):
    return {c: {cat: mean_share(read_shares(c, data_dir)[cat])
                for cat in SELECTED}
            for c in COMMUNITIES}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=DEFAULT_DATA)
    ap.add_argument("--out", default="figure_15_3.png")
    ap.add_argument("--table", action="store_true")
    args = ap.parse_args()

    t = table(args.data_dir)
    order = sorted(SELECTED, key=lambda c: -sum(t[x][c] for x in COMMUNITIES))

    width = max(len(c) for c in SELECTED)
    print(f"{'category':{width}}" + "".join(f"{c:>14}" for c in COMMUNITIES))
    for cat in order:
        print(f"{cat:{width}}" + "".join(f"{t[c][cat]:13.2f}%" for c in COMMUNITIES))
    print(f"{'SUM':{width}}" +
          "".join(f"{sum(t[c].values()):13.2f}%" for c in COMMUNITIES))
    if args.table:
        return

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(13, 6))
    n = len(COMMUNITIES)
    w = 0.8 / n
    xs = range(len(order))
    for i, community in enumerate(COMMUNITIES):
        ax.bar([x + i * w for x in xs],
               [t[community][cat] for cat in order],
               width=w, label=community)
    ax.set_xticks([x + w * (n - 1) / 2 for x in xs])
    ax.set_xticklabels([str(i + 1) for i in xs])
    ax.set_ylabel("Mean monthly share of topic-assigned tweets (%)")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    key = "\n".join(f"{i+1} - {cat}" for i, cat in enumerate(order))
    ax.text(1.005, 0.98, key, transform=ax.transAxes, va="top", fontsize=9)
    fig.tight_layout()
    fig.savefig(args.out, dpi=200, bbox_inches="tight")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
