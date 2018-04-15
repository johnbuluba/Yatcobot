from abc import ABC, abstractmethod


class PluginABC(ABC):

    @property
    def name(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_enabled():
        """Plugins must implement get_enabled"""

    @staticmethod
    @abstractmethod
    def get_config_template():
        """Plugins must implement get_config_template"""
