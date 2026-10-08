"""Deterministic synthetic ecommerce dataset generator.

The dataset is SYNTHETIC (seeded RNG) and ships with the repo so the demo
runs offline without downloading anything. It is realistic in shape --
seasonality, category mix, repeat buyers -- but every number is generated.
See README for details.
"""

import csv
import random

SEED = 20261007

CATEGORIES = {
    "Electronics": [("无线蓝牙耳机", 299), ("智能手表", 899), ("便携充电宝", 129), ("机械键盘", 459)],
    "Apparel": [("纯棉T恤", 89), ("牛仔裤", 259), ("运动外套", 399)],
    "Home": [("香薰加湿器", 159), ("收纳置物架", 199), ("LED台灯", 139)],
    "Beauty": [("保湿面霜", 189), ("防晒乳", 129)],
    "Sports": [("瑜伽垫", 149), ("哑铃套装", 329)],
}
CATEGORY_WEIGHTS = [0.34, 0.24, 0.18, 0.12, 0.12]
# monthly seasonality multipliers, 2026-01 .. 2026-09
# (June spike = mid-year sale, September lift = back-to-school apparel)
MONTH_WEIGHTS = [0.85, 0.90, 1.00, 0.95, 1.05, 1.30, 1.00, 1.05, 1.18]
REGIONS = ["华东", "华南", "华北", "西部"]
REGION_WEIGHTS = [0.38, 0.27, 0.20, 0.15]


def _weighted_choice(rng, items, weights):
    x = rng.random() * sum(weights)
    acc = 0.0
    for item, w in zip(items, weights):
        acc += w
        if x <= acc:
            return item
    return items[-1]


def generate(n_orders=3600, seed=SEED):
    """Generate a list of order dicts."""
    rng = random.Random(seed)
    customers = [f"C{i:05d}" for i in range(2000)]
    # 30% of customers are repeat buyers: pre-assign extra order slots
    repeaters = set(rng.sample(customers, int(len(customers) * 0.30)))
    orders = []
    for i in range(n_orders):
        month = _weighted_choice(rng, list(range(1, 10)), MONTH_WEIGHTS)
        day = rng.randint(1, 28)
        cust = rng.choice(customers)
        if cust in repeaters and rng.random() < 0.25:
            cust = rng.choice(sorted(repeaters))  # funnel extra orders to repeaters
        cat = _weighted_choice(rng, list(CATEGORIES), CATEGORY_WEIGHTS)
        # apparel gets a back-to-school bump in September
        if month == 9 and rng.random() < 0.25:
            cat = "Apparel"
        product, price = rng.choice(CATEGORIES[cat])
        qty = rng.choices([1, 2, 3], weights=[0.72, 0.21, 0.07])[0]
        region = _weighted_choice(rng, REGIONS, REGION_WEIGHTS)
        orders.append({
            "order_id": f"O{i:06d}",
            "order_date": f"2026-{month:02d}-{day:02d}",
            "customer_id": cust,
            "region": region,
            "category": cat,
            "product_name": product,
            "quantity": qty,
            "unit_price": price,
        })
    orders.sort(key=lambda o: o["order_date"])
    return orders


def write_csv(orders, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["order_id", "order_date", "customer_id",
                                          "region", "category", "product_name",
                                          "quantity", "unit_price"])
        w.writeheader()
        w.writerows(orders)


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "datasets/orders.csv"
    write_csv(generate(), out)
    print(f"wrote {out}")
