from typing import Dict
import pandas as pd


from .plugin_abc import Plugin


class SignalPlugin(Plugin):
    """
    A plugin to get signal and provide investment suggestion
    """

    def get_source_name(self) -> str:
        return "aspa"

    def get_spec(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": "get_crypto_asset_signal",
                "description": "Get investment advice based on ASPA's quantitative research signals. These signals are represented as standard deviations. Interpret the signals as follows: 0 indicates a neutral position, a signal greater than 0 suggests going long on the crypto asset, while a signal less than 0 suggests going short. Signals greater than 1 or less than -1 indicate a strong signal, and signals greater than 2 or less than -2 indicate a very strong signal. You can request a suggestion for a single crypto asset or a portfolio strategy, which involves buying the top 5-10% and shorting the bottom 5-10% of assets.",
            },
        }

    async def execute(self, function_name, helper, **kwargs) -> Dict:

        def get_signal():

            signal_database = pd.read_excel("bot/data/cc_composite_signal.xlsx")
            signal_database = signal_database.rename(columns={"Unnamed: 0": "asset"})
            signal_database["asset"] = signal_database["asset"].apply(
                lambda x: x.split("-")[0]
            )
            signal_database = signal_database.set_index("asset")
            return (
                signal_database[signal_database.columns.tolist()[-1]]
                .dropna()
                .sort_values(ascending=False)
                .to_dict()
            )

        return get_signal()
