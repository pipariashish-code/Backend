from flask import Blueprint, request, jsonify, current_app
from flask_bcrypt import Bcrypt
import jwt #pyjwt
import datetime
import os
from app.routes.utils import generate_jwt
from .. import get_mysql_connection
from werkzeug.utils import secure_filename
import uuid
from app.routes.utils import generate_jwt
from .. import get_mysql_connection

bcrypt = Bcrypt()

# Blueprint for authentication
auth_bp = Blueprint('auth', __name__)
# Register the blueprint with the app

# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.form
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    school = data.get('school')
    city = data.get('city')
    state = data.get('state')
    password = data.get('password')
    print(f"Received data: {data}")

    if not all([name, email, phone, school, city, state, password]):
        return jsonify({'message': 'All fields are required'}), 400

    connection = None
    cursor = None
    try:
        # Connect to the database
        connection = get_mysql_connection()
        cursor = connection.cursor()

        # Insert user data into the database
        query = """
            INSERT INTO users (name, email, phone, school, city, state, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute(query, (name, email, phone, school, city, state, hashed_password))
        connection.commit()

        # Assume we have an `id` for the new user
        user_id = cursor.lastrowid  # Get the ID of the inserted row
        print(user_id)
        

        # Generate a JWT token (this part assumes you have a function to create JWTs)
        token = generate_jwt({'id': user_id, 'email': email})

        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {
                'id': user_id,
                'email': email
            }
        }), 201
    except Exception as e:
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 400
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# @auth_bp.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     email_or_username = data.get('username')
#     password = data.get('password')

#     try:
#         connection = get_mysql_connection()
#         cursor = connection.cursor(dictionary=True)

#         query = """
#             SELECT * FROM users WHERE email = %s OR name = %s
#         """
#         cursor.execute(query, (email_or_username, email_or_username))
#         user = cursor.fetchone()

#         if user and (user['password'], password):
#             token = jwt.encode({'id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)},
#                                current_app.config['SECRET_KEY'], algorithm='HS256')
#             return jsonify({'token': token, 'user': {'id': user['id'], 'name': user['name'], 'role': user['role']}})
#         else:
#             return jsonify({'message': 'Invalid credentials'}), 401
#     except Exception as e:
#         return jsonify({'message': 'Login failed', 'error': str(e)}), 400
#     finally:
#         cursor.close()
#         connection.close()

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
        
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({'message': 'Content-Type must be application/json'}), 400

    data = request.json
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    email_or_username = data.get('username')
    password = data.get('password')

    if not email_or_username or not password:
        return jsonify({'message': 'Username/email and password are required'}), 400

    try:
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)

        # Query to check user credentials
        query = """
            SELECT id, name, password, email
            FROM users 
            WHERE email = %s OR name = %s
        """
        cursor.execute(query, (email_or_username, email_or_username))
        user = cursor.fetchone()

        if not user:
            return jsonify({'message': 'User not found'}), 401

        # Passwords are stored as bcrypt hashes
        try:
            password_ok = bcrypt.check_password_hash(user['password'], password)
        except ValueError:
            password_ok = False  # stored value is not a valid hash

        if password_ok:
            # Generate token with minimal payload
            token = generate_jwt({
                'id': user['id'],
                'email': user['email']
            })

            return jsonify({
                'token': token,
                'user': {
                    'id': user['id'],
                    'name': user['name']
                }
            }), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

    except Exception as e:
        print(f"Login error: {str(e)}")  # For debugging
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()



###################################################################################################################
####################  Mentor registration #########################################

def create_unique_filename(original_filename):
    """Create a unique filename to prevent overwrites"""
    ext = original_filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"

def validate_file_size(file, max_size_mb=5):
    """Validate file size (default max 5MB)"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset file pointer
    return size <= max_size_mb * 1024 * 1024

@auth_bp.route('/register_mentor', methods=['POST'])
def register_mentor():
    try:
        # Get form data
        data = request.form
        files = request.files
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'school', 'city', 'state', 'collegeId', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'message': 'Missing required fields',
                'fields': missing_fields
            }), 400

        # Validate files
        if 'collegeIdProof' not in files or 'resume' not in files:
            return jsonify({'message': 'Both college ID proof and resume are required'}), 400

        college_id_proof = files['collegeIdProof']
        resume = files['resume']

        # Validate file types
        if not allowed_file(college_id_proof.filename) or not allowed_file(resume.filename):
            return jsonify({'message': 'Invalid file type. Allowed types are: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400

        # Validate file sizes
        if not validate_file_size(college_id_proof) or not validate_file_size(resume):
            return jsonify({'message': 'File size too large. Maximum size is 5MB per file'}), 400

        # Create database connection
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if email already exists
        cursor.execute("SELECT id FROM mentor_registration WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            return jsonify({'message': 'Email already registered'}), 409

        # Hash password
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        # Save files with unique names
        college_id_filename = create_unique_filename(secure_filename(college_id_proof.filename))
        resume_filename = create_unique_filename(secure_filename(resume.filename))

        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Save files
        college_id_path = os.path.join(UPLOAD_FOLDER, college_id_filename)
        resume_path = os.path.join(UPLOAD_FOLDER, resume_filename)

        college_id_proof.save(college_id_path)
        resume.save(resume_path)

        # Insert mentor data
        query = """
            INSERT INTO mentor_registration (
                name, email, phone, school, city, state, 
                college_id, college_id_proof_path, resume_path, 
                password, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            data['name'], data['email'], data['phone'],
            data['school'], data['city'], data['state'],
            data['collegeId'], college_id_filename, resume_filename,
            hashed_password, 'pending', datetime.datetime.now()
        )

        cursor.execute(query, values)
        connection.commit()
        mentor_id = cursor.lastrowid

        # Generate JWT token
        token = generate_jwt({
            'id': mentor_id,
            'email': data['email'],
            'role': 'mentor'
        })

        return jsonify({
            'message': 'Mentor registration successful',
            'token': token,
            'mentor': {
                'id': mentor_id,
                'email': data['email'],
                'name': data['name'],
                'status': 'pending'
            }
        }), 201

    except Exception as e:
        # Log the error for debugging (implement proper logging)
        print(f"Error in mentor registration: {str(e)}")
        
        # Cleanup any saved files if registration failed
        if 'college_id_path' in locals():
            try: os.remove(college_id_path)
            except: pass
        if 'resume_path' in locals():
            try: os.remove(resume_path)
            except: pass

        return jsonify({
            'message': 'Registration failed',
            'error': 'An unexpected error occurred. Please try again.'
        }), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()