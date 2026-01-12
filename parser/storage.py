import json
import os
import pickle
from typing import Dict, Any

class StorageEngine:
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
    
    def _get_table_path(self, table_name: str) -> str:
        return os.path.join(self.storage_dir, f"{table_name}.json")
    
    def _get_metadata_path(self) -> str:
        return os.path.join(self.storage_dir, "metadata.json")
    
    def save_table(self, table_name: str, data: Dict[str, Any]):
        """Save table data to JSON file"""
        file_path = self._get_table_path(table_name)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_table(self, table_name: str) -> Dict[str, Any]:
        """Load table data from JSON file"""
        file_path = self._get_table_path(table_name)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    
    def delete_table(self, table_name: str):
        """Delete table file"""
        file_path = self._get_table_path(table_name)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def save_metadata(self, metadata: Dict[str, Any]):
        """Save database metadata"""
        file_path = self._get_metadata_path()
        with open(file_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load_metadata(self) -> Dict[str, Any]:
        """Load database metadata"""
        file_path = self._get_metadata_path()
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {'tables': {}}