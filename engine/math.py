# File: engine/math.py

import pandas as pd

def safe_percent_change(current, previous):
    if previous == 0 or previous is None:
        return None
    return ((current - previous) / previous) * 100

def format_delta(val):
    return f"{val:+.1f}%" if val is not None else "N/A"

def calculate(raw_data):
    ads_df = raw_data["ads_df"]
    ga_df = raw_data["ga_df"]
    prev_ads_df = raw_data.get("prev_ads_df")
    prev_ga_df = raw_data.get("prev_ga_df")
    benchmark_cpl = raw_data["benchmark_cpl"]

    # 🧹 Clean current ads data
    ads_df["Cost"] = pd.to_numeric(ads_df["Cost"], errors="coerce")
    ads_df["Conversions"] = pd.to_numeric(ads_df["Conversions"], errors="coerce")
    ads_df["Conv. rate"] = pd.to_numeric(
        ads_df["Conv. rate"].astype(str).str.replace('%', ''), errors="coerce"
    )

    total_cost = ads_df["Cost"].sum()
    total_conversions = ads_df["Conversions"].sum()
    avg_conv_rate = ads_df["Conv. rate"].mean()
    cpl = total_cost / total_conversions if total_conversions > 0 else None

    # 🧮 Get current GA traffic
    ga_users = None
    if "Active users" in ga_df.columns:
        ga_users = pd.to_numeric(ga_df["Active users"], errors="coerce").sum()

    # 🕰️ Process previous data
    prev_cost = prev_conversions = prev_rate = prev_cpl = prev_ga_users = None

    if prev_ads_df is not None:
        prev_ads_df["Cost"] = pd.to_numeric(prev_ads_df["Cost"], errors="coerce")
        prev_ads_df["Conversions"] = pd.to_numeric(prev_ads_df["Conversions"], errors="coerce")
        prev_ads_df["Conv. rate"] = pd.to_numeric(
            prev_ads_df["Conv. rate"].astype(str).str.replace('%', ''), errors="coerce"
        )

        prev_cost = prev_ads_df["Cost"].sum()
        prev_conversions = prev_ads_df["Conversions"].sum()
        prev_rate = prev_ads_df["Conv. rate"].mean()
        prev_cpl = prev_cost / prev_conversions if prev_conversions > 0 else None

    if prev_ga_df is not None and "Active users" in prev_ga_df.columns:
        prev_ga_users = pd.to_numeric(prev_ga_df["Active users"], errors="coerce").sum()

    # 🧮 % Changes
    cpl_change = safe_percent_change(cpl, prev_cpl)
    rate_change = safe_percent_change(avg_conv_rate, prev_rate)
    user_change = safe_percent_change(ga_users, prev_ga_users)
    lead_change = safe_percent_change(total_conversions, prev_conversions)

    # 📊 Debug output
    print("📊 Metrics calculated:")

    return {
        "total_cost": total_cost,
        "total_conversions": total_conversions,
        "conversion_rate": avg_conv_rate,
        "cpl": cpl,
        "ga_users": ga_users,
        "benchmark_cpl": benchmark_cpl,
        "prev_cpl": prev_cpl,
        "prev_conv_rate": prev_rate,
        "prev_ga_users": prev_ga_users,
        "prev_total_conversions": prev_conversions,
        "cpl_change": cpl_change,
        "conversion_rate_change": rate_change,
        "user_change": user_change,
        "lead_change": lead_change
    }
