import time
import requests
import pandas as pd
from urllib.parse import quote

MANUAL_TITLES = {
    "BNB": "Binance_Coin",
    "ADA": "Cardano_(blockchain_platform)",
}

def lookup_title(ticker: str) -> str:
    return MANUAL_TITLES.get(ticker, ticker)

def fetch_wiki_views(title: str, start: str, end: str) -> pd.Series:
    """
    Fetch daily pageviews for a given Wikipedia article title.
    """
    url = (
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/"
        f"per-article/en.wikipedia/all-access/all-agents/"
        f"{quote(title, safe='')}/daily/{start}/{end}"
    )
    headers = {"User-Agent": "StatisticalArbitrage (keyaanmiah@icloud.com)"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    items = r.json().get("items", [])
    dates = [pd.to_datetime(x["timestamp"], format="%Y%m%d%H") for x in items]
    counts = [x["views"] for x in items]
    return pd.Series(counts, index=dates, name=title)

def main():
    df_prices = pd.read_csv("data/coins.csv", index_col=0, parse_dates=True)
    tickers   = df_prices.columns.tolist()

    start, end = "2018010100", "2024123100"

    all_views = {}
    for ticker in tickers:
        title = lookup_title(ticker)
        print(f"Fetching {ticker} → {title}...")
        try:
            s = fetch_wiki_views(title, start, end)
            all_views[ticker] = s
        except Exception as e:
            print(f"  ERROR fetching {title}: {e}")
        time.sleep(1)

    if not all_views:
        raise RuntimeError("No pageview data fetched.  Check your titles & network")

    df_daily = pd.concat(all_views.values(), axis=1)
    df_daily.columns = list(all_views.keys())
    df_daily.index.name = "date"
    df_daily = df_daily.fillna(0)

    df_daily.to_csv("wiki_daily_views_all.csv")
    print("✔︎ Saved daily views to wiki_daily_views_all.csv")

if __name__ == "__main__":
    main()
