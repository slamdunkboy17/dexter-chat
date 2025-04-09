# File: engine/retrieve.py

from utils.drive_utils import get_valid_csvs, get_previous_csvs, download_csv
from utils.notion_utils import get_client_properties_from_notion
import pandas as pd

def collect(slug):
    # 1. Get the latest Google Ads and GA CSVs
    ads_file, ga_file = get_valid_csvs(slug)
    if not ads_file or not ga_file:
        raise ValueError(f"No recent ads or GA files found for slug `{slug}`.")

    ads_df = download_csv(ads_file['id'])
    ga_df = download_csv(ga_file['id'])

    # 2. Get previous versions (optional)
    prev_ads_file, prev_ga_file = get_previous_csvs(slug, exclude_id=ads_file['id'])
    prev_ads_df = download_csv(prev_ads_file['id']) if prev_ads_file else None
    prev_ga_df = download_csv(prev_ga_file['id']) if prev_ga_file else None

    # 3. Get metadata from Notion (normalized keys)
    notion_data = get_client_properties_from_notion(slug)

    industry = notion_data.get("industry", "unknown")
    benchmark_cpl = notion_data.get("benchmark_cpl", 300)


    return {
        "ads_df": ads_df,
        "ga_df": ga_df,
        "prev_ads_df": prev_ads_df,
        "prev_ga_df": prev_ga_df,
        "notion": notion_data,
        "industry": industry,
        "benchmark_cpl": benchmark_cpl
    }
