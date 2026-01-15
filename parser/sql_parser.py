import re
from typing import Dict, Any, List

class SQLParser:
    @staticmethod
    def parse_query(query: str) -> Dict[str, Any]:
        query = query.strip()
        query_upper = query.upper()
        
        if query_upper.startswith('CREATE TABLE'):
            return SQLParser._parse_create_table(query)
        elif query_upper.startswith('DROP TABLE'):
            return SQLParser._parse_drop_table(query)
        elif query_upper.startswith('INSERT INTO'):
            return SQLParser._parse_insert(query)
        elif query_upper.startswith('SELECT'):
            return SQLParser._parse_select(query)
        elif query_upper.startswith('UPDATE'):
            return SQLParser._parse_update(query)
        elif query_upper.startswith('DELETE FROM'):
            return SQLParser._parse_delete(query)
        elif query_upper.startswith('CREATE INDEX'):
            return SQLParser._parse_create_index(query)
        elif query_upper.startswith('DROP INDEX'):
            return SQLParser._parse_drop_index(query)
        else:
            raise ValueError(f"Unsupported SQL query: {query}")
    
    @staticmethod
    def _parse_select(query: str) -> Dict[str, Any]:
        # Parse SELECT with optional WHERE and ORDER BY
        select_pattern = r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+(WHERE\s+(.*?)))?(?:\s+(ORDER BY\s+(.*?)))?(?:\s+(JOIN\s+(.*?)\s+ON\s+(.*?)))?$'
        match = re.search(select_pattern, query, re.IGNORECASE | re.DOTALL)
        
        if not match:
            raise ValueError(f"Invalid SELECT syntax: {query}")
        
        table_name = match.group(2).lower()
        where_clause = match.group(4)
        order_by_clause = match.group(6)
        join_clause = match.group(8)
        join_on = match.group(9)
        
        parsed = {
            'type': 'SELECT',
            'table_name': table_name,
            'where': {},
            'where_operator': '=',  # Default operator
            'order_by': None
        }
        
        if where_clause:
            where_clause = where_clause.strip()
            
            # Handle LIKE operator
            if ' LIKE ' in where_clause.upper():
                parts = re.split(r'\s+LIKE\s+', where_clause, 1, re.IGNORECASE)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    
                    # Remove quotes if present
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    parsed['where'][key] = value
                    parsed['where_operator'] = 'LIKE'
            
            # Handle = operator
            elif '=' in where_clause:
                where_parts = where_clause.split('=', 1)
                if len(where_parts) == 2:
                    key = where_parts[0].strip().lower()
                    value = where_parts[1].strip()
                    
                    # Remove quotes if present
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    elif value.isdigit():
                        value = int(value)
                    
                    parsed['where'][key] = value
                    parsed['where_operator'] = '='
        
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
                        'type': 'INNER',
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
        match = re.search(pattern, query, re.IGNORECASE | re.DOTALL)
        
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
        
        # Parse SET clause
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
                    if i + 1 < len(set_clause) and set_clause[i + 1] == "'":
                        current_value += "''"
                        i += 1
                    else:
                        in_quotes = False
                        current_value += char
                elif not in_quotes and char == ',':
                    set_values[current_key] = current_value.strip()
                    current_key = ""
                    current_value = ""
                    parsing_key = True
                else:
                    current_value += char
            i += 1
        
        if current_key and current_value:
            set_values[current_key] = current_value.strip()
        
        # Clean values
        for key, value in set_values.items():
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
                value = value.replace("''", "'")
            set_values[key] = value
        
        # Parse WHERE clause
        where = {}
        where_operator = '='
        if where_part:
            where_clause = where_part[5:].strip()
            
            # Handle LIKE in WHERE
            if ' LIKE ' in where_clause.upper():
                parts = re.split(r'\s+LIKE\s+', where_clause, 1, re.IGNORECASE)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    where[key] = value
                    where_operator = 'LIKE'
            
            # Handle = in WHERE
            elif '=' in where_clause:
                where_match = re.match(r'(.*?)\s*=\s*(.*)', where_clause, re.IGNORECASE)
                if where_match:
                    key = where_match.group(1).strip().lower()
                    value = where_match.group(2).strip()
                    
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                        value = value.replace("''", "'")
                    elif value.isdigit():
                        value = int(value)
                    
                    where[key] = value
                    where_operator = '='
        
        return {
            'type': 'UPDATE',
            'table_name': table_name,
            'set_values': set_values,
            'where': where if where else None,
            'where_operator': where_operator
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
        
        # Get table name
        table_part_lower = table_part.upper()
        if 'DELETE FROM' in table_part_lower:
            delete_from_index = table_part_lower.find('DELETE FROM') + len('DELETE FROM')
            table_name_part = table_part[delete_from_index:].strip()
        else:
            table_name_part = table_part.strip()        
        table_name = table_name_part.split()[0].lower() if table_name_part else ""
        
        # Parse WHERE clause
        where = {}
        where_operator = '='
        if where_part:
            where_clause = where_part[5:].strip()
            
            # Handle LIKE
            if ' LIKE ' in where_clause.upper():
                parts = re.split(r'\s+LIKE\s+', where_clause, 1, re.IGNORECASE)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    
                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    where[key] = value
                    where_operator = 'LIKE'
            
            # Handle =
            elif '=' in where_clause:
                key, value = where_clause.split('=', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                    value = value.replace("''", "'")
                elif value.isdigit():
                    value = int(value)
                
                where[key] = value
                where_operator = '='
        
        return {
            'type': 'DELETE',
            'table_name': table_name,
            'where': where if where else None,
            'where_operator': where_operator
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
    
    @staticmethod
    def _parse_create_table(query: str) -> Dict[str, Any]:
        pattern = r'CREATE TABLE (\w+)\s*\((.*)\)'
        match = re.search(pattern, query, re.IGNORECASE | re.DOTALL)
        
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        
        table_name = match.group(1).lower()
        columns_text = match.group(2)
        
        columns = []
        current = ''
        paren_depth = 0
        
        for char in columns_text:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                col_def = current.strip()
                if col_def:
                    columns.append(SQLParser._parse_column_definition(col_def))
                current = ''
                continue
            current += char
        
        if current.strip():
            columns.append(SQLParser._parse_column_definition(current.strip()))
        
        return {
            'type': 'CREATE_TABLE',
            'table_name': table_name,
            'columns': columns
        }
    
    @staticmethod
    def _parse_column_definition(col_def: str) -> Dict[str, Any]:
        col_def = col_def.strip()
        parts = col_def.split()
        
        column = {
            'name': parts[0].lower(),
            'data_type': parts[1].upper() if len(parts) > 1 else 'TEXT',
            'primary': False,
            'unique': False,
            'nullable': True
        }
        
        col_def_upper = col_def.upper()
        if 'PRIMARY KEY' in col_def_upper:
            column['primary'] = True
            column['nullable'] = False
        if 'UNIQUE' in col_def_upper:
            column['unique'] = True
        if 'NOT NULL' in col_def_upper:
            column['nullable'] = False
        
        return column

def parse_query(query: str) -> Dict[str, Any]:
    return SQLParser.parse_query(query)