from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from datetime import datetime

# Add the core module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from core.database import Database
from parser.sql_parser import parse_query

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize database
db = Database("contact_manager")

def initialize_database():
    """Initialize database with required tables"""
    try:
        create_contacts_table = """
        CREATE TABLE contacts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            address TEXT,
            company TEXT,
            created_at DATE
        )
        """
        
        db.execute_query(create_contacts_table)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database already initialized: {e}")

initialize_database()

def safe_sql_value(value):
    """Escape SQL special characters to prevent injection"""
    if value is None:
        return "NULL"
    # Escape single quotes by doubling them
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"

@app.route('/')
def index():
    return jsonify({
        'message': 'Simple RDBMS Contact Manager API',
        'endpoints': {
            'contacts': '/api/contacts',
            'single_contact': '/api/contacts/<id>',
            'search': '/api/contacts/search?q=<query>'
        }
    })

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts"""
    try:
        query = "SELECT * FROM contacts ORDER BY name"
        result = db.execute_query(query)
        print(f"GET /api/contacts - Returning {len(result) if result else 0} contacts") 
        
        # Extract just the rows from the result
        if isinstance(result, dict) and 'rows' in result:
            contacts_data = result['rows']
        elif isinstance(result, list):
            contacts_data = result
        else:
            contacts_data = []
            
        return jsonify({'success': True, 'data': contacts_data})
    except Exception as e:
        print(f"GET /api/contacts - Error: {e}")  
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a single contact by ID"""
    try:
        # Use parameterized query style
        query = f"SELECT * FROM contacts WHERE id = {contact_id}"
        result = db.execute_query(query)
        if result:
            return jsonify({'success': True, 'data': result[0]})
        else:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/search', methods=['GET'])
def search_contacts():
    """Search contacts by name, email, or phone"""
    search_query = request.args.get('q', '')
    if not search_query:
        return jsonify({'success': True, 'data': []})
    
    try:
        # Escape search term
        safe_query = search_query.replace("'", "''")
        query = f"""
        SELECT * FROM contacts 
        WHERE name LIKE '%{safe_query}%' 
        OR email LIKE '%{safe_query}%' 
        OR phone LIKE '%{safe_query}%'
        ORDER BY name
        """
        result = db.execute_query(query)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    """Create a new contact"""
    try:
        data = request.json
        
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Prepare safe values
        name = safe_sql_value(data['name'])
        email = safe_sql_value(data['email'])
        phone = safe_sql_value(data.get('phone', ''))
        address = safe_sql_value(data.get('address', ''))
        company = safe_sql_value(data.get('company', ''))
        created_at = safe_sql_value(datetime.now().strftime('%Y-%m-%d'))
        
        query = f"""
        INSERT INTO contacts (name, email, phone, address, company, created_at) 
        VALUES ({name}, {email}, {phone}, {address}, {company}, {created_at})
        """
        
        result = db.execute_query(query)
        print(f"POST /api/contacts - Created contact with result: {result}") 
        
        return jsonify({
            'success': True, 
            'data': {
                'id': result, 
                'name': data['name'],
                'email': data['email'],
                'phone': data.get('phone', ''),
                'address': data.get('address', ''),
                'company': data.get('company', ''),
                'created_at': datetime.now().strftime('%Y-%m-%d')
            },
            'message': 'Contact created successfully'
        })
    except Exception as e:
        print(f"POST /api/contacts - Error: {e}") 
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update an existing contact"""
    try:
        data = request.json
        print(f"UPDATE request for contact {contact_id}: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        set_parts = []
        for key, value in data.items():
            if key != 'id': 
                safe_value = safe_sql_value(value)
                set_parts.append(f"{key} = {safe_value}")
        
        if not set_parts:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        
        set_clause = ', '.join(set_parts)
        query = f"UPDATE contacts SET {set_clause} WHERE id = {contact_id}"
        
        print(f"UPDATE query: {query}")
        
        result = db.execute_query(query)
        print(f"UPDATE result: {result}")

        if result is not None and result != 0:
            get_query = f"SELECT * FROM contacts WHERE id = {contact_id}"
            updated_contact = db.execute_query(get_query)
            
            contact_data = None
            if isinstance(updated_contact, dict) and 'rows' in updated_contact and updated_contact['rows']:
                contact_data = updated_contact['rows'][0]
            elif isinstance(updated_contact, list) and updated_contact:
                contact_data = updated_contact[0]
            
            return jsonify({
                'success': True, 
                'message': 'Contact updated successfully',
                'data': contact_data
            })
        else:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
    except Exception as e:
        print(f"UPDATE Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact"""
    try:
        query = f"DELETE FROM contacts WHERE id = {contact_id}"
        print(f"DELETE query: {query}")
        
        result = db.execute_query(query)
        print(f"DELETE result: {result}")
        
        if result is not None and result != 0:
            return jsonify({'success': True, 'message': 'Contact deleted successfully'})
        else:
            # Check if contact still exists
            check_query = f"SELECT * FROM contacts WHERE id = {contact_id}"
            check_result = db.execute_query(check_query)
            
            exists = False
            if isinstance(check_result, dict) and 'rows' in check_result:
                exists = len(check_result['rows']) > 0
            elif isinstance(check_result, list):
                exists = len(check_result) > 0
            
            if exists:
                return jsonify({'success': False, 'error': 'Failed to delete contact'}), 500
            else:
                return jsonify({'success': False, 'error': 'Contact not found'}), 404
    except Exception as e:
        print(f"DELETE Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 5000

query_history = []

@app.route('/api/sql/execute', methods=['POST'])
def execute_sql():
    """Execute raw SQL query"""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'success': False, 'error': 'No query provided'}), 400
        
        query = data['query'].strip()
        print(f"\n{'='*50}")
        print(f"SQL EXECUTION STARTED")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        # Execute the query
        result = db.execute_query(query)
        print(f"Raw result from db.execute_query(): {result}")
        print(f"Result type: {type(result)}")
        
        # Store in history
        query_history.append({
            'id': len(query_history) + 1,
            'query': query,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 50 queries
        if len(query_history) > 50:
            query_history.pop(0)
        
        response_data = {
            'success': True,
        }
        
        if isinstance(result, list):
            print(f"Result is a list with {len(result)} items")
            response_data['data'] = result
            response_data['rows_affected'] = len(result)
        elif isinstance(result, dict):
            print(f"Result is a dict with keys: {list(result.keys())}")
            if 'rows' in result:
                response_data['data'] = result['rows']
                response_data['rows_affected'] = len(result['rows'])
            else:
                response_data['result'] = result
        elif isinstance(result, int):
            print(f"Result is an int: {result}")
            response_data['rows_affected'] = result
            response_data['message'] = f'Query affected {result} row(s)'
        else:
            print(f"Result is other type: {result}")
            response_data['result'] = result
        
        print(f"Final response data: {response_data}")
        print(f"{'='*50}")
        print(f"SQL EXECUTION COMPLETED")
        print(f"{'='*50}\n")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"\n{'='*50}")
        print(f"SQL EXECUTION ERROR")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*50}\n")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sql/schema', methods=['GET'])
