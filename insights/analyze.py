"""Metrics computation over the orders dataset."""

import csv
from collections import Counter, defaultdict


def load_orders(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["quantity"] = int(r["quantity"])
        r["unit_price"] = float(r["unit_price"])
        r["revenue"] = r["quantity"] * r["unit_price"]
        r["month"] = r["order_date"][:7]
    return rows


def analyze(orders):
    revenue = sum(o["revenue"] for o in orders)
    n_orders = len(orders)
    customers = Counter(o["customer_id"] for o in orders)

    monthly = defaultdict(float)
    monthly_orders = Counter()
    for o in orders:
        monthly[o["month"]] += o["revenue"]
        monthly_orders[o["month"]] += 1
    months = sorted(monthly)
    mom = {}
    for i in range(1, len(months)):
        prev = monthly[months[i - 1]]
        mom[months[i]] = (monthly[months[i]] - prev) / prev if prev else 0.0

    cat_rev = defaultdict(float)
    for o in orders:
        cat_rev[o["category"]] += o["revenue"]

    prod_rev = defaultdict(float)
    prod_qty = Counter()
    for o in orders:
        prod_rev[o["product_name"]] += o["revenue"]
        prod_qty[o["product_name"]] += o["quantity"]

    region_rev = defaultdict(float)
    for o in orders:
        region_rev[o["region"]] += o["revenue"]

    repeaters = sum(1 for c, n in customers.items() if n > 1)

    insights = []
    top_cat, top_cat_rev = max(cat_rev.items(), key=lambda kv: kv[1])
    insights.append(
        f"{top_cat} 是第一大品类，贡献 {top_cat_rev / revenue:.1%} 的 GMV。")
    best_month = max(monthly, key=monthly.get)
    insights.append(
        f"{best_month} 为 GMV 最高月份（{monthly[best_month]:,.0f} 元），"
        f"较 {months[0]} 增长 {(monthly[best_month] - monthly[months[0]]) / monthly[months[0]]:+.1%}。")
    insights.append(
        f"复购用户占比 {repeaters / len(customers):.1%}（{repeaters:,} / {len(customers):,}），"
        "复购是增长杠杆。" if repeaters / len(customers) < 0.35
        else f"复购用户占比 {repeaters / len(customers):.1%}，用户粘性健康。")
    top_region, top_region_rev = max(region_rev.items(), key=lambda kv: kv[1])
    insights.append(f"{top_region} 贡献 {top_region_rev / revenue:.1%} 的 GMV，区域集中度较高。" if top_region_rev / revenue > 0.35
                    else f"区域分布均衡，{top_region} 以 {top_region_rev / revenue:.1%} 领先。")

    return {
        "revenue": revenue,
        "n_orders": n_orders,
        "aov": revenue / n_orders if n_orders else 0,
        "n_customers": len(customers),
        "repeat_rate": repeaters / len(customers) if customers else 0,
        "monthly": dict(sorted(monthly.items())),
        "mom": mom,
        "category_mix": dict(sorted(cat_rev.items(), key=lambda kv: -kv[1])),
        "top_products": sorted(prod_rev.items(), key=lambda kv: -kv[1])[:8],
        "region_mix": dict(sorted(region_rev.items(), key=lambda kv: -kv[1])),
        "insights": insights,
    }
