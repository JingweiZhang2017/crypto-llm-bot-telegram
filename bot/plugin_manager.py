import json
from plugins.coincap_rate import CryptoPlugin
from plugins.eodhd import EodHDPlugin
from plugins.daily_signal import SignalPlugin


class PluginManager:
    """
    A class to manage the plugins and call the correct functions
    """

    def __init__(self, config):
        enabled_plugins = config.get("plugins", [])
        plugin_mapping = {
            "coincap": CryptoPlugin,
            "eodhd": EodHDPlugin,
            "signals": SignalPlugin,
        }
        self.plugins = [
            plugin_mapping[plugin]()
            for plugin in enabled_plugins
            if plugin in plugin_mapping
        ]

    def get_functions_specs(self):
        """
        Return the list of function specs that can be called by the model
        """
        # return [
        #     specs
        #     for specs in map(lambda plugin: plugin.get_spec(), self.plugins)
        # for spec in specs
        # ]
        specs = [plugin.get_spec() for plugin in self.plugins]
        # print(specs)
        return specs

    async def call_function(self, function_name, helper, arguments):
        """
        Call a function based on the name and parameters provided
        """
        plugin = self.__get_plugin_by_function_name(function_name)
        if not plugin:
            return json.dumps({"error": f"Function {function_name} not found"})
        return json.dumps(
            await plugin.execute(function_name, helper, **json.loads(arguments)),
            default=str,
        )

    def get_plugin_source_name(self, function_name) -> str:
        """
        Return the source name of the plugin
        """
        plugin = self.__get_plugin_by_function_name(function_name)
        if not plugin:
            return ""
        return plugin.get_source_name()

    def __get_plugin_by_function_name(self, function_name):

        return next(
            (
                plugin
                for plugin in self.plugins
                if function_name in plugin.get_spec()["function"]["name"]
            ),
            None,
        )
