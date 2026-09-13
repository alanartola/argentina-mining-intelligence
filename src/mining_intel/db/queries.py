import pandas as pd

from mining_intel.db.connection import get_connection


def get_projects_df() -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM projects ORDER BY investment_usd DESC", conn)
    finally:
        conn.close()


def get_tenders_df() -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM tenders ORDER BY publish_date DESC", conn)
    finally:
        conn.close()
