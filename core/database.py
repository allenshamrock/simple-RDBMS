import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from .storage import StorageEngine
from .index import IndexManager
import pickle

class DataType:
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    DATE = "DATE"
    BOOLEAN = "BOOLEAN"
    FLOAT = "FLOAT"

class Column:
    def __init__(self, name: str, data_type: str, 
                 is_primary: bool = False, is_unique: bool = False,
                 nullable: bool = True):
        self.name = name
        self.data_type = data_type
        self.is_primary = is_primary
        self.is_unique = is_unique
        self.nullable = nullable
    
    def validate(self, value: Any) -> bool:
        if value is None:
            return self.nullable
        
        try:
            if self.data_type == DataType.INTEGER:
                return isinstance(value, int)
            elif self.data_type == DataType.FLOAT:
                return isinstance(value, (int, float))
            elif self.data_type == DataType.TEXT:
                return isinstance(value, str)
            elif self.data_type == DataType.DATE:
                if isinstance(value, str):
                    datetime.strptime(value, '%Y-%m-%d')
                    return True
                return isinstance(value, datetime)
            elif self.data_type == DataType.BOOLEAN:
                return isinstance(value, bool)
            return True
        except:
            return False
    
    def to_dict(self):
        return {
            'name': self.name,
            'data_type': self.data_type,
            'is_primary': self.is_primary,
            'is_unique': self.is_unique,
            'nullable': self.nullable
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            data_type=data['data_type'],
            is_primary=data.get('is_primary', False),
            is_unique=data.get('is_unique', False),
            nullable=data.get('nullable', True)
        )

