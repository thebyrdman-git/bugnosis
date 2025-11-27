"""Configuration management for Bugnosis."""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional


class BugnosisConfig:
    """Configuration manager for Bugnosis."""
    
    DEFAULT_CONFIG = {
        'github_token': None,
        'groq_api_key': None,
        'min_impact': 70,
        'watched_repos': [],
        'export_dir': './exports',
        'cache_ttl': 3600,
        'notifications': {
            'enabled': False,
            'threshold': 85
        },
        'preferences': {
            'auto_save': True,
            'use_cache': True,
            'show_details': False
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config manager.
        
        Args:
            config_path: Path to config file (default: ~/.config/bugnosis/config.json)
        """
        if config_path is None:
            config_dir = Path.home() / '.config' / 'bugnosis'
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = str(config_dir / 'config.json')
            
        self.config_path = config_path
        self.config = self.load()
        
    def load(self) -> Dict:
        """Load configuration from file."""
        if not Path(self.config_path).exists():
            return self.DEFAULT_CONFIG.copy()
            
        try:
            with open(self.config_path, 'r') as f:
                loaded = json.load(f)
                # Merge with defaults (in case new keys added)
                config = self.DEFAULT_CONFIG.copy()
                config.update(loaded)
                return config
        except (json.JSONDecodeError, IOError):
            return self.DEFAULT_CONFIG.copy()
            
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config: {e}")
            
    def get(self, key: str, default=None):
        """Get config value."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
        
    def set(self, key: str, value):
        """Set config value."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        
    def get_github_token(self) -> Optional[str]:
        """Get GitHub token from config or environment."""
        return self.config.get('github_token') or os.getenv('GITHUB_TOKEN')
        
    def get_groq_key(self) -> Optional[str]:
        """Get Groq API key from config or environment."""
        return self.config.get('groq_api_key') or os.getenv('GROQ_API_KEY')
        
    def add_watched_repo(self, repo: str):
        """Add repository to watch list."""
        if repo not in self.config['watched_repos']:
            self.config['watched_repos'].append(repo)
            
    def remove_watched_repo(self, repo: str):
        """Remove repository from watch list."""
        if repo in self.config['watched_repos']:
            self.config['watched_repos'].remove(repo)
            
    def get_watched_repos(self) -> List[str]:
        """Get list of watched repositories."""
        return self.config.get('watched_repos', [])


