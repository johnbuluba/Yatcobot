from abc import ABC, abstractmethod


class PluginABC(ABC):

    @staticmethod
    @abstractmethod
    def get_enabled():
        """Plugins must implement get_enabled"""
