# File: engine/polish.py

def refine(narrative: str, metrics: dict, context: dict) -> str:
    slug = context.get("slug", "this business")

    lines = [
        f"{narrative}\n",
        "📊 *Key Metrics:*",
        f"- Ad Spend: ${metrics['total_cost']:.2f}",
        f"- Conversions: {int(metrics['total_conversions'])}",
        f"- Conversion Rate: {metrics['conversion_rate']:.2f}%",
        f"- CPL: ${metrics['cpl']:.2f} vs. Benchmark: ${metrics['benchmark_cpl']}",
    ]

    # Optional deltas
    if metrics.get("cpl_change") is not None:
        lines.append(f"- CPL Change: {metrics['cpl_change']:+.1f}%")
    if metrics.get("lead_change") is not None:
        lines.append(f"- Leads Change: {metrics['lead_change']:+.1f}%")
    if metrics.get("user_change") is not None and metrics.get("ga_users") is not None:
        lines.append(f"- GA Users: {int(metrics['ga_users'])} ({metrics['user_change']:+.1f}%)")

    return "\n".join(lines)
