"""Markdown report generation with ASCII bar charts."""


def _bar(value, max_value, width=28):
    n = int(round(value / max_value * width)) if max_value > 0 else 0
    return "█" * n + "░" * (width - n)


def render_markdown(m):
    L = ["# 销售数据分析报告", ""]
    L += ["## 总览", ""]
    L += [f"- GMV：{m['revenue']:,.0f} 元",
          f"- 订单数：{m['n_orders']:,}",
          f"- 客单价（AOV）：{m['aov']:,.2f} 元",
          f"- 购买用户数：{m['n_customers']:,}",
          f"- 复购率：{m['repeat_rate']:.1%}", ""]

    L += ["## 月度 GMV 趋势", ""]
    L += ["| 月份 | GMV（元） | 环比 |", "|------|-----------|------|"]
    for month, rev in m["monthly"].items():
        g = m["mom"].get(month)
        g_str = f"{g:+.1%}" if g is not None else "--"
        L.append(f"| {month} | {rev:,.0f} | {g_str} |")
    L += ["", "```"]
    peak = max(m["monthly"].values())
    for month, rev in m["monthly"].items():
        L.append(f"{month} {_bar(rev, peak)} {rev:>12,.0f}")
    L += ["```", ""]

    L += ["## 品类结构", ""]
    L += ["| 品类 | GMV（元） | 占比 |", "|------|-----------|------|"]
    for cat, rev in m["category_mix"].items():
        L.append(f"| {cat} | {rev:,.0f} | {rev / m['revenue']:.1%} |")
    L += ["", "## 畅销商品 Top 8（按 GMV）", ""]
    L += ["| 商品 | GMV（元） |", "|------|-----------|"]
    for prod, rev in m["top_products"]:
        L.append(f"| {prod} | {rev:,.0f} |")
    L += ["", "## 区域分布", ""]
    L += ["| 区域 | GMV（元） | 占比 |", "|------|-----------|------|"]
    for region, rev in m["region_mix"].items():
        L.append(f"| {region} | {rev:,.0f} | {rev / m['revenue']:.1%} |")

    L += ["", "## 关键发现", ""]
    for i, ins in enumerate(m["insights"], 1):
        L.append(f"{i}. {ins}")
    L += ["", "_数据为程序生成的演示数据（deterministic seed），分析方法适用于真实业务数据。_", ""]
    return "\n".join(L)


def render_console(m):
    lines = [
        f"GMV {m['revenue']:,.0f} 元 | 订单 {m['n_orders']:,} | "
        f"AOV {m['aov']:,.2f} 元 | 复购率 {m['repeat_rate']:.1%}",
        "品类占比: " + " / ".join(
            f"{c} {r / m['revenue']:.0%}" for c, r in m["category_mix"].items()),
        "发现: " + m["insights"][0],
    ]
    return "\n".join(lines)
