import os
import jwt
import datetime

# Define your secret key (use a strong secret key in production)
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-me')

def generate_jwt(payload):
    """
    Generates a JWT token.

    :param payload: The payload (typically user data like user_id) to include in the token.
    :return: A JWT token.
    """
    # Set expiration time for the token (e.g., 1 hour)
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    # Add expiration time to payload
    payload['exp'] = expiration_time

    # Encode the token with the payload and secret key
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    return token

def verify_jwt(token):
    try:
        # Decode the token using the secret key
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        return {'message': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'message': 'Invalid token'}