class Table:
    def __init__(self, name: str, columns: List[Column], database: 'Database'):
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.database = database
        self.data = []
        self.next_id = 1
        self.indexes = {}
        self.load_data()
    
    def load_data(self):
        """Load table data from storage"""
        storage = StorageEngine()
        table_data = storage.load_table(self.name)
        if table_data:
            self.data = table_data.get('rows', [])
            self.next_id = table_data.get('next_id', 1)
    
    def save_data(self):
        """Save table data to storage"""
        storage = StorageEngine()
        storage.save_table(self.name, {
            'rows': self.data,
            'next_id': self.next_id
        })
    
    def insert(self, values: Dict[str, Any]) -> int:
        """Insert a new row into the table"""
        # Validate all columns
        for col_name, col in self.columns.items():
            if col.is_primary and col_name not in values:
                if col.data_type == DataType.INTEGER:
                    values[col_name] = self.next_id
                    self.next_id += 1
                else:
                    raise ValueError(f"Primary key {col_name} must be provided")
            
            if col_name in values:
                if not col.validate(values[col_name]):
                    raise ValueError(f"Invalid value for column {col_name}")
            elif not col.nullable:
                raise ValueError(f"Column {col_name} cannot be null")
        
        # Check unique constraints
        for col_name, col in self.columns.items():
            if col.is_unique and col_name in values:
                for row in self.data:
                    if row.get(col_name) == values[col_name]:
                        raise ValueError(f"Duplicate value for unique column {col_name}")
        
        # Add the row
        row_id = len(self.data)
        self.data.append(values.copy())
        self.save_data()
        
        # Update indexes
        for index_name, index in self.indexes.items():
            index.add(row_id, values)
        
        return row_id
    
    def select(self, where: Optional[Dict[str, Any]] = None, where_operator: str = '=') -> List[Dict[str, Any]]:
        """Select rows from the table with WHERE clause"""
        results = []
        
        for row in self.data:
            match = True
            if where:
                for key, value in where.items():
                    if key not in row:
                        match = False
                        break
                    
                    row_value = row[key]
                    
                    if where_operator == '=':
                        if row_value != value:
                            match = False
                            break
                    elif where_operator == 'LIKE':
                        if isinstance(value, str) and isinstance(row_value, str):
                            # Convert SQL LIKE pattern to regex
                            pattern = value.replace('%', '.*').replace('_', '.')
                            import re
                            if not re.search(pattern, row_value, re.IGNORECASE):
                                match = False
                                break
                        else:
                            match = False
                            break
            
            if match:
                results.append(row.copy())
        
        return results

    def update(self, set_values: Dict[str, Any], where: Optional[Dict[str, Any]] = None, where_operator: str = '=') -> int:
        """Update rows in the table"""
        updated_count = 0
        
        for i, row in enumerate(self.data):
            match = True
            if where:
                for key, value in where.items():
                    if key not in row:
                        match = False
                        break
                    
                    row_value = row[key]
                    
                    if where_operator == '=':
                        if row_value != value:
                            match = False
                            break
                    elif where_operator == 'LIKE':
                        if isinstance(value, str) and isinstance(row_value, str):
                            pattern = value.replace('%', '.*').replace('_', '.')
                            import re
                            if not re.search(pattern, row_value, re.IGNORECASE):
                                match = False
                                break
                        else:
                            match = False
                            break
            
            if match:
                # Validate new values
                for col_name, new_value in set_values.items():
                    if col_name in self.columns:
                        col = self.columns[col_name]
                        if not col.validate(new_value):
                            raise ValueError(f"Invalid value for column {col_name}")
                
                # Update the row
                old_row = row.copy()
                row.update(set_values)
                updated_count += 1
                
                # Update indexes
                for index_name, index in self.indexes.items():
                    index.update(i, old_row, row)
        
        if updated_count > 0:
            self.save_data()
        
        return updated_count

    def delete(self, where: Optional[Dict[str, Any]] = None, where_operator: str = '=') -> int:
        """Delete rows from the table"""
        deleted_indices = []
        
        for i, row in enumerate(self.data):
            match = True
            if where:
                for key, value in where.items():
                    if key not in row:
                        match = False
                        break
                    
                    row_value = row[key]
                    
                    if where_operator == '=':
                        if row_value != value:
                            match = False
                            break
                    elif where_operator == 'LIKE':
                        if isinstance(value, str) and isinstance(row_value, str):
                            pattern = value.replace('%', '.*').replace('_', '.')
                            import re
                            if not re.search(pattern, row_value, re.IGNORECASE):
                                match = False
                                break
                        else:
                            match = False
                            break
            
            if match:
                deleted_indices.append(i)
        
        # Remove in reverse order
        for i in sorted(deleted_indices, reverse=True):
            old_row = self.data.pop(i)
            
            # Update indexes
            for index_name, index in self.indexes.items():
                index.remove(i, old_row)
        
        if deleted_indices:
            self.save_data()
        
        return len(deleted_indices)
    
    
    def create_index(self, column_name: str, index_name: Optional[str] = None):
        """Create an index on a column"""
        if column_name not in self.columns:
            raise ValueError(f"Column {column_name} does not exist")
        
        if not index_name:
            index_name = f"idx_{self.name}_{column_name}"
        
        index = IndexManager()
        # Build index from existing data
        for i, row in enumerate(self.data):
            if column_name in row:
                index.add(i, {column_name: row[column_name]})
        
        self.indexes[index_name] = index
    
    def drop_index(self, index_name: str):
        """Drop an index"""
        if index_name in self.indexes:
            del self.indexes[index_name]

