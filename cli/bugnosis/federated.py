"""Federated search across multiple bug tracking platforms."""

import concurrent.futures
from typing import List, Dict, Any
from .platforms import get_platform
from .ai import AIEngine

class FederatedSearch:
    """Search engine that queries multiple platforms."""
    
    def __init__(self, min_impact: int = 70):
        self.min_impact = min_impact
        
    def search(self, query: str) -> Dict[str, Any]:
        """
        Search for bugs across all platforms based on a query.
        
        Args:
            query: Search term
            
        Returns:
            Dict with 'results', 'stats', 'targets'
        """
        # 1. Resolve targets using AI
        ai = AIEngine()
        targets = ai.resolve_targets(query)
        
        if not targets:
            # Fallback to searching just github with the query as repo
            targets = [{'platform': 'github', 'target': query}]
            
        results = []
        stats = {}
        
        # 2. Execute searches in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_target = {
                executor.submit(self._search_target, t): t for t in targets
            }
            
            for future in concurrent.futures.as_completed(future_to_target):
                target = future_to_target[future]
                platform_name = target['platform']
                
                try:
                    bugs = future.result()
                    results.extend(bugs)
                    
                    # Update stats
                    count = len(bugs)
                    stats[platform_name] = stats.get(platform_name, 0) + count
                    
                except Exception as e:
                    print(f"Error searching {platform_name}/{target['target']}: {e}")
        
        # 3. Sort merged results
        results.sort(key=lambda x: x.impact_score, reverse=True)
        
        return {
            'results': results,
            'stats': stats,
            'total': len(results),
            'targets_scanned': targets
        }
    
    def _search_target(self, target: Dict[str, str]) -> List[Any]:
        """Helper to search a single target."""
        platform_name = target['platform']
        project = target['target']
        instance = target.get('instance')
        
        kwargs = {}
        if instance:
            kwargs['instance'] = instance
            
        try:
            platform = get_platform(platform_name, **kwargs)
            return platform.search_bugs(project, min_impact=self.min_impact)
        except Exception as e:
            print(f"Platform init error ({platform_name}): {e}")
            return []
