from typing import Dict, Any, List, Set
import bisect

class IndexManager:
    def __init__(self):
        self.index = {} 
        self.sorted_keys = []  # For range queries
    
    def add(self, row_id: int, row: Dict[str, Any]):
        """Add a row to the index"""
        for key, value in row.items():
            if key not in self.index:
                self.index[key] = {}
            
            value_key = str(value)
            if value_key not in self.index[key]:
                self.index[key][value_key] = set()
            
            self.index[key][value_key].add(row_id)
    
    def remove(self, row_id: int, row: Dict[str, Any]):
        """Remove a row from the index"""
        for key, value in row.items():
            if key in self.index:
                value_key = str(value)
                if value_key in self.index[key]:
                    self.index[key][value_key].discard(row_id)
    
    def update(self, row_id: int, old_row: Dict[str, Any], new_row: Dict[str, Any]):
        """Update index for a changed row"""
        self.remove(row_id, old_row)
        self.add(row_id, new_row)
    
    def search(self, column: str, value: Any) -> Set[int]:
        """Search for rows with specific value in column"""
        if column in self.index:
            value_key = str(value)
            return self.index[column].get(value_key, set())
        return set()