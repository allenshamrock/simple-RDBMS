from typing import Dict, List, Any

class IndexManager:
    def __init__(self):
        self.index = {}
    
    def add(self, row_id: int, values: Dict[str, Any]):
        """Add a row to the index"""
        for column_name, value in values.items():
            if column_name not in self.index:
                self.index[column_name] = {}
            
            if value not in self.index[column_name]:
                self.index[column_name][value] = []
            
            if row_id not in self.index[column_name][value]:
                self.index[column_name][value].append(row_id)
    
    def remove(self, row_id: int, values: Dict[str, Any]):
        """Remove a row from the index"""
        for column_name, value in values.items():
            if column_name in self.index and value in self.index[column_name]:
                if row_id in self.index[column_name][value]:
                    self.index[column_name][value].remove(row_id)
                    
                    # Clean up empty lists
                    if not self.index[column_name][value]:
                        del self.index[column_name][value]
    
    def update(self, row_id: int, old_values: Dict[str, Any], new_values: Dict[str, Any]):
        """Update index when a row changes"""
        self.remove(row_id, old_values)
        self.add(row_id, new_values)
    
    def search(self, column_name: str, value: Any) -> List[int]:
        """Search for row IDs by column value"""
        if column_name in self.index and value in self.index[column_name]:
            return self.index[column_name][value].copy()
        return []
    
    def clear(self):
        """Clear the entire index"""
        self.index = {}