@app.route('/api/sql/schema/<table_name>', methods=['GET'])
def get_schema(table_name=None):
    """Get database schema"""
    try:
        schema = []
        
        if table_name:
            table = db.get_table(table_name.lower())
            if not table:
                return jsonify({'success': False, 'error': f'Table {table_name} not found'}), 404
            
            table_schema = {
                'name': table.name,
                'columns': [],
                'indexes': []
            }
            
            for column in table.columns.values():
                table_schema['columns'].append({
                    'name': column.name,
                    'data_type': column.data_type,
                    'is_primary': column.is_primary,
                    'is_unique': column.is_unique,
                    'nullable': column.nullable
                })
            
            for index_name in table.indexes:
                # Extract column name from index name
                col_name = index_name.split('_')[-1] if '_' in index_name else 'unknown'
                table_schema['indexes'].append({
                    'name': index_name,
                    'table_name': table.name,
                    'column_name': col_name
                })
            
            schema.append(table_schema)
        else:
            # Get all tables
            for table_name, table in db.tables.items():
                table_schema = {
                    'name': table.name,
                    'columns': [],
                    'indexes': []
                }
                
                for column in table.columns.values():
                    table_schema['columns'].append({
                        'name': column.name,
                        'data_type': column.data_type,
                        'is_primary': column.is_primary,
                        'is_unique': column.is_unique,
                        'nullable': column.nullable
                    })
                
                for index_name in table.indexes:
                    col_name = index_name.split('_')[-1] if '_' in index_name else 'unknown'
                    table_schema['indexes'].append({
                        'name': index_name,
                        'table_name': table.name,
                        'column_name': col_name
                    })
                
                schema.append(table_schema)
        
        return jsonify({'success': True, 'data': schema})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sql/index', methods=['POST'])
def create_index_route():
    """Create an index"""
    try:
        data = request.json
        required_fields = ['table_name', 'column_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        table_name = data['table_name'].lower()
        column_name = data['column_name'].lower()
        index_name = data.get('index_name')
        
        table = db.get_table(table_name)
        if not table:
            return jsonify({'success': False, 'error': f'Table {table_name} not found'}), 404
        
        # Build CREATE INDEX query
        if index_name:
            query = f"CREATE INDEX {index_name} ON {table_name} ({column_name})"
        else:
            query = f"CREATE INDEX idx_{table_name}_{column_name} ON {table_name} ({column_name})"
        
        db.execute_query(query)
        
        return jsonify({
            'success': True,
            'message': f'Index created on {table_name}.{column_name}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sql/index/<table_name>/<index_name>', methods=['DELETE'])
def drop_index_route(table_name, index_name):
    """Drop an index"""
    try:
        table = db.get_table(table_name.lower())
        if not table:
            return jsonify({'success': False, 'error': f'Table {table_name} not found'}), 404
        
        query = f"DROP INDEX {index_name} ON {table_name}"
        db.execute_query(query)
        
        return jsonify({
            'success': True,
            'message': f'Index {index_name} dropped from {table_name}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sql/history', methods=['GET'])
def get_query_history():
    """Get SQL query history"""
    try:
        return jsonify({
            'success': True,
            'data': query_history[-20:] 
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'database': 'connected'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)