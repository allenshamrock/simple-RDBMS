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
    def _parse_select(query: str) -> Dict[str, Any]:
        # Parse SELECT with optional WHERE and ORDER BY
        select_pattern = r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+(WHERE\s+(.*?)))?(?:\s+(ORDER BY\s+(.*?)))?(?:\s+(JOIN\s+(.*?)\s+ON\s+(.*?)))?$'
        match = re.search(select_pattern, query, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid SELECT syntax")
        
        table_name = match.group(2).lower()
        where_clause = match.group(4)
        order_by_clause = match.group(6)
        join_clause = match.group(8)
        join_on = match.group(9)
        
        parsed = {
            'type': 'SELECT',
            'table_name': table_name,
            'where': {},
            'order_by': None
        }
        
        if where_clause:
            # Handle simple WHERE conditions (key=value)
            where_parts = where_clause.split('=')
            if len(where_parts) == 2:
                key = where_parts[0].strip().lower()
                value = where_parts[1].strip()
                
                # Remove quotes if present
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                elif value.isdigit():
                    value = int(value)
                
                parsed['where'][key] = value
        
        if order_by_clause:
            parsed['order_by'] = order_by_clause.strip().lower()
        
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
    def _parse_update(query: str) -> Dict[str, Any]:
        # Use a more robust UPDATE parser
        query_upper = query.upper()
        
        # Find WHERE clause
        where_index = query_upper.find('WHERE')
        
        if where_index != -1:
            main_part = query[:where_index].strip()
            where_part = query[where_index:].strip()
        else:
            main_part = query.strip()
            where_part = ""
        
        # Parse UPDATE ... SET part
        update_match = re.match(r'UPDATE\s+(\w+)\s+SET\s+(.*)', main_part, re.IGNORECASE)
        if not update_match:
            raise ValueError("Invalid UPDATE syntax")
        
        table_name = update_match.group(1).lower()
        set_clause = update_match.group(2).strip()
        
        # Parse SET clause more carefully
        set_values = {}
        i = 0
        current_key = ""
        current_value = ""
        in_quotes = False
        parsing_key = True
        
        while i < len(set_clause):
            char = set_clause[i]
            
            if parsing_key:
                if char == '=':
                    parsing_key = False
                    current_key = current_key.strip().lower()
                else:
                    current_key += char
            else:
                if not in_quotes and char == "'":
                    in_quotes = True
                    current_value += char
                elif in_quotes and char == "'":
                    # Check for escaped quote
                    if i + 1 < len(set_clause) and set_clause[i + 1] == "'":
                        current_value += "''"
                        i += 1  # Skip next quote
                    else:
                        in_quotes = False
                        current_value += char
                elif not in_quotes and char == ',':
                    # End of this key-value pair
                    set_values[current_key] = current_value.strip()
                    current_key = ""
                    current_value = ""
                    parsing_key = True
                else:
                    current_value += char
            i += 1
        
        # Add the last key-value pair
        if current_key and current_value:
            set_values[current_key] = current_value.strip()
        
        # Clean values (remove surrounding quotes but keep escaped ones)
        for key, value in set_values.items():
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]  # Remove quotes
                # Keep escaped quotes as single quotes
                value = value.replace("''", "'")
            set_values[key] = value
        
        # Parse WHERE clause
        where = {}
        if where_part:
            where_match = re.match(r'WHERE\s+(.*?)\s*=\s*(.*)', where_part, re.IGNORECASE)
            if where_match:
                key = where_match.group(1).strip().lower()
                value = where_match.group(2).strip()
                
                # Clean value
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                    value = value.replace("''", "'")
                elif value.isdigit():
                    value = int(value)
                
                where[key] = value
        
        return {
            'type': 'UPDATE',
            'table_name': table_name,
            'set_values': set_values,
            'where': where if where else None
        }
    
    @staticmethod
    def _parse_delete(query: str) -> Dict[str, Any]:
        query_upper = query.upper()
        
        where_index = query_upper.find('WHERE')
        
        if where_index != -1:
            table_part = query[:where_index].strip()
            where_part = query[where_index:].strip()
        else:
            table_part = query.strip()
            where_part = ""
        
        # Remove "DELETE FROM" from table_part to get just the table name
        # Case-insensitive removal
        table_part_lower = table_part.upper()
        if 'DELETE FROM' in table_part_lower:
            # Find where "DELETE FROM" ends
            delete_from_index = table_part_lower.find('DELETE FROM') + len('DELETE FROM')
            table_name_part = table_part[delete_from_index:].strip()
        else:
            table_name_part = table_part.strip()        
        table_name = table_name_part.split()[0].lower() if table_name_part else ""
        
        # Parse WHERE clause
        where = {}
        if where_part:
            # Remove "WHERE" from the beginning
            where_clause = where_part[5:].strip() 
            
            if '=' in where_clause:
                key, value = where_clause.split('=', 1)
                key = key.strip().lower()
                value = value.strip()
                
                # Clean value
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                    value = value.replace("''", "'")
                elif value.isdigit():
                    value = int(value)
                
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