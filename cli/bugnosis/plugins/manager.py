"""Plugin manager for loading and executing external modules."""

import importlib
import importlib.util
import os
import sys
from typing import Dict, List, Type
from pathlib import Path
from .base import PluginBase

class PluginManager:
    """Manages the discovery and lifecycle of plugins."""

    def __init__(self, plugin_dir: str = None):
        if plugin_dir:
            self.plugin_dir = Path(plugin_dir)
        else:
            # Default to ~/.bugnosis/plugins
            self.plugin_dir = Path.home() / ".bugnosis" / "plugins"
        
        self.plugins: Dict[str, PluginBase] = {}
        self._ensure_plugin_dir()

    def _ensure_plugin_dir(self):
        """Create plugin directory if it doesn't exist."""
        if not self.plugin_dir.exists():
            self.plugin_dir.mkdir(parents=True, exist_ok=True)
            # Create an __init__.py so it can be treated as a package if needed,
            # though we'll load files dynamically.
            (self.plugin_dir / "__init__.py").touch()

    def discover_plugins(self) -> List[str]:
        """Find all python files in the plugin directory that look like plugins."""
        if not self.plugin_dir.exists():
            return []
        
        return [f.stem for f in self.plugin_dir.glob("*.py") if f.name != "__init__.py"]

    def load_plugins(self, context: Dict = None) -> None:
        """
        Load and initialize all plugins found in the plugin directory.
        
        Args:
            context: Dictionary of services to pass to plugins during registration.
        """
        if context is None:
            context = {}

        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name == "__init__.py":
                continue

            try:
                self._load_plugin_from_file(plugin_file, context)
            except Exception as e:
                print(f"Failed to load plugin {plugin_file.name}: {e}")

    def _load_plugin_from_file(self, path: Path, context: Dict) -> None:
        """Import a module from a file and instantiate its Plugin class."""
        module_name = f"bugnosis.plugins.external.{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if not spec or not spec.loader:
            return

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Find the subclass of PluginBase in the module
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if (isinstance(attribute, type) and 
                issubclass(attribute, PluginBase) and 
                attribute is not PluginBase):
                
                # Instantiate and register
                plugin_instance = attribute()
                plugin_instance.register(context)
                self.plugins[plugin_instance.name] = plugin_instance
                print(f"Loaded plugin: {plugin_instance.name} v{plugin_instance.version}")

    def get_plugin(self, name: str) -> PluginBase:
        return self.plugins.get(name)

    def list_plugins(self) -> List[Dict[str, str]]:
        """Return metadata for all loaded plugins."""
        return [
            {
                "name": p.name,
                "version": p.version,
                "description": p.description
            }
            for p in self.plugins.values()
        ]

