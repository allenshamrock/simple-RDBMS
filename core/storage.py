import json
import os
import pickle

class StorageEngine:
    def __init__(self, base_path="data"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def get_table_path(self, table_name):
        return os.path.join(self.base_path, f"{table_name}.json")
    
    def get_metadata_path(self):
        return os.path.join(self.base_path, "metadata.json")
    
    def load_table(self, table_name):
        table_path = self.get_table_path(table_name)
        if os.path.exists(table_path):
            with open(table_path, 'r') as f:
                return json.load(f)
        return None
    
    def save_table(self, table_name, data):
        table_path = self.get_table_path(table_name)
        with open(table_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def delete_table(self, table_name):
        table_path = self.get_table_path(table_name)
        if os.path.exists(table_path):
            os.remove(table_path)
    
    def load_metadata(self):
        metadata_path = self.get_metadata_path()
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                return json.load(f)
        return {'tables': {}}
    
    def save_metadata(self, metadata):
        metadata_path = self.get_metadata_path()
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
