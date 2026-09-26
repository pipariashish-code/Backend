import mysql.connector
from mysql.connector import Error

# Database connection details
host = 'localhost'
port = 3306
user = 'root'
password = 'root'
database = 'user'

# Try to connect to the MySQL database
try:
    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    
    if connection.is_connected():
        print("Connection successful. The MySQL server is running.")
    
except Error as e:
    print(f"Error: {e}")
    
finally:
    if connection.is_connected():
        connection.close()
