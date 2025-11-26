"""Simple caching for API responses."""

import json
import time
from pathlib import Path
from typing import Optional, Any


class APICache:
    """Simple file-based cache for API responses."""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl: int = 3600):
        """
        Initialize cache.
        
        Args:
            cache_dir: Cache directory (default: ~/.cache/bugnosis)
            ttl: Time to live in seconds (default: 1 hour)
        """
        if cache_dir is None:
            cache_dir = Path.home() / '.cache' / 'bugnosis'
        else:
            cache_dir = Path(cache_dir)
            
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key."""
        # Simple hash to create filename
        import hashlib
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self.cache_dir / f"{key_hash}.json"
        
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        cache_file = self._get_cache_path(key)
        
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            # Check if expired
            if time.time() - data['timestamp'] > self.ttl:
                cache_file.unlink()
                return None
                
            return data['value']
        except (json.JSONDecodeError, KeyError, IOError):
            return None
            
    def set(self, key: str, value: Any):
        """Cache a value."""
        cache_file = self._get_cache_path(key)
        
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': time.time(),
                    'value': value
                }, f)
        except IOError:
            pass  # Fail silently if can't write cache
            
    def clear(self):
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                cache_file.unlink()
            except IOError:
                pass

