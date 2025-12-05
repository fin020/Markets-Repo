# data_fetch.py
import os
import requests
import pandas as pd
from datetime import datetime
from io import StringIO

fred_key = os.getenv("FRED_API_KEY")
av_key = os.getenv("AV_API_KEY")

def _get_cache_filename(prefix: str) -> str:
    today = datetime.today().strftime('%Y-%m-%d')
    return f"{prefix}_{today}.csv"

def _load_from_cache(cache_file: str) -> pd.DataFrame | None:
    if os.path.exists(cache_file):
        print(f"Loading {cache_file} from cache...")
        return pd.read_csv(cache_file, parse_dates=['date'], index_col='date') #type: ignore
    return None

def _save_to_cache(df: pd.DataFrame, cache_file: str) -> None:
    df.to_csv(cache_file)
    print(f"Saved to {cache_file}")

def fetch_from_fred(series_id: str = "CPIAUCNS", fred_key: str | None = fred_key,
                    prefix: str = "fred") -> pd.DataFrame:
    cache_file = _get_cache_filename(f"{prefix}_{series_id}")
    df = _load_from_cache(cache_file)
    if df is not None:
        return df

    if fred_key is None:
        raise ValueError("FRED_API_KEY not found in environment variables.")

    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={fred_key}&file_type=json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["observations"])
    df["date"] = pd.to_datetime(df["date"]) 
    df["value"] = pd.to_numeric(df["value"], errors="coerce") #type: ignore
    df = df[["date", "value"]].rename(columns={"value": series_id})
    df.set_index("date", inplace=True)

    _save_to_cache(df, cache_file)
    return df

def fetch_from_alphavantage(symbol: str, function: str = "TIME_SERIES_DAILY",
                            av_key: str | None = av_key, prefix: str = "av") -> pd.DataFrame:
    cache_file = _get_cache_filename(f"{prefix}_{symbol}")
    df = _load_from_cache(cache_file)
    if df is not None:
        return df

    if av_key is None:
        raise ValueError("AV_API_KEY not found in environment variables.")

    url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={av_key}&datatype=csv"
    response = requests.get(url)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text)) #type: ignore

    _save_to_cache(df, cache_file)
    return df

def fetch_from_OECD(name: str, url: str, csv: bool = True,
                    prefix: str = "oecd") -> pd.DataFrame:
    cache_file = _get_cache_filename(f"{prefix}_{name}")
    df = _load_from_cache(cache_file)
    if df is not None:
        return df

    if csv:
        url += "&format=csvfilewithlabels"

    response = requests.get(url)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text)) #type: ignore

    # Try to parse OECD time column if present
    if "TIME" in df.columns:
        df["date"] = pd.to_datetime(df["TIME"])
        df.set_index("date", inplace=True)

    _save_to_cache(df, cache_file)
    return df

if __name__ == "__main__":
    # Quick test run
    print(fetch_from_fred("CPIAUCNS").head())