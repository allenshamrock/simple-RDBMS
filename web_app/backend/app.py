from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the core module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from core.database import Database
from parser.sql_parser import parse_query

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize database
db = Database("contact_manager")

def initialize_database():
    """Initialize database with required tables"""
    try:
        # Create contacts table if it doesn't exist
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

# Initialize database on startup
initialize_database()

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
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a single contact by ID"""
    try:
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
        query = f"""
        SELECT * FROM contacts 
        WHERE name LIKE '%{search_query}%' 
        OR email LIKE '%{search_query}%' 
        OR phone LIKE '%{search_query}%'
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
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        query = f"""
        INSERT INTO contacts (name, email, phone, address, company, created_at) 
        VALUES ('{data['name']}', '{data['email']}', 
                '{data.get('phone', '')}', '{data.get('address', '')}', 
                '{data.get('company', '')}', '{datetime.now().strftime('%Y-%m-%d')}')
        """
        
        result = db.execute_query(query)
        return jsonify({'success': True, 'id': result, 'message': 'Contact created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update an existing contact"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        set_parts = []
        for key, value in data.items():
            if key != 'id':  # Don't update ID
                set_parts.append(f"{key} = '{value}'")
        
        if not set_parts:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        
        set_clause = ', '.join(set_parts)
        query = f"UPDATE contacts SET {set_clause} WHERE id = {contact_id}"
        
        result = db.execute_query(query)
        if result > 0:
            return jsonify({'success': True, 'message': 'Contact updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact"""
    try:
        query = f"DELETE FROM contacts WHERE id = {contact_id}"
        result = db.execute_query(query)
        
        if result > 0:
            return jsonify({'success': True, 'message': 'Contact deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'database': 'connected'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)