class Database:
    def __init__(self, name: str = "default"):
        self.name = name
        self.tables = {}
        self.storage = StorageEngine()
        self.load_metadata()
    
    def load_metadata(self):
        """Load database metadata from storage"""
        metadata = self.storage.load_metadata()
        if metadata:
            for table_name, table_info in metadata.get('tables', {}).items():
                columns = [Column.from_dict(col_data) for col_data in table_info['columns']]
                self.tables[table_name] = Table(table_name, columns, self)
    
    def save_metadata(self):
        """Save database metadata to storage"""
        metadata = {
            'tables': {}
        }
        
        for table_name, table in self.tables.items():
            metadata['tables'][table_name] = {
                'columns': [col.to_dict() for col in table.columns.values()]
            }
        
        self.storage.save_metadata(metadata)
    
    def create_table(self, name: str, columns: List[Column]):
        """Create a new table"""
        if name in self.tables:
            raise ValueError(f"Table {name} already exists")
        
        # Validate only one primary key
        primary_keys = [col for col in columns if col.is_primary]
        if len(primary_keys) > 1:
            raise ValueError("Only one primary key allowed per table")
        
        table = Table(name, columns, self)
        self.tables[name] = table
        self.save_metadata()
        return table
    
    def drop_table(self, name: str):
        """Drop a table"""
        if name in self.tables:
            del self.tables[name]
            self.storage.delete_table(name)
            self.save_metadata()
    
    def get_table(self, name: str) -> Optional[Table]:
        """Get a table by name"""
        return self.tables.get(name)
    
    def execute_query(self, query: str) -> Any:
        """Execute a SQL-like query"""
        try:
            from parser.sql_parser import parse_query
        except ImportError:
            import sys
            import os
            parser_path = os.path.join(os.path.dirname(__file__), '..', 'parser')
            if parser_path not in sys.path:
                sys.path.append(parser_path)
            from sql_parser import parse_query
        
        parsed_query = parse_query(query)
        return self.execute_parsed_query(parsed_query)
    
    def execute_parsed_query(self, parsed_query: Dict[str, Any]) -> Any:
        """Execute a parsed query"""
        query_type = parsed_query.get('type')
        
        if query_type == 'CREATE_TABLE':
            columns = []
            for col_def in parsed_query['columns']:
                col = Column(
                    name=col_def['name'],
                    data_type=col_def['data_type'].upper(),
                    is_primary=col_def.get('primary', False),
                    is_unique=col_def.get('unique', False),
                    nullable=col_def.get('nullable', True)
                )
                columns.append(col)
            return self.create_table(parsed_query['table_name'], columns)
        
        elif query_type == 'DROP_TABLE':
            return self.drop_table(parsed_query['table_name'])
        
        elif query_type == 'INSERT':
            table = self.get_table(parsed_query['table_name'])
            if not table:
                raise ValueError(f"Table {parsed_query['table_name']} not found")
            return table.insert(parsed_query['values'])
        
        elif query_type == 'SELECT':
            table = self.get_table(parsed_query['table_name'])
            if not table:
                raise ValueError(f"Table {parsed_query['table_name']} not found")
            
            # Get WHERE operator (default to '=')
            where_operator = parsed_query.get('where_operator', '=')
            rows = table.select(parsed_query.get('where'), where_operator)
            
            # Handle JOIN if specified
            if 'join' in parsed_query:
                join_table = self.get_table(parsed_query['join']['table'])
                if not join_table:
                    raise ValueError(f"Join table {parsed_query['join']['table']} not found")
                
                join_type = parsed_query['join']['type']
                left_col = parsed_query['join']['on'][0]
                right_col = parsed_query['join']['on'][1]
                
                joined_rows = []
                for left_row in rows:
                    right_rows = join_table.select({right_col: left_row.get(left_col)})
                    
                    if join_type == 'INNER':
                        if right_rows:
                            for right_row in right_rows:
                                joined_row = left_row.copy()
                                joined_row.update({f"{join_table.name}.{k}": v for k, v in right_row.items()})
                                joined_rows.append(joined_row)
                    elif join_type == 'LEFT':
                        if right_rows:
                            for right_row in right_rows:
                                joined_row = left_row.copy()
                                joined_row.update({f"{join_table.name}.{k}": v for k, v in right_row.items()})
                                joined_rows.append(joined_row)
                        else:
                            joined_row = left_row.copy()
                            for col in join_table.columns:
                                joined_row[f"{join_table.name}.{col}"] = None
                            joined_rows.append(joined_row)
                
                rows = joined_rows
            
            return rows
        
        elif query_type == 'UPDATE':
            table = self.get_table(parsed_query['table_name'])
            if not table:
                raise ValueError(f"Table {parsed_query['table_name']} not found")
            
            where_operator = parsed_query.get('where_operator', '=')
            return table.update(
                parsed_query['set_values'], 
                parsed_query.get('where'), 
                where_operator
            )
        
        elif query_type == 'DELETE':
            table = self.get_table(parsed_query['table_name'])
            if not table:
                raise ValueError(f"Table {parsed_query['table_name']} not found")
            
            where_operator = parsed_query.get('where_operator', '=')
            return table.delete(parsed_query.get('where'), where_operator)
        
        elif query_type == 'CREATE_INDEX':
            table = self.get_table(parsed_query['table_name'])
            if not table:
                raise ValueError(f"Table {parsed_query['table_name']} not found")
            return table.create_index(parsed_query['column_name'], parsed_query.get('index_name'))
        
        elif query_type == 'DROP_INDEX':
            table = self.get_table(parsed_query['table_name'])
            if not table:
                raise ValueError(f"Table {parsed_query['table_name']} not found")
            return table.drop_index(parsed_query['index_name'])
        
        else:
            raise ValueError(f"Unknown query type: {query_type}")