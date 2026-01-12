import re
from typing import Dict, Any, List

class SQLParser:
    @staticmethod
    def parse_query(query: str) -> Dict[str, Any]:
        query = query.strip().upper()
        
        if query.startswith('CREATE TABLE'):
            return SQLParser._parse_create_table(query)
        elif query.startswith('DROP TABLE'):
            return SQLParser._parse_drop_table(query)
        elif query.startswith('INSERT INTO'):
            return SQLParser._parse_insert(query)
        elif query.startswith('SELECT'):
            return SQLParser._parse_select(query)
        elif query.startswith('UPDATE'):
            return SQLParser._parse_update(query)
        elif query.startswith('DELETE FROM'):
            return SQLParser._parse_delete(query)
        elif query.startswith('CREATE INDEX'):
            return SQLParser._parse_create_index(query)
        elif query.startswith('DROP INDEX'):
            return SQLParser._parse_drop_index(query)
        else:
            raise ValueError(f"Unsupported SQL query: {query}")
    
    @staticmethod
    def _parse_create_table(query: str) -> Dict[str, Any]:
        # Parse CREATE TABLE query
        pattern = r'CREATE TABLE (\w+)\s*\((.*)\)'
        match = re.search(pattern, query, re.IGNORECASE | re.DOTALL)
        
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        
        table_name = match.group(1).lower()
        columns_text = match.group(2).strip()
        
        columns = []
        column_defs = re.split(r',\s*(?![^()]*\))', columns_text)
        
        for col_def in column_defs:
            col_def = col_def.strip()
            if not col_def:
                continue
            
            # Parse column definition
            col_parts = col_def.split()
            col_name = col_parts[0].lower()
            col_type = col_parts[1].upper()
            
            col_info = {
                'name': col_name,
                'data_type': col_type,
                'primary': 'PRIMARY KEY' in col_def.upper(),
                'unique': 'UNIQUE' in col_def.upper(),
                'nullable': 'NOT NULL' not in col_def.upper()
            }
            
            columns.append(col_info)
        
        return {
            'type': 'CREATE_TABLE',
            'table_name': table_name,
            'columns': columns
        }
    
    @staticmethod
    def _parse_drop_table(query: str) -> Dict[str, Any]:
        pattern = r'DROP TABLE (\w+)'
        match = re.search(pattern, query, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid DROP TABLE syntax")
        
        return {
            'type': 'DROP_TABLE',
            'table_name': match.group(1).lower()
        }
    
    @staticmethod
    def _parse_insert(query: str) -> Dict[str, Any]:
        pattern = r'INSERT INTO (\w+)\s*\((.*?)\)\s*VALUES\s*\((.*)\)'
        match = re.search(pattern, query, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid INSERT syntax")
        
        table_name = match.group(1).lower()
        columns = [col.strip().lower() for col in match.group(2).split(',')]
        values_text = match.group(3)
        
        # Parse values
        values = []
        current = ''
        in_quotes = False
        for char in values_text:
            if char == "'" and not in_quotes:
                in_quotes = True
            elif char == "'" and in_quotes:
                in_quotes = False
            elif char == ',' and not in_quotes:
                values.append(current.strip())
                current = ''
                continue
            current += char
        
        if current:
            values.append(current.strip())
        
        # Convert values to appropriate types
        parsed_values = {}
        for col, val in zip(columns, values):
            if val.upper() == 'NULL':
                parsed_values[col] = None
            elif val.startswith("'") and val.endswith("'"):
                parsed_values[col] = val[1:-1]
            elif '.' in val:
                try:
                    parsed_values[col] = float(val)
                except:
                    parsed_values[col] = val
            else:
                try:
                    parsed_values[col] = int(val)
                except:
                    parsed_values[col] = val
        
        return {
            'type': 'INSERT',
            'table_name': table_name,
            'values': parsed_values
        }
    
    @staticmethod
    def _parse_select(query: str) -> Dict[str, Any]:
        # Parse SELECT with optional JOIN
        select_pattern = r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+(WHERE\s+(.*?)))?(?:\s+(JOIN\s+(.*?)\s+ON\s+(.*?)))?$'
        match = re.search(select_pattern, query, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid SELECT syntax")
        
        table_name = match.group(2).lower()
        where_clause = match.group(4)
        join_clause = match.group(6)
        join_on = match.group(7)
        
        parsed = {
            'type': 'SELECT',
            'table_name': table_name,
            'where': {}
        }
        
        if where_clause:
            where_parts = where_clause.split('=')
            if len(where_parts) == 2:
                key = where_parts[0].strip().lower()
                value = where_parts[1].strip().lower().strip("'")
                parsed['where'][key] = value
        
        if join_clause:
            join_table = join_clause.strip().lower()
            if join_on:
                on_parts = join_on.split('=')
                if len(on_parts) == 2:
                    left_col = on_parts[0].strip().split('.')[-1].lower()
                    right_col = on_parts[1].strip().split('.')[-1].lower()
                    
                    parsed['join'] = {
                        'type': 'INNER',  # Simple implementation
                        'table': join_table,
                        'on': [left_col, right_col]
                    }
        
        return parsed
    
    @staticmethod
    def _parse_update(query: str) -> Dict[str, Any]:
        pattern = r'UPDATE (\w+) SET (.*?)(?: WHERE (.*))?$'
        match = re.search(pattern, query, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        
        table_name = match.group(1).lower()
        set_clause = match.group(2)
        where_clause = match.group(3)
        
        # Parse SET clause
        set_values = {}
        set_parts = set_clause.split(',')
        for part in set_parts:
            key_val = part.split('=')
            if len(key_val) == 2:
                key = key_val[0].strip().lower()
                value = key_val[1].strip().strip("'")
                set_values[key] = value
        
        # Parse WHERE clause
        where = {}
        if where_clause:
            where_parts = where_clause.split('=')
            if len(where_parts) == 2:
                key = where_parts[0].strip().lower()
                value = where_parts[1].strip().strip("'")
                where[key] = value
        
        return {
            'type': 'UPDATE',
            'table_name': table_name,
            'set_values': set_values,
            'where': where if where else None
        }
    
    @staticmethod
    def _parse_delete(query: str) -> Dict[str, Any]:
        pattern = r'DELETE FROM (\w+)(?: WHERE (.*))?$'
        match = re.search(pattern, query, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid DELETE syntax")
        
        table_name = match.group(1).lower()
        where_clause = match.group(2)
        
        where = {}
        if where_clause:
            where_parts = where_clause.split('=')
            if len(where_parts) == 2:
                key = where_parts[0].strip().lower()
                value = where_parts[1].strip().strip("'")
                where[key] = value
        
        return {
            'type': 'DELETE',
            'table_name': table_name,
            'where': where if where else None
        }
    
    @staticmethod
    def _parse_create_index(query: str) -> Dict[str, Any]:
        pattern = r'CREATE INDEX (\w+) ON (\w+) \((\w+)\)'
        match = re.search(pattern, query, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid CREATE INDEX syntax")
        
        return {
            'type': 'CREATE_INDEX',
            'index_name': match.group(1).lower(),
            'table_name': match.group(2).lower(),
            'column_name': match.group(3).lower()
        }
    
    @staticmethod
    def _parse_drop_index(query: str) -> Dict[str, Any]:
        pattern = r'DROP INDEX (\w+) ON (\w+)'
        match = re.search(pattern, query, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid DROP INDEX syntax")
        
        return {
            'type': 'DROP_INDEX',
            'index_name': match.group(1).lower(),
            'table_name': match.group(2).lower()
        }

def parse_query(query: str) -> Dict[str, Any]:
    return SQLParser.parse_query(query)