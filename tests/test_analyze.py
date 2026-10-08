"""Unit tests for sales-insights. Run: python3 -m unittest discover -s tests"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from insights.analyze import analyze
from insights.data_gen import generate


def tiny_orders():
    return [
        {"order_id": "O1", "order_date": "2026-01-05", "customer_id": "A",
         "region": "华东", "category": "Electronics", "product_name": "耳机",
         "quantity": 1, "unit_price": 300, "revenue": 300, "month": "2026-01"},
        {"order_id": "O2", "order_date": "2026-01-06", "customer_id": "B",
         "region": "华南", "category": "Apparel", "product_name": "T恤",
         "quantity": 2, "unit_price": 100, "revenue": 200, "month": "2026-01"},
        {"order_id": "O3", "order_date": "2026-02-01", "customer_id": "A",
         "region": "华东", "category": "Electronics", "product_name": "耳机",
         "quantity": 1, "unit_price": 300, "revenue": 300, "month": "2026-02"},
        {"order_id": "O4", "order_date": "2026-02-02", "customer_id": "C",
         "region": "华北", "category": "Apparel", "product_name": "T恤",
         "quantity": 1, "unit_price": 100, "revenue": 100, "month": "2026-02"},
    ]


class TestAnalyze(unittest.TestCase):
    def test_totals(self):
        m = analyze(tiny_orders())
        self.assertEqual(m["revenue"], 900)
        self.assertEqual(m["n_orders"], 4)
        self.assertAlmostEqual(m["aov"], 225.0)
        self.assertEqual(m["n_customers"], 3)

    def test_repeat_rate(self):
        m = analyze(tiny_orders())
        self.assertAlmostEqual(m["repeat_rate"], 1 / 3)

    def test_monthly_and_mom(self):
        m = analyze(tiny_orders())
        self.assertEqual(m["monthly"], {"2026-01": 500, "2026-02": 400})
        self.assertAlmostEqual(m["mom"]["2026-02"], -0.2)

    def test_category_and_top_products(self):
        m = analyze(tiny_orders())
        self.assertEqual(m["category_mix"]["Electronics"], 600)
        self.assertEqual(m["top_products"][0], ("耳机", 600))

    def test_insights_present(self):
        m = analyze(tiny_orders())
        self.assertGreaterEqual(len(m["insights"]), 3)
        self.assertTrue(any("Electronics" in s for s in m["insights"]))


class TestDataGen(unittest.TestCase):
    def test_deterministic(self):
        a = generate(n_orders=50, seed=1)
        b = generate(n_orders=50, seed=1)
        self.assertEqual(a, b)

    def test_shape(self):
        orders = generate(n_orders=200, seed=7)
        self.assertEqual(len(orders), 200)
        o = orders[0]
        self.assertEqual(set(o), {"order_id", "order_date", "customer_id",
                                  "region", "category", "product_name",
                                  "quantity", "unit_price"})
        # sorted by date
        dates = [x["order_date"] for x in orders]
        self.assertEqual(dates, sorted(dates))


if __name__ == "__main__":
    unittest.main()
