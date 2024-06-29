import requests
import pandas as pd
from io import StringIO
from urllib.parse import urlencode
from datetime import datetime, timedelta

EOD_HISTORICAL_DATA_API_URL = "https://eodhd.com/api"


def _init_session(session):
    """
    Returns a requests.Session (or CachedSession)
    """
    if session is None:
        return requests.Session()
    return session


def _url(url, params):
    """
    Returns long url with parameters
    http://mydomain.com?param1=...&param2=...
    """
    if params is not None and len(params) > 0:
        return url + "?" + urlencode(params)
    else:
        return url


def _process_dates(range):
    """
    range: - str: MTD/YTD
           - int: date backwards


    """

    def _format_date(dt):
        """
        Returns formated date
        """
        if dt is None:
            return dt
        return dt.strftime("%Y-%m-%d")

    end_date = datetime.now().date()
    start_date = None
    if type(range) == str:
        if range == "YTD":
            start_date = end_date.replace(day=1, month=1)
        elif range == "MTD":
            start_date = end_date.replace(day=1)
        else:
            try:
                range = int(range)
                start_date = end_date - timedelta(days=range + 1)
            except:
                Exception("Invalid range. Please put YTD or MTD")

    return _format_date(start_date), _format_date(end_date)


def get_fundamentals_data(
    symbol,
    api_key,
    exchange="CC",
    session=None,
):
    """
    Returns EOD (end of day data) for a given symbol
    """
    symbol_exchange = symbol + "-USD." + exchange
    session = _init_session(session)
    endpoint = "/fundamentals/{symbol_exchange}".format(symbol_exchange=symbol_exchange)
    url = EOD_HISTORICAL_DATA_API_URL + endpoint
    params = {
        "api_token": api_key,
    }
    r = session.get(url, params=params)
    if r.status_code == requests.codes.ok:
        df = pd.read_json(StringIO(r.text))
        return df
    else:
        print(f"Exception: {symbol_exchange} server response code {r.status_code}")
        print(r.reason)
        print(_url(url, params))
        return pd.DataFrame()


def get_eod_data(
    symbol,
    exchange,
    days_back,
    api_key,
    session=None,
):
    """
    Returns EOD (end of day data) for a given symbol
    """
    symbol_exchange = symbol + "." + exchange
    session = _init_session(session)
    start, end = _process_dates(range=days_back)
    endpoint = "/eod/{symbol_exchange}".format(symbol_exchange=symbol_exchange)
    url = EOD_HISTORICAL_DATA_API_URL + endpoint
    params = {
        "api_token": api_key,
        "from": start,
        "to": end,
    }
    r = session.get(url, params=params)
    if r.status_code == requests.codes.ok:
        df = pd.read_csv(
            StringIO(r.text),
            skipfooter=0,
            parse_dates=[0],
            index_col=0,
            engine="python",
        )
        return df
    else:
        print(f"Exception: {symbol_exchange} server response code {r.status_code}")
        print(r.reason)
        print(_url(url, params))
        return pd.DataFrame()
