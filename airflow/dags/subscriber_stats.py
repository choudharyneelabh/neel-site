"""
subscriber_stats DAG

Pipeline: extract -> clean -> compute -> load

Pulls all rows from the `subscribers` table in Supabase, cleans them with
pandas, computes how many whole days have passed since the most recent
signup, and writes that single number into the `misc_stats` table so the
website's Misc page can display it.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd
from airflow.sdk import dag, task
from supabase import create_client


def get_supabase_client():
    """Build a Supabase client using the service_role key (server-side only)."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SECRET_KEY"]
    return create_client(url, key)


@dag(
    dag_id="subscriber_stats",
    description="Computes days since the last subscriber and updates misc_stats",
    schedule="@daily",
    start_date=datetime(2026, 8, 30),
    catchup=False,
    tags=["neel-site"],
)
def subscriber_stats():

    @task()
    def extract_subscribers() -> list[dict]:
        """Extract: pull raw subscriber rows (email, created_at) from Supabase."""
        supabase = get_supabase_client()
        response = supabase.table("subscribers").select("email, created_at").execute()
        return response.data

    @task()
    def clean_data(raw_rows: list[dict]) -> list[dict]:
        """Transform: parse timestamps, drop bad/duplicate rows with pandas."""
        df = pd.DataFrame(raw_rows)
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
        df = df.dropna(subset=["created_at"]).drop_duplicates(subset=["email"])
        # XCom (how Airflow passes data between tasks) needs JSON-serializable
        # data, so timestamps go back to plain strings for the trip.
        df["created_at"] = df["created_at"].astype(str)
        return df.to_dict(orient="records")

    @task()
    def compute_days_since_last_subscriber(clean_rows: list[dict]) -> int:
        """Analyze: how many whole days since the most recent signup."""
        df = pd.DataFrame(clean_rows)
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
        most_recent = df["created_at"].max()
        days_since = (datetime.now(timezone.utc) - most_recent).days
        return int(days_since)

    @task()
    def load_to_supabase(days_since: int) -> None:
        """Load: write the computed stat into the single-row misc_stats table."""
        supabase = get_supabase_client()
        supabase.table("misc_stats").upsert(
            {"id": 1, "days_since_last_subscriber": days_since}
        ).execute()

    raw = extract_subscribers()
    cleaned = clean_data(raw)
    days_since = compute_days_since_last_subscriber(cleaned)
    load_to_supabase(days_since)


subscriber_stats()
