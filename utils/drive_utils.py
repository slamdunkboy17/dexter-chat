# File: drive_utils.py

import os
import io
from datetime import datetime, timezone, timedelta
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from dateutil.parser import isoparse
from datetime import timezone

# Setup Google Drive Service
SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('drive', 'v3', credentials=credentials)

FRESHNESS_DAYS = 7

def get_latest_file(slug_part):
    response = service.files().list(
        q=f"name contains '{slug_part}' and mimeType='text/csv'",
        spaces='drive',
        fields='files(id, name, modifiedTime)',
        orderBy='modifiedTime desc'
    ).execute()
    return response['files'][0] if response['files'] else None

def is_fresh(file_metadata, days=FRESHNESS_DAYS):
    if not file_metadata:
        return False
    mod_time = isoparse(file_metadata['modifiedTime']).astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    return mod_time > now - timedelta(days=days)

def download_csv(file_id, skiprows=2):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)
    return pd.read_csv(fh, skiprows=skiprows, on_bad_lines='skip')

def get_valid_csvs(slug):
    ads_file = get_latest_file(f"{slug}_ads")
    ga_file = get_latest_file(f"{slug}_ga")

    if not (is_fresh(ads_file) and is_fresh(ga_file)):
        return None, None

    return ads_file, ga_file

def get_previous_csvs(slug, exclude_id=None):
    def get_previous(slug_key):
        response = service.files().list(
            q=f"name contains '{slug_key}' and mimeType='text/csv'",
            spaces='drive',
            fields='files(id, name, modifiedTime)',
            orderBy='modifiedTime desc'
        ).execute()

        files = response['files']
        for f in files:
            if f['id'] != exclude_id:
                return f
        return None

    return get_previous(f"{slug}_ads"), get_previous(f"{slug}_ga")