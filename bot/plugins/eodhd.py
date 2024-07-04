from typing import Dict
import os

import requests
from .utils.eodhd_funcs import get_eod_data, get_fundamentals_data
from .plugin_abc import Plugin


# data provider: "https://eodhd.com/api"
class EodHDPlugin(Plugin):
    """
    A plugin to fetch the current rate of various cryptocurrencies
    """

    def __init__(self):
        eod_historical_app_id = os.getenv("EOD_HISTORICAL_API_KEY")
        # if not eod_historical_app_id:
        #     raise ValueError('WOLFRAM_APP_ID environment variable must be set to use WolframAlphaPlugin')
        self.app_id = eod_historical_app_id

    def get_source_name(self) -> str:
        return "EODHD APIs"

    def get_spec(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": "get_historical_price_and_analytics",
                "description": "Retrieve the historical data and perform analytics for a specified cryptocurrency within a given time range.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "The symbol of the cryptocurrency (e.g., BTC for Bitcoin, ETH for Ethereum). Convert the currency name in the request to its symbol.",
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "A list of requested data fields for the specified symbol. Available options are ['Open', 'High', 'Low', 'Close', 'Volume']. Use 'Close' for historical end-of-day prices. The default value is ['Close']",
                        },
                        "days_back": {
                            "type": "string",
                            "description": "The number of days of historical data to retrieve. This is usually a number (as a string) but can also be 'MTD' (Month to Date) or 'YTD' (Year to Date).",
                        },
                        "analytics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "A list of analytics to perform on the historical data. Valid values are ['highest', 'lowest', 'average', 'return'].The default value is the full list",
                        },
                    },
                    "required": ["symbol", "days_back", "fields", "analytics"],
                },
            },
        }

    async def execute(self, function_name, helper, **kwargs) -> Dict:

        def get_historical_price_and_analytics(
            symbol, days_back, fields=["Close"], analytics=[]
        ):

            data = get_eod_data(
                symbol="%s-USD" % symbol,
                exchange="CC",
                days_back=days_back,
                api_key=self.app_id,
                session=None,
            )[fields]
            data.index = data.index.astype(str)

            analytics_dic = {
                "highest": data.max().to_dict(),
                "lowest": data.min().to_dict(),
                "average": data.mean().to_dict(),
                "return": (
                    (data.iloc[-1] - data.iloc[0]) * 100 / data.iloc[0]
                ).to_dict(),
            }

            if len(analytics) > 0:
                analytics_dic = {
                    key: value
                    for key, value in analytics_dic.items()
                    if key in analytics
                }

            return {"data": data.to_dict(), "analytics": analytics_dic}

        return get_historical_price_and_analytics(
            kwargs["symbol"], kwargs["days_back"], kwargs["fields"], kwargs["analytics"]
        )
