import mysql.connector
import os

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'studio_beleza')
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Erro de conexão: {err}")
        return None
def get_dict_cursor(connection): 
    return connection.cursor(dictionary=True)