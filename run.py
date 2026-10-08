#!/usr/bin/env python3
"""CLI: analyze the sales dataset and write a Markdown report.

Usage:
    python3 run.py                          # analyze datasets/orders.csv
    python3 run.py --regen                   # regenerate the dataset first
    python3 run.py --out report.md
"""

import argparse
import os
import sys

from insights.analyze import analyze, load_orders
from insights.data_gen import generate, write_csv
from insights.report import render_console, render_markdown

BASE = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.join(BASE, "datasets", "orders.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description="Ecommerce sales insights.")
    parser.add_argument("--regen", action="store_true",
                        help="regenerate the synthetic dataset")
    parser.add_argument("--dataset", default=DATASET)
    parser.add_argument("--out", default="report.md")
    args = parser.parse_args()

    if args.regen or not os.path.exists(args.dataset):
        os.makedirs(os.path.dirname(args.dataset), exist_ok=True)
        write_csv(generate(), args.dataset)
        print(f"dataset written to {args.dataset}")

    orders = load_orders(args.dataset)
    m = analyze(orders)
    print(render_console(m))
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(render_markdown(m))
    print(f"report written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
