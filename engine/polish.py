# File: engine/polish.py

def refine(narrative: str, metrics: dict, context: dict) -> str:
    slug = context.get("slug", "this business")

    lines = [narrative.strip(), "", "📊 *Key Metrics:*"]

    # Ad Spend
    total_cost = metrics.get("total_cost")
    total_cost_str = f"${total_cost:.2f}" if total_cost is not None else "N/A"
    lines.append(f"- Ad Spend: {total_cost_str}")

    # Conversions
    total_conversions = metrics.get("total_conversions")
    conv_str = str(int(total_conversions)) if total_conversions is not None else "N/A"
    lines.append(f"- Conversions: {conv_str}")

    # Conversion Rate
    conversion_rate = metrics.get("conversion_rate")
    conv_rate_str = f"{conversion_rate:.2f}%" if conversion_rate is not None else "N/A"
    lines.append(f"- Conversion Rate: {conv_rate_str}")

    # CPL vs Benchmark
    cpl = metrics.get("cpl")
    cpl_str = f"${cpl:.2f}" if cpl is not None else "N/A"
    bench_cpl = metrics.get("benchmark_cpl")
    bench_cpl_str = f"${bench_cpl:.2f}" if bench_cpl is not None else "N/A"
    lines.append(f"- CPL: {cpl_str} vs. Benchmark: {bench_cpl_str}")

    # Optional deltas
    if metrics.get("cpl_change") is not None:
        lines.append(f"- CPL Change: {metrics['cpl_change']:+.1f}%")

    if metrics.get("lead_change") is not None:
        lines.append(f"- Leads Change: {metrics['lead_change']:+.1f}%")

    # GA Users & user_change
    user_change = metrics.get("user_change")
    ga_users = metrics.get("ga_users")
    if user_change is not None and ga_users is not None:
        lines.append(f"- GA Users: {int(ga_users)} ({user_change:+.1f}%)")

    return "\n".join(lines)
