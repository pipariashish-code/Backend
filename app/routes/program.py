# from flask import Flask, jsonify, request
# import mysql.connector

# # Initialize Flask app
# app = Flask(__name__)

# # MySQL Connection
# connection = mysql.connector.connect(
#     host='localhost',
#     port=3306,
#     user='root',
#     password='root',
#     database='user'
# )
# cursor = connection.cursor(dictionary=True)

# @app.route('/api/programs', methods=['GET'])
# def get_programs():
#     # Retrieve query parameters
#     campus = request.args.get('campus', '')
#     search = request.args.get('search', '').lower()
#     disciplines = request.args.getlist('disciplines')
#     duration = request.args.get('duration', '')

#     # Build MySQL query filters based on parameters
#     query = "SELECT * FROM program_data WHERE 1=1"
#     params = []
    
#     if campus:
#         query += " AND campus = %s"
#         params.append(campus)
#     if search:
#         query += " AND program_name LIKE %s"
#         params.append(f"%{search}%")
#     if disciplines:
#         query += " AND department IN (%s)"  # Assuming 'disciplines' is a comma-separated list
#         params.append(', '.join(disciplines))
#     if duration:
#         query += " AND duration = %s"
#         params.append(duration)

#     try:
#         # Execute the query
#         cursor.execute(query, params)
#         programs = cursor.fetchall()

#         # Format the result
#         formatted_programs = []
#         for program in programs:
#             formatted_program = {
#                 'Program Name': program.get('program_name', ''),
#                 'Department': program.get('department', ''),
#                 'Campus': program.get('campus', ''),
#                 'Duration': program.get('duration', ''),
#                 'Program Type': program.get('program_type', ''),
#             }
#             formatted_programs.append(formatted_program)

#         return jsonify({'status': 'success', 'data': formatted_programs})

#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})

# # Close the MySQL connection when the app is stopped
# @app.before_first_request
# def before_first_request():
#     pass

# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     cursor.close()
#     connection.close()

# if __name__ == '__main__':
#     app.run(debug=True)


# from flask import Flask, jsonify
# from flask_cors import CORS
# import mysql.connector
# from mysql.connector import Error

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# # Database configuration
# DB_CONFIG = {
#     'host': 'localhost',
#     'port': 3306,
#     'user': 'root',
#     'password': 'root',
#     'database': 'user'
# }

# def get_db_connection():
#     """Create and return a database connection"""
#     try:
#         connection = mysql.connector.connect(**DB_CONFIG)
#         return connection
#     except Error as e:
#         print(f"Error connecting to MySQL Database: {e}")
#         return None

# @app.route('/api/programs', methods=['GET'])
# def get_programs():
#     try:
#         connection = get_db_connection()
        
#         if connection is None:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Database connection failed'
#             }), 500

#         cursor = connection.cursor(dictionary=True)
        
#         # Query to fetch all programs
#         query = """
#         SELECT 
#             id as _id,
#             program_name as 'Program Name',
#             department as Department,
#             campus as Campus,
#             duration as Duration,
#             program_type as 'Program Type'
#         FROM programs
#         """
        
#         cursor.execute(query)
#         programs = cursor.fetchall()
        
#         cursor.close()
#         connection.close()
        
#         return jsonify({
#             'status': 'success',
#             'data': programs
#         })

#     except Error as e:
#         print(f"Error: {e}")
#         return jsonify({
#             'status': 'error',
#             'message': str(e)
#         }), 500

# # Error handlers
# @app.errorhandler(404)
# def not_found_error(error):
#     return jsonify({
#         'status': 'error',
#         'message': 'Resource not found'
#     }), 404

# @app.errorhandler(500)
# def internal_error(error):
#     return jsonify({
#         'status': 'error',
#         'message': 'Internal server error'
#     }), 500

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Blueprint, jsonify
from .. import get_mysql_connection
from mysql.connector import Error


program_bp = Blueprint('program_bp', __name__, url_prefix='/api')

@program_bp.route('/programs', methods=['GET'])
def get_programs():
    try:
        connection = get_mysql_connection()
        
        if connection is None:
            return jsonify({
                'status': 'error',
                'message': 'Database connection failed'
            }), 500

        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            id as _id,
            program_name as 'Program_Name',
            department as Department,
            campus as Campus,
            duration as Duration,
            program_type as 'Program_Type'
        FROM program_data
        """
        
        cursor.execute(query)
        programs = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': programs
        })

    except Error as e:
        print(f"Error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500