"""Base class for Bugnosis plugins."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class PluginBase(ABC):
    """Abstract base class that all plugins must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the plugin."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what the plugin does."""
        pass

    @abstractmethod
    def register(self, context: Dict[str, Any]) -> None:
        """
        Called when the plugin is loaded.
        
        Args:
            context: A dictionary containing access to core Bugnosis services
                     (e.g., {'logger': ..., 'config': ..., 'db': ...})
        """
        pass

    def shutdown(self) -> None:
        """Called when the application is shutting down. Optional cleanup."""
        pass

