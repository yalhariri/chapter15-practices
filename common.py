"""Shared helpers for reading the monthly-share CSVs."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(HERE, "data")


def read_shares(community, data_dir=DEFAULT_DATA):
    """{category: {YYYY_M: share}} for one community, or 'All'."""
    path = os.path.join(data_dir, f"Topics_Discussed_by_{community}.csv")
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    cats = [c for c in rows[0] if c != "Year-month"]
    return {c: {r["Year-month"]: float(r[c]) for r in rows} for c in cats}


def month_order(community, data_dir=DEFAULT_DATA):
    path = os.path.join(data_dir, f"Topics_Discussed_by_{community}.csv")
    with open(path, encoding="utf-8") as fh:
        return [r["Year-month"] for r in csv.DictReader(fh)]


def mean_share(series):
    """Mean of the monthly shares, as a percentage."""
    return sum(series.values()) / len(series) * 100
