import cmd
import sys
from ..core.database import Database
from .sql_parser import parse_query

class RDBMSRepl(cmd.Cmd):
    intro = "Welcome to Simple RDBMS. Type 'help' for commands, 'exit' to quit."
    prompt = "rdbms> "
    
    def __init__(self):
        super().__init__()
        self.db = Database()
    
    def do_create(self, arg):
        """Create a new table: CREATE TABLE table_name (col1 TYPE, col2 TYPE)"""
        try:
            query = f"CREATE TABLE {arg}"
            result = self.db.execute_query(query)
            print(f"Table created successfully")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_insert(self, arg):
        """Insert data: INSERT INTO table_name (col1, col2) VALUES (val1, val2)"""
        try:
            query = f"INSERT INTO {arg}"
            result = self.db.execute_query(query)
            print(f"Inserted row with ID: {result}")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_select(self, arg):
        """Select data: SELECT * FROM table_name [WHERE condition] [JOIN other_table ON condition]"""
        try:
            query = f"SELECT * FROM {arg}"
            result = self.db.execute_query(query)
            
            if result:
                # Print header
                if result:
                    keys = result[0].keys()
                    header = " | ".join(keys)
                    print(header)
                    print("-" * len(header))
                    
                    # Print rows
                    for row in result:
                        values = [str(row[key]) for key in keys]
                        print(" | ".join(values))
                print(f"\n{len(result)} row(s) returned")
            else:
                print("No rows found")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_update(self, arg):
        """Update data: UPDATE table_name SET col1=val1 WHERE condition"""
        try:
            query = f"UPDATE {arg}"
            result = self.db.execute_query(query)
            print(f"Updated {result} row(s)")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_delete(self, arg):
        """Delete data: DELETE FROM table_name WHERE condition"""
        try:
            query = f"DELETE FROM {arg}"
            result = self.db.execute_query(query)
            print(f"Deleted {result} row(s)")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_drop(self, arg):
        """Drop a table: DROP TABLE table_name"""
        try:
            query = f"DROP TABLE {arg}"
            result = self.db.execute_query(query)
            print(f"Table dropped successfully")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_index(self, arg):
        """Create an index: CREATE INDEX idx_name ON table_name (column_name)"""
        try:
            query = f"CREATE INDEX {arg}"
            result = self.db.execute_query(query)
            print(f"Index created successfully")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_tables(self, arg):
        """List all tables"""
        if self.db.tables:
            print("Tables in database:")
            for table_name in self.db.tables.keys():
                print(f"  - {table_name}")
        else:
            print("No tables in database")
    
    def do_sql(self, arg):
        """Execute a full SQL statement"""
        try:
            result = self.db.execute_query(arg)
            
            if isinstance(result, list):
                if result:
                    keys = result[0].keys()
                    header = " | ".join(keys)
                    print(header)
                    print("-" * len(header))
                    
                    for row in result:
                        values = [str(row[key]) for key in keys]
                        print(" | ".join(values))
                    print(f"\n{len(result)} row(s) returned")
                else:
                    print("Query executed successfully (no rows returned)")
            elif isinstance(result, int):
                print(f"Query executed successfully ({result} rows affected)")
            else:
                print("Query executed successfully")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_exit(self, arg):
        """Exit the REPL"""
        print("Goodbye!")
        return True
    
    def do_quit(self, arg):
        """Exit the REPL"""
        return self.do_exit(arg)
    
    def do_EOF(self, arg):
        """Exit on Ctrl+D"""
        print()
        return self.do_exit(arg)

def run_repl():
    repl = RDBMSRepl()
    repl.cmdloop()

if __name__ == "__main__":
    run_repl()