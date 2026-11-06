#!/usr/bin/env python3
"""
Redraw Figure 15.4 from the monthly shares in data/.

One panel per community. Each row is a category, each marker is one month,
and MARKER SIZE IS THE MONTHLY SHARE, not a count of tweets or of accounts.
The axis is labelled by quarter, so each quarter label spans three markers.

    python make_figure_15_4.py          # writes figure_15_4.png

Pass --plotly to reproduce the original interactive HTML instead.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_shares, month_order, DEFAULT_DATA
from topic_groups import SELECTED, TOPIC_COLORS, COMMUNITIES

PANEL = ["(A) Atheists", "(B) Theists", "(C) Rationalists", "(D) Tanweeris"]


def quarter_labels(ms):
    """Label every third month with its quarter, blank elsewhere."""
    out = []
    for m in ms:
        y, mo = (int(x) for x in m.split("_"))
        out.append(f"{y} Q{(mo - 1) // 3 + 1}" if mo % 3 == 2 else "")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=DEFAULT_DATA)
    ap.add_argument("--out", default="figure_15_4.png")
    ap.add_argument("--plotly", action="store_true")
    args = ap.parse_args()

    ms = month_order(COMMUNITIES[0], args.data_dir)
    data = {c: read_shares(c, args.data_dir) for c in COMMUNITIES}

    if args.plotly:
        import plotly.graph_objects as go
        for community in COMMUNITIES:
            fig = go.Figure()
            for cat in SELECTED:
                fig.add_trace(go.Scatter(
                    x=ms, y=[cat] * len(ms), name=cat, text=cat,
                    mode="markers",
                    marker=dict(size=[data[community][cat][m] for m in ms],
                                sizemode="diameter", sizeref=0.005,
                                color=TOPIC_COLORS[cat], line_width=2)))
            fig.update_layout(showlegend=False,
                              xaxis=dict(tickmode="array", tickvals=ms,
                                         ticktext=quarter_labels(ms)))
            path = f"figure_15_4_{community}.html"
            fig.write_html(path)
            print(f"wrote {path}")
        return

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(16, 9), sharex=True, sharey=True)
    for ax, community, title in zip(axes.ravel(), COMMUNITIES, PANEL):
        for row, cat in enumerate(SELECTED):
            vals = [data[community][cat][m] for m in ms]
            ax.scatter(range(len(ms)), [len(SELECTED) - row] * len(ms),
                       s=[v * 4000 for v in vals],
                       color=TOPIC_COLORS[cat], alpha=0.85,
                       edgecolors="white", linewidths=0.5)
        ax.set_title(title, fontsize=11)
        ax.set_yticks(range(1, len(SELECTED) + 1))
        ax.set_yticklabels([])
        ax.set_xticks(range(len(ms)))
        ax.set_xticklabels(quarter_labels(ms), rotation=90, fontsize=7)
        ax.spines[["top", "right", "left"]].set_visible(False)
    handles = [plt.Line2D([], [], marker="o", linestyle="", color=TOPIC_COLORS[c],
                          label=c) for c in SELECTED]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               fontsize=9)
    fig.suptitle("Monthly prevalence of the nine retained topic categories; "
                 "marker size is the monthly share", fontsize=11)
    fig.tight_layout(rect=(0, 0.14, 1, 0.97))
    fig.savefig(args.out, dpi=200)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
